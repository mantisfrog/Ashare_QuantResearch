"""Factor diagnostics: coverage, rank IC, and quantile group returns.

Uses forward returns over :data:`factor_config.FORWARD_HORIZONS_MONTHS`
rebalance steps. Implemented alongside the value factors in Phase 3+.
"""
from __future__ import annotations

import pandas as pd

from factor_config import FORWARD_HORIZONS_MONTHS


def coverage(exposure: pd.DataFrame, universe: pd.DataFrame) -> pd.DataFrame:
    """Per (date_id, factor_code): universe_count, valid_count, coverage. (Phase 3)"""
    raise NotImplementedError("Phase 3: diagnostics")


def rank_ic(exposure: pd.DataFrame, forward_returns: pd.DataFrame) -> pd.DataFrame:
    """Spearman rank IC per (date_id, factor_code) for each forward horizon. (Phase 3)"""
    raise NotImplementedError("Phase 3: diagnostics")


def group_returns(
    exposure: pd.DataFrame,
    forward_returns: pd.DataFrame,
    groups: int = 10,
) -> pd.DataFrame:
    """Forward returns by factor quantile group. (Phase 3)"""
    raise NotImplementedError("Phase 3: diagnostics")
