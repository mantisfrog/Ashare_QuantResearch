"""Composite style scores from neutralized factor exposures.

Combines per-factor neutralized exposures into one score per style
(value / quality / growth / momentum / reversal / risk) and an equal-weighted total.

Method (per rebalance cross-section):
  1. within-style equal weight: average the neutralized exposures of the
     factors that belong to a style (skipping missing factors);
  2. re-standardize each style score (cross-sectional z-score) so styles with
     different factor counts / correlations are comparable;
  3. total_score = equal weight across the styles that have a value for the
     stock (styles with no implemented factor are simply absent).
Neutralized exposures already have ``direction`` applied, so larger is better.
"""
from __future__ import annotations

import pandas as pd

import preprocess
from factor_config import STYLES

STYLE_SCORE_COLUMNS = [f"{style}_score" for style in STYLES]
COMPOSITE_COLUMNS = ["date_id", "stock_code", *STYLE_SCORE_COLUMNS, "total_score"]


def composite_style_scores(
    exposure_long: pd.DataFrame,
    catalog: pd.DataFrame,
) -> pd.DataFrame:
    """Aggregate neutralized exposures into style scores + ``total_score``.

    ``exposure_long`` has columns (date_id, stock_code, factor_code,
    neutralized_value); ``catalog`` maps factor_code -> style (indexed by
    factor_code or carrying it as a column). Returns a frame keyed by
    (date_id, stock_code) with one ``<style>_score`` column per
    :data:`factor_config.STYLES` plus ``total_score``.
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

    # 1) within-style equal weight -> one raw score per (date, stock, style).
    per_style = (
        work.groupby(["date_id", "stock_code", "style"], observed=True)["neutralized_value"]
        .mean()
        .rename("style_raw")
        .reset_index()
    )
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
    # 3) equal weight across the styles present for each stock.
    wide["total_score"] = wide[STYLE_SCORE_COLUMNS].mean(axis=1, skipna=True)
    return wide.reset_index().loc[:, COMPOSITE_COLUMNS]
