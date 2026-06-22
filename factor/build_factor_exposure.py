"""Build processed factor exposures (Phase 3).

Per rebalance cross-section and factor: direction-align -> winsorize (MAD x3) ->
z-score + percentile rank -> neutralize on ln(market_cap) + industry. For
``financial_na`` factors, financial-sector stocks are excluded first. All
intermediate values are kept. Output: data/factor/exposure/<factor>/.
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
import preprocess
from neutralize import neutralize
from etl_logging import append_summary
from factor_config import CALC_VERSION, FINANCIAL_SECTOR_KEYWORDS
from paths import FACTOR_CATALOG_FILE, FACTOR_EXPOSURE_DIR, FACTOR_RAW_DIR

EXPOSURE_COLUMNS = [
    "date_id", "stock_code", "factor_code", "calc_version",
    "raw_value", "winsorized_value", "zscore_value",
    "neutralized_value", "percentile_rank",
]


def month_bound_date_id(month: str, *, upper: bool) -> int:
    value = int(month)
    return value * 100 + (31 if upper else 1)


def _is_financial_na(catalog: pd.DataFrame, code: str) -> bool:
    return str(catalog.loc[code, "financial_na"]).strip().lower() in ("true", "1", "t", "yes")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build processed factor exposures.")
    parser.add_argument("--start", default="201501", help="First rebalance month YYYYMM.")
    parser.add_argument("--end", default="latest", help="Last rebalance month YYYYMM or 'latest'.")
    parser.add_argument("--factors", default="all", help="Comma-separated factor_code list, or 'all'.")
    parser.add_argument("--calc-version", default=CALC_VERSION, help="calc_version stamp.")
    parser.add_argument("--rebuild", action="store_true", help="Recompute months already present.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    catalog = pd.read_csv(FACTOR_CATALOG_FILE).set_index("factor_code")
    requested = list(catalog.index) if args.factors == "all" else [c.strip() for c in args.factors.split(",")]

    start_id = month_bound_date_id(args.start, upper=False)
    end_id = 99999999 if args.end == "latest" else month_bound_date_id(args.end, upper=True)
    target_set = set(loaders.rebalance_date_ids(start_id, end_id))

    raw_cross: dict[str, dict[int, pd.Series]] = {}
    implemented: list[str] = []
    for code in requested:
        if code not in catalog.index:
            continue
        raw = factor_io.read_year_partitioned_csv(
            FACTOR_RAW_DIR, code, subdir=code, date_ids=target_set,
            calc_version=args.calc_version,
        )
        if raw.empty:
            continue
        implemented.append(code)
        raw_cross[code] = {
            int(date_id): group.set_index("stock_code")["factor_value"]
            for date_id, group in raw.groupby("date_id")
        }
    if not implemented:
        print("[factor] build_factor_exposure: no raw factors found; run build_factor_raw first", flush=True)
        return 0

    if args.rebuild:
        fully_done: set[int] = set()
    else:
        done_sets = [
            factor_io.done_date_ids(
                FACTOR_EXPOSURE_DIR, code, subdir=code, calc_version=args.calc_version
            )
            for code in implemented
        ]
        fully_done = set.intersection(*done_sets) if done_sets else set()

    dates = sorted(
        ({int(d) for code in implemented for d in raw_cross[code]} & target_set) - fully_done
    )
    append_summary("factor_exposure", f"range={args.start}..{args.end} months={len(dates)} factors={','.join(implemented)}")
    if not dates:
        print("[factor] build_factor_exposure: nothing to do (use --rebuild)", flush=True)
        return 0

    conn = loaders.get_connection()
    out_frames: dict[str, list[pd.DataFrame]] = {code: [] for code in implemented}
    try:
        industry = loaders.load_stock_industry(conn)
        financial_sectors = loaders.load_financial_sector_codes(conn, FINANCIAL_SECTOR_KEYWORDS)
        for index, date_id in enumerate(dates, start=1):
            market_cap = loaders.load_daily_snapshot(conn, date_id)["market_cap"]
            log_mc = np.log(market_cap.where(market_cap > 0))
            for code in implemented:
                cross = raw_cross[code].get(date_id)
                if cross is None or cross.empty:
                    continue
                if _is_financial_na(catalog, code):
                    keep = [s for s in cross.index if industry.get(s) not in financial_sectors]
                    cross = cross.loc[keep]
                    if cross.empty:
                        continue
                aligned = preprocess.align_direction(cross, int(catalog.loc[code, "direction"]))
                winsorized = preprocess.winsorize_mad(aligned)
                zscore = preprocess.zscore(winsorized)
                percentile = preprocess.percentile_rank(winsorized)
                neutralized = neutralize(
                    zscore, log_mc.reindex(cross.index), industry.reindex(cross.index)
                )
                out_frames[code].append(pd.DataFrame({
                    "date_id": date_id,
                    "stock_code": cross.index,
                    "factor_code": code,
                    "calc_version": args.calc_version,
                    "raw_value": cross.to_numpy(),
                    "winsorized_value": winsorized.to_numpy(),
                    "zscore_value": zscore.to_numpy(),
                    "neutralized_value": neutralized.reindex(cross.index).to_numpy(),
                    "percentile_rank": percentile.to_numpy(),
                }))
            if index % 12 == 0 or index == len(dates):
                print(f"  [{index}/{len(dates)}] {date_id}", flush=True)
    finally:
        conn.close()

    total = 0
    for code in implemented:
        if not out_frames[code]:
            continue
        out = pd.concat(out_frames[code], ignore_index=True)[EXPOSURE_COLUMNS]
        factor_io.write_year_partitioned_csv(out, FACTOR_EXPOSURE_DIR, code, subdir=code)
        total += len(out)
        print(f"  {code}: rows={len(out)}", flush=True)

    factor_io.append_manifest(
        run_id=run_id, calc_version=args.calc_version, layer="exposure",
        factor_code=",".join(implemented), start_date_id=dates[0], end_date_id=dates[-1],
        row_count=total, valid_count=total, coverage="", status="success",
    )
    append_summary("factor_exposure", f"done rows={total}")
    print(f"[factor] exposure: factors={len(implemented)} rows={total}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
