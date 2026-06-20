"""Composite style scores from neutralized factor exposures.

Combines per-factor neutralized exposures into one score per style
(value / quality / growth / momentum / risk) and an equal-weighted total.
Implemented in Phase 5.
"""
from __future__ import annotations

import pandas as pd

from factor_config import STYLES


def composite_style_scores(
    exposure_long: pd.DataFrame,
    catalog: pd.DataFrame,
) -> pd.DataFrame:
    """Aggregate neutralized exposures into style scores + total_score. (Phase 5)

    ``exposure_long`` has columns (date_id, stock_code, factor_code,
    neutralized_value); ``catalog`` maps factor_code -> style. Returns a wide
    frame keyed by (date_id, stock_code) with one column per style in
    :data:`factor_config.STYLES` plus ``total_score``.
    """
    raise NotImplementedError("Phase 5: composite")
