"""Cross-sectional factor preprocessing: direction, winsorize, standardize.

Each function operates on one factor's values for a single rebalance date
(a pandas Series indexed by stock_code). Implemented in Phase 3.
"""
from __future__ import annotations

import pandas as pd

from factor_config import WINSOR_MAD_MULTIPLIER


def align_direction(values: pd.Series, direction: int) -> pd.Series:
    """Flip sign when ``direction == -1`` so that larger is always better."""
    raise NotImplementedError("Phase 3: exposure")


def winsorize_mad(values: pd.Series, k: float = WINSOR_MAD_MULTIPLIER) -> pd.Series:
    """Clip to median +/- k * MAD."""
    raise NotImplementedError("Phase 3: exposure")


def zscore(values: pd.Series) -> pd.Series:
    """Standardize to mean 0 / std 1 within the cross-section."""
    raise NotImplementedError("Phase 3: exposure")


def percentile_rank(values: pd.Series) -> pd.Series:
    """Map to [0, 1] cross-sectional percentile rank."""
    raise NotImplementedError("Phase 3: exposure")
