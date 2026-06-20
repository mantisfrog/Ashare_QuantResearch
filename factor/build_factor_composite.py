"""Build composite style scores (Phase 1 skeleton).

Aggregates neutralized exposures into one score per style
(value / quality / growth / momentum / risk) and an equal-weighted total_score.
Output: data/factor/composite/. Implemented in Phase 5.
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
    parser = argparse.ArgumentParser(description="Build composite style scores.")
    parser.add_argument("--start", default="201501", help="First rebalance month YYYYMM.")
    parser.add_argument("--end", default="latest", help="Last rebalance month YYYYMM or 'latest'.")
    parser.add_argument("--factors", default="all", help="Accepted for a uniform CLI; unused here.")
    parser.add_argument("--calc-version", default=CALC_VERSION, help="calc_version stamp.")
    parser.add_argument("--rebuild", action="store_true", help="Recompute all months.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    append_summary(
        "factor_composite",
        f"start range={args.start}..{args.end} version={args.calc_version}",
    )
    print("[factor] build_factor_composite: SKELETON — composite lands in Phase 5", flush=True)
    # TODO(Phase 5): combine neutralized exposures -> style scores + total_score
    # -> data/factor/composite/composite_<year>.csv.
    append_summary("factor_composite", "skeleton-noop")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
