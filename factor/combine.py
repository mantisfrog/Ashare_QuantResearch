"""Composite style scores from neutralized factor exposures.

Combines per-factor exposures into one score per style and an equal-weighted
alpha total.

Method (per rebalance cross-section):
  1. within-style aggregation: equal-weighted by default, or weighted by
     factor_config.COMPOSITE_FACTOR_WEIGHTS when enabled;
  2. re-standardize each style score (cross-sectional z-score) so styles with
     different factor counts / correlations are comparable;
  3. total_score = equal weight across configured alpha styles that have a
     value for the stock.
Exposures already have ``direction`` applied, so larger is better.
"""
from __future__ import annotations

import pandas as pd

import preprocess
from factor_config import (
    COMPOSITE_EQUAL_WEIGHT,
    COMPOSITE_FACTOR_WEIGHTS,
    STYLES,
    TOTAL_SCORE_STYLES,
)

STYLE_SCORE_COLUMNS = [f"{style}_score" for style in STYLES]
COMPOSITE_COLUMNS = ["date_id", "stock_code", *STYLE_SCORE_COLUMNS, "total_score"]


def composite_style_scores(
    exposure_long: pd.DataFrame,
    catalog: pd.DataFrame,
) -> pd.DataFrame:
    """Aggregate exposures into style scores + alpha ``total_score``.

    ``exposure_long`` has columns (date_id, stock_code, factor_code,
    neutralized_value); ``catalog`` maps factor_code -> style. Returns a frame
    keyed by (date_id, stock_code) with one ``<style>_score`` column per
    :data:`factor_config.STYLES` plus ``total_score`` over
    :data:`factor_config.TOTAL_SCORE_STYLES`.
    """
    if exposure_long is None or exposure_long.empty:
        return pd.DataFrame(columns=COMPOSITE_COLUMNS)

    style_by_code = (
        catalog["style"]
        if catalog.index.name == "factor_code"
        else catalog.set_index("factor_code")["style"]
    )
    work = exposure_long.loc[
        :, ["date_id", "stock_code", "factor_code", "neutralized_value"]
    ].copy()
    work["style"] = work["factor_code"].map(style_by_code)
    work = work[work["style"].notna() & work["neutralized_value"].notna()]
    if work.empty:
        return pd.DataFrame(columns=COMPOSITE_COLUMNS)

    # 1) within-style factor aggregation -> one raw score per (date, stock, style).
    per_style = _aggregate_within_style(work)
    # 2) re-standardize each style cross-section so styles are comparable.
    per_style["style_score"] = (
        per_style.groupby(["date_id", "style"], observed=True)["style_raw"]
        .transform(preprocess.zscore)
    )

    wide = per_style.pivot_table(
        index=["date_id", "stock_code"], columns="style", values="style_score"
    )
    wide = wide.reindex(columns=list(STYLES))
    wide.columns = STYLE_SCORE_COLUMNS
    # 3) equal weight across alpha styles present for each stock.
    total_score_columns = [f"{style}_score" for style in TOTAL_SCORE_STYLES]
    wide["total_score"] = wide[total_score_columns].mean(axis=1, skipna=True)
    return wide.reset_index().loc[:, COMPOSITE_COLUMNS]


def _aggregate_within_style(work: pd.DataFrame) -> pd.DataFrame:
    group_cols = ["date_id", "stock_code", "style"]
    if COMPOSITE_EQUAL_WEIGHT:
        return (
            work.groupby(group_cols, observed=True)["neutralized_value"]
            .mean()
            .rename("style_raw")
            .reset_index()
        )

    weighted = work.merge(
        _configured_weights_frame(),
        on=["style", "factor_code"],
        how="left",
    )
    missing = weighted["factor_weight"].isna()
    if missing.any():
        first = weighted.loc[missing, ["style", "factor_code"]].drop_duplicates().iloc[0]
        raise ValueError(
            "missing composite weight for "
            f"style={first['style']!r} factor={first['factor_code']!r}"
        )
    weighted["weighted_value"] = weighted["neutralized_value"] * weighted["factor_weight"]
    grouped = weighted.groupby(group_cols, observed=True)
    numerator = grouped["weighted_value"].sum()
    denominator = grouped["factor_weight"].sum()
    per_style = (numerator / denominator).rename("style_raw").reset_index()
    return per_style


def _configured_weights_frame() -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for style, weights in COMPOSITE_FACTOR_WEIGHTS.items():
        for factor_code, weight in weights.items():
            value = float(weight)
            if not value >= 0:
                raise ValueError(
                    f"composite weight must be non-negative for style={style!r} "
                    f"factor={factor_code!r}: {value}"
                )
            rows.append({
                "style": str(style),
                "factor_code": str(factor_code),
                "factor_weight": value,
            })
    return pd.DataFrame(rows, columns=["style", "factor_code", "factor_weight"])
