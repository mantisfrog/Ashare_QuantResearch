"""Size / industry neutralization via cross-sectional regression residuals.

The standardized exposure is regressed on ``ln(market_cap)`` plus industry
dummies (``tdx_sector_code``); the residual is the neutralized exposure.
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def neutralize(
    exposure: pd.Series,
    log_market_cap: pd.Series,
    industry: pd.Series,
) -> pd.Series:
    """Return residual of ``exposure ~ ln(market_cap) + C(industry)``.

    Stocks missing the exposure or ``log_market_cap`` are dropped from the fit
    and get NaN residuals. The result is reindexed to ``exposure.index``.
    """
    frame = pd.DataFrame(
        {"y": exposure, "lmc": log_market_cap, "ind": industry}
    ).dropna(subset=["y", "lmc"])
    if frame.empty:
        return pd.Series(np.nan, index=exposure.index, dtype="float64")

    dummies = pd.get_dummies(
        frame["ind"].astype("object"), prefix="ind", dummy_na=False, dtype=float
    )
    design = pd.concat(
        [pd.Series(1.0, index=frame.index, name="const"), frame["lmc"].astype(float), dummies],
        axis=1,
    )
    x = design.to_numpy(dtype=float)
    y = frame["y"].to_numpy(dtype=float)
    beta, *_ = np.linalg.lstsq(x, y, rcond=None)
    residual = pd.Series(y - x @ beta, index=frame.index)
    return residual.reindex(exposure.index)

