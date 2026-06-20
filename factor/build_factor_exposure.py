"""Build processed factor exposures (Phase 1 skeleton).

Per rebalance cross-section: direction alignment -> winsorize (MAD x3) ->
z-score + percentile rank -> neutralize on ln(market_cap) + industry. Financial
sector is NULLed for ``financial_na`` factors before neutralization. All
intermediate values are kept for audit. Output: data/factor/exposure/<factor>/.

Implemented in Phase 3.
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
    parser = argparse.ArgumentParser(description="Build processed factor exposures.")
    parser.add_argument("--start", default="201501", help="First rebalance month YYYYMM.")
    parser.add_argument("--end", default="latest", help="Last rebalance month YYYYMM or 'latest'.")
    parser.add_argument("--factors", default="all", help="Comma-separated factor_code list, or 'all'.")
    parser.add_argument("--calc-version", default=CALC_VERSION, help="calc_version stamp.")
    parser.add_argument("--rebuild", action="store_true", help="Recompute all months.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    append_summary(
        "factor_exposure",
        f"start range={args.start}..{args.end} factors={args.factors} version={args.calc_version}",
    )
    print("[factor] build_factor_exposure: SKELETON — processing lands in Phase 3", flush=True)
    # TODO(Phase 3): align/winsorize/standardize/neutralize raw values ->
    # data/factor/exposure/<factor>/<year>.csv (raw, winsorized, zscore,
    # neutralized, percentile).
    append_summary("factor_exposure", "skeleton-noop")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
