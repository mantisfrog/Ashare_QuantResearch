"""Build monthly stock-universe snapshots (Phase 2).

For every month-end trading day in the requested range, screen the active
universe and write one long-format CSV per year under ``data/factor/universe/``.

Screens (a stock enters the universe only if all pass):
  - listed >= 120 trading days (market trading days since first listing),
  - not suspended on the rebalance day (it traded that day),
  - valid close and market_cap on the rebalance day,
  - trailing-120-day average amount not in the bottom 20% (liquidity),
  - not flagged ST (name-based approximation; historical ST is unavailable, so
    only the current name is used).

Point-in-time safe: only fact_daily rows with date_id <= t are read.
"""
from __future__ import annotations

import sys
from pathlib import Path

_ETL_DIR = Path(__file__).resolve().parents[1] / "etl"
if str(_ETL_DIR) not in sys.path:
    sys.path.insert(0, str(_ETL_DIR))

import argparse
from datetime import datetime

import numpy as np
import pandas as pd

import factor_io
import loaders
from etl_logging import append_summary
from factor_config import (
    CALC_VERSION,
    LIQUIDITY_DROP_FRACTION,
    LIQUIDITY_LOOKBACK_TRADE_DAYS,
    LISTED_MIN_TRADING_DAYS,
)
from paths import FACTOR_UNIVERSE_DIR

CANON_COLUMNS = [
    "date_id", "stock_code", "calc_version",
    "is_listed", "is_suspended", "listed_days",
    "liquidity_ok", "has_price", "has_market_cap",
    "is_st_approx", "in_universe", "reason",
]


def month_bound_date_id(month: str, *, upper: bool) -> int:
    """Convert YYYYMM to a date_id bound (``YYYYMM01`` or ``YYYYMM31``)."""
    value = int(month)
    return value * 100 + (31 if upper else 1)


def screen_one_date(
    window: pd.DataFrame,
    date_id: int,
    tdi_t: int,
    first_tdi: dict[str, int],
    names: dict[str, str],
    calc_version: str,
) -> pd.DataFrame:
    """Apply the universe screen to one rebalance cross-section."""
    df = window.copy()
    df["avg_amount"] = pd.to_numeric(df["avg_amount"], errors="coerce")
    df["close_t"] = pd.to_numeric(df["close_t"], errors="coerce")
    df["market_cap_t"] = pd.to_numeric(df["market_cap_t"], errors="coerce")
    df["traded_on_t"] = df["traded_on_t"].astype(int) == 1

    first = df["stock_code"].map(first_tdi)
    listed_days = tdi_t - first + 1
    listed_days = listed_days.where(first.notna(), 1)
    df["listed_days"] = listed_days.astype(int)

    name_series = df["stock_code"].map(names).fillna("")
    df["is_st_approx"] = name_series.str.upper().str.contains("ST")
    df["is_suspended"] = ~df["traded_on_t"]
    df["has_price"] = df["close_t"].notna()
    df["has_market_cap"] = df["market_cap_t"].notna()
    df["is_listed"] = True

    seasoned = df[
        (df["listed_days"] >= LISTED_MIN_TRADING_DAYS)
        & df["traded_on_t"]
        & df["avg_amount"].notna()
    ]
    if len(seasoned):
        threshold = float(seasoned["avg_amount"].quantile(LIQUIDITY_DROP_FRACTION))
        df["liquidity_ok"] = df["avg_amount"] >= threshold
    else:
        df["liquidity_ok"] = False

    conditions = [
        df["listed_days"] < LISTED_MIN_TRADING_DAYS,
        df["is_suspended"],
        ~df["has_price"],
        ~df["has_market_cap"],
        df["is_st_approx"].fillna(False),
        ~df["liquidity_ok"].fillna(False),
    ]
    reasons = ["not_listed_120d", "suspended", "no_price", "no_market_cap", "st", "illiquid"]
    df["reason"] = np.select(conditions, reasons, default="")
    df["in_universe"] = df["reason"] == ""
    df["date_id"] = date_id
    df["calc_version"] = calc_version
    return df[CANON_COLUMNS]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build monthly stock-universe snapshots.")
    parser.add_argument("--start", default="201501", help="First rebalance month YYYYMM.")
    parser.add_argument("--end", default="latest", help="Last rebalance month YYYYMM or 'latest'.")
    parser.add_argument("--factors", default="all", help="Accepted for a uniform CLI; unused here.")
    parser.add_argument("--calc-version", default=CALC_VERSION, help="calc_version stamp.")
    parser.add_argument("--rebuild", action="store_true", help="Recompute months already present.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    start_id = month_bound_date_id(args.start, upper=False)
    end_id = 99999999 if args.end == "latest" else month_bound_date_id(args.end, upper=True)

    targets = loaders.rebalance_date_ids(start_id, end_id)
    if not args.rebuild:
        done = factor_io.done_date_ids(
            FACTOR_UNIVERSE_DIR, "universe", calc_version=args.calc_version
        )
        targets = [date_id for date_id in targets if date_id not in done]

    append_summary(
        "factor_universe",
        f"range={args.start}..{args.end} months={len(targets)} version={args.calc_version}",
    )
    if not targets:
        print("[factor] build_universe: nothing to do (use --rebuild to recompute)", flush=True)
        factor_io.append_manifest(
            run_id=run_id, calc_version=args.calc_version, layer="universe",
            factor_code="universe", start_date_id=start_id, end_date_id=end_id,
            row_count=0, valid_count=0, coverage="", status="skipped",
        )
        return 0

    conn = loaders.get_connection()
    frames: list[pd.DataFrame] = []
    try:
        dateid_to_tdi, tdi_to_dateid = loaders.load_trade_day_index_maps(conn)
        min_tdi = min(tdi_to_dateid)
        first_date = loaders.load_stock_first_listing_date(conn)
        first_tdi = {
            code: dateid_to_tdi[date_id]
            for code, date_id in first_date.items()
            if date_id in dateid_to_tdi
        }
        names = loaders.load_stock_names(conn)

        for index, date_id in enumerate(targets, start=1):
            tdi_t = dateid_to_tdi.get(date_id)
            if tdi_t is None:
                continue
            window_tdi = max(min_tdi, tdi_t - (LIQUIDITY_LOOKBACK_TRADE_DAYS - 1))
            window_start = tdi_to_dateid[window_tdi]
            window = loaders.load_universe_window(conn, window_start, date_id)
            if window.empty:
                continue
            frame = screen_one_date(window, date_id, tdi_t, first_tdi, names, args.calc_version)
            frames.append(frame)
            print(
                f"  [{index}/{len(targets)}] {date_id}: "
                f"candidates={len(frame)} in_universe={int(frame['in_universe'].sum())}",
                flush=True,
            )
    finally:
        conn.close()

    result = pd.concat(frames, ignore_index=True)
    total = len(result)
    valid = int(result["in_universe"].sum())
    factor_io.write_year_partitioned_csv(result, FACTOR_UNIVERSE_DIR, "universe")

    coverage = round(valid / total, 6) if total else 0.0
    factor_io.append_manifest(
        run_id=run_id, calc_version=args.calc_version, layer="universe",
        factor_code="universe", start_date_id=targets[0], end_date_id=targets[-1],
        row_count=total, valid_count=valid, coverage=coverage, status="success",
    )
    print(
        f"[factor] universe: months={len(frames)} rows={total} "
        f"in_universe={valid} ({coverage:.1%})",
        flush=True,
    )
    append_summary("factor_universe", f"done rows={total} in_universe={valid}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
