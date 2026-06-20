import csv
import time
from collections import Counter
from pathlib import Path

from tqcenter import tq

from etl_logging import (
    append_summary,
    capture_output,
    captured_output_from_error,
    print_progress,
    report_captured_output,
)
from paths import DATA_DIR


BASE_DIR = Path(__file__).resolve().parent
STOCK_CSV = DATA_DIR / "dim_stock.csv"
INDUSTRY_CSV = DATA_DIR / "dim_tdx_industry.csv"
TEMP_CSV = DATA_DIR / "dim_stock.csv.tmp"
INDUSTRY_TEMP_CSV = DATA_DIR / "dim_tdx_industry.csv.tmp"

OUTPUT_FIELDS = [
    "stock_code",
    "stock_name",
    "tdx_sector_code",
]
SOURCE_FIELDS = {
    "stock_name": "Name",
    "tdx_sector_code": "blockzscode",
}
INFO_FIELDS = ["Name", "rs_hyname", "blockzscode"]
MAX_RETRIES = 3
MAX_CONSECUTIVE_FAILURES = 5


class StockInfoUnavailable(RuntimeError):
    pass


def load_stock_rows() -> list[dict[str, str]]:
    with STOCK_CSV.open("r", newline="", encoding="utf-8-sig") as csv_file:
        rows: list[dict[str, str]] = []
        for row in csv.DictReader(csv_file):
            stock_code = row.get("stock_code", "").strip()
            if not stock_code:
                continue
            rows.append(
                {
                    "stock_code": stock_code,
                    "stock_name": clean_value(
                        row.get("stock_name", row.get("name", "")),
                    ),
                    "tdx_sector_code": clean_value(row.get("tdx_sector_code")),
                }
            )

    stock_codes = [row["stock_code"] for row in rows]
    if len(stock_codes) != len(set(stock_codes)):
        raise ValueError("dim_stock.csv contains duplicate stock_code values")

    return rows


def load_industries() -> dict[str, str]:
    if not INDUSTRY_CSV.exists():
        return {}

    industries: dict[str, str] = {}
    with INDUSTRY_CSV.open("r", newline="", encoding="utf-8-sig") as csv_file:
        for row in csv.DictReader(csv_file):
            sector_code = clean_value(row.get("tdx_sector_code"))
            sector_name = clean_value(row.get("tdx_sector_name"))
            if sector_code and sector_name:
                industries[sector_code] = sector_name
    return industries


def get_stock_info(
    stock_code: str,
    tq_messages: Counter[str],
) -> dict[str, object]:
    last_error: Exception | None = None

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            result, messages = capture_output(
                tq.get_stock_info,
                stock_code=stock_code,
                field_list=INFO_FIELDS,
            )
            tq_messages.update(messages)
            if not isinstance(result, dict):
                raise TypeError(
                    f"get_stock_info returned {type(result).__name__}"
                )
            if not result:
                raise StockInfoUnavailable("get_stock_info returned empty result")
            return result
        except StockInfoUnavailable:
            raise
        except Exception as error:
            tq_messages.update(captured_output_from_error(error))
            last_error = error
            if attempt < MAX_RETRIES:
                time.sleep(attempt)

    raise RuntimeError(
        f"get_stock_info failed after {MAX_RETRIES} attempts"
    ) from last_error


def clean_value(value: object) -> str:
    if value is None:
        return ""
    return str(value).strip()


def needs_stock_info_refresh(row: dict[str, str], industries: dict[str, str]) -> bool:
    stock_name = row.get("stock_name", "")
    sector_code = row.get("tdx_sector_code", "")
    if not stock_name or not sector_code:
        return True
    return sector_code not in industries


def row_from_info(
    stock_code: str,
    info: dict[str, object],
    fallback: dict[str, str],
) -> tuple[dict[str, str], str]:
    row = {"stock_code": stock_code}
    for output_field, source_field in SOURCE_FIELDS.items():
        row[output_field] = clean_value(info.get(source_field)) or fallback.get(
            output_field,
            "",
        )
    sector_name = clean_value(info.get("rs_hyname"))
    return row, sector_name


def diagnostic_sample(rows: list[tuple[str, str]], limit: int = 5) -> str:
    return "; ".join(f"{stock_code}: {message}" for stock_code, message in rows[:limit])


def main() -> None:
    stock_rows = load_stock_rows()
    warnings: list[tuple[str, str]] = []
    empty_counts = {field: 0 for field in SOURCE_FIELDS}
    industries = load_industries()
    rows_to_query = [
        row for row in stock_rows if needs_stock_info_refresh(row, industries)
    ]
    query_total = len(rows_to_query)
    tq_messages: Counter[str] = Counter()
    queried = 0
    query_failures = 0
    skipped_queries = 0
    consecutive_failures = 0
    stock_info_disabled = False
    last_progress_reported = 0
    reused = 0

    if query_total:
        print(
            f"querying tqcenter stock info: {query_total} stocks; "
            "raw tqcenter messages are summarized",
            flush=True,
        )
        _, messages = capture_output(tq.initialize, __file__)
        tq_messages.update(messages)

    try:
        with TEMP_CSV.open("w", newline="", encoding="utf-8-sig") as csv_file:
            writer = csv.DictWriter(
                csv_file,
                fieldnames=OUTPUT_FIELDS,
                lineterminator="\n",
            )
            writer.writeheader()

            for stock_row in stock_rows:
                stock_code = stock_row["stock_code"]
                row = dict(stock_row)
                sector_name = ""
                if needs_stock_info_refresh(row, industries):
                    if stock_info_disabled:
                        skipped_queries += 1
                    else:
                        try:
                            info = get_stock_info(stock_code, tq_messages)
                            row, sector_name = row_from_info(stock_code, info, row)
                            queried += 1
                            consecutive_failures = 0
                        except Exception as error:
                            warnings.append((stock_code, str(error)))
                            query_failures += 1
                            queried += 1
                            consecutive_failures += 1
                            if consecutive_failures >= MAX_CONSECUTIVE_FAILURES:
                                stock_info_disabled = True
                                warnings.append(
                                    (
                                        "tqcenter",
                                        "disabled stock info enrichment after "
                                        f"{consecutive_failures} consecutive "
                                        "failures; remaining stocks keep existing "
                                        "metadata or blank values",
                                    )
                                )
                else:
                    reused += 1

                sector_code = row["tdx_sector_code"]
                if sector_code:
                    if sector_name:
                        previous_name = industries.get(sector_code)
                        if previous_name is not None and previous_name != sector_name:
                            warnings.append(
                                (
                                    stock_code,
                                    f"industry code {sector_code} has conflicting "
                                    f"names: {previous_name!r} and {sector_name!r}; "
                                    "kept existing industry name",
                                )
                            )
                        else:
                            industries[sector_code] = sector_name
                    elif sector_code not in industries:
                        warnings.append(
                            (
                                stock_code,
                                f"missing industry name for sector code {sector_code}; "
                                "cleared tdx_sector_code",
                            )
                        )
                        row["tdx_sector_code"] = ""

                for output_field in SOURCE_FIELDS:
                    if not row[output_field]:
                        empty_counts[output_field] += 1

                writer.writerow(row)
                progress_done = queried + skipped_queries
                if (
                    query_total
                    and progress_done > last_progress_reported
                    and (
                        progress_done % 20 == 0
                        or progress_done == query_total
                    )
                ):
                    print_progress(
                        "stock info queries",
                        min(progress_done, query_total),
                        query_total,
                        (
                            f"attempted={queried} skipped={skipped_queries} "
                            f"unresolved={query_failures} warnings={len(warnings)}"
                        ),
                    )
                    last_progress_reported = progress_done

            if query_total:
                progress_done = queried + skipped_queries
                if progress_done > last_progress_reported:
                    print_progress(
                        "stock info queries",
                        min(progress_done, query_total),
                        query_total,
                        (
                            f"attempted={queried} skipped={skipped_queries} "
                            f"unresolved={query_failures} warnings={len(warnings)}"
                        ),
                    )
    finally:
        close_method = getattr(tq, "close", None)
        if callable(close_method):
            _, messages = capture_output(close_method)
            tq_messages.update(messages)

    if warnings:
        append_summary(
            "dim_stock",
            f"warnings={len(warnings)} sample={diagnostic_sample(warnings)}",
        )
        print(
            f"stock info warnings: {len(warnings)}; "
            f"sample: {diagnostic_sample(warnings)}",
            flush=True,
        )

    try:
        with INDUSTRY_TEMP_CSV.open(
            "w",
            newline="",
            encoding="utf-8-sig",
        ) as csv_file:
            writer = csv.writer(csv_file, lineterminator="\n")
            writer.writerow(["tdx_sector_code", "tdx_sector_name"])
            for sector_code, sector_name in sorted(industries.items()):
                writer.writerow([sector_code, sector_name])
    except Exception:
        TEMP_CSV.unlink(missing_ok=True)
        INDUSTRY_TEMP_CSV.unlink(missing_ok=True)
        raise

    TEMP_CSV.replace(STOCK_CSV)
    INDUSTRY_TEMP_CSV.replace(INDUSTRY_CSV)
    report_captured_output("tqcenter_dim_stock", tq_messages)
    summary = (
        f"stocks={len(stock_rows)} reused={reused} queried={queried} "
        f"skipped_queries={skipped_queries} query_failures={query_failures} "
        f"industries={len(industries)} "
        f"warnings={len(warnings)} "
        + "empty_values="
        + ",".join(f"{field}:{count}" for field, count in empty_counts.items())
    )
    print(f"stock dimension summary: {summary}")
    append_summary("dim_stock", summary)


if __name__ == "__main__":
    main()
