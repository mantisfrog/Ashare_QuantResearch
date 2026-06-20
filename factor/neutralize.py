"""Size / industry neutralization via cross-sectional regression residuals.

For each rebalance date the standardized exposure is regressed on
``ln(market_cap)`` plus industry dummies (``tdx_sector_code``); the residual is
the neutralized exposure. Implemented in Phase 3.
"""
from __future__ import annotations

import pandas as pd


def neutralize(
    exposure: pd.Series,
    log_market_cap: pd.Series,
    industry: pd.Series,
) -> pd.Series:
    """Return residual of exposure ~ ln(market_cap) + C(industry). (Phase 3)"""
    raise NotImplementedError("Phase 3: exposure")
