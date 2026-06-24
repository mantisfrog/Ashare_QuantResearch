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

import numpy as np
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


def load_financial_metrics(conn, date_id: int, metric_codes) -> pd.DataFrame:
    """Point-in-time financials at ``date_id``, pivoted wide by FN metric_code.

    Uses the latest report visible on ``date_id`` per stock (the bridge), so no
    look-ahead. Returns a frame indexed by stock_code with one column per code
    in ``metric_codes`` (missing values are NaN).
    """
    codes = list(metric_codes)
    query = """
        SELECT b.stock_code, v.metric_code, v.metric_value
        FROM bridge_trade_day_financial_report b
        JOIN fact_financial_value v ON v.report_id = b.report_id
        WHERE b.date_id = %(t)s AND v.metric_code = ANY(%(codes)s)
    """
    with conn.cursor() as cur:
        cur.execute(query, {"t": date_id, "codes": codes})
        rows = cur.fetchall()
    if not rows:
        return pd.DataFrame(columns=codes, dtype="float64")
    long = pd.DataFrame(rows, columns=["stock_code", "metric_code", "metric_value"])
    long["metric_value"] = pd.to_numeric(long["metric_value"], errors="coerce")
    wide = long.pivot_table(
        index="stock_code", columns="metric_code", values="metric_value", aggfunc="first"
    )
    return wide.reindex(columns=codes)


def load_quarterly_metrics_history(
    conn, date_id: int, metric_codes, history_years: int
) -> pd.DataFrame:
    """Point-in-time quarterly history of several FN metrics as of ``date_id``.

    Returns long rows (stock_code, report_period, metric_code, metric_value) for
    reports announced on or before ``date_id`` whose period falls within the
    trailing ``history_years`` calendar years. ``report_period`` is the period-end
    date, so callers can build single-quarter / YoY / TTM series. No look-ahead:
    filtered by ``announce_date_id <= date_id``.
    """
    codes = list(metric_codes)
    min_period = f"{date_id // 10000 - history_years}-01-01"
    query = """
        SELECT r.stock_code, r.report_period, v.metric_code, v.metric_value
        FROM fact_financial_report r
        JOIN fact_financial_value v
          ON v.report_id = r.report_id AND v.metric_code = ANY(%(codes)s)
        WHERE r.announce_date_id <= %(t)s
          AND r.report_period >= %(minp)s
    """
    with conn.cursor() as cur:
        cur.execute(query, {"codes": codes, "t": date_id, "minp": min_period})
        rows = cur.fetchall()
    frame = pd.DataFrame(
        rows, columns=["stock_code", "report_period", "metric_code", "metric_value"]
    )
    if frame.empty:
        return frame
    frame["report_period"] = pd.to_datetime(frame["report_period"])
    frame["metric_value"] = pd.to_numeric(frame["metric_value"], errors="coerce")
    return frame


def load_daily_snapshot(conn, date_id: int) -> pd.DataFrame:
    """Daily point-in-time fields on ``date_id`` indexed by stock_code."""
    with conn.cursor() as cur:
        cur.execute(
            "SELECT stock_code, close, market_cap, float_market_cap "
            "FROM fact_daily WHERE date_id = %s",
            (date_id,),
        )
        rows = cur.fetchall()
    frame = pd.DataFrame(
        rows,
        columns=["stock_code", "close", "market_cap", "float_market_cap"],
    ).set_index("stock_code")
    for column in ("close", "market_cap", "float_market_cap"):
        frame[column] = pd.to_numeric(frame[column], errors="coerce")
    return frame


def load_trailing_dividends(conn, date_id: int) -> pd.Series:
    """Trailing-12m cash dividend per share (sum of bonus/10) indexed by stock_code."""
    query = """
        SELECT stock_code, SUM(bonus) / 10.0 AS dps_ttm
        FROM fact_dividend
        WHERE action_type = 1 AND bonus > 0
          AND date_id > %(t)s - 10000 AND date_id <= %(t)s
        GROUP BY stock_code
    """
    with conn.cursor() as cur:
        cur.execute(query, {"t": date_id})
        rows = cur.fetchall()
    return pd.Series(
        {code: float(value) for code, value in rows}, name="dps_ttm", dtype="float64"
    )


def load_stock_industry(conn) -> pd.Series:
    """Return stock_code -> tdx_sector_code as a Series (for neutralization)."""
    with conn.cursor() as cur:
        cur.execute("SELECT stock_code, tdx_sector_code FROM dim_stock")
        rows = cur.fetchall()
    return pd.Series({code: sector for code, sector in rows}, name="industry")


def load_financial_sector_codes(conn, keywords) -> set[str]:
    """tdx_sector_code values whose name matches any financial keyword."""
    with conn.cursor() as cur:
        cur.execute("SELECT tdx_sector_code, tdx_sector_name FROM dim_tdx_industry")
        rows = cur.fetchall()
    return {
        code
        for code, name in rows
        if name and any(keyword in name for keyword in keywords)
    }


def load_rebalance_adjusted_close(conn, date_ids) -> pd.DataFrame:
    """Back-adjusted close (close * adjust_factor) at the given rebalance dates.

    Returns long rows (date_id, stock_code, adj_close) for diagnostics.
    """
    query = """
        SELECT f.date_id, f.stock_code, f.close * a.adjust_factor AS adj_close
        FROM fact_daily f
        JOIN fact_adjustment_factor_period a
          ON a.stock_code = f.stock_code
         AND f.date_id BETWEEN a.valid_from_date_id AND a.valid_to_date_id
        WHERE f.date_id = ANY(%s)
    """
    with conn.cursor() as cur:
        cur.execute(query, (list(date_ids),))
        rows = cur.fetchall()
    frame = pd.DataFrame(rows, columns=["date_id", "stock_code", "adj_close"])
    frame["adj_close"] = pd.to_numeric(frame["adj_close"], errors="coerce")
    return frame


def load_price_window(conn, window_start_date_id: int, t_date_id: int) -> pd.DataFrame:
    """Back-adjusted daily prices + volume over [window_start, t] for price factors.

    Long rows (date_id, stock_code, adj_close, vol, float_shares). adj_close =
    close * adjust_factor handles splits/dividends within the window.
    """
    query = """
        SELECT f.date_id, f.stock_code,
               f.close * a.adjust_factor AS adj_close,
               f.vol, f.float_shares
        FROM fact_daily f
        JOIN fact_adjustment_factor_period a
          ON a.stock_code = f.stock_code
         AND f.date_id BETWEEN a.valid_from_date_id AND a.valid_to_date_id
        WHERE f.date_id BETWEEN %(win)s AND %(t)s
    """
    with conn.cursor() as cur:
        cur.execute(query, {"win": window_start_date_id, "t": t_date_id})
        rows = cur.fetchall()
        columns = [desc[0] for desc in cur.description]
    frame = pd.DataFrame(rows, columns=columns)
    for column in ("adj_close", "vol", "float_shares"):
        frame[column] = pd.to_numeric(frame[column], errors="coerce")
    return frame
