"""Build monthly style group and long-short return CSVs for Tableau.

Simplest research version:
  - one row per rebalance month, style, and quantile group;
  - five equal-count score groups by default, Q1 lowest and Q5 highest;
  - equal-weight group returns from next-trading-day entry close to exit close;
  - long-short return = Q5 return - Q1 return;
  - no transaction cost, no shorting constraint, no benchmark adjustment.
"""
from __future__ import annotations

import argparse
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

from paths import DATA_DIR, FACTOR_COMPOSITE_DIR, FACTOR_DATA_DIR  # noqa: E402

try:
    from factor_config import CALC_VERSION, STYLES
except ImportError:  # pragma: no cover - keeps CLI usable from unusual cwd.
    CALC_VERSION = "v1"
    STYLES = ("value", "quality", "growth", "momentum", "reversal", "risk")


STYLE_SCORE_COLUMNS = [f"{style}_score" for style in STYLES]


@dataclass(frozen=True)
class OutputPaths:
    group_returns: Path
    long_short_returns: Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build style quantile group returns and Q5-Q1 long-short returns."
    )
    parser.add_argument(
        "--start",
        type=parse_date_id,
        help="Optional first signal date as YYYYMMDD or YYYY-MM-DD.",
    )
    parser.add_argument(
        "--end",
        type=parse_date_id,
        help="Optional last exit date as YYYYMMDD or YYYY-MM-DD.",
    )
    parser.add_argument(
        "--group-count",
        type=int,
        default=5,
        help="Number of score groups. Default: 5.",
    )
    parser.add_argument(
        "--styles",
        help=(
            "Comma-separated styles to run. Default: all composite styles "
            f"({','.join(STYLES)})."
        ),
    )
    parser.add_argument(
        "--calc-version",
        default=CALC_VERSION,
        help=f"Composite calc_version to use. Default: {CALC_VERSION}.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=FACTOR_DATA_DIR / "style_backtest",
        help="Output directory. Default: data/factor/style_backtest.",
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
        "--allow-partial-latest-period",
        action="store_true",
        help="Include the latest partial month if it exists. Default: complete months only.",
    )
    return parser.parse_args()


def parse_date_id(value: str) -> int:
    text = str(value).strip().replace("-", "")
    if len(text) != 8 or not text.isdigit():
        raise argparse.ArgumentTypeError(f"invalid date_id: {value!r}")
    return int(text)


def parse_styles(value: str | None) -> list[str]:
    if not value:
        return list(STYLES)
    requested = [item.strip() for item in value.split(",") if item.strip()]
    unknown = sorted(set(requested) - set(STYLES))
    if unknown:
        raise ValueError(f"unknown style(s): {', '.join(unknown)}")
    return requested


def load_trade_calendar(path: Path) -> pd.DataFrame:
    raw = pd.read_csv(path, usecols=["date_id", "date", "is_trade_day"])
    raw["date"] = pd.to_datetime(raw["date"])
    is_trade_day = raw["is_trade_day"].astype(str).str.lower().isin(
        ["1", "true", "yes"]
    )
    calendar = raw[is_trade_day].copy()
    calendar["date_id"] = calendar["date_id"].astype("int64")
    calendar = calendar.sort_values("date_id").reset_index(drop=True)
    calendar.attrs["max_calendar_date"] = raw["date"].max()
    return calendar


def latest_complete_month_end_date_id(calendar: pd.DataFrame) -> int:
    max_calendar_date = pd.Timestamp(
        calendar.attrs.get("max_calendar_date", calendar["date"].max())
    )
    max_period = max_calendar_date.to_period("M")
    month_end = max_period.to_timestamp(how="end").normalize()
    complete_period = max_period if max_calendar_date.normalize() >= month_end else max_period - 1

    complete_calendar = calendar[
        calendar["date"].dt.to_period("M") <= complete_period
    ]
    if complete_calendar.empty:
        raise ValueError("no complete month is available in the trading calendar")
    return int(complete_calendar["date_id"].max())


def load_composite(
    composite_dir: Path,
    calc_version: str,
    styles: Iterable[str],
) -> pd.DataFrame:
    score_columns = [f"{style}_score" for style in styles]
    usecols = ["date_id", "stock_code", "calc_version", *score_columns]
    frames: list[pd.DataFrame] = []
    for path in sorted(composite_dir.glob("composite_*.csv")):
        frame = pd.read_csv(path, usecols=usecols, dtype={"stock_code": "string"})
        frame = frame[frame["calc_version"].astype(str) == str(calc_version)]
        if not frame.empty:
            frames.append(frame.drop(columns=["calc_version"]))
    if not frames:
        raise FileNotFoundError(f"no composite rows found in {composite_dir}")
    composite = pd.concat(frames, ignore_index=True)
    composite["date_id"] = composite["date_id"].astype("int64")
    composite["stock_code"] = composite["stock_code"].astype(str)
    return composite.sort_values(["date_id", "stock_code"]).reset_index(drop=True)


def build_monthly_schedule(
    signal_dates: Iterable[int],
    trade_ids: np.ndarray,
    start_date_id: int | None,
    end_date_id: int | None,
) -> pd.DataFrame:
    dates = sorted(int(value) for value in signal_dates)
    if end_date_id is not None:
        dates = [value for value in dates if value <= int(end_date_id)]
    rows: list[dict[str, int]] = []
    for signal_date_id, exit_date_id in zip(dates, dates[1:], strict=False):
        if start_date_id is not None and signal_date_id < int(start_date_id):
            continue
        if end_date_id is not None and exit_date_id > int(end_date_id):
            continue
        entry_pos = int(np.searchsorted(trade_ids, signal_date_id, side="right"))
        if entry_pos >= len(trade_ids):
            continue
        entry_date_id = int(trade_ids[entry_pos])
        rows.append({
            "signal_date_id": int(signal_date_id),
            "entry_date_id": entry_date_id,
            "exit_date_id": int(exit_date_id),
        })
    if not rows:
        raise ValueError("no complete monthly signal periods found")
    return pd.DataFrame(rows).sort_values("signal_date_id").reset_index(drop=True)


def load_daily_snapshots(
    daily_path: Path,
    stock_codes: set[str],
    date_ids: Iterable[int],
    chunksize: int,
) -> pd.DataFrame:
    usecols = ["date_id", "stock_code", "close", "market_cap", "float_market_cap"]
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
        raise ValueError("no daily snapshots found for requested dates")
    snapshots = pd.concat(frames, ignore_index=True)
    snapshots["stock_code"] = snapshots["stock_code"].astype(str)
    for column in ("close", "market_cap", "float_market_cap"):
        snapshots[column] = pd.to_numeric(snapshots[column], errors="coerce")
    snapshots = snapshots[snapshots["close"] > 0].copy()
    return snapshots.sort_values(["stock_code", "date_id"]).reset_index(drop=True)


def add_adjusted_close(
    snapshots: pd.DataFrame,
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
        raise ValueError("no adjustment factor rows found for requested stocks")

    adjusted_frames: list[pd.DataFrame] = []
    for stock_code, stock_snapshots in snapshots.groupby("stock_code", sort=False):
        stock_adjustment = adjustment[adjustment["stock_code"].astype(str) == stock_code]
        if stock_adjustment.empty:
            continue
        merged = pd.merge_asof(
            stock_snapshots.sort_values("date_id"),
            stock_adjustment.sort_values("valid_from_date_id"),
            left_on="date_id",
            right_on="valid_from_date_id",
            direction="backward",
            suffixes=("", "_adj"),
        )
        valid = merged["date_id"] <= merged["valid_to_date_id"]
        merged = merged[valid].copy()
        merged["stock_code"] = stock_code
        adjusted_frames.append(merged[
            ["date_id", "stock_code", "close", "market_cap", "float_market_cap", "adjust_factor"]
        ])

    if not adjusted_frames:
        raise ValueError("daily snapshots could not be matched to adjustment factors")
    adjusted = pd.concat(adjusted_frames, ignore_index=True)
    adjusted["adjust_factor"] = pd.to_numeric(adjusted["adjust_factor"], errors="coerce")
    adjusted = adjusted[adjusted["adjust_factor"] > 0].copy()
    adjusted["adj_close"] = adjusted["close"] * adjusted["adjust_factor"]
    return adjusted[
        ["date_id", "stock_code", "adj_close", "market_cap", "float_market_cap"]
    ]


def build_stock_forward_returns(
    composite: pd.DataFrame,
    schedule: pd.DataFrame,
    snapshots: pd.DataFrame,
) -> pd.DataFrame:
    work = composite.merge(
        schedule,
        left_on="date_id",
        right_on="signal_date_id",
        how="inner",
    ).drop(columns=["date_id"])

    signal_snapshot = snapshots.rename(columns={
        "date_id": "signal_date_id",
        "adj_close": "signal_adj_close",
        "market_cap": "signal_market_cap",
        "float_market_cap": "signal_float_market_cap",
    })
    entry_snapshot = snapshots.rename(columns={
        "date_id": "entry_date_id",
        "adj_close": "entry_adj_close",
        "market_cap": "entry_market_cap",
        "float_market_cap": "entry_float_market_cap",
    })[[
        "entry_date_id",
        "stock_code",
        "entry_adj_close",
        "entry_market_cap",
        "entry_float_market_cap",
    ]]
    exit_snapshot = snapshots.rename(columns={
        "date_id": "exit_date_id",
        "adj_close": "exit_adj_close",
        "market_cap": "exit_market_cap",
        "float_market_cap": "exit_float_market_cap",
    })[["exit_date_id", "stock_code", "exit_adj_close", "exit_market_cap", "exit_float_market_cap"]]

    work = work.merge(
        signal_snapshot,
        on=["signal_date_id", "stock_code"],
        how="left",
    )
    work = work.merge(
        entry_snapshot,
        on=["entry_date_id", "stock_code"],
        how="left",
    )
    work = work.merge(
        exit_snapshot,
        on=["exit_date_id", "stock_code"],
        how="left",
    )
    work["forward_return"] = work["exit_adj_close"] / work["entry_adj_close"] - 1.0
    work = work.replace([np.inf, -np.inf], np.nan)
    return work


def build_style_group_returns(
    stock_returns: pd.DataFrame,
    styles: Iterable[str],
    group_count: int,
    date_map: dict[int, str],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    group_rows: list[dict[str, object]] = []
    group_count = int(group_count)
    if group_count < 2:
        raise ValueError("--group-count must be at least 2")

    for signal_date_id, period in stock_returns.groupby("signal_date_id", sort=True):
        period_meta = period.iloc[0]
        for style in styles:
            score_column = f"{style}_score"
            if score_column not in period.columns:
                continue
            work = period[
                period[score_column].notna() & period["forward_return"].notna()
            ].copy()
            if len(work) < group_count:
                continue
            ranks = work[score_column].rank(method="first")
            work["group_rank"] = (
                pd.qcut(ranks, q=group_count, labels=False).astype(int) + 1
            )
            work["group_label"] = "Q" + work["group_rank"].astype(str)
            for group_rank, group in work.groupby("group_rank", sort=True):
                period_return = float(group["forward_return"].mean())
                group_rows.append({
                    "signal_date_id": int(signal_date_id),
                    "signal_date": date_map.get(int(signal_date_id), ""),
                    "entry_date_id": int(period_meta["entry_date_id"]),
                    "entry_date": date_map.get(int(period_meta["entry_date_id"]), ""),
                    "exit_date_id": int(period_meta["exit_date_id"]),
                    "exit_date": date_map.get(int(period_meta["exit_date_id"]), ""),
                    "style": style,
                    "score_column": score_column,
                    "group_count": group_count,
                    "group_rank": int(group_rank),
                    "group_label": f"Q{int(group_rank)}",
                    "holding_count": int(len(group)),
                    "weight_method": "equal",
                    "period_return": period_return,
                    "avg_score": float(group[score_column].mean()),
                    "min_score": float(group[score_column].min()),
                    "max_score": float(group[score_column].max()),
                    "avg_market_cap": float(group["signal_market_cap"].mean()),
                    "avg_float_market_cap": float(group["signal_float_market_cap"].mean()),
                })

    group_returns = pd.DataFrame(group_rows)
    if group_returns.empty:
        raise ValueError("no group returns were produced")
    group_returns = group_returns.sort_values(
        ["style", "group_rank", "signal_date_id"]
    ).reset_index(drop=True)
    group_returns["net_value"] = (
        1.0 + group_returns["period_return"]
    ).groupby([group_returns["style"], group_returns["group_rank"]]).cumprod()
    group_returns["cum_return"] = group_returns["net_value"] - 1.0

    long_short = build_long_short_returns(group_returns, group_count)
    return group_returns, long_short


def build_long_short_returns(group_returns: pd.DataFrame, group_count: int) -> pd.DataFrame:
    long_rows: list[dict[str, object]] = []
    keys = ["signal_date_id", "style"]
    for (signal_date_id, style), period in group_returns.groupby(keys, sort=True):
        long = period[period["group_rank"] == group_count]
        short = period[period["group_rank"] == 1]
        if long.empty or short.empty:
            continue
        long_row = long.iloc[0]
        short_row = short.iloc[0]
        long_return = float(long_row["period_return"])
        short_return = float(short_row["period_return"])
        long_rows.append({
            "signal_date_id": int(signal_date_id),
            "signal_date": long_row["signal_date"],
            "entry_date_id": int(long_row["entry_date_id"]),
            "entry_date": long_row["entry_date"],
            "exit_date_id": int(long_row["exit_date_id"]),
            "exit_date": long_row["exit_date"],
            "style": style,
            "score_column": long_row["score_column"],
            "group_count": int(group_count),
            "long_group": f"Q{group_count}",
            "short_group": "Q1",
            "long_return": long_return,
            "short_return": short_return,
            "long_short_return": long_return - short_return,
            "long_count": int(long_row["holding_count"]),
            "short_count": int(short_row["holding_count"]),
            "weight_method": "equal",
        })
    result = pd.DataFrame(long_rows).sort_values(
        ["style", "signal_date_id"]
    ).reset_index(drop=True)
    result["long_net_value"] = (
        1.0 + result["long_return"]
    ).groupby(result["style"]).cumprod()
    result["short_net_value"] = (
        1.0 + result["short_return"]
    ).groupby(result["style"]).cumprod()
    result["long_short_net_value"] = (
        1.0 + result["long_short_return"]
    ).groupby(result["style"]).cumprod()
    result["cum_long_short_return"] = result["long_short_net_value"] - 1.0
    return result


def output_paths(output_dir: Path) -> OutputPaths:
    return OutputPaths(
        group_returns=output_dir / "style_group_returns.csv",
        long_short_returns=output_dir / "style_long_short_returns.csv",
    )


def main() -> int:
    args = parse_args()
    styles = parse_styles(args.styles)
    calendar = load_trade_calendar(args.dim_date_path)
    date_map = {
        int(row.date_id): row.date.strftime("%Y-%m-%d")
        for row in calendar.itertuples(index=False)
    }
    trade_ids = calendar["date_id"].to_numpy(dtype=np.int64)
    end_date_id = args.end
    if end_date_id is None and not args.allow_partial_latest_period:
        end_date_id = latest_complete_month_end_date_id(calendar)

    composite = load_composite(args.composite_dir, args.calc_version, styles)
    schedule = build_monthly_schedule(
        composite["date_id"].unique(),
        trade_ids,
        start_date_id=args.start,
        end_date_id=end_date_id,
    )
    composite = composite[composite["date_id"].isin(schedule["signal_date_id"])].copy()
    stock_codes = set(composite["stock_code"].astype(str))
    snapshot_dates = set(schedule["signal_date_id"].astype(int)) | set(
        schedule["exit_date_id"].astype(int)
    ) | set(
        schedule["entry_date_id"].astype(int)
    )
    snapshots = load_daily_snapshots(
        args.daily_path,
        stock_codes=stock_codes,
        date_ids=snapshot_dates,
        chunksize=args.chunksize,
    )
    snapshots = add_adjusted_close(snapshots, args.adjustment_path, stock_codes)
    stock_returns = build_stock_forward_returns(composite, schedule, snapshots)
    group_returns, long_short_returns = build_style_group_returns(
        stock_returns,
        styles=styles,
        group_count=args.group_count,
        date_map=date_map,
    )

    paths = output_paths(args.output_dir)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    group_returns.to_csv(paths.group_returns, index=False)
    long_short_returns.to_csv(paths.long_short_returns, index=False)

    print("Style group backtest complete")
    print(f"  styles: {','.join(styles)}")
    if end_date_id is not None:
        print(f"  effective_end: {end_date_id}")
    print(f"  periods: {schedule['signal_date_id'].min()} - {schedule['exit_date_id'].max()}")
    print(f"  group_count: {args.group_count}")
    print(f"  group_rows: {len(group_returns)}")
    print(f"  long_short_rows: {len(long_short_returns)}")
    print(f"  group_returns: {paths.group_returns}")
    print(f"  long_short_returns: {paths.long_short_returns}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
