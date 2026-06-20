"""Create (and later load) the factor-library PostgreSQL tables.

Reuses the connection + SQL helpers from ``etl/build_postgres_from_csv.py``.
Factor tables follow the existing star-schema conventions: ``VARCHAR(9)`` stock
codes and yearly ``RANGE`` partitions on ``date_id``. Unlike the base ETL this
loader is additive (``IF NOT EXISTS``) and never drops base data.

Phase 1 creates the schema only. The CSV ``COPY`` load is added once the
raw/exposure builders produce files (later phase).

Assumes the base schema (dim_date, dim_stock) already exists.
"""
from __future__ import annotations

import sys
from pathlib import Path

_ETL_DIR = Path(__file__).resolve().parents[1] / "etl"
if str(_ETL_DIR) not in sys.path:
    sys.path.insert(0, str(_ETL_DIR))

import argparse

import pandas as pd
from psycopg2.extras import execute_values

from build_postgres_from_csv import (
    connect,
    db_config,
    dim_date_year_bounds,
    execute_statements,
    load_env,
)
from paths import (
    ENV_FILE,
    FACTOR_CATALOG_FILE,
    FACTOR_COMPOSITE_DIR,
    FACTOR_DIAGNOSTICS_DIR,
    FACTOR_EXPOSURE_DIR,
    FACTOR_RAW_DIR,
    FACTOR_UNIVERSE_DIR,
)
from factor_config import START_YEAR

DATE_RANGE_FACTOR_TABLES = (
    "fact_stock_universe",
    "fact_factor_raw",
    "fact_factor_exposure",
    "fact_factor_composite",
    "fact_factor_diagnostics",
)

CREATE_FACTOR_TABLES_SQL = """
CREATE TABLE IF NOT EXISTS dim_factor (
    factor_code    VARCHAR(64) PRIMARY KEY,
    factor_name    VARCHAR(128) NOT NULL,
    style          VARCHAR(32) NOT NULL,
    direction      SMALLINT NOT NULL,
    unit           VARCHAR(32),
    formula_text   TEXT,
    source_metrics TEXT,
    financial_na   BOOLEAN NOT NULL DEFAULT FALSE,
    version        VARCHAR(32) NOT NULL,
    is_active      BOOLEAN NOT NULL DEFAULT TRUE,
    created_at     TIMESTAMP NOT NULL DEFAULT now(),
    CONSTRAINT ck_dim_factor_direction CHECK (direction IN (-1, 1))
);

CREATE TABLE IF NOT EXISTS fact_stock_universe (
    date_id        INTEGER NOT NULL,
    stock_code     VARCHAR(9) NOT NULL,
    calc_version   VARCHAR(32) NOT NULL,
    is_listed      BOOLEAN NOT NULL,
    is_suspended   BOOLEAN NOT NULL,
    listed_days    INTEGER,
    liquidity_ok   BOOLEAN,
    has_price      BOOLEAN,
    has_market_cap BOOLEAN,
    is_st_approx   BOOLEAN,
    in_universe    BOOLEAN NOT NULL,
    reason         VARCHAR(64),
    created_at     TIMESTAMP NOT NULL DEFAULT now(),
    CONSTRAINT pk_fact_stock_universe PRIMARY KEY (date_id, stock_code, calc_version),
    CONSTRAINT fk_universe_date FOREIGN KEY (date_id) REFERENCES dim_date (date_id),
    CONSTRAINT fk_universe_stock FOREIGN KEY (stock_code) REFERENCES dim_stock (stock_code)
) PARTITION BY RANGE (date_id);

CREATE TABLE IF NOT EXISTS fact_factor_raw (
    date_id      INTEGER NOT NULL,
    stock_code   VARCHAR(9) NOT NULL,
    factor_code  VARCHAR(64) NOT NULL,
    calc_version VARCHAR(32) NOT NULL,
    factor_value NUMERIC(24, 8),
    created_at   TIMESTAMP NOT NULL DEFAULT now(),
    CONSTRAINT pk_fact_factor_raw PRIMARY KEY (date_id, stock_code, factor_code, calc_version),
    CONSTRAINT fk_factor_raw_date FOREIGN KEY (date_id) REFERENCES dim_date (date_id),
    CONSTRAINT fk_factor_raw_stock FOREIGN KEY (stock_code) REFERENCES dim_stock (stock_code),
    CONSTRAINT fk_factor_raw_factor FOREIGN KEY (factor_code) REFERENCES dim_factor (factor_code)
) PARTITION BY RANGE (date_id);

CREATE TABLE IF NOT EXISTS fact_factor_exposure (
    date_id           INTEGER NOT NULL,
    stock_code        VARCHAR(9) NOT NULL,
    factor_code       VARCHAR(64) NOT NULL,
    calc_version      VARCHAR(32) NOT NULL,
    raw_value         NUMERIC(24, 8),
    winsorized_value  NUMERIC(24, 8),
    zscore_value      NUMERIC(24, 8),
    neutralized_value NUMERIC(24, 8),
    percentile_rank   NUMERIC(10, 6),
    created_at        TIMESTAMP NOT NULL DEFAULT now(),
    CONSTRAINT pk_fact_factor_exposure PRIMARY KEY (date_id, stock_code, factor_code, calc_version),
    CONSTRAINT fk_factor_exposure_date FOREIGN KEY (date_id) REFERENCES dim_date (date_id),
    CONSTRAINT fk_factor_exposure_stock FOREIGN KEY (stock_code) REFERENCES dim_stock (stock_code),
    CONSTRAINT fk_factor_exposure_factor FOREIGN KEY (factor_code) REFERENCES dim_factor (factor_code)
) PARTITION BY RANGE (date_id);

CREATE TABLE IF NOT EXISTS fact_factor_composite (
    date_id        INTEGER NOT NULL,
    stock_code     VARCHAR(9) NOT NULL,
    calc_version   VARCHAR(32) NOT NULL,
    value_score    NUMERIC(12, 6),
    quality_score  NUMERIC(12, 6),
    growth_score   NUMERIC(12, 6),
    momentum_score NUMERIC(12, 6),
    risk_score     NUMERIC(12, 6),
    total_score    NUMERIC(12, 6),
    created_at     TIMESTAMP NOT NULL DEFAULT now(),
    CONSTRAINT pk_fact_factor_composite PRIMARY KEY (date_id, stock_code, calc_version),
    CONSTRAINT fk_factor_composite_date FOREIGN KEY (date_id) REFERENCES dim_date (date_id),
    CONSTRAINT fk_factor_composite_stock FOREIGN KEY (stock_code) REFERENCES dim_stock (stock_code)
) PARTITION BY RANGE (date_id);

CREATE TABLE IF NOT EXISTS fact_factor_diagnostics (
    date_id        INTEGER NOT NULL,
    factor_code    VARCHAR(64) NOT NULL,
    calc_version   VARCHAR(32) NOT NULL,
    universe_count INTEGER,
    valid_count    INTEGER,
    coverage       NUMERIC(10, 6),
    rank_ic_1m     NUMERIC(12, 6),
    rank_ic_3m     NUMERIC(12, 6),
    rank_ic_6m     NUMERIC(12, 6),
    created_at     TIMESTAMP NOT NULL DEFAULT now(),
    CONSTRAINT pk_fact_factor_diagnostics PRIMARY KEY (date_id, factor_code, calc_version),
    CONSTRAINT fk_factor_diag_date FOREIGN KEY (date_id) REFERENCES dim_date (date_id),
    CONSTRAINT fk_factor_diag_factor FOREIGN KEY (factor_code) REFERENCES dim_factor (factor_code)
) PARTITION BY RANGE (date_id);
"""

FACTOR_INDEXES_SQL = """
CREATE INDEX IF NOT EXISTS idx_universe_date_in
    ON fact_stock_universe (date_id, in_universe);
CREATE INDEX IF NOT EXISTS idx_factor_raw_factor_date
    ON fact_factor_raw (factor_code, date_id);
CREATE INDEX IF NOT EXISTS idx_factor_exposure_factor_date
    ON fact_factor_exposure (factor_code, date_id);
CREATE INDEX IF NOT EXISTS idx_factor_diag_factor_date
    ON fact_factor_diagnostics (factor_code, date_id);
"""


def build_factor_partition_sql(min_year: int, max_year: int) -> str:
    statements: list[str] = []
    for table in DATE_RANGE_FACTOR_TABLES:
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
    return "\n".join(statements)


def _to_bool(value: object) -> bool:
    return str(value).strip().lower() in ("true", "1", "t", "yes")


def load_dim_factor(cur) -> None:
    """Upsert factor definitions from factor_catalog.csv into dim_factor."""
    catalog = pd.read_csv(FACTOR_CATALOG_FILE)
    rows = [
        (
            row.factor_code, row.factor_name, row.style, int(row.direction),
            row.unit, row.formula_text, row.source_metrics,
            _to_bool(row.financial_na), str(row.version),
        )
        for row in catalog.itertuples(index=False)
    ]
    execute_values(
        cur,
        """
        INSERT INTO dim_factor (
            factor_code, factor_name, style, direction, unit,
            formula_text, source_metrics, financial_na, version
        ) VALUES %s
        ON CONFLICT (factor_code) DO UPDATE SET
            factor_name = EXCLUDED.factor_name,
            style = EXCLUDED.style,
            direction = EXCLUDED.direction,
            unit = EXCLUDED.unit,
            formula_text = EXCLUDED.formula_text,
            source_metrics = EXCLUDED.source_metrics,
            financial_na = EXCLUDED.financial_na,
            version = EXCLUDED.version
        """,
        rows,
    )
    print(f"dim_factor upserted: {len(rows)} rows", flush=True)


UNIVERSE_COLUMNS = [
    "date_id", "stock_code", "calc_version",
    "is_listed", "is_suspended", "listed_days",
    "liquidity_ok", "has_price", "has_market_cap",
    "is_st_approx", "in_universe", "reason",
]


def load_universe(cur) -> None:
    """Incrementally load data/factor/universe/*.csv into fact_stock_universe.

    Idempotent: rows for the date_ids present in each file are deleted before the
    file is COPYed, so re-running replaces those months without touching others.
    """
    files = sorted(FACTOR_UNIVERSE_DIR.glob("universe_*.csv"))
    if not files:
        print("no universe CSVs found; skipping universe load", flush=True)
        return
    column_sql = ", ".join(UNIVERSE_COLUMNS)
    copy_sql = (
        f"COPY fact_stock_universe ({column_sql}) "
        "FROM STDIN WITH (FORMAT CSV, HEADER TRUE, NULL '')"
    )
    for path in files:
        dates = sorted({int(value) for value in pd.read_csv(path, usecols=["date_id"])["date_id"].unique()})
        if dates:
            cur.execute("DELETE FROM fact_stock_universe WHERE date_id = ANY(%s)", (dates,))
        with path.open("r", encoding="utf-8", newline="") as handle:
            cur.copy_expert(copy_sql, handle)
        print(f"loaded {path.name} ({len(dates)} month(s))", flush=True)


RAW_COLUMNS = ["date_id", "stock_code", "factor_code", "factor_value", "calc_version"]
EXPOSURE_COLUMNS = [
    "date_id", "stock_code", "factor_code", "calc_version",
    "raw_value", "winsorized_value", "zscore_value",
    "neutralized_value", "percentile_rank",
]
COMPOSITE_COLUMNS = [
    "date_id", "stock_code", "calc_version",
    "value_score", "quality_score", "growth_score",
    "momentum_score", "risk_score", "total_score",
]
DIAGNOSTICS_COLUMNS = [
    "date_id", "factor_code", "calc_version",
    "universe_count", "valid_count", "coverage",
    "rank_ic_1m", "rank_ic_3m", "rank_ic_6m",
]


def _load_per_factor_dir(cur, base_dir, table, columns) -> None:
    """Incrementally load per-factor subdir CSVs (delete by factor_code + date)."""
    files = sorted(base_dir.glob("*/*.csv"))
    if not files:
        print(f"no {table} CSVs found; skipping", flush=True)
        return
    column_sql = ", ".join(columns)
    copy_sql = f"COPY {table} ({column_sql}) FROM STDIN WITH (FORMAT CSV, HEADER TRUE, NULL '')"
    for path in files:
        meta = pd.read_csv(path, usecols=["date_id", "factor_code"])
        factor_code = str(meta["factor_code"].iloc[0])
        dates = sorted({int(value) for value in meta["date_id"].unique()})
        if dates:
            cur.execute(
                f"DELETE FROM {table} WHERE factor_code = %s AND date_id = ANY(%s)",
                (factor_code, dates),
            )
        with path.open("r", encoding="utf-8", newline="") as handle:
            cur.copy_expert(copy_sql, handle)
    print(f"{table}: loaded {len(files)} file(s)", flush=True)


def load_factor_raw(cur) -> None:
    _load_per_factor_dir(cur, FACTOR_RAW_DIR, "fact_factor_raw", RAW_COLUMNS)


def load_factor_exposure(cur) -> None:
    _load_per_factor_dir(cur, FACTOR_EXPOSURE_DIR, "fact_factor_exposure", EXPOSURE_COLUMNS)


def load_factor_composite(cur) -> None:
    """Incrementally load composite_*.csv into fact_factor_composite (delete by date_id)."""
    files = sorted(FACTOR_COMPOSITE_DIR.glob("composite_*.csv"))
    if not files:
        print("no composite CSVs found; skipping", flush=True)
        return
    column_sql = ", ".join(COMPOSITE_COLUMNS)
    copy_sql = (
        f"COPY fact_factor_composite ({column_sql}) "
        "FROM STDIN WITH (FORMAT CSV, HEADER TRUE, NULL '')"
    )
    for path in files:
        dates = sorted({int(value) for value in pd.read_csv(path, usecols=["date_id"])["date_id"].unique()})
        if dates:
            cur.execute("DELETE FROM fact_factor_composite WHERE date_id = ANY(%s)", (dates,))
        with path.open("r", encoding="utf-8", newline="") as handle:
            cur.copy_expert(copy_sql, handle)
    print(f"fact_factor_composite: loaded {len(files)} file(s)", flush=True)


def load_factor_diagnostics(cur) -> None:
    """Incrementally load diagnostics_*.csv (delete by date_id; all factors regen)."""
    files = sorted(FACTOR_DIAGNOSTICS_DIR.glob("diagnostics_*.csv"))
    if not files:
        print("no diagnostics CSVs found; skipping", flush=True)
        return
    column_sql = ", ".join(DIAGNOSTICS_COLUMNS)
    copy_sql = (
        f"COPY fact_factor_diagnostics ({column_sql}) "
        "FROM STDIN WITH (FORMAT CSV, HEADER TRUE, NULL '')"
    )
    for path in files:
        dates = sorted({int(value) for value in pd.read_csv(path, usecols=["date_id"])["date_id"].unique()})
        if dates:
            cur.execute("DELETE FROM fact_factor_diagnostics WHERE date_id = ANY(%s)", (dates,))
        with path.open("r", encoding="utf-8", newline="") as handle:
            cur.copy_expert(copy_sql, handle)
    print(f"fact_factor_diagnostics: loaded {len(files)} file(s)", flush=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create factor-library PostgreSQL tables.")
    parser.add_argument(
        "--database",
        help="Target database name. Overrides POSTGRES_DB/PGDATABASE from .env.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    load_env(ENV_FILE)
    target_db = args.database or str(db_config()["dbname"])
    _, max_year = dim_date_year_bounds()
    partition_sql = build_factor_partition_sql(START_YEAR, max_year)

    print(
        "connecting to PostgreSQL "
        f"host={db_config()['host']} port={db_config()['port']} dbname={target_db}",
        flush=True,
    )
    with connect(target_db) as conn:
        with conn.cursor() as cur:
            print("creating factor tables", flush=True)
            execute_statements(cur, CREATE_FACTOR_TABLES_SQL)
            conn.commit()
            print("creating factor partitions", flush=True)
            execute_statements(cur, partition_sql)
            conn.commit()
            print("creating factor indexes", flush=True)
            execute_statements(cur, FACTOR_INDEXES_SQL)
            conn.commit()
            print("loading dim_factor from catalog", flush=True)
            load_dim_factor(cur)
            conn.commit()
            print("loading fact_stock_universe", flush=True)
            load_universe(cur)
            conn.commit()
            print("loading fact_factor_raw", flush=True)
            load_factor_raw(cur)
            conn.commit()
            print("loading fact_factor_exposure", flush=True)
            load_factor_exposure(cur)
            conn.commit()
            print("loading fact_factor_composite", flush=True)
            load_factor_composite(cur)
            conn.commit()
            print("loading fact_factor_diagnostics", flush=True)
            load_factor_diagnostics(cur)
            conn.commit()
    print("factor schema ready", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
