"""Build daily Growth/Momentum 1D and 5D Rank IC diagnostics.

The monthly factor library only writes rebalance-date exposures. This script
builds daily cross-sections for the factors in the Growth and Momentum styles,
uses adjusted-price forward returns, and writes:

    data/factor/growth_momentum_rank_ic/rank_ic_detail.csv
    data/factor/growth_momentum_rank_ic/rank_ic_summary.csv

1D uses every eligible daily cross-section. 5D uses non-overlapping samples:
starting at the first eligible date in its own window, then every 5 trading days.
The two horizons intentionally use independent eligible windows, so a missing
latest 5D label does not truncate the latest 1D diagnostics.
"""
from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

_ETL_DIR = Path(__file__).resolve().parents[1] / "etl"
if str(_ETL_DIR) not in sys.path:
    sys.path.insert(0, str(_ETL_DIR))

import argparse
from collections.abc import Iterable

import numpy as np
import pandas as pd

import factor_io
import loaders
import preprocess
from diagnostics import spearman_ic
from etl_logging import append_summary
from factor_config import (
    CALC_VERSION,
    GROWTH_ACCEL_HISTORY_YEARS,
    GROWTH_ACCEL_LOOKBACK_QUARTERS,
    GROWTH_ACCEL_YOY_QUARTERS,
    LIQUIDITY_DROP_FRACTION,
    LIQUIDITY_LOOKBACK_TRADE_DAYS,
    LISTED_MIN_TRADING_DAYS,
    MOMENTUM_HALF_TRADE_DAYS,
    MOMENTUM_SKIP_TRADE_DAYS,
)
from neutralize import neutralize
from paths import FACTOR_CATALOG_FILE, FACTOR_DATA_DIR

TARGET_STYLES = ("growth", "momentum")
HORIZONS = (1, 5)
OUTPUT_DIR = FACTOR_DATA_DIR / "growth_momentum_rank_ic"
DETAIL_FILE = OUTPUT_DIR / "rank_ic_detail.csv"
SUMMARY_FILE = OUTPUT_DIR / "rank_ic_summary.csv"
DETAIL_COLUMNS = [
    "eval_date_id", "forward_date_id", "horizon_td", "sample_step_td",
    "style", "signal_type", "factor_code", "factor_name", "calc_version",
    "universe_count", "valid_signal_count", "valid_return_count",
    "pair_count", "rank_ic",
]
SUMMARY_COLUMNS = [
    "window_start_date_id", "window_end_date_id", "horizon_td", "sample_step_td",
    "style", "signal_type", "factor_code", "factor_name", "calc_version",
    "n_cross_sections", "mean_rank_ic", "median_rank_ic", "std_rank_ic",
    "ic_ir", "positive_rate", "mean_pair_count",
]
GROWTH_SNAPSHOT_METRICS = {
    "revenue_growth_yoy": "FN183",
    "profit_growth_yoy": "FN184",
}
EARNINGS_ACCEL_FACTOR = "earnings_accel_2q_avg"
MOMENTUM_FACTOR = "mom_6_1"
MIN_PIVOT_DENSITY = 0.0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build daily 1D/5D Rank IC for Growth and Momentum factors."
    )
    parser.add_argument(
        "--lookback-trade-days",
        type=int,
        default=1260,
        help="Number of recent eligible trading-day cross-sections per horizon.",
    )
    parser.add_argument(
        "--end-date",
        default="latest",
        help="Latest adjusted-price date_id to use, YYYYMMDD or 'latest'.",
    )
    parser.add_argument(
        "--calc-version",
        default=CALC_VERSION,
        help="calc_version stamp written to output rows.",
    )
    parser.add_argument(
        "--min-names",
        type=int,
        default=30,
        help="Minimum paired stocks required to calculate one cross-sectional IC.",
    )
    parser.add_argument(
        "--output-dir",
        default=str(OUTPUT_DIR),
        help="Directory for rank_ic_detail.csv and rank_ic_summary.csv.",
    )
    return parser.parse_args()


def _as_int_list(values: Iterable[int]) -> list[int]:
    return [int(value) for value in values]


def load_trade_dates(conn, end_date_id: int) -> pd.DataFrame:
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT date_id, trade_day_index
            FROM dim_date
            WHERE is_trade_day = TRUE
              AND trade_day_index IS NOT NULL
              AND date_id <= %s
            ORDER BY trade_day_index
            """,
            (end_date_id,),
        )
        rows = cur.fetchall()
    return pd.DataFrame(rows, columns=["date_id", "trade_day_index"])


def latest_price_date_id(conn, end_date_id: int) -> int:
    with conn.cursor() as cur:
        cur.execute("SELECT MAX(date_id) FROM fact_daily WHERE date_id <= %s", (end_date_id,))
        value = cur.fetchone()[0]
    if value is None:
        raise RuntimeError("fact_daily has no rows on or before the requested end date")
    return int(value)


def select_eval_dates(
    trade_dates: list[int],
    *,
    lookback_trade_days: int,
) -> dict[int, list[int]]:
    """Select horizon-specific evaluation dates.

    Each horizon gets its own last-N eligible window. For 5D, only every fifth
    date from that horizon window is used, giving non-overlapping labels.
    """
    selected: dict[int, list[int]] = {}
    for horizon in HORIZONS:
        if len(trade_dates) <= horizon:
            selected[horizon] = []
            continue
        eligible = trade_dates[:-horizon]
        window = eligible[-lookback_trade_days:]
        if horizon == 5:
            window = window[::5]
        selected[horizon] = _as_int_list(window)
    return selected


def load_daily_market_window(
    conn,
    start_date_id: int,
    end_date_id: int,
) -> pd.DataFrame:
    query = """
        SELECT f.date_id, f.stock_code,
               f.close * a.adjust_factor AS adj_close,
               f.close, f.amount, f.market_cap
        FROM fact_daily f
        JOIN fact_adjustment_factor_period a
          ON a.stock_code = f.stock_code
         AND f.date_id BETWEEN a.valid_from_date_id AND a.valid_to_date_id
        WHERE f.date_id BETWEEN %(start)s AND %(end)s
        ORDER BY f.date_id, f.stock_code
    """
    with conn.cursor() as cur:
        cur.execute(query, {"start": start_date_id, "end": end_date_id})
        rows = cur.fetchall()
        columns = [desc[0] for desc in cur.description]
    frame = pd.DataFrame(rows, columns=columns)
    for column in ("adj_close", "close", "amount", "market_cap"):
        frame[column] = pd.to_numeric(frame[column], errors="coerce")
    frame["date_id"] = frame["date_id"].astype(int)
    return frame


def pivot_daily(
    market: pd.DataFrame,
    value: str,
    trade_dates: list[int],
) -> pd.DataFrame:
    if market.empty:
        return pd.DataFrame(index=trade_dates)
    pivot = market.pivot_table(
        index="date_id",
        columns="stock_code",
        values=value,
        aggfunc="first",
        observed=True,
    )
    return pivot.reindex(trade_dates).sort_index()


def load_growth_snapshot_panels(
    conn,
    eval_dates: list[int],
    factor_codes: list[str],
) -> dict[str, pd.DataFrame]:
    codes = [GROWTH_SNAPSHOT_METRICS[code] for code in factor_codes]
    if not codes:
        return {}
    query = """
        SELECT b.date_id, b.stock_code, v.metric_code, v.metric_value
        FROM bridge_trade_day_financial_report b
        JOIN fact_financial_value v ON v.report_id = b.report_id
        WHERE b.date_id = ANY(%(dates)s)
          AND v.metric_code = ANY(%(codes)s)
    """
    with conn.cursor() as cur:
        cur.execute(query, {"dates": eval_dates, "codes": codes})
        rows = cur.fetchall()
    if not rows:
        return {
            code: pd.DataFrame(index=eval_dates, dtype="float64")
            for code in factor_codes
        }
    frame = pd.DataFrame(rows, columns=["date_id", "stock_code", "metric_code", "metric_value"])
    frame["date_id"] = frame["date_id"].astype(int)
    frame["metric_value"] = pd.to_numeric(frame["metric_value"], errors="coerce")
    panels: dict[str, pd.DataFrame] = {}
    for factor_code, metric_code in GROWTH_SNAPSHOT_METRICS.items():
        if factor_code not in factor_codes:
            continue
        subset = frame[frame["metric_code"] == metric_code]
        if subset.empty:
            panels[factor_code] = pd.DataFrame(index=eval_dates, dtype="float64")
            continue
        panels[factor_code] = subset.pivot_table(
            index="date_id",
            columns="stock_code",
            values="metric_value",
            aggfunc="first",
            observed=True,
        ).reindex(eval_dates)
    return panels


def load_earnings_accel_panel(
    conn,
    eval_dates: list[int],
    *,
    min_eval_date_id: int,
    max_eval_date_id: int,
) -> pd.DataFrame:
    min_period = f"{min_eval_date_id // 10000 - GROWTH_ACCEL_HISTORY_YEARS}-01-01"
    query = """
        SELECT r.stock_code, r.report_period, r.announce_date_id, v.metric_value
        FROM fact_financial_report r
        JOIN fact_financial_value v
          ON v.report_id = r.report_id AND v.metric_code = 'FN324'
        WHERE r.announce_date_id <= %(max_date)s
          AND r.report_period >= %(min_period)s
        ORDER BY r.stock_code, r.report_period, r.announce_date_id
    """
    with conn.cursor() as cur:
        cur.execute(
            query,
            {
                "max_date": max_eval_date_id,
                "min_period": min_period,
            },
        )
        rows = cur.fetchall()
    if not rows:
        return pd.DataFrame(index=eval_dates, dtype="float64")
    reports = pd.DataFrame(
        rows,
        columns=["stock_code", "report_period", "announce_date_id", "metric_value"],
    )
    reports["report_period"] = pd.to_datetime(reports["report_period"])
    reports["announce_date_id"] = reports["announce_date_id"].astype(int)
    reports["metric_value"] = pd.to_numeric(reports["metric_value"], errors="coerce")
    events = _earnings_accel_events(reports)
    if events.empty:
        return pd.DataFrame(index=eval_dates, dtype="float64")
    return _events_to_daily_panel(events, eval_dates)


def _earnings_accel_events(reports: pd.DataFrame) -> pd.DataFrame:
    event_frames: list[pd.DataFrame] = []
    for stock_code, group in reports.groupby("stock_code", sort=False):
        # Keep the last announced value for duplicate stock/period events.
        deduped = (
            group.sort_values(["report_period", "announce_date_id"])
            .dropna(subset=["metric_value", "announce_date_id"])
            .drop_duplicates(["report_period"], keep="last")
        )
        if deduped.empty:
            continue
        values = deduped.set_index("report_period")["metric_value"].sort_index()
        announce = deduped.set_index("report_period")["announce_date_id"].sort_index()
        grid = pd.date_range(values.index.min(), values.index.max(), freq="QE")
        values = values.reindex(grid)
        announce = announce.reindex(grid)
        yoy = values - values.shift(GROWTH_ACCEL_YOY_QUARTERS)
        rows: list[dict[str, object]] = []
        for pos, period in enumerate(grid):
            announce_date_id = announce.iloc[pos]
            if pd.isna(announce_date_id):
                continue
            score = _earnings_accel_score(yoy.iloc[: pos + 1])
            if pd.isna(score):
                continue
            rows.append(
                {
                    "date_id": int(announce_date_id),
                    "stock_code": stock_code,
                    "factor_value": float(score),
                }
            )
        if rows:
            event_frames.append(pd.DataFrame(rows))
    if not event_frames:
        return pd.DataFrame(columns=["date_id", "stock_code", "factor_value"])
    return pd.concat(event_frames, ignore_index=True)


def _earnings_accel_score(yoy: pd.Series) -> float:
    valid = yoy.dropna()
    periods = 2
    lookback = GROWTH_ACCEL_LOOKBACK_QUARTERS
    if len(valid) < lookback + periods:
        return float("nan")
    recent_index = valid.index[-periods:]
    for previous, current in zip(recent_index[:-1], recent_index[1:]):
        if previous.to_period("Q") != current.to_period("Q") - 1:
            return float("nan")
    scores: list[float] = []
    start = len(valid) - periods
    for position in range(start, len(valid)):
        past = valid.iloc[position - lookback:position]
        if len(past) < lookback:
            return float("nan")
        std = past.std(ddof=1)
        if not np.isfinite(std) or std == 0:
            return float("nan")
        scores.append(float((valid.iloc[position] - past.mean()) / std))
    return float(np.mean(scores)) if len(scores) == periods else float("nan")


def _events_to_daily_panel(events: pd.DataFrame, eval_dates: list[int]) -> pd.DataFrame:
    eval_index = pd.Index(eval_dates, name="date_id")
    if events.empty:
        return pd.DataFrame(index=eval_index, dtype="float64")
    panels: list[pd.Series] = []
    for stock_code, group in events.groupby("stock_code", sort=False):
        series = (
            group.sort_values("date_id")
            .drop_duplicates("date_id", keep="last")
            .set_index("date_id")["factor_value"]
        )
        combined_index = eval_index.union(pd.Index(series.index, name="date_id")).sort_values()
        daily = series.reindex(combined_index).ffill().reindex(eval_index)
        if daily.notna().mean() >= MIN_PIVOT_DENSITY:
            daily.name = stock_code
            panels.append(daily)
    if not panels:
        return pd.DataFrame(index=eval_index, dtype="float64")
    return pd.concat(panels, axis=1)


def build_universe_members(
    eval_dates: list[int],
    trade_index_by_date: dict[int, int],
    first_tdi: dict[str, int],
    names: dict[str, str],
    close: pd.DataFrame,
    market_cap: pd.DataFrame,
    amount: pd.DataFrame,
) -> dict[int, pd.Index]:
    rolling_amount = amount.rolling(LIQUIDITY_LOOKBACK_TRADE_DAYS, min_periods=1).mean()
    st_codes = pd.Index(
        [code for code, name in names.items() if "ST" in (name or "").upper()],
        name="stock_code",
    )
    universe: dict[int, pd.Index] = {}
    for date_id in eval_dates:
        if date_id not in close.index:
            universe[date_id] = pd.Index([], name="stock_code")
            continue
        stocks = close.columns
        first = pd.Series(stocks, index=stocks).map(first_tdi)
        listed_days = trade_index_by_date[date_id] - first + 1
        listed_ok = listed_days >= LISTED_MIN_TRADING_DAYS
        traded = close.loc[date_id].notna()
        has_market_cap = market_cap.loc[date_id].notna()
        avg_amount = rolling_amount.loc[date_id]
        seasoned = listed_ok & traded & avg_amount.notna()
        if seasoned.any():
            threshold = float(avg_amount.loc[seasoned].quantile(LIQUIDITY_DROP_FRACTION))
            liquidity_ok = avg_amount >= threshold
        else:
            liquidity_ok = pd.Series(False, index=stocks)
        not_st = ~stocks.isin(st_codes)
        mask = listed_ok & traded & has_market_cap & liquidity_ok & not_st
        universe[date_id] = pd.Index(stocks[mask.fillna(False)], name="stock_code")
    return universe


def momentum_panel(adj_close: pd.DataFrame, eval_dates: list[int]) -> pd.DataFrame:
    # Use label-based positions through the full trade-day index to match the
    # existing monthly factor definition: adj[t-21] / adj[t-126] - 1.
    loc_by_date = {int(date_id): pos for pos, date_id in enumerate(adj_close.index)}
    rows: list[pd.Series] = []
    for date_id in eval_dates:
        pos = loc_by_date.get(int(date_id))
        if pos is None or pos < MOMENTUM_HALF_TRADE_DAYS:
            rows.append(pd.Series(name=date_id, dtype="float64"))
            continue
        recent = adj_close.iloc[pos - MOMENTUM_SKIP_TRADE_DAYS]
        past = adj_close.iloc[pos - MOMENTUM_HALF_TRADE_DAYS]
        signal = recent / past.where(past > 0) - 1.0
        signal.name = date_id
        rows.append(signal.replace([np.inf, -np.inf], np.nan))
    if not rows:
        return pd.DataFrame(index=eval_dates, dtype="float64")
    return pd.DataFrame(rows).reindex(eval_dates)


def forward_returns(adj_close: pd.DataFrame, horizons: Iterable[int]) -> dict[int, pd.DataFrame]:
    return {
        int(horizon): adj_close.shift(-int(horizon)) / adj_close - 1.0
        for horizon in horizons
    }


def preprocess_cross_section(
    raw: pd.Series,
    *,
    direction: int,
    market_cap: pd.Series,
    industry: pd.Series,
) -> pd.Series:
    raw = raw.replace([np.inf, -np.inf], np.nan).dropna()
    if raw.empty:
        return pd.Series(dtype="float64")
    aligned = preprocess.align_direction(raw, direction)
    winsorized = preprocess.winsorize_mad(aligned)
    zscore = preprocess.zscore(winsorized)
    log_mc = np.log(market_cap.reindex(zscore.index).where(market_cap.reindex(zscore.index) > 0))
    return neutralize(zscore, log_mc, industry.reindex(zscore.index))


def composite_by_style(
    factor_signals: dict[str, pd.Series],
    catalog: pd.DataFrame,
    styles: Iterable[str],
) -> dict[str, pd.Series]:
    composites: dict[str, pd.Series] = {}
    for style in styles:
        factors = [
            code
            for code in factor_signals
            if code in catalog.index and str(catalog.loc[code, "style"]) == style
        ]
        if not factors:
            continue
        frame = pd.DataFrame({code: factor_signals[code] for code in factors})
        raw_style = frame.mean(axis=1, skipna=True).dropna()
        if raw_style.empty:
            composites[style] = pd.Series(dtype="float64")
        else:
            composites[style] = preprocess.zscore(raw_style)
    return composites


def pair_count(signal: pd.Series, forward: pd.Series) -> int:
    return int(pd.concat([signal, forward], axis=1).dropna().shape[0])


def valid_count(series: pd.Series) -> int:
    return int(series.replace([np.inf, -np.inf], np.nan).dropna().shape[0])


def build_detail_rows(
    *,
    eval_dates_by_horizon: dict[int, list[int]],
    all_eval_dates: list[int],
    target_factors: list[str],
    catalog: pd.DataFrame,
    raw_panels: dict[str, pd.DataFrame],
    forward: dict[int, pd.DataFrame],
    universe_members: dict[int, pd.Index],
    market_cap: pd.DataFrame,
    industry: pd.Series,
    trade_dates: list[int],
    calc_version: str,
    min_names: int,
) -> list[dict[str, object]]:
    trade_pos = {int(date_id): pos for pos, date_id in enumerate(trade_dates)}
    horizon_eval_sets = {
        horizon: set(eval_dates)
        for horizon, eval_dates in eval_dates_by_horizon.items()
    }
    rows: list[dict[str, object]] = []
    for index, date_id in enumerate(all_eval_dates, start=1):
        members = universe_members.get(date_id, pd.Index([], name="stock_code"))
        if members.empty:
            continue
        mc = market_cap.loc[date_id] if date_id in market_cap.index else pd.Series(dtype="float64")
        factor_signals: dict[str, pd.Series] = {}
        for code in target_factors:
            panel = raw_panels.get(code)
            if panel is None or date_id not in panel.index:
                continue
            raw = panel.loc[date_id].reindex(members)
            signal = preprocess_cross_section(
                raw,
                direction=int(catalog.loc[code, "direction"]),
                market_cap=mc,
                industry=industry,
            )
            if not signal.empty:
                factor_signals[code] = signal
        composites = composite_by_style(factor_signals, catalog, TARGET_STYLES)
        for horizon, eval_set in horizon_eval_sets.items():
            if date_id not in eval_set:
                continue
            forward_date = trade_dates[trade_pos[date_id] + horizon]
            returns = forward[horizon].loc[date_id] if date_id in forward[horizon].index else pd.Series(dtype="float64")
            for code, signal in factor_signals.items():
                pair_n = pair_count(signal, returns)
                ic = spearman_ic(signal, returns, min_names=min_names)
                rows.append(
                    {
                        "eval_date_id": date_id,
                        "forward_date_id": forward_date,
                        "horizon_td": horizon,
                        "sample_step_td": horizon,
                        "style": str(catalog.loc[code, "style"]),
                        "signal_type": "factor",
                        "factor_code": code,
                        "factor_name": str(catalog.loc[code, "factor_name"]),
                        "calc_version": calc_version,
                        "universe_count": int(len(members)),
                        "valid_signal_count": valid_count(signal),
                        "valid_return_count": valid_count(returns.reindex(members)),
                        "pair_count": pair_n,
                        "rank_ic": "" if pd.isna(ic) else round(float(ic), 6),
                    }
                )
            for style, signal in composites.items():
                pair_n = pair_count(signal, returns)
                ic = spearman_ic(signal, returns, min_names=min_names)
                rows.append(
                    {
                        "eval_date_id": date_id,
                        "forward_date_id": forward_date,
                        "horizon_td": horizon,
                        "sample_step_td": horizon,
                        "style": style,
                        "signal_type": "composite",
                        "factor_code": f"{style}_composite",
                        "factor_name": f"{style} composite",
                        "calc_version": calc_version,
                        "universe_count": int(len(members)),
                        "valid_signal_count": valid_count(signal),
                        "valid_return_count": valid_count(returns.reindex(members)),
                        "pair_count": pair_n,
                        "rank_ic": "" if pd.isna(ic) else round(float(ic), 6),
                    }
                )
        if index % 100 == 0 or index == len(all_eval_dates):
            print(f"  [{index}/{len(all_eval_dates)}] daily IC signal date {date_id}", flush=True)
    return rows


def build_summary(detail: pd.DataFrame) -> pd.DataFrame:
    if detail.empty:
        return pd.DataFrame(columns=SUMMARY_COLUMNS)
    work = detail.copy()
    work["rank_ic_numeric"] = pd.to_numeric(work["rank_ic"], errors="coerce")
    work["pair_count_numeric"] = pd.to_numeric(work["pair_count"], errors="coerce")
    group_cols = [
        "horizon_td", "sample_step_td", "style", "signal_type",
        "factor_code", "factor_name", "calc_version",
    ]
    rows: list[dict[str, object]] = []
    for keys, group in work.groupby(group_cols, sort=True, dropna=False):
        ic = group["rank_ic_numeric"].dropna()
        std = float(ic.std(ddof=1)) if len(ic) > 1 else float("nan")
        mean = float(ic.mean()) if len(ic) else float("nan")
        rows.append(
            {
                "window_start_date_id": int(group["eval_date_id"].min()),
                "window_end_date_id": int(group["eval_date_id"].max()),
                "horizon_td": keys[0],
                "sample_step_td": keys[1],
                "style": keys[2],
                "signal_type": keys[3],
                "factor_code": keys[4],
                "factor_name": keys[5],
                "calc_version": keys[6],
                "n_cross_sections": int(ic.count()),
                "mean_rank_ic": "" if pd.isna(mean) else round(mean, 6),
                "median_rank_ic": "" if ic.empty else round(float(ic.median()), 6),
                "std_rank_ic": "" if pd.isna(std) else round(std, 6),
                "ic_ir": "" if pd.isna(std) or std == 0 else round(mean / std, 6),
                "positive_rate": "" if ic.empty else round(float((ic > 0).mean()), 6),
                "mean_pair_count": round(float(group["pair_count_numeric"].mean()), 2),
            }
        )
    return pd.DataFrame(rows, columns=SUMMARY_COLUMNS)


def main() -> int:
    args = parse_args()
    requested_end = 99999999 if args.end_date == "latest" else int(args.end_date)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    catalog = pd.read_csv(FACTOR_CATALOG_FILE).set_index("factor_code")
    target_factors = [
        code
        for code, row in catalog.iterrows()
        if str(row["style"]) in TARGET_STYLES
    ]
    missing_supported = sorted(set(target_factors) - set(GROWTH_SNAPSHOT_METRICS) - {EARNINGS_ACCEL_FACTOR, MOMENTUM_FACTOR})
    if missing_supported:
        raise RuntimeError(f"unsupported Growth/Momentum factors in catalog: {missing_supported}")

    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    conn = loaders.get_connection()
    try:
        latest_price = latest_price_date_id(conn, requested_end)
        trade_frame = load_trade_dates(conn, latest_price)
        if trade_frame.empty:
            raise RuntimeError("no trade dates found")
        trade_dates = _as_int_list(trade_frame["date_id"])
        trade_index_by_date = {
            int(row.date_id): int(row.trade_day_index)
            for row in trade_frame.itertuples(index=False)
        }
        tdi_to_date = {
            int(row.trade_day_index): int(row.date_id)
            for row in trade_frame.itertuples(index=False)
        }
        eval_dates_by_horizon = select_eval_dates(
            trade_dates,
            lookback_trade_days=args.lookback_trade_days,
        )
        all_eval_dates = sorted({date for dates in eval_dates_by_horizon.values() for date in dates})
        if not all_eval_dates:
            raise RuntimeError("no eligible evaluation dates")

        first_eval_tdi = min(trade_index_by_date[date_id] for date_id in all_eval_dates)
        market_start_tdi = max(
            min(tdi_to_date),
            first_eval_tdi - max(MOMENTUM_HALF_TRADE_DAYS, LIQUIDITY_LOOKBACK_TRADE_DAYS - 1),
        )
        market_start = tdi_to_date[market_start_tdi]
        market_end = latest_price
        market_trade_dates = [
            int(date_id)
            for date_id in trade_dates
            if market_start <= int(date_id) <= market_end
        ]
        print(
            "[factor] growth_momentum_daily_rank_ic: "
            f"1D_dates={len(eval_dates_by_horizon[1])} "
            f"5D_dates={len(eval_dates_by_horizon[5])} "
            f"signal_dates={len(all_eval_dates)} "
            f"price_window={market_start}..{market_end}",
            flush=True,
        )

        market = load_daily_market_window(conn, market_start, market_end)
        if market.empty:
            raise RuntimeError("no market rows loaded for selected window")
        adj_close = pivot_daily(market, "adj_close", market_trade_dates)
        close = pivot_daily(market, "close", market_trade_dates)
        amount = pivot_daily(market, "amount", market_trade_dates)
        market_cap = pivot_daily(market, "market_cap", market_trade_dates)

        first_date = loaders.load_stock_first_listing_date(conn)
        first_tdi = {
            code: trade_index_by_date[date_id]
            for code, date_id in first_date.items()
            if date_id in trade_index_by_date
        }
        names = loaders.load_stock_names(conn)
        industry = loaders.load_stock_industry(conn)

        universe_members = build_universe_members(
            all_eval_dates,
            trade_index_by_date,
            first_tdi,
            names,
            close,
            market_cap,
            amount,
        )

        snapshot_factors = [code for code in target_factors if code in GROWTH_SNAPSHOT_METRICS]
        raw_panels = load_growth_snapshot_panels(conn, all_eval_dates, snapshot_factors)
        if EARNINGS_ACCEL_FACTOR in target_factors:
            raw_panels[EARNINGS_ACCEL_FACTOR] = load_earnings_accel_panel(
                conn,
                all_eval_dates,
                min_eval_date_id=min(all_eval_dates),
                max_eval_date_id=max(all_eval_dates),
            )
        if MOMENTUM_FACTOR in target_factors:
            raw_panels[MOMENTUM_FACTOR] = momentum_panel(adj_close, all_eval_dates)
    finally:
        conn.close()

    forward = forward_returns(adj_close, HORIZONS)
    detail_rows = build_detail_rows(
        eval_dates_by_horizon=eval_dates_by_horizon,
        all_eval_dates=all_eval_dates,
        target_factors=target_factors,
        catalog=catalog,
        raw_panels=raw_panels,
        forward=forward,
        universe_members=universe_members,
        market_cap=market_cap,
        industry=industry,
        trade_dates=trade_dates,
        calc_version=args.calc_version,
        min_names=args.min_names,
    )
    detail = pd.DataFrame(detail_rows, columns=DETAIL_COLUMNS)
    summary = build_summary(detail)
    detail_path = output_dir / DETAIL_FILE.name
    summary_path = output_dir / SUMMARY_FILE.name
    detail.to_csv(detail_path, index=False)
    summary.to_csv(summary_path, index=False)

    factor_io.append_manifest(
        run_id=run_id,
        calc_version=args.calc_version,
        layer="growth_momentum_daily_rank_ic",
        factor_code=",".join(target_factors),
        start_date_id=int(min(all_eval_dates)),
        end_date_id=int(max(all_eval_dates)),
        row_count=len(detail),
        valid_count=int(pd.to_numeric(detail["rank_ic"], errors="coerce").notna().sum()) if not detail.empty else 0,
        coverage="",
        status="success",
    )
    append_summary(
        "growth_momentum_daily_rank_ic",
        f"done rows={len(detail)} summary_rows={len(summary)} output={output_dir}",
    )
    print(f"[factor] wrote {detail_path} rows={len(detail)}", flush=True)
    print(f"[factor] wrote {summary_path} rows={len(summary)}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
