"""Factor diagnostics: forward returns, Spearman rank IC, and factor correlation.

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


def mean_rank_corr_matrix(
    exposure_cross: dict[str, dict[int, pd.Series]],
    factor_order: list[str],
    date_ids: list[int],
    min_names: int = 30,
) -> pd.DataFrame:
    """Average monthly cross-sectional Spearman correlation across factors.

    ``exposure_cross`` maps factor_code -> date_id -> stock-indexed exposure.
    The result is a wide factor x factor matrix, ordered by ``factor_order``.
    """
    factors = [code for code in factor_order if code in exposure_cross]
    if not factors:
        return pd.DataFrame()

    matrices: list[pd.DataFrame] = []
    for date_id in date_ids:
        columns = {
            code: exposure_cross[code][date_id]
            for code in factors
            if date_id in exposure_cross[code]
        }
        if len(columns) < 2:
            continue
        frame = pd.DataFrame(columns).reindex(columns=factors)
        corr = frame.corr(method="spearman", min_periods=min_names)
        matrices.append(corr.reindex(index=factors, columns=factors))

    if matrices:
        mean_corr = pd.concat(matrices, keys=range(len(matrices))).groupby(level=1).mean()
        mean_corr = mean_corr.reindex(index=factors, columns=factors)
    else:
        mean_corr = pd.DataFrame(index=factors, columns=factors, dtype="float64")

    for code in factors:
        mean_corr.loc[code, code] = 1.0
    return mean_corr

