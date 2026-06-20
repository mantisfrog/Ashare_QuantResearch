"""Factor diagnostics: forward returns and Spearman rank IC.

Forward returns use month-end-to-month-end adjusted prices over
:data:`factor_config.FORWARD_HORIZONS_MONTHS` rebalance steps. Coverage is
computed directly in the build script from the universe + exposure counts.
"""
from __future__ import annotations

import pandas as pd


def forward_returns(adj_pivot: pd.DataFrame, horizons) -> dict[int, pd.DataFrame]:
    """Forward returns over each horizon (in rebalance steps).

    ``adj_pivot`` is indexed by rebalance ``date_id`` (ascending) with one column
    per stock holding the adjusted close. Returns {horizon: date x stock returns}.
    """
    return {int(h): adj_pivot.shift(-int(h)) / adj_pivot - 1.0 for h in horizons}


def spearman_ic(signal: pd.Series, forward: pd.Series, min_names: int = 5) -> float:
    """Spearman rank correlation between a signal and forward returns.

    Computed as the Pearson correlation of ranks to avoid a scipy dependency.
    """
    pair = pd.concat([signal, forward], axis=1).dropna()
    if len(pair) < min_names:
        return float("nan")
    ranked = pair.rank()
    return float(ranked.iloc[:, 0].corr(ranked.iloc[:, 1]))

