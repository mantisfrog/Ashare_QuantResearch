"""Build raw factor values (Phase 1 skeleton).

For each rebalance date and in-universe stock, evaluate every factor in
factor_catalog.csv straight from the formula (point-in-time via the bridge for
fundamentals, back-adjusted prices for technicals). No cleaning happens here:
NaN / extreme values are written as-is. Output: data/factor/raw/<factor>/.

Fundamental factors land in Phase 3, price factors in Phase 4.
"""
from __future__ import annotations

import sys
from pathlib import Path

_ETL_DIR = Path(__file__).resolve().parents[1] / "etl"
if str(_ETL_DIR) not in sys.path:
    sys.path.insert(0, str(_ETL_DIR))

import argparse

from etl_logging import append_summary
from factor_config import CALC_VERSION


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build raw factor values.")
    parser.add_argument("--start", default="201501", help="First rebalance month YYYYMM.")
    parser.add_argument("--end", default="latest", help="Last rebalance month YYYYMM or 'latest'.")
    parser.add_argument("--factors", default="all", help="Comma-separated factor_code list, or 'all'.")
    parser.add_argument("--calc-version", default=CALC_VERSION, help="calc_version stamp.")
    parser.add_argument("--rebuild", action="store_true", help="Recompute all months.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    append_summary(
        "factor_raw",
        f"start range={args.start}..{args.end} factors={args.factors} version={args.calc_version}",
    )
    print("[factor] build_factor_raw: SKELETON — formulas land in Phase 3/4", flush=True)
    # TODO(Phase 3/4): load catalog + universe -> compute raw factor_value per
    # (date_id, stock_code, factor_code) -> data/factor/raw/<factor>/<year>.csv.
    append_summary("factor_raw", "skeleton-noop")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
