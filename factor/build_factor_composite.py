"""Build composite style scores (Phase 5).

Per rebalance cross-section, aggregates the neutralized factor exposures into
one score per style (value / quality / growth / momentum / reversal / risk) and an
equal-weighted ``total_score``. Output: data/factor/composite/.
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

import combine
import factor_io
import loaders
from combine import COMPOSITE_COLUMNS, STYLE_SCORE_COLUMNS
from etl_logging import append_summary
from factor_config import CALC_VERSION, STYLES
from paths import FACTOR_CATALOG_FILE, FACTOR_COMPOSITE_DIR, FACTOR_EXPOSURE_DIR

OUTPUT_COLUMNS = [
    "date_id", "stock_code", "calc_version", *STYLE_SCORE_COLUMNS, "total_score",
]
_SCORE_COLUMNS = [*STYLE_SCORE_COLUMNS, "total_score"]


def month_bound_date_id(month: str, *, upper: bool) -> int:
    value = int(month)
    return value * 100 + (31 if upper else 1)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build composite style scores.")
    parser.add_argument("--start", default="201501", help="First rebalance month YYYYMM.")
    parser.add_argument("--end", default="latest", help="Last rebalance month YYYYMM or 'latest'.")
    parser.add_argument("--factors", default="all", help="Must be 'all'; composites require the full catalog.")
    parser.add_argument("--calc-version", default=CALC_VERSION, help="calc_version stamp.")
    parser.add_argument("--rebuild", action="store_true", help="Recompute months already present.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.factors != "all":
        print("[factor] build_factor_composite: --factors must be 'all' for composite builds", flush=True)
        return 1
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    catalog = pd.read_csv(FACTOR_CATALOG_FILE).set_index("factor_code")

    start_id = month_bound_date_id(args.start, upper=False)
    end_id = 99999999 if args.end == "latest" else month_bound_date_id(args.end, upper=True)
    target_set = set(loaders.rebalance_date_ids(start_id, end_id))
    if not target_set:
        print("[factor] build_factor_composite: no rebalance dates in range", flush=True)
        return 0

    if args.rebuild:
        compute_dates = set(target_set)
    else:
        compute_dates = target_set - factor_io.done_date_ids(
            FACTOR_COMPOSITE_DIR, "composite", calc_version=args.calc_version
        )
    append_summary(
        "factor_composite",
        f"range={args.start}..{args.end} months={len(compute_dates)} version={args.calc_version}",
    )
    if not compute_dates:
        print("[factor] build_factor_composite: nothing to do (use --rebuild)", flush=True)
        return 0

    # Gather neutralized exposures (long) across every factor that has data.
    frames: list[pd.DataFrame] = []
    implemented: list[str] = []
    for code in catalog.index:
        expo = factor_io.read_year_partitioned_csv(
            FACTOR_EXPOSURE_DIR, code, subdir=code, date_ids=compute_dates,
            usecols=["date_id", "stock_code", "neutralized_value"],
            calc_version=args.calc_version,
        )
        if expo.empty:
            continue
        expo["factor_code"] = code
        implemented.append(code)
        frames.append(expo)
    if not frames:
        print("[factor] build_factor_composite: no exposures found; run build_factor_exposure first", flush=True)
        return 0

    exposure_long = pd.concat(frames, ignore_index=True)
    composite = combine.composite_style_scores(exposure_long, catalog)
    if composite.empty:
        print("[factor] build_factor_composite: no composite rows produced", flush=True)
        return 0

    composite["calc_version"] = args.calc_version
    for column in _SCORE_COLUMNS:
        composite[column] = composite[column].round(6)
    composite = composite.loc[:, OUTPUT_COLUMNS]

    factor_io.write_year_partitioned_csv(composite, FACTOR_COMPOSITE_DIR, "composite")

    present = [s for s in STYLES if composite[f"{s}_score"].notna().any()]
    factor_io.append_manifest(
        run_id=run_id, calc_version=args.calc_version, layer="composite",
        factor_code=",".join(present), start_date_id=min(compute_dates),
        end_date_id=max(compute_dates), row_count=len(composite),
        valid_count=int(composite["total_score"].notna().sum()), coverage="",
        status="success",
    )
    append_summary("factor_composite", f"done rows={len(composite)} styles={','.join(present)}")
    print(
        f"[factor] composite: dates={len(compute_dates)} rows={len(composite)} "
        f"styles_present={present}",
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
