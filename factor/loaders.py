"""Data-access helpers for the monthly factor library.

All reads go through PostgreSQL. Point-in-time fundamentals are resolved via
``bridge_trade_day_financial_report`` (announce_date_id), and prices are
back-adjusted with ``fact_adjustment_factor_period``.

``get_connection`` and ``rebalance_date_ids`` are implemented now because the
universe and orchestration layers depend on them. The heavier panel loaders are
filled in during later phases (marked below).
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

# Allow `from paths import ...` / `from build_postgres_from_csv import ...`
# both when run via update_factors.py and when a build script is run directly.
_ETL_DIR = Path(__file__).resolve().parents[1] / "etl"
if str(_ETL_DIR) not in sys.path:
    sys.path.insert(0, str(_ETL_DIR))

from build_postgres_from_csv import connect as _pg_connect, load_env
from paths import ENV_FILE


def get_connection(database: str | None = None):
    """Open a psycopg2 connection using the project's .env settings."""
    load_env(ENV_FILE)
    return _pg_connect(database)


def rebalance_date_ids(start_date_id: int, end_date_id: int) -> list[int]:
    """Month-end trading days (last ``is_trade_day`` per year/month) in range.

    Returns an ascending list of ``date_id`` values, one per calendar month that
    has at least one trading day inside ``[start_date_id, end_date_id]``.
    """
    query = """
        SELECT date_id
        FROM (
            SELECT date_id,
                   ROW_NUMBER() OVER (
                       PARTITION BY year_num, month_num
                       ORDER BY date_id DESC
                   ) AS rn
            FROM dim_date
            WHERE is_trade_day = TRUE
              AND date_id BETWEEN %s AND %s
        ) ranked
        WHERE rn = 1
        ORDER BY date_id
    """
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(query, (start_date_id, end_date_id))
        return [int(row[0]) for row in cur.fetchall()]


def load_trade_day_index_maps(conn) -> tuple[dict[int, int], dict[int, int]]:
    """Return (date_id -> trade_day_index, trade_day_index -> date_id) for trade days."""
    with conn.cursor() as cur:
        cur.execute(
            "SELECT date_id, trade_day_index FROM dim_date "
            "WHERE is_trade_day = TRUE AND trade_day_index IS NOT NULL"
        )
        rows = cur.fetchall()
    dateid_to_tdi = {int(date_id): int(tdi) for date_id, tdi in rows}
    tdi_to_dateid = {int(tdi): int(date_id) for date_id, tdi in rows}
    return dateid_to_tdi, tdi_to_dateid


def load_stock_first_listing_date(conn) -> dict[str, int]:
    """Return {stock_code: first fact_daily date_id} (uses the PK, fast)."""
    with conn.cursor() as cur:
        cur.execute("SELECT stock_code, MIN(date_id) FROM fact_daily GROUP BY stock_code")
        return {code: int(first) for code, first in cur.fetchall()}


def load_stock_names(conn) -> dict[str, str]:
    """Return {stock_code: stock_name} for the ST approximation."""
    with conn.cursor() as cur:
        cur.execute("SELECT stock_code, stock_name FROM dim_stock")
        return {code: (name or "") for code, name in cur.fetchall()}


def load_universe_window(conn, window_start_date_id: int, t_date_id: int) -> pd.DataFrame:
    """Aggregate fact_daily over [window_start, t] for the universe screen.

    One row per stock active in the window: average amount over the window, a
    flag for whether it traded on ``t``, and its close / market_cap on ``t``.
    """
    query = """
        SELECT f.stock_code,
               AVG(f.amount) AS avg_amount,
               MAX((f.date_id = %(t)s)::int) AS traded_on_t,
               MAX(CASE WHEN f.date_id = %(t)s THEN f.close END) AS close_t,
               MAX(CASE WHEN f.date_id = %(t)s THEN f.market_cap END) AS market_cap_t
        FROM fact_daily f
        WHERE f.date_id BETWEEN %(win)s AND %(t)s
        GROUP BY f.stock_code
    """
    with conn.cursor() as cur:
        cur.execute(query, {"t": t_date_id, "win": window_start_date_id})
        rows = cur.fetchall()
        columns = [desc[0] for desc in cur.description]
    return pd.DataFrame(rows, columns=columns)


def load_financial_metrics(date_id: int, metric_codes):
    """PIT financials at ``date_id`` pivoted to columns by FN metric_code. (Phase 3)

    Join chain: bridge_trade_day_financial_report -> fact_financial_report ->
    fact_financial_value, filtered to ``metric_codes`` and pivoted wide.
    """
    raise NotImplementedError("Phase 3: fundamental factors")


def load_adjusted_price_panel(start_date_id: int, end_date_id: int):
    """Back-adjusted close panel (close * adjust_factor) for price factors. (Phase 4)"""
    raise NotImplementedError("Phase 4: price factors")


def load_trailing_dividends(date_id: int):
    """Trailing-12m cash dividend per share (sum of bonus/10). (Phase 3)"""
    raise NotImplementedError("Phase 3: dividend yield")
