from __future__ import annotations

import argparse
import csv
import os
import re
import sys
from pathlib import Path
from typing import Iterable

import psycopg2
from psycopg2 import sql

from etl_logging import append_summary
from paths import DATA_DIR, ENV_FILE


TABLES = [
    "dim_tdx_industry",
    "dim_stock",
    "dim_date",
    "dim_financial_metric",
    "fact_dividend",
    "fact_daily",
    "fact_adjustment_factor_period",
    "fact_financial_report",
    "fact_financial_value",
    "bridge_trade_day_financial_report",
]

CSV_LOADS = [
    (
        "dim_tdx_industry",
        "dim_tdx_industry.csv",
        ["tdx_sector_code", "tdx_sector_name"],
    ),
    (
        "dim_stock",
        "dim_stock.csv",
        ["stock_code", "stock_name", "tdx_sector_code"],
    ),
    (
        "dim_date",
        "dim_date.csv",
        [
            "date_id",
            "date",
            "year_num",
            "quarter_num",
            "month_num",
            "day_week",
            "is_trade_day",
            "trade_day_index",
        ],
    ),
    (
        "dim_financial_metric",
        "dim_financial_metric.csv",
        ["metric_code", "metric_name"],
    ),
    (
        "fact_dividend",
        "fact_dividend.csv",
        [
            "stock_code",
            "date_id",
            "action_type",
            "bonus",
            "allot_price",
            "share_bonus",
            "allotment",
        ],
    ),
    (
        "fact_daily",
        "fact_daily.csv",
        [
            "date_id",
            "stock_code",
            "open",
            "high",
            "low",
            "close",
            "vol",
            "amount",
            "total_shares",
            "float_shares",
            "market_cap",
            "float_market_cap",
        ],
    ),
    (
        "fact_adjustment_factor_period",
        "fact_adjustment_factor_period.csv",
        [
            "stock_code",
            "valid_from_date_id",
            "valid_to_date_id",
            "adjust_factor",
        ],
    ),
    (
        "fact_financial_report",
        "fact_financial_report.csv",
        ["report_id", "stock_code", "report_period", "announce_date_id"],
    ),
    (
        "fact_financial_value",
        "fact_financial_value.csv",
        ["report_id", "metric_code", "metric_value"],
    ),
    (
        "bridge_trade_day_financial_report",
        "bridge_trade_day_financial_report.csv",
        ["date_id", "stock_code", "report_id"],
    ),
]

DATE_RANGE_PARTITIONED_TABLES = (
    "fact_daily",
    "bridge_trade_day_financial_report",
)
FINANCIAL_VALUE_HASH_PARTITIONS = 16

LOAD_SESSION_SQL = """
SET synchronous_commit = off;
SET maintenance_work_mem = '1GB';
SET work_mem = '128MB';
"""

CREATE_TABLES_SQL = """
CREATE TABLE IF NOT EXISTS dim_tdx_industry (
    tdx_sector_code VARCHAR(6) NOT NULL,
    tdx_sector_name VARCHAR(50) NOT NULL
);

CREATE TABLE IF NOT EXISTS dim_stock (
    stock_code VARCHAR(9) NOT NULL,
    stock_name VARCHAR(50),
    tdx_sector_code VARCHAR(6)
);

CREATE TABLE IF NOT EXISTS dim_date (
    date_id       INTEGER NOT NULL,
    date          DATE NOT NULL,
    year_num      SMALLINT NOT NULL,
    quarter_num   SMALLINT NOT NULL,
    month_num     SMALLINT NOT NULL,
    day_week      SMALLINT NOT NULL,
    is_trade_day  BOOLEAN NOT NULL,
    trade_day_index INTEGER
);

CREATE TABLE IF NOT EXISTS dim_financial_metric (
    metric_code VARCHAR(10) NOT NULL,
    metric_name VARCHAR(500) NOT NULL
);

CREATE TABLE IF NOT EXISTS fact_dividend (
    stock_code   VARCHAR(9) NOT NULL,
    date_id      INTEGER NOT NULL,
    action_type  SMALLINT NOT NULL,
    bonus        NUMERIC(18,6) NOT NULL DEFAULT 0,
    allot_price  NUMERIC(18,6) NOT NULL DEFAULT 0,
    share_bonus  NUMERIC(18,6) NOT NULL DEFAULT 0,
    allotment    NUMERIC(18,6) NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS fact_daily (
    date_id     INTEGER NOT NULL,
    stock_code  VARCHAR(9) NOT NULL,
    open        NUMERIC(18,2) NOT NULL,
    high        NUMERIC(18,2) NOT NULL,
    low         NUMERIC(18,2) NOT NULL,
    close       NUMERIC(18,2) NOT NULL,
    vol         BIGINT NOT NULL,
    amount      NUMERIC(20,4) NOT NULL,
    total_shares BIGINT,
    float_shares BIGINT,
    market_cap  NUMERIC(24,4),
    float_market_cap NUMERIC(24,4)
) PARTITION BY RANGE (date_id);

CREATE TABLE IF NOT EXISTS fact_financial_report (
    report_id        BIGINT NOT NULL,
    stock_code       VARCHAR(9) NOT NULL,
    report_period    DATE NOT NULL,
    announce_date_id INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS fact_financial_value (
    report_id    BIGINT NOT NULL,
    metric_code  VARCHAR(10) NOT NULL,
    metric_value NUMERIC(28,6) NOT NULL
) PARTITION BY HASH (metric_code);

CREATE TABLE IF NOT EXISTS fact_adjustment_factor_period (
    stock_code          VARCHAR(9) NOT NULL,
    valid_from_date_id  INTEGER NOT NULL,
    valid_to_date_id    INTEGER NOT NULL,
    adjust_factor       NUMERIC(28,12) NOT NULL
);

CREATE TABLE IF NOT EXISTS bridge_trade_day_financial_report (
    date_id    INTEGER NOT NULL,
    stock_code VARCHAR(9) NOT NULL,
    report_id  BIGINT NOT NULL
) PARTITION BY RANGE (date_id);
"""

DROP_SQL = """
DROP TABLE IF EXISTS bridge_trade_day_financial_report CASCADE;
DROP TABLE IF EXISTS fact_financial_value CASCADE;
DROP TABLE IF EXISTS fact_financial_report CASCADE;
DROP TABLE IF EXISTS fact_adjustment_factor_period CASCADE;
DROP TABLE IF EXISTS fact_adjustment_factor CASCADE;
DROP TABLE IF EXISTS fact_daily CASCADE;
DROP TABLE IF EXISTS fact_dividend CASCADE;
DROP TABLE IF EXISTS dim_financial_metric CASCADE;
DROP TABLE IF EXISTS dim_date CASCADE;
DROP TABLE IF EXISTS dim_stock CASCADE;
DROP TABLE IF EXISTS dim_tdx_industry CASCADE;
"""

CONSTRAINTS_AND_INDEXES_SQL = """
ALTER TABLE dim_tdx_industry
    ADD CONSTRAINT pk_dim_tdx_industry PRIMARY KEY (tdx_sector_code),
    ADD CONSTRAINT ck_dim_tdx_industry_code
        CHECK (tdx_sector_code ~ '^[0-9]{6}$');

ALTER TABLE dim_stock
    ADD CONSTRAINT pk_dim_stock PRIMARY KEY (stock_code),
    ADD CONSTRAINT ck_dim_stock_code
        CHECK (
            stock_code ~ '^(6[0-9]{5}\\.SH|0[0-9]{5}\\.SZ|30[0-9]{4}\\.SZ)$'
        ),
    ADD CONSTRAINT ck_dim_stock_tdx_sector_code
        CHECK (
            tdx_sector_code IS NULL
            OR tdx_sector_code ~ '^[0-9]{6}$'
        ),
    ADD CONSTRAINT fk_dim_stock_tdx_industry
        FOREIGN KEY (tdx_sector_code)
        REFERENCES dim_tdx_industry (tdx_sector_code);

ALTER TABLE dim_date
    ADD CONSTRAINT pk_dim_date PRIMARY KEY (date_id),
    ADD CONSTRAINT uq_dim_date_date UNIQUE (date),
    ADD CONSTRAINT ck_dim_date_id
        CHECK (date_id = TO_CHAR(date, 'YYYYMMDD')::INTEGER),
    ADD CONSTRAINT ck_dim_date_year
        CHECK (year_num = EXTRACT(YEAR FROM date)::SMALLINT),
    ADD CONSTRAINT ck_dim_date_quarter
        CHECK (
            quarter_num BETWEEN 1 AND 4
            AND quarter_num = EXTRACT(QUARTER FROM date)::SMALLINT
        ),
    ADD CONSTRAINT ck_dim_date_month
        CHECK (
            month_num BETWEEN 1 AND 12
            AND month_num = EXTRACT(MONTH FROM date)::SMALLINT
        ),
    ADD CONSTRAINT ck_dim_date_day_week
        CHECK (
            day_week BETWEEN 1 AND 7
            AND day_week = EXTRACT(ISODOW FROM date)::SMALLINT
        ),
    ADD CONSTRAINT ck_dim_date_trade_day_index
        CHECK (
            (
                is_trade_day = TRUE
                AND trade_day_index IS NOT NULL
                AND trade_day_index > 0
            )
            OR (
                is_trade_day = FALSE
                AND trade_day_index IS NULL
            )
        );

ALTER TABLE dim_financial_metric
    ADD CONSTRAINT pk_dim_financial_metric PRIMARY KEY (metric_code),
    ADD CONSTRAINT ck_dim_financial_metric_code
        CHECK (metric_code ~ '^FN[0-9]+$');

ALTER TABLE fact_dividend
    ADD CONSTRAINT pk_fact_dividend
        PRIMARY KEY (stock_code, date_id, action_type),
    ADD CONSTRAINT fk_fact_dividend_stock
        FOREIGN KEY (stock_code)
        REFERENCES dim_stock (stock_code),
    ADD CONSTRAINT fk_fact_dividend_date
        FOREIGN KEY (date_id)
        REFERENCES dim_date (date_id),
    ADD CONSTRAINT ck_fact_dividend_action_type
        CHECK (action_type IN (1, 11, 15)),
    ADD CONSTRAINT ck_fact_dividend_values
        CHECK (
            bonus >= 0
            AND allot_price >= 0
            AND share_bonus >= 0
            AND allotment >= 0
        );

ALTER TABLE fact_daily
    ADD CONSTRAINT pk_fact_daily
        PRIMARY KEY (stock_code, date_id),
    ADD CONSTRAINT fk_fact_daily_stock
        FOREIGN KEY (stock_code)
        REFERENCES dim_stock (stock_code),
    ADD CONSTRAINT fk_fact_daily_date
        FOREIGN KEY (date_id)
        REFERENCES dim_date (date_id),
    ADD CONSTRAINT ck_fact_daily_prices
        CHECK (
            open > 0
            AND high > 0
            AND low > 0
            AND close > 0
            AND high >= GREATEST(open, low, close)
            AND low <= LEAST(open, high, close)
        ),
    ADD CONSTRAINT ck_fact_daily_volume
        CHECK (vol >= 0),
    ADD CONSTRAINT ck_fact_daily_amount
        CHECK (amount >= 0),
    ADD CONSTRAINT ck_fact_daily_capital
        CHECK (
            (
                total_shares IS NULL
                AND float_shares IS NULL
                AND market_cap IS NULL
                AND float_market_cap IS NULL
            )
            OR (
                total_shares > 0
                AND float_shares > 0
                AND float_shares <= total_shares
                AND market_cap > 0
                AND float_market_cap > 0
                AND float_market_cap <= market_cap
            )
        );

ALTER TABLE fact_financial_report
    ADD CONSTRAINT pk_fact_financial_report PRIMARY KEY (report_id),
    ADD CONSTRAINT ck_fact_financial_report_id
        CHECK (report_id > 0),
    ADD CONSTRAINT uq_fact_financial_report_business
        UNIQUE (stock_code, report_period),
    ADD CONSTRAINT fk_fact_financial_report_stock
        FOREIGN KEY (stock_code)
        REFERENCES dim_stock (stock_code),
    ADD CONSTRAINT fk_fact_financial_report_announce_date
        FOREIGN KEY (announce_date_id)
        REFERENCES dim_date (date_id),
    ADD CONSTRAINT ck_fact_financial_report_period
        CHECK (
            EXTRACT(MONTH FROM report_period) IN (3, 6, 9, 12)
            AND report_period = (
                DATE_TRUNC('month', report_period)
                + INTERVAL '1 month - 1 day'
            )::DATE
        ),
    ADD CONSTRAINT ck_fact_financial_report_announce_date
        CHECK (
            announce_date_id >=
            TO_CHAR(report_period, 'YYYYMMDD')::INTEGER
        );

ALTER TABLE fact_financial_value
    ADD CONSTRAINT pk_fact_financial_value
        PRIMARY KEY (report_id, metric_code),
    ADD CONSTRAINT fk_fact_financial_value_report
        FOREIGN KEY (report_id)
        REFERENCES fact_financial_report (report_id)
        ON DELETE CASCADE,
    ADD CONSTRAINT fk_fact_financial_value_metric
        FOREIGN KEY (metric_code)
        REFERENCES dim_financial_metric (metric_code);

ALTER TABLE fact_adjustment_factor_period
    ADD CONSTRAINT pk_fact_adjustment_factor_period
        PRIMARY KEY (stock_code, valid_from_date_id),
    ADD CONSTRAINT fk_adjustment_factor_period_from_daily
        FOREIGN KEY (stock_code, valid_from_date_id)
        REFERENCES fact_daily (stock_code, date_id)
        ON DELETE CASCADE,
    ADD CONSTRAINT fk_adjustment_factor_period_to_daily
        FOREIGN KEY (stock_code, valid_to_date_id)
        REFERENCES fact_daily (stock_code, date_id)
        ON DELETE CASCADE,
    ADD CONSTRAINT ck_adjustment_factor_period_range
        CHECK (valid_from_date_id <= valid_to_date_id),
    ADD CONSTRAINT ck_adjustment_factor_period_positive
        CHECK (adjust_factor > 0);

ALTER TABLE bridge_trade_day_financial_report
    ADD CONSTRAINT pk_bridge_trade_day_financial_report
        PRIMARY KEY (date_id, stock_code),
    ADD CONSTRAINT fk_bridge_financial_date
        FOREIGN KEY (date_id)
        REFERENCES dim_date (date_id),
    ADD CONSTRAINT fk_bridge_financial_stock
        FOREIGN KEY (stock_code)
        REFERENCES dim_stock (stock_code),
    ADD CONSTRAINT fk_bridge_financial_report
        FOREIGN KEY (report_id)
        REFERENCES fact_financial_report (report_id)
        ON DELETE CASCADE;

CREATE INDEX idx_fact_dividend_date_stock
    ON fact_dividend (date_id, stock_code);
CREATE UNIQUE INDEX uq_dim_date_trade_day_index
    ON dim_date (trade_day_index)
    WHERE trade_day_index IS NOT NULL;
CREATE INDEX idx_fact_daily_date_stock
    ON fact_daily (date_id, stock_code);
CREATE INDEX idx_adjustment_factor_period_lookup
    ON fact_adjustment_factor_period (
        stock_code,
        valid_from_date_id,
        valid_to_date_id
    );
CREATE INDEX idx_adjustment_factor_period_date_range
    ON fact_adjustment_factor_period (
        valid_from_date_id,
        valid_to_date_id,
        stock_code
    );
CREATE INDEX idx_fact_financial_report_announce_stock
    ON fact_financial_report (announce_date_id, stock_code);
CREATE INDEX idx_fact_financial_value_metric_report
    ON fact_financial_value (metric_code, report_id);
CREATE INDEX idx_bridge_financial_report
    ON bridge_trade_day_financial_report (report_id);
"""

MIGRATE_DIM_DATE_TRADE_DAY_INDEX_SQL = """
ALTER TABLE dim_date
    ADD COLUMN IF NOT EXISTS trade_day_index INTEGER;

WITH indexed_trade_days AS (
    SELECT
        date_id,
        ROW_NUMBER() OVER (ORDER BY date_id) AS trade_day_index
    FROM dim_date
    WHERE is_trade_day = TRUE
)
UPDATE dim_date AS d
SET trade_day_index = i.trade_day_index
FROM indexed_trade_days AS i
WHERE d.date_id = i.date_id;

UPDATE dim_date
SET trade_day_index = NULL
WHERE is_trade_day = FALSE;

ALTER TABLE dim_date
    DROP CONSTRAINT IF EXISTS ck_dim_date_trade_day_index;

ALTER TABLE dim_date
    ADD CONSTRAINT ck_dim_date_trade_day_index
        CHECK (
            (
                is_trade_day = TRUE
                AND trade_day_index IS NOT NULL
                AND trade_day_index > 0
            )
            OR (
                is_trade_day = FALSE
                AND trade_day_index IS NULL
            )
        );

CREATE UNIQUE INDEX IF NOT EXISTS uq_dim_date_trade_day_index
    ON dim_date (trade_day_index)
    WHERE trade_day_index IS NOT NULL;
"""


def load_env(path: Path) -> None:
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def env_first(*names: str, default: str | None = None) -> str | None:
    for name in names:
        value = os.environ.get(name)
        if value:
            return value
    return default


def db_config(database: str | None = None) -> dict[str, object]:
    user = env_first("POSTGRES_USER", "PGUSER")
    password = env_first("POSTGRES_PASSWORD", "PGPASSWORD")
    dbname = database or env_first(
        "POSTGRES_DB",
        "POSTGRES_DATABASE",
        "PGDATABASE",
        default=user,
    )
    missing = [
        name
        for name, value in [
            ("POSTGRES_USER", user),
            ("POSTGRES_PASSWORD", password),
            ("POSTGRES_DB/PGDATABASE", dbname),
        ]
        if not value
    ]
    if missing:
        raise SystemExit(f"Missing required database settings: {', '.join(missing)}")
    return {
        "host": env_first("POSTGRES_HOST", "PGHOST", default="localhost"),
        "port": int(env_first("POSTGRES_PORT", "PGPORT", default="5432")),
        "dbname": dbname,
        "user": user,
        "password": password,
    }


def connect(database: str | None = None):
    return psycopg2.connect(**db_config(database))


def ensure_database(target_db: str) -> None:
    maintenance_db = env_first(
        "POSTGRES_MAINTENANCE_DB",
        "PGMAINTENANCEDB",
        default="postgres",
    )
    cfg = db_config(maintenance_db)
    conn = psycopg2.connect(**cfg)
    conn.autocommit = True
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (target_db,))
            if cur.fetchone():
                print(f"database exists: {target_db}", flush=True)
                return
            cur.execute(
                sql.SQL("CREATE DATABASE {}").format(sql.Identifier(target_db))
            )
            print(f"created database: {target_db}", flush=True)
    finally:
        conn.close()


def execute_statements(cur, script: str) -> None:
    for statement in iter_sql_statements(script):
        cur.execute(statement)


def iter_sql_statements(script: str) -> Iterable[str]:
    statement = []
    for line in script.splitlines():
        statement.append(line)
        if line.rstrip().endswith(";"):
            text = "\n".join(statement).strip()
            if text:
                yield text
            statement = []
    tail = "\n".join(statement).strip()
    if tail:
        yield tail


def table_exists(cur, table: str) -> bool:
    cur.execute(
        """
        SELECT EXISTS (
            SELECT 1
            FROM information_schema.tables
            WHERE table_schema = 'public'
              AND table_name = %s
        )
        """,
        (table,),
    )
    return bool(cur.fetchone()[0])


def table_row_count(cur, table: str) -> int:
    cur.execute(sql.SQL("SELECT COUNT(*) FROM {}").format(sql.Identifier(table)))
    return int(cur.fetchone()[0])


def refuse_non_empty_tables(cur) -> None:
    non_empty = []
    for table in TABLES:
        if table_exists(cur, table):
            count = table_row_count(cur, table)
            if count:
                non_empty.append((table, count))
    if non_empty:
        lines = ", ".join(f"{table}={count}" for table, count in non_empty)
        raise SystemExit(
            "Refusing to load into non-empty tables. "
            f"Use --reset to drop and rebuild. Existing rows: {lines}"
        )


def validate_csv_headers(loads: list[tuple[str, str, list[str]]]) -> None:
    errors: list[str] = []
    for _table, csv_file, expected_columns in loads:
        path = DATA_DIR / csv_file
        if not path.exists():
            errors.append(f"{csv_file}: file does not exist")
            continue
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            actual_columns = next(csv.reader(handle), [])
        if actual_columns != expected_columns:
            errors.append(
                f"{csv_file}: header mismatch; "
                f"actual={actual_columns}; expected={expected_columns}"
            )

    if errors:
        detail = "\n".join(f"- {error}" for error in errors)
        raise SystemExit(
            "CSV preflight failed; database was not modified.\n"
            f"{detail}\n"
            "Regenerate the listed CSV files before loading PostgreSQL."
        )


def dim_date_year_bounds() -> tuple[int, int]:
    path = DATA_DIR / "dim_date.csv"
    min_year: int | None = None
    max_year: int | None = None
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            date_id_text = row.get("date_id", "").strip()
            if not date_id_text:
                continue
            year = int(date_id_text) // 10000
            min_year = year if min_year is None else min(min_year, year)
            max_year = year if max_year is None else max(max_year, year)
    if min_year is None or max_year is None:
        raise SystemExit(f"{path.name} has no date_id rows; cannot build partitions.")
    return min_year, max_year


def build_partition_sql(min_year: int, max_year: int) -> str:
    statements: list[str] = []
    for table in DATE_RANGE_PARTITIONED_TABLES:
        for year in range(min_year, max_year + 1):
            statements.append(
                f"CREATE TABLE IF NOT EXISTS {table}_y{year} "
                f"PARTITION OF {table} "
                f"FOR VALUES FROM ({year}0101) TO ({year + 1}0101);"
            )
        statements.append(
            f"CREATE TABLE IF NOT EXISTS {table}_default "
            f"PARTITION OF {table} DEFAULT;"
        )

    for remainder in range(FINANCIAL_VALUE_HASH_PARTITIONS):
        statements.append(
            f"CREATE TABLE IF NOT EXISTS fact_financial_value_h{remainder:02d} "
            "PARTITION OF fact_financial_value "
            f"FOR VALUES WITH (MODULUS {FINANCIAL_VALUE_HASH_PARTITIONS}, "
            f"REMAINDER {remainder});"
        )

    return "\n".join(statements)


def validate_database(cur) -> None:
    table_counts: list[str] = []
    for table in TABLES:
        actual = table_row_count(cur, table)
        print(f"{table}: {actual}", flush=True)
        table_counts.append(f"{table}={actual}")

    checks = [
        (
            "fact_daily rows must be trade days",
            """
            SELECT COUNT(*)
            FROM fact_daily AS f
            JOIN dim_date AS d USING (date_id)
            WHERE d.is_trade_day = FALSE
            """,
        ),
        (
            "bridge rows must be trade days",
            """
            SELECT COUNT(*)
            FROM bridge_trade_day_financial_report AS b
            JOIN dim_date AS d USING (date_id)
            WHERE d.is_trade_day = FALSE
            """,
        ),
        (
            "bridge report must be visible on bridge date",
            """
            SELECT COUNT(*)
            FROM bridge_trade_day_financial_report AS b
            JOIN fact_financial_report AS r USING (report_id)
            WHERE r.announce_date_id > b.date_id
            """,
        ),
        (
            "adjustment factor periods must cover daily bars",
            """
            SELECT COUNT(*)
            FROM fact_daily AS d
            WHERE NOT EXISTS (
                SELECT 1
                FROM fact_adjustment_factor_period AS a
                WHERE a.stock_code = d.stock_code
                  AND d.date_id BETWEEN
                      a.valid_from_date_id AND a.valid_to_date_id
            )
            """,
        ),
        (
            "adjustment factor periods must not overlap",
            """
            SELECT COUNT(*)
            FROM (
                SELECT
                    stock_code,
                    valid_from_date_id,
                    LAG(valid_to_date_id) OVER (
                        PARTITION BY stock_code
                        ORDER BY valid_from_date_id, valid_to_date_id
                    ) AS previous_valid_to_date_id
                FROM fact_adjustment_factor_period
            ) AS ranges
            WHERE previous_valid_to_date_id IS NOT NULL
              AND valid_from_date_id <= previous_valid_to_date_id
            """,
        ),
        (
            "adjustment factor periods must be positive",
            """
            SELECT COUNT(*)
            FROM fact_adjustment_factor_period
            WHERE adjust_factor <= 0
            """,
        ),
        (
            "market caps must match shares and close",
            """
            SELECT COUNT(*)
            FROM fact_daily
            WHERE total_shares IS NOT NULL
              AND (
                  ABS(market_cap - close * total_shares / 10000.0) > 0.01
                  OR ABS(float_market_cap - close * float_shares / 10000.0) > 0.01
              )
            """,
        ),
        (
            "trade day index must be continuous",
            """
            SELECT CASE
                WHEN COUNT(*) = 0 THEN 1
                WHEN MIN(trade_day_index) = 1
                 AND MAX(trade_day_index) = COUNT(*)
                 AND COUNT(DISTINCT trade_day_index) = COUNT(*)
                THEN 0
                ELSE 1
            END
            FROM dim_date
            WHERE is_trade_day = TRUE
            """,
        ),
    ]
    for name, query in checks:
        cur.execute(query)
        actual = int(cur.fetchone()[0])
        print(f"{name}: {actual}", flush=True)
        if actual != 0:
            raise SystemExit(f"Validation failed: {name} returned {actual}")
    append_summary("postgres_validate", " ".join(table_counts))


def copy_csv(cur, table: str, csv_file: str, columns: list[str]) -> str:
    path = DATA_DIR / csv_file
    if not path.exists():
        raise FileNotFoundError(path)
    column_sql = sql.SQL(", ").join(sql.Identifier(column) for column in columns)
    copy_sql = sql.SQL(
        "COPY {} ({}) FROM STDIN WITH (FORMAT CSV, HEADER TRUE, NULL '')"
    ).format(sql.Identifier(table), column_sql)
    with path.open("r", encoding="utf-8", newline="") as handle:
        cur.copy_expert(copy_sql.as_string(cur), handle)
    return cur.statusmessage


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build the PostgreSQL database from local CSV files."
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Drop existing target tables before loading CSV files.",
    )
    parser.add_argument(
        "--database",
        help="Target database name. Overrides POSTGRES_DB/PGDATABASE from .env.",
    )
    parser.add_argument(
        "--create-db",
        action="store_true",
        help="Create POSTGRES_DB if it does not already exist.",
    )
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Only validate connection and target table state; do not load CSV files.",
    )
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Only run row count and integrity checks on an existing loaded database.",
    )
    parser.add_argument(
        "--analyze-only",
        action="store_true",
        help="Only run ANALYZE on the target database.",
    )
    parser.add_argument(
        "--migrate-dim-date-trade-day-index",
        action="store_true",
        help="Add and populate dim_date.trade_day_index in an existing database.",
    )
    parser.add_argument(
        "--allow-postgres-db",
        action="store_true",
        help="Allow loading into the default postgres database.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    load_env(ENV_FILE)

    target_db = args.database or str(db_config()["dbname"])
    if not re.fullmatch(r"[A-Za-z0-9_][A-Za-z0-9_\-]*", target_db):
        raise SystemExit(f"Unsafe database name: {target_db!r}")
    if target_db == "postgres" and not args.allow_postgres_db:
        raise SystemExit(
            "Target database resolved to 'postgres'. Set POSTGRES_DB in .env "
            "or pass --allow-postgres-db if this is intentional."
        )
    is_load_mode = not (
        args.check_only
        or args.validate_only
        or args.analyze_only
        or args.migrate_dim_date_trade_day_index
    )
    partition_sql = ""
    if is_load_mode:
        validate_csv_headers(CSV_LOADS)
        partition_sql = build_partition_sql(*dim_date_year_bounds())
    if args.create_db:
        ensure_database(target_db)

    print(
        "connecting to PostgreSQL "
        f"host={db_config()['host']} port={db_config()['port']} dbname={target_db}",
        flush=True,
    )
    with connect(target_db) as conn:
        with conn.cursor() as cur:
            if args.check_only:
                refuse_non_empty_tables(cur)
                print("connection ok; target tables are absent or empty", flush=True)
                return 0
            if args.validate_only:
                validate_database(cur)
                print("validation complete", flush=True)
                return 0
            if args.analyze_only:
                print("running ANALYZE", flush=True)
                cur.execute("ANALYZE;")
                conn.commit()
                print("analyze complete", flush=True)
                return 0
            if args.migrate_dim_date_trade_day_index:
                print("migrating dim_date.trade_day_index", flush=True)
                execute_statements(cur, MIGRATE_DIM_DATE_TRADE_DAY_INDEX_SQL)
                conn.commit()
                print("migration complete", flush=True)
                return 0

            execute_statements(cur, LOAD_SESSION_SQL)

            if args.reset:
                print("dropping existing tables", flush=True)
                execute_statements(cur, DROP_SQL)
                conn.commit()
            else:
                refuse_non_empty_tables(cur)

            print("creating tables", flush=True)
            execute_statements(cur, CREATE_TABLES_SQL)
            conn.commit()

            print("creating table partitions", flush=True)
            execute_statements(cur, partition_sql)
            conn.commit()

            for position, (table, csv_file, columns) in enumerate(
                CSV_LOADS,
                start=1,
            ):
                print(
                    f"[db {position}/{len(CSV_LOADS)}] "
                    f"copying {csv_file} -> {table}",
                    flush=True,
                )
                status = copy_csv(cur, table, csv_file, columns)
                conn.commit()
                print(status, flush=True)

            print("adding constraints and indexes", flush=True)
            execute_statements(cur, CONSTRAINTS_AND_INDEXES_SQL)
            conn.commit()

            print("running ANALYZE", flush=True)
            cur.execute("ANALYZE;")
            conn.commit()

    print("database build complete", flush=True)
    append_summary("postgres_build", "complete")
    return 0


if __name__ == "__main__":
    sys.exit(main())
