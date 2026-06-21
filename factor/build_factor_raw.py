"""Build raw value-factor values (Phase 3).

For each rebalance date and in-universe stock, evaluate the value factors
straight from their formulas, point-in-time via the bridge. No cleaning: only
NaN / inf are dropped. Output: data/factor/raw/<factor>/<factor>_<year>.csv.

Units (verified): market_cap is 万元; FN308/FN319 are 万元; FN271/FN307 are 元;
bonus is per 10 shares (dps = bonus/10).
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
    GROWTH_ACCEL_HISTORY_YEARS,
    GROWTH_ACCEL_LOOKBACK_QUARTERS,
    GROWTH_ACCEL_YOY_QUARTERS,
    MOMENTUM_LONG_TRADE_DAYS,
    MOMENTUM_SKIP_TRADE_DAYS,
    REVERSAL_TRADE_DAYS,
    ROIC_DEBT_CODES_WAN,
    ROIC_DEBT_CODES_YUAN,
    ROIC_EBIT_CODE,
    ROIC_EQUITY_CODE,
    ROIC_HISTORY_YEARS,
    ROIC_TAX_RETENTION,
    TURNOVER_TRADE_DAYS,
    VOLATILITY_TRADE_DAYS,
)
from paths import FACTOR_RAW_DIR, FACTOR_UNIVERSE_DIR

# FN metrics pulled once per cross-section for the snapshot (point-in-time) factors.
FUNDAMENTAL_FN_CODES = [
    "FN308", "FN271", "FN319", "FN307", "FN276", "FN40", "FN202", "FN183", "FN184",
]
RAW_COLUMNS = ["date_id", "stock_code", "factor_code", "factor_value", "calc_version"]

# Snapshot factors: each maps a per-date feature frame -> factor Series (by stock).
# Units (verified): market_cap, FN308, FN319 are 万元; FN271/FN307/FN276/FN40 are 元;
# FN202/FN183/FN184 are %/ratios used directly (rank-invariant to scale).
COMPUTE = {
    "ep_ttm": lambda b: b["FN308"] / b["market_cap"],
    "bp_mrq": lambda b: b["FN271"] / (b["market_cap"] * 1e4),
    "sp_ttm": lambda b: b["FN319"] / b["market_cap"],
    "cfp_ttm": lambda b: b["FN307"] / (b["market_cap"] * 1e4),
    "div_yield_ttm": lambda b: b["dps_ttm"] / b["close"],
    "roe_ttm": lambda b: b["FN308"] * 1e4 / b["FN271"],
    "roa_ttm": lambda b: b["FN276"] / b["FN40"],
    "gross_margin": lambda b: b["FN202"],
    "accruals": lambda b: (b["FN276"] - b["FN307"]) / b["FN40"],
    "revenue_growth_yoy": lambda b: b["FN183"],
    "profit_growth_yoy": lambda b: b["FN184"],
}

PRICE_FACTORS = ["mom_12_1", "reversal_1m", "volatility_252d", "turnover_21d"]

# Growth acceleration (point-in-time quarterly history, not a snapshot).
GROWTH_ACCEL_METRIC = "FN324"  # 净利润(单季度)(万元)
GROWTH_ACCEL_FACTORS = ["earnings_accel"]

# ROIC TTM (point-in-time quarterly history; EBIT is cumulative, IC is a balance).
ROIC_FACTORS = ["roic_ttm"]
ROIC_METRIC_CODES = [ROIC_EBIT_CODE, ROIC_EQUITY_CODE, *ROIC_DEBT_CODES_YUAN, *ROIC_DEBT_CODES_WAN]

ALL_FACTORS = list(COMPUTE) + PRICE_FACTORS + GROWTH_ACCEL_FACTORS + ROIC_FACTORS


def _long(date_id: int, code: str, series: pd.Series, calc_version: str) -> pd.DataFrame:
    return pd.DataFrame({
        "date_id": date_id,
        "stock_code": series.index,
        "factor_code": code,
        "factor_value": series.to_numpy(),
        "calc_version": calc_version,
    })


def compute_price_factors(window, tdi_t, dateid_to_tdi, members, requested) -> dict[str, pd.Series]:
    """Compute price factors from a trailing daily window keyed by trade-day index."""
    df = window.copy()
    df["tdi"] = df["date_id"].map(dateid_to_tdi)
    df = df.dropna(subset=["tdi"])
    df["tdi"] = df["tdi"].astype(int)
    full_tdi = list(range(tdi_t - MOMENTUM_LONG_TRADE_DAYS, tdi_t + 1))
    price = (
        df.pivot_table(index="tdi", columns="stock_code", values="adj_close", aggfunc="first")
        .reindex(full_tdi)
        .ffill()
    )
    raw: dict[str, pd.Series] = {}
    if "mom_12_1" in requested:
        raw["mom_12_1"] = (
            price.loc[tdi_t - MOMENTUM_SKIP_TRADE_DAYS] / price.loc[tdi_t - MOMENTUM_LONG_TRADE_DAYS] - 1.0
        )
    if "reversal_1m" in requested:
        raw["reversal_1m"] = -(price.loc[tdi_t] / price.loc[tdi_t - REVERSAL_TRADE_DAYS] - 1.0)
    if "volatility_252d" in requested:
        returns = price.pct_change()
        raw["volatility_252d"] = returns.iloc[-VOLATILITY_TRADE_DAYS:].std()
    if "turnover_21d" in requested:
        df["turnover"] = df["vol"] / df["float_shares"].where(df["float_shares"] > 0)
        turn = (
            df.pivot_table(index="tdi", columns="stock_code", values="turnover", aggfunc="first")
            .reindex(full_tdi)
        )
        raw["turnover_21d"] = turn.iloc[-TURNOVER_TRADE_DAYS:].mean()
    member_idx = pd.Index(sorted(members), name="stock_code")
    result: dict[str, pd.Series] = {}
    for code, series in raw.items():
        result[code] = series.reindex(member_idx).replace([np.inf, -np.inf], np.nan).dropna()
    return result


def compute_growth_acceleration(
    history: pd.DataFrame, members, *, lookback: int, yoy_lag: int
) -> pd.Series:
    """Standardized single-quarter net-profit YoY-change acceleration.

    ``history`` is long (stock_code, report_period, metric_code, metric_value)
    point-in-time single-quarter net profit. Per stock: ``alpha`` = single-quarter
    net profit YoY change (difference vs the same quarter one year earlier); the
    factor is ``(alpha_t - mean(last `lookback` alpha)) / std(last `lookback`
    alpha)`` -- how far the latest YoY change sits above its own recent history.
    The outer standardization is per stock, so the absolute unit does not matter.
    Returns a Series indexed by stock_code (in-universe members only).
    """
    if history.empty:
        return pd.Series(dtype="float64")
    wide = (
        history.pivot_table(
            index="report_period", columns="stock_code",
            values="metric_value", aggfunc="first",
        )
        .sort_index()
    )
    # Complete quarter-end grid so shift(yoy_lag) lands on the year-ago quarter.
    grid = pd.date_range(wide.index.min(), wide.index.max(), freq="QE")
    wide = wide.reindex(grid)
    yoy = wide - wide.shift(yoy_lag)
    member_set = set(members)
    scores: dict[str, float] = {}
    for stock in wide.columns:
        if stock not in member_set:
            continue
        series = yoy[stock].dropna()
        if len(series) < lookback + 1:
            continue
        current = series.iloc[-1]
        past = series.iloc[-(lookback + 1):-1]
        std = past.std(ddof=1)
        if not np.isfinite(std) or std == 0:
            continue
        scores[stock] = (current - past.mean()) / std
    return pd.Series(scores, dtype="float64")


def compute_roic_ttm(
    history: pd.DataFrame, members, *, ebit_code, equity_code,
    debt_codes_yuan, debt_codes_wan, tax_retention,
) -> pd.Series:
    """Trailing-twelve-month ROIC ~= tax_retention * EBIT_TTM / avg invested capital.

    ``history`` is long (stock_code, report_period, metric_code, metric_value),
    point-in-time. EBIT (``ebit_code``) is a cumulative (YTD) flow, so for an
    interim latest period P:
        EBIT_TTM = EBIT[P] + EBIT[last FY] - EBIT[P - 1 year]
    and for an annual P (Dec 31): EBIT_TTM = EBIT[P]. Invested capital is a
    balance: equity + interest-bearing debt (lease debt is 万元 -> *1e4), averaged
    across P and the year-ago balance. NOPAT is approximated as ``tax_retention *
    EBIT`` (no reliable tax-expense field). Returns a Series indexed by stock_code
    (in-universe members only).
    """
    if history.empty:
        return pd.Series(dtype="float64")
    codes = [ebit_code, equity_code, *debt_codes_yuan, *debt_codes_wan]
    wide = history.pivot_table(
        index=["stock_code", "report_period"], columns="metric_code",
        values="metric_value", aggfunc="first",
    ).reindex(columns=codes)
    member_set = set(members)
    scores: dict[str, float] = {}

    def invested_capital(row) -> float:
        equity = row.get(equity_code, np.nan)
        if not np.isfinite(equity):
            return np.nan
        total = float(equity)
        for code in debt_codes_yuan:
            value = row.get(code, np.nan)
            if np.isfinite(value):
                total += float(value)
        for code in debt_codes_wan:
            value = row.get(code, np.nan)
            if np.isfinite(value):
                total += float(value) * 1e4
        return total

    for stock, group in wide.groupby(level="stock_code"):
        if stock not in member_set:
            continue
        g = group.droplevel("stock_code").sort_index()
        period = g.index[-1]
        year_ago = period - pd.DateOffset(years=1)
        last_fy = pd.Timestamp(period.year - 1, 12, 31)
        if year_ago not in g.index:
            continue
        ebit = g[ebit_code]
        if period.month == 12 and period.day == 31:
            ebit_ttm = ebit.get(period, np.nan)
        elif last_fy in g.index:
            ebit_ttm = ebit.get(period, np.nan) + ebit.get(last_fy, np.nan) - ebit.get(year_ago, np.nan)
        else:
            continue
        if not np.isfinite(ebit_ttm):
            continue
        ic_now = invested_capital(g.loc[period])
        ic_prev = invested_capital(g.loc[year_ago])
        if not (np.isfinite(ic_now) and np.isfinite(ic_prev)):
            continue
        avg_ic = (ic_now + ic_prev) / 2.0
        if avg_ic <= 0:
            continue
        scores[stock] = tax_retention * ebit_ttm / avg_ic
    return pd.Series(scores, dtype="float64")


def month_bound_date_id(month: str, *, upper: bool) -> int:
    value = int(month)
    return value * 100 + (31 if upper else 1)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build raw factor values.")
    parser.add_argument("--start", default="201501", help="First rebalance month YYYYMM.")
    parser.add_argument("--end", default="latest", help="Last rebalance month YYYYMM or 'latest'.")
    parser.add_argument("--factors", default="all", help="Comma-separated factor_code list, or 'all'.")
    parser.add_argument("--calc-version", default=CALC_VERSION, help="calc_version stamp.")
    parser.add_argument("--rebuild", action="store_true", help="Recompute months already present.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    requested = list(ALL_FACTORS) if args.factors == "all" else [c.strip() for c in args.factors.split(",")]
    implemented = [code for code in requested if code in ALL_FACTORS]
    skipped = [code for code in requested if code not in ALL_FACTORS]
    snapshot_requested = [code for code in implemented if code in COMPUTE]
    price_requested = [code for code in implemented if code in PRICE_FACTORS]
    accel_requested = [code for code in implemented if code in GROWTH_ACCEL_FACTORS]
    roic_requested = [code for code in implemented if code in ROIC_FACTORS]
    if skipped:
        print(f"[factor] build_factor_raw: not implemented: {', '.join(skipped)}", flush=True)
    if not implemented:
        print("[factor] build_factor_raw: no implemented factors requested", flush=True)
        return 0

    start_id = month_bound_date_id(args.start, upper=False)
    end_id = 99999999 if args.end == "latest" else month_bound_date_id(args.end, upper=True)
    targets = loaders.rebalance_date_ids(start_id, end_id)
    if not args.rebuild:
        done_sets = [factor_io.done_date_ids(FACTOR_RAW_DIR, code, subdir=code) for code in implemented]
        fully_done = set.intersection(*done_sets) if done_sets else set()
        targets = [date_id for date_id in targets if date_id not in fully_done]

    append_summary(
        "factor_raw",
        f"range={args.start}..{args.end} months={len(targets)} factors={','.join(implemented)}",
    )
    if not targets:
        print("[factor] build_factor_raw: nothing to do (use --rebuild)", flush=True)
        return 0

    universe = factor_io.read_year_partitioned_csv(
        FACTOR_UNIVERSE_DIR, "universe", date_ids=targets,
        usecols=["date_id", "stock_code", "in_universe"],
    )
    if universe.empty:
        print("[factor] build_factor_raw: no universe found; run build_universe first", flush=True)
        return 1
    universe = universe[universe["in_universe"].astype(bool)]
    members = {int(date_id): list(group["stock_code"]) for date_id, group in universe.groupby("date_id")}

    conn = loaders.get_connection()
    frames: dict[str, list[pd.DataFrame]] = {code: [] for code in implemented}
    dateid_to_tdi: dict[int, int] = {}
    tdi_to_dateid: dict[int, int] = {}
    if price_requested:
        dateid_to_tdi, tdi_to_dateid = loaders.load_trade_day_index_maps(conn)
    try:
        for index, date_id in enumerate(targets, start=1):
            stocks = members.get(date_id, [])
            if not stocks:
                continue
            idx = pd.Index(sorted(stocks), name="stock_code")
            if snapshot_requested:
                financials = loaders.load_financial_metrics(conn, date_id, FUNDAMENTAL_FN_CODES).reindex(idx)
                base = loaders.load_daily_snapshot(conn, date_id).reindex(idx).join(financials)
                base["dps_ttm"] = loaders.load_trailing_dividends(conn, date_id).reindex(idx).fillna(0.0)
                for code in snapshot_requested:
                    series = COMPUTE[code](base).replace([np.inf, -np.inf], np.nan).dropna()
                    if not series.empty:
                        frames[code].append(_long(date_id, code, series, args.calc_version))
            if accel_requested:
                history = loaders.load_quarterly_metrics_history(
                    conn, date_id, [GROWTH_ACCEL_METRIC], GROWTH_ACCEL_HISTORY_YEARS
                )
                accel = compute_growth_acceleration(
                    history, stocks,
                    lookback=GROWTH_ACCEL_LOOKBACK_QUARTERS, yoy_lag=GROWTH_ACCEL_YOY_QUARTERS,
                ).replace([np.inf, -np.inf], np.nan).dropna()
                if not accel.empty:
                    code = GROWTH_ACCEL_FACTORS[0]
                    frames[code].append(_long(date_id, code, accel, args.calc_version))
            if roic_requested:
                history = loaders.load_quarterly_metrics_history(
                    conn, date_id, ROIC_METRIC_CODES, ROIC_HISTORY_YEARS
                )
                roic = compute_roic_ttm(
                    history, stocks,
                    ebit_code=ROIC_EBIT_CODE, equity_code=ROIC_EQUITY_CODE,
                    debt_codes_yuan=ROIC_DEBT_CODES_YUAN, debt_codes_wan=ROIC_DEBT_CODES_WAN,
                    tax_retention=ROIC_TAX_RETENTION,
                ).replace([np.inf, -np.inf], np.nan).dropna()
                if not roic.empty:
                    code = ROIC_FACTORS[0]
                    frames[code].append(_long(date_id, code, roic, args.calc_version))
            if price_requested:
                tdi_t = dateid_to_tdi.get(date_id)
                window_start = tdi_to_dateid.get(tdi_t - MOMENTUM_LONG_TRADE_DAYS) if tdi_t is not None else None
                if window_start is not None:
                    window = loaders.load_price_window(conn, window_start, date_id)
                    priced = compute_price_factors(window, tdi_t, dateid_to_tdi, stocks, price_requested)
                    for code, series in priced.items():
                        if not series.empty:
                            frames[code].append(_long(date_id, code, series, args.calc_version))
            if index % 12 == 0 or index == len(targets):
                print(f"  [{index}/{len(targets)}] {date_id}", flush=True)
    finally:
        conn.close()

    total = 0
    for code in implemented:
        if not frames[code]:
            continue
        out = pd.concat(frames[code], ignore_index=True)[RAW_COLUMNS]
        factor_io.write_year_partitioned_csv(out, FACTOR_RAW_DIR, code, subdir=code)
        total += len(out)
        print(f"  {code}: rows={len(out)}", flush=True)

    factor_io.append_manifest(
        run_id=run_id, calc_version=args.calc_version, layer="raw",
        factor_code=",".join(implemented), start_date_id=targets[0], end_date_id=targets[-1],
        row_count=total, valid_count=total, coverage="", status="success",
    )
    append_summary("factor_raw", f"done rows={total}")
    print(f"[factor] raw: factors={len(implemented)} rows={total}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
