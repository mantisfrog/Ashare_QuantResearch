"""Locked pipeline constants for the monthly factor library.

Factor *definitions* (codes, formulas, direction) live in ``factor_catalog.csv``.
This module only holds the build-level parameters that were decided up front, so
the build scripts avoid scattering magic numbers. Decisions locked 2026-06.
"""
from __future__ import annotations

from collections.abc import Mapping

# calc_version stamped on every output row (raw / exposure / composite / etc.).
CALC_VERSION = "v1"

# History start: the first rebalance month is 2015-01.
START_YEAR = 2015
START_MONTH = "201501"
START_DATE_ID = 20150101

# Universe screen: a stock needs at least this many trading days since listing.
LISTED_MIN_TRADING_DAYS = 120

# Liquidity screen: drop the bottom fraction by trailing ~6-month average amount.
LIQUIDITY_DROP_FRACTION = 0.20
LIQUIDITY_LOOKBACK_TRADE_DAYS = 120

# Winsorization: clip each cross-section at median +/- N * MAD.
WINSOR_MAD_MULTIPLIER = 3.0

# Forward-return horizons for diagnostics, expressed in rebalance steps (months).
FORWARD_HORIZONS_MONTHS = (1, 3, 6)

# Price-factor lookback windows, in trading days.
MOMENTUM_LONG_TRADE_DAYS = 252
MOMENTUM_HALF_TRADE_DAYS = 126
MOMENTUM_SKIP_TRADE_DAYS = 21
REVERSAL_TRADE_DAYS = 21
REVERSAL_LONG_TRADE_DAYS = 756
REVERSAL_LONG_SKIP_TRADE_DAYS = 126
VOLATILITY_TRADE_DAYS = 252
TURNOVER_TRADE_DAYS = 21

# Growth acceleration: standardize the latest single-quarter net-profit YoY change
# against its own recent history. alpha = single-quarter net profit YoY change;
# factor = (alpha_t - mean of past N alpha) / (std of past N alpha).
GROWTH_ACCEL_LOOKBACK_QUARTERS = 8   # the "past 8 periods" baseline window
GROWTH_ACCEL_YOY_QUARTERS = 4        # 4 quarters back = the year-ago quarter
GROWTH_ACCEL_HISTORY_YEARS = 5       # trailing years of reports to pull (PIT)

# Quality stability: average and dispersion of the latest consecutive ROE_TTM observations.
QUALITY_ROE_PERIODS = (12,)
QUALITY_HISTORY_YEARS = 5

# Composite styles (must match the ``style`` column in factor_catalog.csv).
STYLES = ("value", "quality", "growth", "momentum", "reversal", "risk")

# Composite aggregation. When ``COMPOSITE_EQUAL_WEIGHT`` is True, every factor
# within a style receives equal weight and the mapping below is only documented
# for review. Set it to False to use the configured weights within each style;
# weights are re-normalized across the factors available for each stock/date.
COMPOSITE_EQUAL_WEIGHT = False
COMPOSITE_FACTOR_WEIGHTS: dict[str, dict[str, float]] = {
    "value": {
        "ep_ttm": 1.0,
        "bp_mrq": 1.0,
        "sp_ttm": 1.0,
        "cfp_ttm": 1.0,
        "div_yield_ttm": 1.0,
    },
    "quality": {
        "roe_ttm_12q_avg": 1.0,
        "roe_stability_12q": 1.0,
        "fcfe_to_equity": 1.0,
        "accruals": 1.0,
    },
    "growth": {
        "revenue_growth_yoy": 1.0,
        "profit_growth_yoy": 1.0,
        "earnings_accel_2q_avg": 1.0,
    },
    "momentum": {
        "mom_6_1": 1.0,
    },
    "reversal": {
        "reversal_1m": 1.0,
        "reversal_3y_6m": 1.0,
    },
    "risk": {
        "volatility_252d": 1.0,
        "turnover_21d": 1.0,
    },
}

# Industry-name keywords (dim_tdx_industry.tdx_sector_name) used to NULL out
# financial-sensitive factors before neutralization.
# TODO(Phase 3): verify these against the actual dim_tdx_industry names.
FINANCIAL_SECTOR_KEYWORDS = ("银行", "证券", "保险", "多元金融", "信托")


def factor_config_snapshot_lines() -> list[str]:
    """Return a concise, readable config snapshot for the factor run log."""
    lines = [
        "factor_config:",
        f"  CALC_VERSION: {CALC_VERSION}",
        f"  START_MONTH: {START_MONTH}",
        f"  START_DATE_ID: {START_DATE_ID}",
        "  universe:",
        f"    LISTED_MIN_TRADING_DAYS: {LISTED_MIN_TRADING_DAYS}",
        f"    LIQUIDITY_DROP_FRACTION: {LIQUIDITY_DROP_FRACTION}",
        f"    LIQUIDITY_LOOKBACK_TRADE_DAYS: {LIQUIDITY_LOOKBACK_TRADE_DAYS}",
        "  preprocessing:",
        f"    WINSOR_MAD_MULTIPLIER: {WINSOR_MAD_MULTIPLIER}",
        "  diagnostics:",
        f"    FORWARD_HORIZONS_MONTHS: {FORWARD_HORIZONS_MONTHS}",
        "  price_windows:",
        f"    MOMENTUM_LONG_TRADE_DAYS: {MOMENTUM_LONG_TRADE_DAYS}",
        f"    MOMENTUM_HALF_TRADE_DAYS: {MOMENTUM_HALF_TRADE_DAYS}",
        f"    MOMENTUM_SKIP_TRADE_DAYS: {MOMENTUM_SKIP_TRADE_DAYS}",
        f"    REVERSAL_TRADE_DAYS: {REVERSAL_TRADE_DAYS}",
        f"    REVERSAL_LONG_TRADE_DAYS: {REVERSAL_LONG_TRADE_DAYS}",
        f"    REVERSAL_LONG_SKIP_TRADE_DAYS: {REVERSAL_LONG_SKIP_TRADE_DAYS}",
        f"    VOLATILITY_TRADE_DAYS: {VOLATILITY_TRADE_DAYS}",
        f"    TURNOVER_TRADE_DAYS: {TURNOVER_TRADE_DAYS}",
        "  growth_acceleration:",
        f"    GROWTH_ACCEL_LOOKBACK_QUARTERS: {GROWTH_ACCEL_LOOKBACK_QUARTERS}",
        f"    GROWTH_ACCEL_YOY_QUARTERS: {GROWTH_ACCEL_YOY_QUARTERS}",
        f"    GROWTH_ACCEL_HISTORY_YEARS: {GROWTH_ACCEL_HISTORY_YEARS}",
        "  quality_history:",
        f"    QUALITY_ROE_PERIODS: {QUALITY_ROE_PERIODS}",
        f"    QUALITY_HISTORY_YEARS: {QUALITY_HISTORY_YEARS}",
        "  composite:",
        f"    STYLES: {STYLES}",
        f"    COMPOSITE_EQUAL_WEIGHT: {COMPOSITE_EQUAL_WEIGHT}",
        "    COMPOSITE_FACTOR_WEIGHTS:",
    ]
    lines.extend(_format_nested_weights(COMPOSITE_FACTOR_WEIGHTS, indent=6))
    lines.extend([
        "  financial_sector_keywords:",
        f"    FINANCIAL_SECTOR_KEYWORDS: {FINANCIAL_SECTOR_KEYWORDS}",
    ])
    return lines


def _format_nested_weights(weights: Mapping[str, Mapping[str, float]], indent: int) -> list[str]:
    prefix = " " * indent
    child_prefix = " " * (indent + 2)
    lines: list[str] = []
    for style in STYLES:
        lines.append(f"{prefix}{style}:")
        for factor_code, weight in weights.get(style, {}).items():
            lines.append(f"{child_prefix}{factor_code}: {weight}")
    extra_styles = sorted(set(weights) - set(STYLES))
    for style in extra_styles:
        lines.append(f"{prefix}{style}:")
        for factor_code, weight in weights[style].items():
            lines.append(f"{child_prefix}{factor_code}: {weight}")
    return lines
