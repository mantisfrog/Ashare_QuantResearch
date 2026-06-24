"""Build factor diagnostics (Phase 3): coverage + Spearman rank IC.

Per (rebalance date, factor): universe_count, valid_count, coverage, and the
rank IC of the neutralized and raw/non-neutralized exposure against 1m/3m/6m
forward returns (month-end to month-end, back-adjusted). Also writes wide
display matrices of average cross-sectional factor rank correlations.
Output: data/factor/diagnostics/.
"""
from __future__ import annotations

import sys
from pathlib import Path

_ETL_DIR = Path(__file__).resolve().parents[1] / "etl"
if str(_ETL_DIR) not in sys.path:
    sys.path.insert(0, str(_ETL_DIR))

import argparse
from datetime import datetime

import pandas as pd

import diagnostics
import factor_io
import loaders
from etl_logging import append_summary
from factor_config import CALC_VERSION, FORWARD_HORIZONS_MONTHS
from paths import (
    FACTOR_CATALOG_FILE,
    FACTOR_DIAGNOSTICS_DIR,
    FACTOR_EXPOSURE_DIR,
    FACTOR_UNIVERSE_DIR,
)

DIAG_COLUMNS = [
    "date_id", "factor_code", "calc_version",
    "universe_count", "valid_count", "coverage",
    "rank_ic_1m", "rank_ic_3m", "rank_ic_6m",
    "raw_rank_ic_1m", "raw_rank_ic_3m", "raw_rank_ic_6m",
]
NEUTRALIZED_IC_COLUMNS = {1: "rank_ic_1m", 3: "rank_ic_3m", 6: "rank_ic_6m"}
RAW_IC_COLUMNS = {1: "raw_rank_ic_1m", 3: "raw_rank_ic_3m", 6: "raw_rank_ic_6m"}
RANK_CORR_MEAN_FILE = FACTOR_DIAGNOSTICS_DIR / "rank_corr_mean.csv"
RANK_CORR_ROLLING_12M_FILE = FACTOR_DIAGNOSTICS_DIR / "rank_corr_rolling_12m.csv"
RANK_CORR_ROLLING_MONTHS = 12


def month_bound_date_id(month: str, *, upper: bool) -> int:
    value = int(month)
    return value * 100 + (31 if upper else 1)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build factor diagnostics.")
    parser.add_argument("--start", default="201501", help="First rebalance month YYYYMM.")
    parser.add_argument("--end", default="latest", help="Last rebalance month YYYYMM or 'latest'.")
    parser.add_argument("--factors", default="all", help="Comma-separated factor_code list, or 'all'.")
    parser.add_argument("--calc-version", default=CALC_VERSION, help="calc_version stamp.")
    parser.add_argument("--rebuild", action="store_true", help="Accepted for a uniform CLI; diagnostics always recompute.")
    return parser.parse_args()


def write_rank_corr_matrix(matrix: pd.DataFrame, path: Path) -> None:
    """Write a factor x factor display matrix for manual diagnostics."""
    if matrix.empty:
        return
    output = matrix.copy()
    output.index.name = "factor_code"
    output.to_csv(path, float_format="%.4f")


def write_rank_corr_mean(matrix: pd.DataFrame) -> None:
    """Write the full-sample factor rank-correlation display matrix."""
    write_rank_corr_matrix(matrix, RANK_CORR_MEAN_FILE)


def main() -> int:
    args = parse_args()
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    catalog = pd.read_csv(FACTOR_CATALOG_FILE).set_index("factor_code")
    requested = list(catalog.index) if args.factors == "all" else [c.strip() for c in args.factors.split(",")]

    start_id = month_bound_date_id(args.start, upper=False)
    end_id = 99999999 if args.end == "latest" else month_bound_date_id(args.end, upper=True)
    targets = loaders.rebalance_date_ids(start_id, end_id)
    target_set = set(targets)
    if not targets:
        print("[factor] build_factor_diagnostics: no rebalance dates in range", flush=True)
        return 0

    # Exposure per factor; only factors with data are processed.
    neutralized_cross: dict[str, dict[int, pd.Series]] = {}
    raw_cross: dict[str, dict[int, pd.Series]] = {}
    implemented: list[str] = []
    for code in requested:
        if code not in catalog.index:
            continue
        expo = factor_io.read_year_partitioned_csv(
            FACTOR_EXPOSURE_DIR, code, subdir=code, date_ids=target_set,
            usecols=["date_id", "stock_code", "neutralized_value", "zscore_value"],
            calc_version=args.calc_version,
        )
        if expo.empty:
            continue
        implemented.append(code)
        neutralized_cross[code] = {
            int(date_id): group.set_index("stock_code")["neutralized_value"]
            for date_id, group in expo.groupby("date_id")
        }
        raw_cross[code] = {
            int(date_id): group.set_index("stock_code")["zscore_value"]
            for date_id, group in expo.groupby("date_id")
        }
    if not implemented:
        print("[factor] build_factor_diagnostics: no exposures found; run build_factor_exposure first", flush=True)
        return 0

    rank_corr_mean = diagnostics.mean_rank_corr_matrix(neutralized_cross, implemented, targets)
    write_rank_corr_matrix(rank_corr_mean, RANK_CORR_MEAN_FILE)
    print(
        f"[factor] rank_corr_mean: wrote {RANK_CORR_MEAN_FILE} "
        f"factors={len(rank_corr_mean)}",
        flush=True,
    )
    rolling_dates = targets[-RANK_CORR_ROLLING_MONTHS:]
    rank_corr_rolling_12m = diagnostics.mean_rank_corr_matrix(
        neutralized_cross, implemented, rolling_dates
    )
    write_rank_corr_matrix(rank_corr_rolling_12m, RANK_CORR_ROLLING_12M_FILE)
    print(
        f"[factor] rank_corr_rolling_12m: wrote {RANK_CORR_ROLLING_12M_FILE} "
        f"dates={len(rolling_dates)} factors={len(rank_corr_rolling_12m)}",
        flush=True,
    )

    # Universe counts per date.
    universe = factor_io.read_year_partitioned_csv(
        FACTOR_UNIVERSE_DIR, "universe", date_ids=target_set,
        usecols=["date_id", "stock_code", "in_universe"],
        calc_version=args.calc_version,
    )
    universe = universe[universe["in_universe"].astype(bool)]
    universe_count = universe.groupby("date_id")["stock_code"].count().to_dict()

    # Forward returns need rebalance dates beyond the requested end.
    conn = loaders.get_connection()
    try:
        all_dates = loaders.rebalance_date_ids(start_id, 99999999)
        adjusted = loaders.load_rebalance_adjusted_close(conn, all_dates)
    finally:
        conn.close()
    adj_pivot = adjusted.pivot_table(index="date_id", columns="stock_code", values="adj_close").reindex(all_dates)
    forward = diagnostics.forward_returns(adj_pivot, FORWARD_HORIZONS_MONTHS)

    rows: list[dict] = []
    for code in implemented:
        for date_id in targets:
            signal = neutralized_cross[code].get(date_id)
            if signal is None:
                continue
            raw_signal = raw_cross[code].get(date_id)
            valid = int(signal.notna().sum())
            count = int(universe_count.get(date_id, 0))
            record = {
                "date_id": date_id, "factor_code": code, "calc_version": args.calc_version,
                "universe_count": count, "valid_count": valid,
                "coverage": round(valid / count, 6) if count else "",
            }
            for horizon, column in NEUTRALIZED_IC_COLUMNS.items():
                frame = forward.get(horizon)
                if frame is not None and date_id in frame.index:
                    ic = diagnostics.spearman_ic(signal, frame.loc[date_id])
                else:
                    ic = float("nan")
                record[column] = "" if pd.isna(ic) else round(ic, 6)
            for horizon, column in RAW_IC_COLUMNS.items():
                frame = forward.get(horizon)
                if raw_signal is not None and frame is not None and date_id in frame.index:
                    ic = diagnostics.spearman_ic(raw_signal, frame.loc[date_id])
                else:
                    ic = float("nan")
                record[column] = "" if pd.isna(ic) else round(ic, 6)
            rows.append(record)

    result = pd.DataFrame(rows, columns=DIAG_COLUMNS)
    factor_io.write_year_partitioned_csv(
        result, FACTOR_DIAGNOSTICS_DIR, "diagnostics", sort_cols=("date_id", "factor_code")
    )

    summary = (
        result.assign(
            **{
                column: pd.to_numeric(result[column], errors="coerce")
                for column in [
                    "coverage",
                    "rank_ic_1m", "rank_ic_3m", "rank_ic_6m",
                    "raw_rank_ic_1m", "raw_rank_ic_3m", "raw_rank_ic_6m",
                ]
            }
        )
        .groupby("factor_code")[
            [
                "coverage",
                "rank_ic_1m", "rank_ic_3m", "rank_ic_6m",
                "raw_rank_ic_1m", "raw_rank_ic_3m", "raw_rank_ic_6m",
            ]
        ]
        .mean()
    )
    print("[factor] diagnostics (mean over dates):", flush=True)
    print(summary.round(4).to_string(), flush=True)
    factor_io.append_manifest(
        run_id=run_id, calc_version=args.calc_version, layer="diagnostics",
        factor_code=",".join(implemented), start_date_id=targets[0], end_date_id=targets[-1],
        row_count=len(result), valid_count=len(result), coverage="", status="success",
    )
    append_summary("factor_diagnostics", f"done rows={len(result)} factors={len(implemented)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
