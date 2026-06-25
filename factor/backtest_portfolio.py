"""Reusable CSV-based factor portfolio backtest.

The script builds a monthly three-stage filtered portfolio from composite style
scores and rebalance-date market cap, then computes daily returns from adjusted
close prices.

Default convention:
  - score at rebalance date R is known after R close;
  - the portfolio starts on the next trading day;
  - daily returns use close-to-close adjusted prices;
  - default filters are market_cap top 30%, growth_score top 10%, and
    quality_score not in the bottom 50%;
  - default raw weights are market_cap * growth_score, with a 10% single-stock
    cap and proportional redistribution.
"""
from __future__ import annotations

import argparse
import math
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd

_PROJECT_ROOT = Path(__file__).resolve().parents[1]
_ETL_DIR = _PROJECT_ROOT / "etl"
if str(_ETL_DIR) not in sys.path:
    sys.path.insert(0, str(_ETL_DIR))

from paths import DATA_DIR, FACTOR_COMPOSITE_DIR  # noqa: E402

try:
    from factor_config import CALC_VERSION
except ImportError:  # pragma: no cover - keeps CLI usable from unusual cwd.
    CALC_VERSION = "v1"


SCORE_COLUMNS = {
    "growth": "growth_score",
    "quality": "quality_score",
}


@dataclass(frozen=True)
class Window:
    start_date_id: int
    end_date_id: int
    price_start_date_id: int


@dataclass(frozen=True)
class OutputPaths:
    daily_returns: Path
    holdings: Path
    rebalance_summary: Path
    summary: Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Backtest an intersection portfolio from factor composite style scores."
        )
    )
    parser.add_argument(
        "--start",
        type=parse_date_id,
        help="Backtest start date as YYYYMMDD or YYYY-MM-DD. Defaults to end - lookback-days.",
    )
    parser.add_argument(
        "--end",
        type=parse_date_id,
        help="Backtest end date as YYYYMMDD or YYYY-MM-DD. Defaults to latest trade day.",
    )
    parser.add_argument(
        "--lookback-days",
        type=int,
        default=365,
        help="Calendar lookback when --start is omitted. Default: 365.",
    )
    parser.add_argument(
        "--growth-top",
        type=parse_fraction,
        default=0.10,
        help="Keep the top fraction by growth_score. Default: 0.10.",
    )
    parser.add_argument(
        "--quality-top",
        type=parse_fraction,
        default=0.50,
        help=(
            "Keep this top fraction by quality_score. Default: 0.50, "
            "equivalent to excluding the bottom 50%."
        ),
    )
    parser.add_argument(
        "--market-cap-top",
        dest="market_cap_top",
        type=parse_fraction,
        default=0.30,
        help=(
            "Keep the top fraction by rebalance-date market_cap. Default: 0.30."
        ),
    )
    parser.add_argument(
        "--calc-version",
        default=CALC_VERSION,
        help=f"Composite calc_version to use. Default: {CALC_VERSION}.",
    )
    parser.add_argument(
        "--portfolio-name",
        help="Output file prefix. Defaults to a name generated from the thresholds.",
    )
    parser.add_argument(
        "--weighting",
        choices=("market_cap_growth_capped", "market_cap_growth", "float_market_cap", "equal"),
        default="market_cap_growth_capped",
        help="Holding weight method. Default: market_cap_growth_capped.",
    )
    parser.add_argument(
        "--max-weight",
        type=parse_fraction,
        default=0.10,
        help="Single-stock cap used by market_cap_growth_capped. Default: 0.10.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DATA_DIR / "backtest",
        help="Directory for output CSV files. Default: data/backtest.",
    )
    parser.add_argument(
        "--daily-path",
        type=Path,
        default=DATA_DIR / "fact_daily.csv",
        help="Daily OHLCV CSV path. Default: data/fact_daily.csv.",
    )
    parser.add_argument(
        "--adjustment-path",
        type=Path,
        default=DATA_DIR / "fact_adjustment_factor_period.csv",
        help="Adjustment factor period CSV path.",
    )
    parser.add_argument(
        "--dim-date-path",
        type=Path,
        default=DATA_DIR / "dim_date.csv",
        help="Trading calendar CSV path.",
    )
    parser.add_argument(
        "--composite-dir",
        type=Path,
        default=FACTOR_COMPOSITE_DIR,
        help="Composite factor directory. Default: data/factor/composite.",
    )
    parser.add_argument(
        "--chunksize",
        type=int,
        default=1_000_000,
        help="Rows per chunk when reading fact_daily.csv. Default: 1000000.",
    )
    parser.add_argument(
        "--no-write",
        action="store_true",
        help="Run the backtest and print the summary without writing CSV outputs.",
    )
    return parser.parse_args()


def parse_date_id(value: str) -> int:
    text = str(value).strip().replace("-", "")
    if len(text) != 8 or not text.isdigit():
        raise argparse.ArgumentTypeError(f"invalid date_id: {value!r}")
    return int(text)


def parse_fraction(value: str) -> float:
    text = str(value).strip()
    is_percent = text.endswith("%")
    if is_percent:
        text = text[:-1]
    number = float(text)
    if is_percent or number > 1:
        number = number / 100.0
    if not 0 < number <= 1:
        raise argparse.ArgumentTypeError("fraction must be in (0, 1] or 0-100%")
    return number


def load_trade_calendar(path: Path) -> pd.DataFrame:
    calendar = pd.read_csv(path, usecols=["date_id", "date", "is_trade_day"])
    calendar = calendar[calendar["is_trade_day"].astype(bool)].copy()
    calendar["date_id"] = calendar["date_id"].astype("int64")
    calendar["date"] = pd.to_datetime(calendar["date"])
    return calendar.sort_values("date_id").reset_index(drop=True)


def resolve_window(
    calendar: pd.DataFrame,
    start: int | None,
    end: int | None,
    lookback_days: int,
) -> Window:
    trade_ids = calendar["date_id"].to_numpy(dtype=np.int64)
    if len(trade_ids) == 0:
        raise ValueError("trading calendar has no trade days")

    if end is None:
        end_date_id = int(trade_ids[-1])
    else:
        end_pos = int(np.searchsorted(trade_ids, end, side="right") - 1)
        if end_pos < 0:
            raise ValueError(f"--end {end} is before the first trade day")
        end_date_id = int(trade_ids[end_pos])

    if start is None:
        end_date = calendar.loc[calendar["date_id"] == end_date_id, "date"].iloc[0]
        target_date = end_date - pd.Timedelta(days=int(lookback_days))
        start_pos = int(np.searchsorted(calendar["date"].to_numpy(), target_date))
    else:
        start_pos = int(np.searchsorted(trade_ids, start, side="left"))
    if start_pos >= len(trade_ids):
        raise ValueError("resolved --start is after the last trade day")

    start_date_id = int(trade_ids[start_pos])
    if start_date_id > end_date_id:
        raise ValueError(f"resolved start {start_date_id} is after end {end_date_id}")

    price_start_pos = max(0, start_pos - 1)
    return Window(
        start_date_id=start_date_id,
        end_date_id=end_date_id,
        price_start_date_id=int(trade_ids[price_start_pos]),
    )


def load_composite(
    composite_dir: Path,
    start_year: int,
    end_year: int,
    calc_version: str,
) -> pd.DataFrame:
    usecols = [
        "date_id",
        "stock_code",
        "calc_version",
        *SCORE_COLUMNS.values(),
    ]
    frames: list[pd.DataFrame] = []
    for year in range(start_year, end_year + 1):
        path = composite_dir / f"composite_{year}.csv"
        if not path.exists():
            continue
        frame = pd.read_csv(path, usecols=usecols, dtype={"stock_code": "string"})
        frame = frame[frame["calc_version"].astype(str) == str(calc_version)]
        if not frame.empty:
            frames.append(frame.drop(columns=["calc_version"]))
    if not frames:
        raise FileNotFoundError(
            f"no composite rows found in {composite_dir} for years {start_year}-{end_year}"
        )
    composite = pd.concat(frames, ignore_index=True)
    composite["date_id"] = composite["date_id"].astype("int64")
    return composite


def build_signal_schedule(
    composite_dates: Iterable[int],
    trade_ids: np.ndarray,
    start_date_id: int,
    end_date_id: int,
) -> pd.DataFrame:
    rows: list[dict[str, int]] = []
    sorted_dates = sorted(int(value) for value in composite_dates if int(value) <= end_date_id)
    for rebalance_date_id in sorted_dates:
        entry_pos = int(np.searchsorted(trade_ids, rebalance_date_id, side="right"))
        if entry_pos >= len(trade_ids):
            continue
        entry_date_id = int(trade_ids[entry_pos])
        if entry_date_id > end_date_id:
            continue
        rows.append({
            "rebalance_date_id": int(rebalance_date_id),
            "entry_date_id": entry_date_id,
        })
    if not rows:
        raise ValueError("no rebalance signals have an entry date in the test window")

    schedule = pd.DataFrame(rows).sort_values("entry_date_id").reset_index(drop=True)
    next_entry = schedule["entry_date_id"].shift(-1)
    exit_ids: list[int] = []
    for value in next_entry:
        if pd.isna(value):
            exit_ids.append(int(end_date_id))
            continue
        pos = int(np.searchsorted(trade_ids, int(value), side="left") - 1)
        exit_ids.append(int(trade_ids[pos]))
    schedule["exit_date_id"] = exit_ids
    active = (
        (schedule["entry_date_id"] <= int(end_date_id))
        & (schedule["exit_date_id"] >= int(start_date_id))
    )
    schedule = schedule[active].copy()
    if schedule.empty:
        raise ValueError("no rebalance interval overlaps the requested test window")
    return schedule.reset_index(drop=True)


def top_mask(values: pd.Series, fraction: float) -> tuple[pd.Series, float]:
    valid = pd.to_numeric(values, errors="coerce")
    threshold = float(valid.dropna().quantile(1.0 - fraction))
    return valid >= threshold, threshold


def select_holdings(
    composite: pd.DataFrame,
    market_cap_snapshots: pd.DataFrame,
    schedule: pd.DataFrame,
    tops: dict[str, float],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    holding_frames: list[pd.DataFrame] = []
    summary_rows: list[dict[str, float | int]] = []
    schedule_by_rebalance = schedule.set_index("rebalance_date_id")

    for rebalance_date_id, cross_section in composite.groupby("date_id", sort=True):
        rebalance_date_id = int(rebalance_date_id)
        if rebalance_date_id not in schedule_by_rebalance.index:
            continue

        market_cap_snapshot = market_cap_snapshots[
            market_cap_snapshots["date_id"].eq(rebalance_date_id)
        ].drop(columns=["date_id"])
        cross_section = cross_section.merge(
            market_cap_snapshot,
            on="stock_code",
            how="left",
        )
        mask = pd.Series(True, index=cross_section.index)
        thresholds: dict[str, float] = {}
        counts: dict[str, int] = {}
        for style, fraction in tops.items():
            column = (
                SCORE_COLUMNS[style]
                if style in SCORE_COLUMNS
                else "market_cap"
            )
            style_mask, threshold = top_mask(cross_section[column], fraction)
            mask &= style_mask
            thresholds[style] = threshold
            counts[style] = int(style_mask.sum())

        selected = cross_section.loc[
            mask,
            ["stock_code", *SCORE_COLUMNS.values(), "market_cap"],
        ].copy()
        selected_count = len(selected)
        entry_date_id = int(schedule_by_rebalance.loc[rebalance_date_id, "entry_date_id"])
        exit_date_id = int(schedule_by_rebalance.loc[rebalance_date_id, "exit_date_id"])

        if selected_count:
            selected.insert(0, "rebalance_date_id", rebalance_date_id)
            selected.insert(1, "entry_date_id", entry_date_id)
            selected.insert(2, "exit_date_id", exit_date_id)
            holding_frames.append(selected)

        summary_rows.append({
            "rebalance_date_id": rebalance_date_id,
            "entry_date_id": entry_date_id,
            "exit_date_id": exit_date_id,
            "universe_count": int(len(cross_section)),
            "market_cap_top_count": counts["market_cap"],
            "growth_top_count": counts["growth"],
            "quality_top_count": counts["quality"],
            "selected_count": int(selected_count),
            "market_cap_threshold": thresholds["market_cap"],
            "growth_threshold": thresholds["growth"],
            "quality_threshold": thresholds["quality"],
        })

    if not holding_frames:
        raise ValueError("intersection selection produced no holdings")
    holdings = pd.concat(holding_frames, ignore_index=True)
    rebalance_summary = pd.DataFrame(summary_rows)
    return holdings, rebalance_summary


def load_market_cap_snapshots(
    daily_path: Path,
    stock_codes: set[str],
    date_ids: Iterable[int],
    chunksize: int,
) -> pd.DataFrame:
    usecols = ["date_id", "stock_code", "market_cap"]
    wanted_dates = {int(value) for value in date_ids}
    frames: list[pd.DataFrame] = []
    for chunk in pd.read_csv(
        daily_path,
        usecols=usecols,
        dtype={"stock_code": "string"},
        chunksize=int(chunksize),
    ):
        chunk["date_id"] = chunk["date_id"].astype("int64")
        mask = chunk["date_id"].isin(wanted_dates) & chunk["stock_code"].isin(stock_codes)
        if mask.any():
            frames.append(chunk.loc[mask].copy())
    if not frames:
        raise ValueError("no market_cap snapshots found for rebalance dates")
    snapshots = pd.concat(frames, ignore_index=True)
    snapshots["stock_code"] = snapshots["stock_code"].astype(str)
    snapshots["market_cap"] = pd.to_numeric(snapshots["market_cap"], errors="coerce")
    return snapshots[snapshots["market_cap"] > 0].copy()


def load_daily_prices(
    daily_path: Path,
    stock_codes: set[str],
    start_date_id: int,
    end_date_id: int,
    chunksize: int,
) -> pd.DataFrame:
    usecols = ["date_id", "stock_code", "close", "float_market_cap"]
    frames: list[pd.DataFrame] = []
    for chunk in pd.read_csv(
        daily_path,
        usecols=usecols,
        dtype={"stock_code": "string"},
        chunksize=int(chunksize),
    ):
        chunk["date_id"] = chunk["date_id"].astype("int64")
        mask = (
            chunk["date_id"].between(start_date_id, end_date_id)
            & chunk["stock_code"].isin(stock_codes)
        )
        if mask.any():
            frames.append(chunk.loc[mask].copy())
    if not frames:
        raise ValueError("no daily price rows found for selected holdings")
    daily = pd.concat(frames, ignore_index=True)
    daily["stock_code"] = daily["stock_code"].astype(str)
    daily["close"] = pd.to_numeric(daily["close"], errors="coerce")
    daily["float_market_cap"] = pd.to_numeric(
        daily["float_market_cap"], errors="coerce"
    )
    daily = daily[daily["close"] > 0].copy()
    return daily


def apply_holding_weights(
    holdings: pd.DataFrame,
    rebalance_summary: pd.DataFrame,
    daily_prices: pd.DataFrame,
    weighting: str,
    max_weight: float,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    weighted_frames: list[pd.DataFrame] = []
    summary_frames: list[pd.DataFrame] = []
    market_cap_snapshots = daily_prices.loc[
        :,
        ["date_id", "stock_code", "float_market_cap"],
    ].copy()

    for rebalance_date_id, group in holdings.groupby("rebalance_date_id", sort=True):
        group = group.copy()
        if weighting == "equal":
            group["weight"] = 1.0 / len(group)
            group["raw_weight_signal"] = 1.0
            group["uncapped_weight"] = group["weight"]
            invalid_weight_signal_count = 0
        else:
            if weighting == "float_market_cap":
                snapshot = market_cap_snapshots[
                    market_cap_snapshots["date_id"].eq(int(rebalance_date_id))
                ].drop(columns=["date_id"])
                group = group.merge(snapshot, on="stock_code", how="left")
                group["raw_weight_signal"] = pd.to_numeric(
                    group["float_market_cap"], errors="coerce"
                )
            else:
                group["market_cap"] = pd.to_numeric(group["market_cap"], errors="coerce")
                group["growth_score"] = pd.to_numeric(
                    group["growth_score"], errors="coerce"
                )
                group["raw_weight_signal"] = group["market_cap"] * group["growth_score"]

            valid_signal = group["raw_weight_signal"] > 0
            invalid_weight_signal_count = int((~valid_signal).sum())
            group = group[valid_signal].copy()
            if group.empty:
                raise ValueError(
                    f"no positive raw weight signal rows for rebalance {rebalance_date_id}"
                )
            group["uncapped_weight"] = group["raw_weight_signal"] / group[
                "raw_weight_signal"
            ].sum()
            if weighting == "market_cap_growth_capped":
                group["weight"] = cap_and_redistribute_weights(
                    group["raw_weight_signal"],
                    max_weight=max_weight,
                )
            else:
                group["weight"] = group["uncapped_weight"]

        weighted_frames.append(group)
        summary_frames.append(pd.DataFrame([{
            "rebalance_date_id": int(rebalance_date_id),
            "weighted_count": int(len(group)),
            "invalid_weight_signal_count": invalid_weight_signal_count,
            "weight_sum": float(group["weight"].sum()),
            "max_weight": float(group["weight"].max()),
            "capped_weight_count": int((group["weight"] >= max_weight - 1e-12).sum())
            if weighting == "market_cap_growth_capped"
            else 0,
        }]))

    weighted = pd.concat(weighted_frames, ignore_index=True)
    weight_summary = pd.concat(summary_frames, ignore_index=True)
    rebalance_summary = rebalance_summary.merge(
        weight_summary,
        on="rebalance_date_id",
        how="left",
    )
    rebalance_summary["weighting"] = weighting
    return weighted, rebalance_summary


def cap_and_redistribute_weights(raw_signal: pd.Series, max_weight: float) -> pd.Series:
    """Normalize positive raw signals, cap weights, and redistribute excess."""
    raw = pd.to_numeric(raw_signal, errors="coerce").astype("float64")
    if (raw <= 0).any() or raw.isna().any():
        raise ValueError("raw_signal must be positive and non-null before capping")
    if len(raw) * max_weight < 1.0 - 1e-12:
        raise ValueError(
            f"max_weight={max_weight} is infeasible for {len(raw)} holdings"
        )

    weights = raw / raw.sum()
    final = pd.Series(0.0, index=raw.index, dtype="float64")
    remaining = pd.Series(True, index=raw.index)
    remaining_weight = 1.0
    remaining_raw = raw.copy()

    while remaining.any():
        candidate = remaining_raw[remaining] / remaining_raw[remaining].sum()
        candidate = candidate * remaining_weight
        over_cap = candidate > max_weight
        if not over_cap.any():
            final.loc[candidate.index] = candidate
            break
        capped_index = candidate[over_cap].index
        final.loc[capped_index] = max_weight
        remaining.loc[capped_index] = False
        remaining_weight = 1.0 - final.sum()
        if remaining_weight <= 1e-12:
            break

    return final / final.sum()


def add_adjusted_close(
    daily: pd.DataFrame,
    adjustment_path: Path,
    stock_codes: set[str],
) -> pd.DataFrame:
    adjustment = pd.read_csv(
        adjustment_path,
        usecols=[
            "stock_code",
            "valid_from_date_id",
            "valid_to_date_id",
            "adjust_factor",
        ],
        dtype={"stock_code": "string"},
    )
    adjustment = adjustment[adjustment["stock_code"].isin(stock_codes)].copy()
    if adjustment.empty:
        raise ValueError("no adjustment factor rows found for selected holdings")

    adjusted_frames: list[pd.DataFrame] = []
    for stock_code, stock_daily in daily.groupby("stock_code", sort=False):
        stock_adjustment = adjustment[adjustment["stock_code"].astype(str) == stock_code]
        if stock_adjustment.empty:
            continue
        merged = pd.merge_asof(
            stock_daily.sort_values("date_id"),
            stock_adjustment.sort_values("valid_from_date_id"),
            left_on="date_id",
            right_on="valid_from_date_id",
            direction="backward",
            suffixes=("", "_adj"),
        )
        valid = merged["date_id"] <= merged["valid_to_date_id"]
        merged = merged[valid].copy()
        merged["stock_code"] = stock_code
        adjusted_frames.append(merged[["date_id", "stock_code", "close", "adjust_factor"]])

    if not adjusted_frames:
        raise ValueError("daily prices could not be matched to adjustment factors")
    adjusted = pd.concat(adjusted_frames, ignore_index=True)
    adjusted["adjust_factor"] = pd.to_numeric(adjusted["adjust_factor"], errors="coerce")
    adjusted = adjusted[adjusted["adjust_factor"] > 0].copy()
    adjusted["adj_close"] = adjusted["close"] * adjusted["adjust_factor"]
    return adjusted[["date_id", "stock_code", "adj_close"]]


def build_return_matrix(
    adjusted_prices: pd.DataFrame,
    trade_ids: np.ndarray,
    price_start_date_id: int,
    end_date_id: int,
) -> pd.DataFrame:
    active_trade_ids = [
        int(value)
        for value in trade_ids
        if int(price_start_date_id) <= int(value) <= int(end_date_id)
    ]
    price_pivot = adjusted_prices.pivot_table(
        index="date_id",
        columns="stock_code",
        values="adj_close",
        aggfunc="last",
    )
    price_pivot = price_pivot.reindex(active_trade_ids).sort_index().ffill()
    returns = price_pivot.pct_change(fill_method=None)
    returns = returns.replace([np.inf, -np.inf], np.nan)
    return returns


def compute_portfolio_returns(
    returns: pd.DataFrame,
    holdings: pd.DataFrame,
    calendar: pd.DataFrame,
    schedule: pd.DataFrame,
    start_date_id: int,
    end_date_id: int,
) -> pd.DataFrame:
    output_dates = calendar[
        calendar["date_id"].between(int(start_date_id), int(end_date_id))
    ][["date_id", "date"]].copy()
    output_dates["date_id"] = output_dates["date_id"].astype("int64")

    daily_frames: list[pd.DataFrame] = []
    holdings_by_rebalance = {
        int(key): frame.copy()
        for key, frame in holdings.groupby("rebalance_date_id", sort=False)
    }
    for row in schedule.itertuples(index=False):
        rebalance_date_id = int(row.rebalance_date_id)
        if rebalance_date_id not in holdings_by_rebalance:
            continue
        period_dates = output_dates[
            output_dates["date_id"].between(
                max(int(row.entry_date_id), int(start_date_id)),
                min(int(row.exit_date_id), int(end_date_id)),
            )
        ].copy()
        if period_dates.empty:
            continue

        period_holdings = holdings_by_rebalance[rebalance_date_id]
        stock_codes = period_holdings["stock_code"].astype(str).tolist()
        weights = period_holdings.set_index("stock_code")["weight"].astype("float64")
        stock_returns = returns.reindex(index=period_dates["date_id"], columns=stock_codes)
        available_count = stock_returns.notna().sum(axis=1).astype(int)
        portfolio_return = stock_returns.fillna(0.0).mul(weights, axis=1).sum(axis=1)

        period_dates["rebalance_date_id"] = rebalance_date_id
        period_dates["holding_count"] = int(len(stock_codes))
        period_dates["priced_holding_count"] = available_count.to_numpy()
        period_dates["portfolio_return"] = portfolio_return.to_numpy(dtype="float64")
        daily_frames.append(period_dates)

    if not daily_frames:
        raise ValueError("no active portfolio return rows were produced")

    daily = pd.concat(daily_frames, ignore_index=True)
    daily = daily.sort_values("date_id").reset_index(drop=True)
    daily["net_value"] = (1.0 + daily["portfolio_return"]).cumprod()
    daily["cum_return"] = daily["net_value"] - 1.0
    daily["date"] = daily["date"].dt.strftime("%Y-%m-%d")
    return daily[
        [
            "date_id",
            "date",
            "rebalance_date_id",
            "holding_count",
            "priced_holding_count",
            "portfolio_return",
            "net_value",
            "cum_return",
        ]
    ]


def summarize_performance(
    daily: pd.DataFrame,
    holdings: pd.DataFrame,
    rebalance_summary: pd.DataFrame,
    tops: dict[str, float],
    calc_version: str,
    weighting: str,
    max_weight: float,
) -> pd.DataFrame:
    returns = daily["portfolio_return"].astype("float64")
    net_value = daily["net_value"].astype("float64")
    trading_days = int(len(daily))
    total_return = float(net_value.iloc[-1] - 1.0)
    annual_return = (
        float((1.0 + total_return) ** (252.0 / trading_days) - 1.0)
        if trading_days > 0 and total_return > -1.0
        else float("nan")
    )
    annual_vol = float(returns.std(ddof=1) * math.sqrt(252.0))
    sharpe = (
        float(returns.mean() / returns.std(ddof=1) * math.sqrt(252.0))
        if returns.std(ddof=1) > 0
        else float("nan")
    )
    drawdown = net_value / net_value.cummax() - 1.0
    max_drawdown = float(drawdown.min())
    win_rate = float((returns > 0).mean())
    count_column = (
        "weighted_count" if "weighted_count" in rebalance_summary.columns else "selected_count"
    )
    avg_holding_count = float(rebalance_summary[count_column].mean())

    rows = [
        ("calc_version", calc_version),
        ("weighting", weighting),
        ("max_position_weight", max_weight),
        ("market_cap_top", tops["market_cap"]),
        ("growth_top", tops["growth"]),
        ("quality_top", tops["quality"]),
        ("start_date_id", int(daily["date_id"].iloc[0])),
        ("end_date_id", int(daily["date_id"].iloc[-1])),
        ("trading_days", trading_days),
        ("rebalance_count", int(rebalance_summary["selected_count"].gt(0).sum())),
        ("holding_rows", int(len(holdings))),
        ("avg_holding_count", avg_holding_count),
        ("min_holding_count", int(rebalance_summary[count_column].min())),
        ("max_holding_count", int(rebalance_summary[count_column].max())),
        ("total_return", total_return),
        ("annual_return", annual_return),
        ("annual_vol", annual_vol),
        ("sharpe_0rf", sharpe),
        ("max_drawdown", max_drawdown),
        ("win_rate", win_rate),
    ]
    return pd.DataFrame(rows, columns=["metric", "value"])


def output_paths(output_dir: Path, portfolio_name: str) -> OutputPaths:
    return OutputPaths(
        daily_returns=output_dir / f"{portfolio_name}_daily_returns.csv",
        holdings=output_dir / f"{portfolio_name}_holdings.csv",
        rebalance_summary=output_dir / f"{portfolio_name}_rebalance_summary.csv",
        summary=output_dir / f"{portfolio_name}_summary.csv",
    )


def default_portfolio_name(tops: dict[str, float], weighting: str) -> str:
    parts = [
        f"market_cap_top{int(round(tops['market_cap'] * 100))}",
        f"growth_top{int(round(tops['growth'] * 100))}",
        f"quality_top{int(round(tops['quality'] * 100))}",
        "intersection",
        weighting,
    ]
    return "_".join(parts)


def write_outputs(
    daily: pd.DataFrame,
    holdings: pd.DataFrame,
    rebalance_summary: pd.DataFrame,
    summary: pd.DataFrame,
    paths: OutputPaths,
) -> None:
    paths.daily_returns.parent.mkdir(parents=True, exist_ok=True)
    daily.to_csv(paths.daily_returns, index=False)
    holdings.to_csv(paths.holdings, index=False)
    rebalance_summary.to_csv(paths.rebalance_summary, index=False)
    summary.to_csv(paths.summary, index=False)


def format_percent(value: object) -> str:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return str(value)
    return f"{number:.2%}"


def print_summary(summary: pd.DataFrame, paths: OutputPaths | None) -> None:
    values = dict(zip(summary["metric"], summary["value"], strict=False))
    print("Backtest summary")
    print(f"  weighting: {values['weighting']}")
    print(f"  period: {int(values['start_date_id'])} - {int(values['end_date_id'])}")
    print(f"  trading_days: {int(values['trading_days'])}")
    print(f"  rebalance_count: {int(values['rebalance_count'])}")
    print(f"  avg_holding_count: {float(values['avg_holding_count']):.1f}")
    print(f"  total_return: {format_percent(values['total_return'])}")
    print(f"  annual_return: {format_percent(values['annual_return'])}")
    print(f"  annual_vol: {format_percent(values['annual_vol'])}")
    print(f"  sharpe_0rf: {float(values['sharpe_0rf']):.3f}")
    print(f"  max_drawdown: {format_percent(values['max_drawdown'])}")
    if paths is not None:
        print("Outputs")
        print(f"  daily_returns: {paths.daily_returns}")
        print(f"  holdings: {paths.holdings}")
        print(f"  rebalance_summary: {paths.rebalance_summary}")
        print(f"  summary: {paths.summary}")


def main() -> int:
    args = parse_args()
    tops = {
        "market_cap": float(args.market_cap_top),
        "growth": float(args.growth_top),
        "quality": float(args.quality_top),
    }
    portfolio_name = args.portfolio_name or default_portfolio_name(tops, args.weighting)

    calendar = load_trade_calendar(args.dim_date_path)
    window = resolve_window(calendar, args.start, args.end, args.lookback_days)
    trade_ids = calendar["date_id"].to_numpy(dtype=np.int64)
    start_year = window.start_date_id // 10000 - 1
    end_year = window.end_date_id // 10000
    composite = load_composite(
        args.composite_dir,
        start_year=start_year,
        end_year=end_year,
        calc_version=args.calc_version,
    )
    composite = composite[composite["date_id"] <= window.end_date_id].copy()
    schedule = build_signal_schedule(
        composite["date_id"].unique(),
        trade_ids=trade_ids,
        start_date_id=window.start_date_id,
        end_date_id=window.end_date_id,
    )
    earliest_signal = int(schedule["rebalance_date_id"].min())
    price_start = min(window.price_start_date_id, earliest_signal)

    candidate_stock_codes = set(composite["stock_code"].astype(str))
    market_cap_snapshots = load_market_cap_snapshots(
        args.daily_path,
        stock_codes=candidate_stock_codes,
        date_ids=schedule["rebalance_date_id"].unique(),
        chunksize=args.chunksize,
    )
    holdings, rebalance_summary = select_holdings(
        composite,
        market_cap_snapshots,
        schedule,
        tops,
    )
    stock_codes = set(holdings["stock_code"].astype(str))
    daily_prices = load_daily_prices(
        args.daily_path,
        stock_codes=stock_codes,
        start_date_id=price_start,
        end_date_id=window.end_date_id,
        chunksize=args.chunksize,
    )
    holdings, rebalance_summary = apply_holding_weights(
        holdings,
        rebalance_summary,
        daily_prices,
        weighting=args.weighting,
        max_weight=float(args.max_weight),
    )
    adjusted_prices = add_adjusted_close(
        daily_prices,
        adjustment_path=args.adjustment_path,
        stock_codes=stock_codes,
    )
    stock_returns = build_return_matrix(
        adjusted_prices,
        trade_ids=trade_ids,
        price_start_date_id=price_start,
        end_date_id=window.end_date_id,
    )
    daily = compute_portfolio_returns(
        stock_returns,
        holdings,
        calendar,
        schedule,
        start_date_id=window.start_date_id,
        end_date_id=window.end_date_id,
    )
    summary = summarize_performance(
        daily,
        holdings,
        rebalance_summary,
        tops=tops,
        calc_version=str(args.calc_version),
        weighting=str(args.weighting),
        max_weight=float(args.max_weight),
    )

    paths: OutputPaths | None = None
    if not args.no_write:
        paths = output_paths(args.output_dir, portfolio_name)
        write_outputs(daily, holdings, rebalance_summary, summary, paths)
    print_summary(summary, paths)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
