"""Build raw value-factor values (Phase 3).

For each rebalance date and in-universe stock, evaluate the value factors
straight from their formulas, point-in-time via the bridge. No cleaning: only
NaN / inf are dropped. Output: data/factor/raw/<factor>/<factor>_<year>.csv.

Units (verified): market_cap is 万元; FN308/FN319/FN276/FN40 are 万元;
FN271/FN307 are 元; FN322 is 元/share; bonus is per 10 shares
(dps = bonus/10).
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
    MOMENTUM_HALF_TRADE_DAYS,
    MOMENTUM_LONG_TRADE_DAYS,
    MOMENTUM_SKIP_TRADE_DAYS,
    QUALITY_HISTORY_YEARS,
    QUALITY_ROE_PERIODS,
    REVERSAL_LONG_SKIP_TRADE_DAYS,
    REVERSAL_LONG_TRADE_DAYS,
    REVERSAL_TRADE_DAYS,
    TURNOVER_TRADE_DAYS,
    VOLATILITY_TRADE_DAYS,
)
from paths import FACTOR_RAW_DIR, FACTOR_UNIVERSE_DIR

# FN metrics pulled once per cross-section for the snapshot (point-in-time) factors.
FUNDAMENTAL_FN_CODES = [
    "FN308", "FN271", "FN319", "FN307", "FN276", "FN40",
    "FN183", "FN184", "FN322",
]
RAW_COLUMNS = ["date_id", "stock_code", "factor_code", "factor_value", "calc_version"]

# Snapshot factors: each maps a per-date feature frame -> factor Series (by stock).
# Units (verified): market_cap, FN308, FN319, FN276, FN40 are 万元;
# FN271/FN307 are 元; FN322 is 元/share; FN183/FN184 are % used directly
# (rank-invariant to scale).
COMPUTE = {
    "ep_ttm": lambda b: b["FN308"] / b["market_cap"].where(b["market_cap"] > 0),
    "bp_mrq": lambda b: b["FN271"] / (b["market_cap"] * 1e4),
    "sp_ttm": lambda b: b["FN319"] / b["market_cap"],
    "cfp_ttm": lambda b: b["FN307"] / (b["market_cap"] * 1e4),
    "div_yield_ttm": lambda b: b["dps_ttm"] / b["close"],
    "fcfe_to_equity": lambda b: (
        b["FN322"]
        * (b["market_cap"] * 1e4 / b["close"].where(b["close"] > 0))
        / b["FN271"].where(b["FN271"] > 0)
    ),
    "accruals": lambda b: (b["FN276"] - b["FN307"]) / b["FN40"].where(b["FN40"] > 0),
    "revenue_growth_yoy": lambda b: b["FN183"],
    "profit_growth_yoy": lambda b: b["FN184"],
}

PRICE_FACTORS = [
    "mom_6_1", "reversal_1m", "reversal_3y_6m",
    "volatility_252d", "turnover_21d",
]
PRICE_FACTOR_LOOKBACKS = {
    "mom_6_1": MOMENTUM_HALF_TRADE_DAYS,
    "reversal_1m": REVERSAL_TRADE_DAYS,
    "reversal_3y_6m": REVERSAL_LONG_TRADE_DAYS,
    "volatility_252d": VOLATILITY_TRADE_DAYS,
    "turnover_21d": TURNOVER_TRADE_DAYS,
}

# Growth acceleration (point-in-time quarterly history, not a snapshot).
GROWTH_ACCEL_METRIC = "FN324"  # 净利润(单季度)(万元)
GROWTH_ACCEL_FACTORS = ["earnings_accel_2q_avg"]

# Quality history factors.
QUALITY_ROE_METRICS = ["FN308", "FN271"]  # TTM net profit, latest equity
QUALITY_ROE_FACTORS = {
    "roe_ttm_12q_avg": ("mean", 12),
    "roe_stability_12q": ("std", 12),
}
if sorted(periods for _, periods in QUALITY_ROE_FACTORS.values()) != sorted(
    [p for p in QUALITY_ROE_PERIODS for _ in (0, 1)]
):
    raise RuntimeError("QUALITY_ROE_FACTORS must match QUALITY_ROE_PERIODS.")

ALL_FACTORS = (
    list(COMPUTE)
    + PRICE_FACTORS
    + GROWTH_ACCEL_FACTORS
    + list(QUALITY_ROE_FACTORS)
)


def _long(date_id: int, code: str, series: pd.Series, calc_version: str) -> pd.DataFrame:
    return pd.DataFrame({
        "date_id": date_id,
        "stock_code": series.index,
        "factor_code": code,
        "factor_value": series.to_numpy(),
        "calc_version": calc_version,
    })


def _price_lookback_trade_days(requested) -> int:
    return max(PRICE_FACTOR_LOOKBACKS[code] for code in requested if code in PRICE_FACTOR_LOOKBACKS)


def compute_price_factors(window, tdi_t, dateid_to_tdi, members, requested) -> dict[str, pd.Series]:
    """Compute price factors from a trailing daily window keyed by trade-day index."""
    df = window.copy()
    df["tdi"] = df["date_id"].map(dateid_to_tdi)
    df = df.dropna(subset=["tdi"])
    df["tdi"] = df["tdi"].astype(int)
    full_tdi = list(range(tdi_t - _price_lookback_trade_days(requested), tdi_t + 1))
    price = (
        df.pivot_table(index="tdi", columns="stock_code", values="adj_close", aggfunc="first")
        .reindex(full_tdi)
        .ffill()
    )
    raw: dict[str, pd.Series] = {}
    if "mom_6_1" in requested:
        raw["mom_6_1"] = (
            price.loc[tdi_t - MOMENTUM_SKIP_TRADE_DAYS] / price.loc[tdi_t - MOMENTUM_HALF_TRADE_DAYS] - 1.0
        )
    if "reversal_1m" in requested:
        raw["reversal_1m"] = -(price.loc[tdi_t] / price.loc[tdi_t - REVERSAL_TRADE_DAYS] - 1.0)
    if "reversal_3y_6m" in requested:
        raw["reversal_3y_6m"] = -(
            price.loc[tdi_t - REVERSAL_LONG_SKIP_TRADE_DAYS]
            / price.loc[tdi_t - REVERSAL_LONG_TRADE_DAYS]
            - 1.0
        )
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


def compute_earnings_accel_2q_avg(
    history: pd.DataFrame, members, *, lookback: int, yoy_lag: int
) -> pd.Series:
    """Average the latest two consecutive earnings-acceleration scores.

    For each reported quarter, alpha is single-quarter net-profit YoY change:
    ``FN324_q - FN324_q-4``. Each of the latest two consecutive alpha values is
    standardized against its own preceding ``lookback`` alpha history, then the
    two standardized scores are averaged.
    """
    if history.empty:
        return pd.Series(dtype="float64")
    wide = _quarterly_metric_wide(history, GROWTH_ACCEL_METRIC)
    if wide.empty:
        return pd.Series(dtype="float64")
    yoy = wide - wide.shift(yoy_lag)
    member_set = set(members)
    scores: dict[str, float] = {}
    for stock in wide.columns:
        if stock not in member_set:
            continue
        consecutive_scores = _standardized_recent_yoy_scores(
            yoy[stock], lookback=lookback, periods=2
        )
        if len(consecutive_scores) == 2:
            scores[stock] = float(np.mean(consecutive_scores))
    return pd.Series(scores, dtype="float64")


def compute_roe_ttm_history_factor(
    history: pd.DataFrame, members, *, periods: int, statistic: str
) -> pd.Series:
    """Summarize the latest consecutive ROE_TTM observations.

    ``FN308`` is trailing-12m parent net profit in 万元; ``FN271`` is latest
    parent equity in 元. The factor requires ``periods`` consecutive quarterly
    observations with positive equity.
    """
    if history.empty:
        return pd.Series(dtype="float64")
    profit = _quarterly_metric_wide(history, "FN308")
    equity = _quarterly_metric_wide(history, "FN271")
    if profit.empty or equity.empty:
        return pd.Series(dtype="float64")
    profit, equity = profit.align(equity, join="inner", axis=0)
    roe = profit * 1e4 / equity.where(equity > 0)
    member_set = set(members)
    scores: dict[str, float] = {}
    for stock in roe.columns:
        if stock not in member_set:
            continue
        values = _recent_consecutive_values(roe[stock], periods=periods)
        if len(values) == periods:
            if statistic == "mean":
                scores[stock] = float(np.mean(values))
            elif statistic == "std":
                std = float(np.std(values, ddof=1))
                if np.isfinite(std):
                    scores[stock] = std
            else:
                raise ValueError(f"Unsupported ROE statistic: {statistic}")
    return pd.Series(scores, dtype="float64")


def _quarterly_metric_wide(history: pd.DataFrame, metric_code: str) -> pd.DataFrame:
    metric = history[history["metric_code"] == metric_code]
    if metric.empty:
        return pd.DataFrame()
    wide = (
        metric.pivot_table(
            index="report_period", columns="stock_code",
            values="metric_value", aggfunc="first",
        )
        .sort_index()
    )
    grid = pd.date_range(wide.index.min(), wide.index.max(), freq="QE")
    return wide.reindex(grid)


def _standardized_recent_yoy_scores(
    series: pd.Series, *, lookback: int, periods: int
) -> list[float]:
    valid = series.dropna()
    if len(valid) < lookback + periods:
        return []
    recent_index = valid.index[-periods:]
    for previous, current in zip(recent_index[:-1], recent_index[1:]):
        if previous.to_period("Q") != current.to_period("Q") - 1:
            return []

    scores: list[float] = []
    start = len(valid) - periods
    for position in range(start, len(valid)):
        past = valid.iloc[position - lookback:position]
        if len(past) < lookback:
            return []
        std = past.std(ddof=1)
        if not np.isfinite(std) or std == 0:
            return []
        scores.append(float((valid.iloc[position] - past.mean()) / std))
    return scores


def _recent_consecutive_values(series: pd.Series, *, periods: int) -> list[float]:
    valid = series.dropna()
    if len(valid) < periods:
        return []
    recent = valid.iloc[-periods:]
    recent_index = recent.index
    for previous, current in zip(recent_index[:-1], recent_index[1:]):
        if previous.to_period("Q") != current.to_period("Q") - 1:
            return []
    return [float(value) for value in recent.to_numpy()]


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
    quality_roe_requested = [code for code in implemented if code in QUALITY_ROE_FACTORS]
    needs_snapshot_base = bool(snapshot_requested)
    needs_quality_roe = bool(quality_roe_requested)
    if skipped:
        print(f"[factor] build_factor_raw: not implemented: {', '.join(skipped)}", flush=True)
    if not implemented:
        print("[factor] build_factor_raw: no implemented factors requested", flush=True)
        return 0

    start_id = month_bound_date_id(args.start, upper=False)
    end_id = 99999999 if args.end == "latest" else month_bound_date_id(args.end, upper=True)
    targets = loaders.rebalance_date_ids(start_id, end_id)
    if not args.rebuild:
        done_sets = [
            factor_io.done_date_ids(
                FACTOR_RAW_DIR, code, subdir=code, calc_version=args.calc_version
            )
            for code in implemented
        ]
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
        calc_version=args.calc_version,
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
            base = pd.DataFrame()
            if needs_snapshot_base:
                financials = loaders.load_financial_metrics(conn, date_id, FUNDAMENTAL_FN_CODES).reindex(idx)
                base = loaders.load_daily_snapshot(conn, date_id).reindex(idx).join(financials)
                if "div_yield_ttm" in snapshot_requested:
                    base["dps_ttm"] = loaders.load_trailing_dividends(conn, date_id).reindex(idx).fillna(0.0)
                for code in snapshot_requested:
                    series = COMPUTE[code](base).replace([np.inf, -np.inf], np.nan).dropna()
                    if not series.empty:
                        frames[code].append(_long(date_id, code, series, args.calc_version))

            history = pd.DataFrame()
            if accel_requested or needs_quality_roe:
                metric_codes = []
                history_years = 0
                if accel_requested:
                    metric_codes.append(GROWTH_ACCEL_METRIC)
                    history_years = max(history_years, GROWTH_ACCEL_HISTORY_YEARS)
                if needs_quality_roe:
                    metric_codes.extend(QUALITY_ROE_METRICS)
                    history_years = max(history_years, QUALITY_HISTORY_YEARS)
                history = loaders.load_quarterly_metrics_history(
                    conn, date_id, list(dict.fromkeys(metric_codes)), history_years
                )

            if needs_quality_roe:
                for code in quality_roe_requested:
                    statistic, periods = QUALITY_ROE_FACTORS[code]
                    roe_factor = compute_roe_ttm_history_factor(
                        history, stocks, periods=periods, statistic=statistic
                    ).replace([np.inf, -np.inf], np.nan).dropna()
                    if not roe_factor.empty:
                        frames[code].append(_long(date_id, code, roe_factor, args.calc_version))

            if accel_requested:
                accel = compute_earnings_accel_2q_avg(
                    history, stocks,
                    lookback=GROWTH_ACCEL_LOOKBACK_QUARTERS, yoy_lag=GROWTH_ACCEL_YOY_QUARTERS,
                ).replace([np.inf, -np.inf], np.nan).dropna()
                for code in accel_requested:
                    if not accel.empty:
                        frames[code].append(_long(date_id, code, accel, args.calc_version))
            if price_requested:
                tdi_t = dateid_to_tdi.get(date_id)
                window_start = (
                    tdi_to_dateid.get(tdi_t - _price_lookback_trade_days(price_requested))
                    if tdi_t is not None
                    else None
                )
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
