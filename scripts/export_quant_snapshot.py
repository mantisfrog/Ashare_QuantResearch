"""Export an immutable Parquet snapshot for an external quant research repo."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
from datetime import date, datetime, timezone
from decimal import Decimal
from pathlib import Path
from typing import Any, Iterable, Iterator, Sequence

import pyarrow as pa
import pyarrow.parquet as pq


ROOT = Path(__file__).resolve().parents[1]
ETL_DIR = ROOT / "etl"
if str(ETL_DIR) not in sys.path:
    sys.path.insert(0, str(ETL_DIR))

from build_postgres_from_csv import connect, load_env  # noqa: E402
from paths import ENV_FILE  # noqa: E402


SCHEMA_VERSION = "1.0.0"
DEFAULT_START_DATE = date(2011, 1, 1)
DEFAULT_FINANCIAL_START_PERIOD = date(2010, 1, 1)
DEFAULT_OUTPUT_ROOT = ROOT / "data" / "deliverables"
FETCH_SIZE = 100_000

METRIC_GROUPS: dict[str, tuple[str, Sequence[tuple[str, str, str]]]] = {
    "balance_sheet": (
        "stock",
        (
            ("FN8", "货币资金", "元"), ("FN11", "应收账款", "元"),
            ("FN17", "存货", "元"), ("FN21", "流动资产合计", "元"),
            ("FN25", "长期股权投资", "元"), ("FN27", "固定资产", "元"),
            ("FN28", "在建工程", "元"), ("FN33", "无形资产", "元"),
            ("FN35", "商誉", "元"), ("FN40", "资产总计", "元"),
            ("FN41", "短期借款", "元"), ("FN44", "应付账款", "元"),
            ("FN54", "流动负债合计", "元"), ("FN55", "长期借款", "元"),
            ("FN56", "应付债券", "元"), ("FN62", "非流动负债合计", "元"),
            ("FN63", "负债合计", "元"), ("FN64", "实收资本（或股本）", "元"),
            ("FN68", "未分配利润", "元"), ("FN69", "少数股东权益", "元"),
            ("FN72", "所有者权益合计", "元"),
            ("FN271", "归属于母公司股东权益", "元"),
        ),
    ),
    "income_statement": (
        "ytd",
        (
            ("FN74", "营业收入", "元"), ("FN75", "营业成本", "元"),
            ("FN76", "营业税金及附加", "元"), ("FN77", "销售费用", "元"),
            ("FN78", "管理费用", "元"), ("FN80", "财务费用", "元"),
            ("FN81", "资产减值损失", "元"), ("FN82", "公允价值变动净收益", "元"),
            ("FN83", "投资收益", "元"), ("FN86", "营业利润", "元"),
            ("FN88", "营业外收入", "元"), ("FN89", "营业外支出", "元"),
            ("FN92", "利润总额", "元"), ("FN93", "所得税", "元"),
            ("FN95", "净利润", "元"), ("FN96", "归属于母公司所有者的净利润", "元"),
            ("FN304", "研发费用", "元"),
        ),
    ),
    "cash_flow_statement": (
        "ytd",
        (
            ("FN98", "销售商品、提供劳务收到的现金", "元"),
            ("FN107", "经营活动产生的现金流量净额", "元"),
            ("FN114", "购建固定资产、无形资产和其他长期资产支付的现金", "元"),
            ("FN115", "投资支付的现金", "元"),
            ("FN119", "投资活动产生的现金流量净额", "元"),
            ("FN124", "偿还债务支付的现金", "元"),
            ("FN125", "分配股利、利润或偿付利息支付的现金", "元"),
            ("FN128", "筹资活动产生的现金流量净额", "元"),
            ("FN131", "现金及现金等价物净增加额", "元"),
            ("FN133", "期末现金及现金等价物余额", "元"),
        ),
    ),
    "single_quarter": (
        "single_quarter",
        (
            ("FN230", "营业收入（单季度）", "元"),
            ("FN328", "营业成本（单季度）", "万元"),
            ("FN231", "营业利润（单季度）", "元"),
            ("FN324", "净利润（单季度）", "万元"),
            ("FN232", "归母净利润（单季度）", "元"),
            ("FN233", "扣非净利润（单季度）", "元"),
            ("FN234", "经营活动现金流净额（单季度）", "元"),
            ("FN235", "投资活动现金流净额（单季度）", "元"),
            ("FN236", "筹资活动现金流净额（单季度）", "元"),
        ),
    ),
    "ttm": (
        "ttm",
        (
            ("FN319", "营业总收入TTM", "万元"),
            ("FN338", "营业成本TTM-非金融类", "万元"),
            ("FN323", "营业利润TTM", "万元"), ("FN276", "净利润TTM", "元"),
            ("FN308", "归母净利润TTM", "万元"),
            ("FN309", "扣非净利润TTM", "万元"),
            ("FN307", "经营活动现金流净额TTM", "元"),
            ("FN316", "投资活动现金流净额TTM", "万元"),
            ("FN310", "现金净流量TTM", "万元"),
        ),
    ),
}

METRIC_ROWS = tuple(
    (code, name, category, value_kind, unit)
    for category, (value_kind, metrics) in METRIC_GROUPS.items()
    for code, name, unit in metrics
)
METRIC_CODES = tuple(row[0] for row in METRIC_ROWS)

MARKET_SCHEMA = pa.schema(
    [
        ("date_id", pa.int32()), ("date", pa.date32()), ("stock_code", pa.string()),
        ("open", pa.decimal128(18, 2)), ("high", pa.decimal128(18, 2)),
        ("low", pa.decimal128(18, 2)), ("close", pa.decimal128(18, 2)),
        ("adjust_factor", pa.decimal128(28, 12)),
        ("adj_open", pa.decimal128(38, 8)), ("adj_high", pa.decimal128(38, 8)),
        ("adj_low", pa.decimal128(38, 8)), ("adj_close", pa.decimal128(38, 8)),
        ("vol", pa.int64()), ("amount", pa.decimal128(20, 4)),
        ("total_shares", pa.int64()), ("float_shares", pa.int64()),
        ("market_cap", pa.decimal128(24, 4)),
        ("float_market_cap", pa.decimal128(24, 4)),
    ]
)

FINANCIAL_SCHEMA = pa.schema(
    [
        ("report_id", pa.int64()), ("stock_code", pa.string()),
        ("report_period", pa.date32()), ("announce_date_id", pa.int32()),
        ("metric_code", pa.string()), ("metric_value", pa.decimal128(28, 6)),
    ]
)

STOCK_SCHEMA = pa.schema(
    [
        ("stock_code", pa.string()), ("stock_name", pa.string()),
        ("tdx_sector_code", pa.string()), ("tdx_sector_name", pa.string()),
    ]
)

CALENDAR_SCHEMA = pa.schema(
    [
        ("date_id", pa.int32()), ("date", pa.date32()), ("year_num", pa.int16()),
        ("quarter_num", pa.int8()), ("month_num", pa.int8()), ("day_week", pa.int8()),
        ("is_trade_day", pa.bool_()), ("trade_day_index", pa.int32()),
    ]
)

METRIC_SCHEMA = pa.schema(
    [
        ("metric_code", pa.string()), ("metric_name", pa.string()),
        ("statement_category", pa.string()), ("value_kind", pa.string()),
        ("unit", pa.string()), ("is_financial_sector_specific", pa.bool_()),
    ]
)


def parse_iso_date(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError(f"invalid ISO date: {value}") from error


def date_id(value: date) -> int:
    return value.year * 10_000 + value.month * 100 + value.day


def id_date(value: int) -> date:
    text = str(value)
    return date(int(text[:4]), int(text[4:6]), int(text[6:]))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--database")
    parser.add_argument("--start-date", type=parse_iso_date, default=DEFAULT_START_DATE)
    parser.add_argument(
        "--financial-start-period",
        type=parse_iso_date,
        default=DEFAULT_FINANCIAL_START_PERIOD,
    )
    parser.add_argument("--end-date", type=parse_iso_date)
    return parser.parse_args()


def iter_batches(cursor, query: str, params: Any, size: int = FETCH_SIZE) -> Iterator[list[tuple]]:
    cursor.itersize = size
    cursor.execute(query, params)
    while True:
        rows = cursor.fetchmany(size)
        if not rows:
            return
        yield rows


def write_query_parquet(
    conn,
    path: Path,
    schema: pa.Schema,
    query: str,
    params: Any,
    cursor_name: str,
) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    row_count = 0
    writer: pq.ParquetWriter | None = None
    try:
        with conn.cursor(name=cursor_name) as cursor:
            for rows in iter_batches(cursor, query, params):
                table = pa.Table.from_pylist(
                    [dict(zip(schema.names, row)) for row in rows], schema=schema
                )
                if writer is None:
                    writer = pq.ParquetWriter(path, schema, compression="zstd")
                writer.write_table(table, row_group_size=FETCH_SIZE)
                row_count += len(rows)
    finally:
        if writer is not None:
            writer.close()
    if writer is None:
        pq.write_table(pa.Table.from_pylist([], schema=schema), path, compression="zstd")
    return row_count


def write_table(path: Path, schema: pa.Schema, rows: Iterable[Sequence[Any]]) -> int:
    values = list(rows)
    path.parent.mkdir(parents=True, exist_ok=True)
    table = pa.Table.from_pylist(
        [dict(zip(schema.names, row)) for row in values], schema=schema
    )
    pq.write_table(table, path, compression="zstd")
    return len(values)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def file_record(root: Path, path: Path, rows: int) -> dict[str, Any]:
    return {
        "path": path.relative_to(root).as_posix(),
        "rows": rows,
        "bytes": path.stat().st_size,
        "sha256": sha256_file(path),
    }


def schema_record(schema: pa.Schema) -> list[dict[str, Any]]:
    return [
        {"name": field.name, "type": str(field.type), "nullable": field.nullable}
        for field in schema
    ]


def validate_parquet(path: Path, expected_schema: pa.Schema, expected_rows: int) -> None:
    parquet = pq.ParquetFile(path)
    if parquet.metadata.num_rows != expected_rows:
        raise RuntimeError(f"row count mismatch for {path}")
    if not parquet.schema_arrow.equals(expected_schema):
        raise RuntimeError(f"schema mismatch for {path}")


def source_bounds(conn, requested_end: date | None) -> tuple[int, int]:
    with conn.cursor() as cursor:
        cursor.execute("SELECT MIN(date_id), MAX(date_id) FROM fact_daily")
        minimum, maximum = cursor.fetchone()
    if maximum is None:
        raise RuntimeError("fact_daily is empty")
    selected_end = date_id(requested_end) if requested_end else int(maximum)
    if selected_end > int(maximum):
        raise ValueError(f"end date {selected_end} exceeds source maximum {maximum}")
    return int(minimum), selected_end


def write_readme(root: Path, start_id: int, end_id: int, financial_start: date) -> None:
    text = f"""# Quant research snapshot

- Schema version: `{SCHEMA_VERSION}`
- Market range: `{id_date(start_id).isoformat()}` through `{id_date(end_id).isoformat()}`
- Financial report periods: `{financial_start.isoformat()}` onward, with announcements through `{id_date(end_id).isoformat()}`
- Prices: raw OHLC and back-adjusted OHLC (`raw * adjust_factor`)
- Volume and amount: unadjusted actual values
- Financial availability: filter with `announce_date_id <= research_date_id`

```python
import pandas as pd

market = pd.read_parquet("market", filters=[("year", ">=", 2020)])
financials = pd.read_parquet("financials", filters=[("report_year", ">=", 2020)])
```

`stocks.parquet` contains current names and industries, not historical point-in-time names,
ST flags, or industries. Financial values retain source-native units; consult
`dimensions/financial_metrics.parquet` before combining metrics.
"""
    (root / "README.md").write_text(text, encoding="utf-8")


def export_snapshot(args: argparse.Namespace) -> Path:
    load_env(ENV_FILE)
    output_root = args.output_root.resolve()
    output_root.mkdir(parents=True, exist_ok=True)

    conn = connect(args.database)
    conn.set_session(isolation_level="REPEATABLE READ", readonly=True, autocommit=False)
    temp_root: Path | None = None
    try:
        _, end_id = source_bounds(conn, args.end_date)
        requested_start_id = date_id(args.start_date)
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT MIN(date_id) FROM fact_daily WHERE date_id BETWEEN %s AND %s",
                (requested_start_id, end_id),
            )
            actual_start_id = cursor.fetchone()[0]
        if actual_start_id is None:
            raise RuntimeError("no market rows in requested date range")

        snapshot_name = f"quant_snapshot_{requested_start_id}_{end_id}_v1"
        final_root = output_root / snapshot_name
        temp_root = output_root / f".{snapshot_name}.tmp-{os.getpid()}"
        if final_root.exists():
            raise FileExistsError(f"snapshot already exists: {final_root}")
        if temp_root.exists():
            shutil.rmtree(temp_root)
        temp_root.mkdir()

        files: list[dict[str, Any]] = []
        market_query = """
            SELECT f.date_id, d.date, f.stock_code,
                   f.open, f.high, f.low, f.close, a.adjust_factor,
                   CAST(f.open * a.adjust_factor AS NUMERIC(38,8)),
                   CAST(f.high * a.adjust_factor AS NUMERIC(38,8)),
                   CAST(f.low * a.adjust_factor AS NUMERIC(38,8)),
                   CAST(f.close * a.adjust_factor AS NUMERIC(38,8)),
                   f.vol, f.amount, f.total_shares, f.float_shares,
                   f.market_cap, f.float_market_cap
            FROM fact_daily f
            JOIN dim_date d ON d.date_id = f.date_id
            JOIN fact_adjustment_factor_period a
              ON a.stock_code = f.stock_code
             AND f.date_id BETWEEN a.valid_from_date_id AND a.valid_to_date_id
            WHERE f.date_id BETWEEN %s AND %s
            ORDER BY f.date_id, f.stock_code
        """
        market_total = 0
        for year in range(id_date(actual_start_id).year, id_date(end_id).year + 1):
            year_start = max(actual_start_id, year * 10_000 + 101)
            year_end = min(end_id, year * 10_000 + 1231)
            path = temp_root / "market" / f"year={year}" / "part-00000.parquet"
            rows = write_query_parquet(
                conn, path, MARKET_SCHEMA, market_query, (year_start, year_end), f"market_{year}"
            )
            validate_parquet(path, MARKET_SCHEMA, rows)
            files.append(file_record(temp_root, path, rows))
            market_total += rows
            print(f"market {year}: {rows:,} rows", flush=True)

        financial_query = """
            SELECT r.report_id, r.stock_code, r.report_period, r.announce_date_id,
                   v.metric_code, v.metric_value
            FROM fact_financial_report r
            JOIN fact_financial_value v ON v.report_id = r.report_id
            WHERE r.report_period BETWEEN %s AND %s
              AND r.announce_date_id <= %s
              AND v.metric_code = ANY(%s)
            ORDER BY r.report_period, r.stock_code, v.metric_code
        """
        financial_total = 0
        financial_end = id_date(end_id)
        for year in range(args.financial_start_period.year, financial_end.year + 1):
            period_start = max(args.financial_start_period, date(year, 1, 1))
            period_end = min(financial_end, date(year, 12, 31))
            path = temp_root / "financials" / f"report_year={year}" / "part-00000.parquet"
            rows = write_query_parquet(
                conn,
                path,
                FINANCIAL_SCHEMA,
                financial_query,
                (period_start, period_end, end_id, list(METRIC_CODES)),
                f"financial_{year}",
            )
            validate_parquet(path, FINANCIAL_SCHEMA, rows)
            files.append(file_record(temp_root, path, rows))
            financial_total += rows
            print(f"financial {year}: {rows:,} rows", flush=True)

        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT s.stock_code, s.stock_name, s.tdx_sector_code, i.tdx_sector_name
                FROM dim_stock s
                LEFT JOIN dim_tdx_industry i ON i.tdx_sector_code = s.tdx_sector_code
                ORDER BY s.stock_code
                """
            )
            stock_rows = cursor.fetchall()
            cursor.execute(
                """
                SELECT date_id, date, year_num, quarter_num, month_num, day_week,
                       is_trade_day, trade_day_index
                FROM dim_date WHERE date_id BETWEEN %s AND %s ORDER BY date_id
                """,
                (requested_start_id, end_id),
            )
            calendar_rows = cursor.fetchall()

        dimension_specs = (
            ("dimensions/stocks.parquet", STOCK_SCHEMA, stock_rows),
            ("dimensions/calendar.parquet", CALENDAR_SCHEMA, calendar_rows),
            (
                "dimensions/financial_metrics.parquet",
                METRIC_SCHEMA,
                ((*row, False) for row in METRIC_ROWS),
            ),
        )
        for relative, schema, rows in dimension_specs:
            path = temp_root / relative
            count = write_table(path, schema, rows)
            validate_parquet(path, schema, count)
            files.append(file_record(temp_root, path, count))

        write_readme(temp_root, actual_start_id, end_id, args.financial_start_period)
        manifest = {
            "schema_version": SCHEMA_VERSION,
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "source": "PostgreSQL",
            "requested_market_start": args.start_date.isoformat(),
            "actual_market_start": id_date(actual_start_id).isoformat(),
            "market_end": id_date(end_id).isoformat(),
            "financial_start_period": args.financial_start_period.isoformat(),
            "metric_count": len(METRIC_CODES),
            "row_counts": {"market": market_total, "financials": financial_total},
            "schemas": {
                "market": schema_record(MARKET_SCHEMA),
                "financials": schema_record(FINANCIAL_SCHEMA),
                "stocks": schema_record(STOCK_SCHEMA),
                "calendar": schema_record(CALENDAR_SCHEMA),
                "financial_metrics": schema_record(METRIC_SCHEMA),
            },
            "files": files,
        }
        manifest_path = temp_root / "manifest.json"
        manifest_path.write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        checksum_paths = sorted(
            path for path in temp_root.rglob("*") if path.is_file() and path.name != "checksums.sha256"
        )
        checksum_text = "".join(
            f"{sha256_file(path)}  {path.relative_to(temp_root).as_posix()}\n"
            for path in checksum_paths
        )
        (temp_root / "checksums.sha256").write_text(checksum_text, encoding="ascii")

        conn.rollback()
        temp_root.rename(final_root)
        print(f"snapshot published: {final_root}", flush=True)
        return final_root
    except Exception:
        conn.rollback()
        if temp_root is not None and temp_root.exists():
            shutil.rmtree(temp_root)
        raise
    finally:
        conn.close()


def main() -> int:
    args = parse_args()
    export_snapshot(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())