"""Cross-sectional factor preprocessing: direction, winsorize, standardize.

Each function operates on one factor's values for a single rebalance date
(a pandas Series indexed by stock_code), assumed already free of NaN.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from factor_config import WINSOR_MAD_MULTIPLIER

# Scale factor making MAD a consistent estimator of std under normality.
_MAD_TO_STD = 1.4826


def align_direction(values: pd.Series, direction: int) -> pd.Series:
    """Flip sign when ``direction == -1`` so that larger is always better."""
    return values if int(direction) == 1 else -values


def winsorize_mad(values: pd.Series, k: float = WINSOR_MAD_MULTIPLIER) -> pd.Series:
    """Clip to median +/- k * (1.4826 * MAD). No-op when MAD is 0/undefined."""
    median = values.median()
    mad = (values - median).abs().median()
    if not np.isfinite(mad) or mad == 0:
        return values.copy()
    scale = _MAD_TO_STD * mad
    return values.clip(lower=median - k * scale, upper=median + k * scale)


def zscore(values: pd.Series) -> pd.Series:
    """Standardize to mean 0 / std 1 within the cross-section."""
    std = values.std(ddof=0)
    if not np.isfinite(std) or std == 0:
        return pd.Series(0.0, index=values.index)
    return (values - values.mean()) / std


def percentile_rank(values: pd.Series) -> pd.Series:
    """Map to (0, 1] cross-sectional percentile rank."""
    return values.rank(pct=True)

