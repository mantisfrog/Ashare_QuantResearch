"""Locked pipeline constants for the monthly factor library.

Factor *definitions* (codes, formulas, direction) live in ``factor_catalog.csv``.
This module only holds the build-level parameters that were decided up front, so
the build scripts avoid scattering magic numbers. Decisions locked 2026-06.
"""
from __future__ import annotations

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
MOMENTUM_SKIP_TRADE_DAYS = 21
REVERSAL_TRADE_DAYS = 21
VOLATILITY_TRADE_DAYS = 252
TURNOVER_TRADE_DAYS = 21

# Growth acceleration: standardize the latest single-quarter net-profit YoY change
# against its own recent history. alpha = single-quarter net profit YoY change;
# factor = (alpha_t - mean of past N alpha) / (std of past N alpha).
GROWTH_ACCEL_LOOKBACK_QUARTERS = 8   # the "past 8 periods" baseline window
GROWTH_ACCEL_YOY_QUARTERS = 4        # 4 quarters back = the year-ago quarter
GROWTH_ACCEL_HISTORY_YEARS = 5       # trailing years of reports to pull (PIT)

# ROIC (TTM): EBIT (FN207) is a cumulative YTD flow, so TTM = YTD + last FY - year-ago
# YTD (annual period: the FY value). Invested capital = equity + interest-bearing debt,
# averaged with the year-ago balance. NOPAT ~= 0.80 * EBIT (no reliable tax field).
ROIC_EBIT_CODE = "FN207"           # 息税前利润 EBIT (元, cumulative YTD)
ROIC_EQUITY_CODE = "FN72"          # 所有者权益合计 (元)
ROIC_DEBT_CODES_YUAN = ("FN41", "FN52", "FN55", "FN56")  # 短借/一年内到期/长借/应付债券 (元)
ROIC_DEBT_CODES_WAN = ("FN439",)   # 租赁负债 (万元 -> *1e4)
ROIC_TAX_RETENTION = 0.80
ROIC_HISTORY_YEARS = 3

# Composite styles (must match the ``style`` column in factor_catalog.csv).
STYLES = ("value", "quality", "growth", "momentum", "risk")

# Industry-name keywords (dim_tdx_industry.tdx_sector_name) used to NULL out
# margin / accruals-type factors for financials before neutralization.
# TODO(Phase 3): verify these against the actual dim_tdx_industry names.
FINANCIAL_SECTOR_KEYWORDS = ("银行", "证券", "保险", "多元金融", "信托")
