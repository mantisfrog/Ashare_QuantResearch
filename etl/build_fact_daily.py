import csv
import math
import struct
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
from paths import DATA_DIR, RAW_DIR


BASE_DIR = Path(__file__).resolve().parent
DIM_STOCK_CSV = DATA_DIR / "dim_stock.csv"
DIM_DATE_CSV = DATA_DIR / "dim_date.csv"
DIM_DATE_TEMP_CSV = DATA_DIR / "dim_date.csv.tmp"
DAY_DIRECTORIES = (
    RAW_DIR / "vipdoc" / "sh" / "lday",
    RAW_DIR / "vipdoc" / "sz" / "lday",
)
OUTPUT_CSV = DATA_DIR / "fact_daily.csv"
TEMP_CSV = DATA_DIR / "fact_daily.csv.tmp"

OUTPUT_FIELDS = [
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
]
DAY_RECORD = struct.Struct("<5If2I")
RECORD_SIZE = DAY_RECORD.size
MAX_RETRIES = 3
RETRY_SLEEP_SECONDS = 1.0
CAPITAL_SCALE = 10000
ISSUE_SAMPLE_LIMIT = 10


def load_stock_codes() -> set[str]:
    with DIM_STOCK_CSV.open("r", newline="", encoding="utf-8-sig") as csv_file:
        stock_codes = {
            row["stock_code"].strip()
            for row in csv.DictReader(csv_file)
            if row.get("stock_code", "").strip()
        }

    if not stock_codes:
        raise ValueError("dim_stock.csv contains no stock codes")

    return stock_codes


def load_dates() -> dict[int, bool]:
    with DIM_DATE_CSV.open("r", newline="", encoding="utf-8-sig") as csv_file:
        dates = {
            int(row["date_id"]): row["is_trade_day"].strip().lower() == "true"
            for row in csv.DictReader(csv_file)
        }

    if not dates:
        raise ValueError("dim_date.csv contains no dates")

    return dates


def stock_code_from_path(day_path: Path) -> str | None:
    name = day_path.stem.lower()
    if len(name) != 8 or name[:2] not in {"sh", "sz"}:
        return None
    if not name[2:].isdigit():
        return None
    raw_code = name[2:]
    market = name[:2].upper()
    if market == "SH" and not raw_code.startswith("6"):
        return None
    if market == "SZ" and not (
        raw_code.startswith("0") or raw_code.startswith("30")
    ):
        return None
    return f"{raw_code}.{market}"


def issue_sample(rows: list[str], message: str) -> None:
    if len(rows) < ISSUE_SAMPLE_LIMIT:
        rows.append(message)


def parse_share_count(value: object) -> int | None:
    try:
        numeric_value = float(value)
    except (TypeError, ValueError):
        return None

    if not math.isfinite(numeric_value) or numeric_value <= 0:
        return None

    return int(round(numeric_value))


def load_share_capital(
    stock_code: str,
    date_ids: list[int],
    tq_messages: Counter[str],
    capital_issues: Counter[str],
    capital_issue_samples: list[str],
) -> dict[int, tuple[int, int] | None]:
    if not date_ids:
        return {}

    request_dates = [str(date_id) for date_id in date_ids]
    last_error: Exception | None = None

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            result, messages = capture_output(
                tq.get_gb_info,
                stock_code=stock_code,
                date_list=request_dates,
                count=len(request_dates),
            )
            tq_messages.update(messages)
            if not isinstance(result, list):
                raise TypeError(
                    f"get_gb_info returned {type(result).__name__}"
                )
            if len(result) != len(date_ids):
                raise ValueError(
                    f"get_gb_info returned {len(result)} rows, "
                    f"expected {len(date_ids)}"
                )

            share_capital: dict[int, tuple[int, int] | None] = {}
            for item in result:
                if not isinstance(item, dict):
                    raise TypeError(
                        f"get_gb_info row has type {type(item).__name__}"
                    )
                date_id = int(float(item["Date"]))
                total_shares = parse_share_count(item.get("Zgb"))
                float_shares = parse_share_count(item.get("Ltgb"))
                if total_shares is None or float_shares is None:
                    capital_issues["invalid_or_missing_share_count"] += 1
                    issue_sample(
                        capital_issue_samples,
                        (
                            f"{stock_code} {date_id}: "
                            f"Zgb={item.get('Zgb')!r}, Ltgb={item.get('Ltgb')!r}"
                        ),
                    )
                    share_capital[date_id] = None
                    continue
                if float_shares > total_shares:
                    capital_issues["float_shares_exceed_total_shares"] += 1
                    issue_sample(
                        capital_issue_samples,
                        (
                            f"{stock_code} {date_id}: "
                            f"Ltgb={float_shares} exceeds Zgb={total_shares}"
                        ),
                    )
                    share_capital[date_id] = None
                    continue
                share_capital[date_id] = (total_shares, float_shares)

            missing_dates = set(date_ids).difference(share_capital)
            if missing_dates:
                capital_issues["missing_get_gb_info_dates"] += len(missing_dates)
                for date_id in sorted(missing_dates):
                    issue_sample(
                        capital_issue_samples,
                        f"{stock_code} {date_id}: get_gb_info returned no row",
                    )
                    share_capital[date_id] = None

            return share_capital
        except Exception as error:
            tq_messages.update(captured_output_from_error(error))
            last_error = error
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_SLEEP_SECONDS * attempt)

    capital_issues["get_gb_info_request_failed"] += len(date_ids)
    issue_sample(
        capital_issue_samples,
        f"{stock_code}: get_gb_info failed after {MAX_RETRIES} attempts: {last_error}",
    )
    return {date_id: None for date_id in date_ids}


def find_day_files(valid_stock_codes: set[str]) -> list[tuple[str, Path]]:
    files_by_code: dict[str, Path] = {}
    ignored: list[str] = []

    for directory in DAY_DIRECTORIES:
        for day_path in directory.glob("*.day"):
            stock_code = stock_code_from_path(day_path)
            if stock_code is None:
                ignored.append(day_path.name)
                continue
            if stock_code not in valid_stock_codes:
                raise ValueError(
                    f"{day_path.name} maps to {stock_code}, "
                    "which is missing from dim_stock.csv"
                )
            if stock_code in files_by_code:
                raise ValueError(f"duplicate .day files for {stock_code}")
            if day_path.stat().st_size % RECORD_SIZE != 0:
                raise ValueError(
                    f"{day_path.name} size is not divisible by {RECORD_SIZE}"
                )
            files_by_code[stock_code] = day_path

    missing_codes = valid_stock_codes.difference(files_by_code)
    if missing_codes:
        sample = ", ".join(sorted(missing_codes)[:10])
        raise ValueError(
            f"{len(missing_codes)} stocks have no .day file; sample: {sample}"
        )

    if ignored:
        sample = ", ".join(ignored[:10])
        print(
            f"Ignored {len(ignored)} non-target day files; sample: {sample}"
        )

    return sorted(files_by_code.items())


def synchronize_trade_day_flags(
    day_files: list[tuple[str, Path]],
) -> int:
    bar_date_ids: set[int] = set()
    for _, day_path in day_files:
        bar_date_ids.update(
            record[0]
            for record in DAY_RECORD.iter_unpack(day_path.read_bytes())
        )

    with DIM_DATE_CSV.open("r", newline="", encoding="utf-8-sig") as csv_file:
        reader = csv.DictReader(csv_file)
        fieldnames = reader.fieldnames
        if fieldnames is None or "is_trade_day" not in fieldnames:
            raise ValueError("dim_date.csv is missing is_trade_day")
        if "trade_day_index" not in fieldnames:
            fieldnames = [*fieldnames, "trade_day_index"]
        date_rows = list(reader)

    dimension_date_ids = {int(row["date_id"]) for row in date_rows}
    missing_date_ids = bar_date_ids.difference(dimension_date_ids)
    if missing_date_ids:
        sample = ", ".join(str(value) for value in sorted(missing_date_ids)[:10])
        raise ValueError(
            f"{len(missing_date_ids)} bar dates are missing from dim_date.csv; "
            f"sample: {sample}"
        )

    changed_count = 0
    for row in date_rows:
        if (
            int(row["date_id"]) in bar_date_ids
            and row["is_trade_day"].strip().lower() != "true"
        ):
            row["is_trade_day"] = "True"
            changed_count += 1

    sorted_trade_days = sorted(
        int(row["date_id"])
        for row in date_rows
        if row["is_trade_day"].strip().lower() == "true"
    )
    trade_day_indexes = {
        date_id: position
        for position, date_id in enumerate(sorted_trade_days, start=1)
    }
    index_changed_count = 0
    for row in date_rows:
        date_id = int(row["date_id"])
        expected_index = (
            str(trade_day_indexes[date_id])
            if row["is_trade_day"].strip().lower() == "true"
            else ""
        )
        if row.get("trade_day_index", "") != expected_index:
            row["trade_day_index"] = expected_index
            index_changed_count += 1

    if changed_count == 0 and index_changed_count == 0:
        return 0

    try:
        with DIM_DATE_TEMP_CSV.open(
            "w",
            newline="",
            encoding="utf-8",
        ) as csv_file:
            writer = csv.DictWriter(
                csv_file,
                fieldnames=fieldnames,
                lineterminator="\n",
            )
            writer.writeheader()
            writer.writerows(date_rows)
        DIM_DATE_TEMP_CSV.replace(DIM_DATE_CSV)
    except Exception:
        DIM_DATE_TEMP_CSV.unlink(missing_ok=True)
        raise

    return changed_count


def validate_prices(
    stock_code: str,
    date_id: int,
    open_raw: int,
    high_raw: int,
    low_raw: int,
    close_raw: int,
) -> None:
    prices = (open_raw, high_raw, low_raw, close_raw)
    if any(price <= 0 for price in prices):
        raise ValueError(
            f"{stock_code} {date_id}: OHLC must all be greater than zero"
        )
    if high_raw < max(open_raw, low_raw, close_raw):
        raise ValueError(
            f"{stock_code} {date_id}: high is below another OHLC value"
        )
    if low_raw > min(open_raw, high_raw, close_raw):
        raise ValueError(
            f"{stock_code} {date_id}: low is above another OHLC value"
        )


def write_stock_rows(
    writer: csv.writer,
    stock_code: str,
    day_path: Path,
    valid_dates: dict[int, bool],
    tq_messages: Counter[str],
    capital_issues: Counter[str],
    capital_issue_samples: list[str],
) -> tuple[int, int]:
    data = day_path.read_bytes()
    records = list(DAY_RECORD.iter_unpack(data))
    share_capital = load_share_capital(
        stock_code,
        [record[0] for record in records],
        tq_messages,
        capital_issues,
        capital_issue_samples,
    )
    previous_date_id = 0
    row_count = 0
    capital_row_count = 0

    for record in records:
        (
            date_id,
            open_raw,
            high_raw,
            low_raw,
            close_raw,
            amount_raw,
            volume,
            _reserved,
        ) = record

        if date_id <= previous_date_id:
            raise ValueError(
                f"{stock_code}: dates are not strictly increasing at {date_id}"
            )
        previous_date_id = date_id

        is_trade_day = valid_dates.get(date_id)
        if is_trade_day is None:
            raise ValueError(
                f"{stock_code} {date_id}: date_id is missing from dim_date.csv"
            )
        if not is_trade_day:
            raise ValueError(
                f"{stock_code} {date_id}: daily bar falls on a non-trading day"
            )

        validate_prices(
            stock_code,
            date_id,
            open_raw,
            high_raw,
            low_raw,
            close_raw,
        )
        if not math.isfinite(amount_raw) or amount_raw < 0:
            raise ValueError(
                f"{stock_code} {date_id}: amount must be finite and non-negative"
            )

        close_price = close_raw / 100
        capital = share_capital[date_id]
        if capital is None:
            total_shares = ""
            float_shares = ""
            market_cap = ""
            float_market_cap = ""
        else:
            total_share_count, float_share_count = capital
            total_shares = total_share_count
            float_shares = float_share_count
            market_cap = (
                f"{close_price * total_share_count / CAPITAL_SCALE:.4f}"
            )
            float_market_cap = (
                f"{close_price * float_share_count / CAPITAL_SCALE:.4f}"
            )
            capital_row_count += 1

        writer.writerow(
            (
                date_id,
                stock_code,
                f"{open_raw / 100:.2f}",
                f"{high_raw / 100:.2f}",
                f"{low_raw / 100:.2f}",
                f"{close_raw / 100:.2f}",
                volume,
                f"{amount_raw / 10000:.4f}",
                total_shares,
                float_shares,
                market_cap,
                float_market_cap,
            )
        )
        row_count += 1

    return row_count, capital_row_count


def main() -> None:
    tq_messages: Counter[str] = Counter()
    capital_issues: Counter[str] = Counter()
    capital_issue_samples: list[str] = []
    print(
        "querying tqcenter share capital once per stock; "
        "raw tqcenter messages are summarized"
    )
    _, messages = capture_output(tq.initialize, __file__)
    tq_messages.update(messages)
    stock_codes = load_stock_codes()
    day_files = find_day_files(stock_codes)
    changed_trade_days = synchronize_trade_day_flags(day_files)
    if changed_trade_days:
        print(
            f"Updated {changed_trade_days} historical trading-day flags "
            "in dim_date.csv"
        )
    valid_dates = load_dates()
    expected_rows = sum(
        day_path.stat().st_size // RECORD_SIZE for _, day_path in day_files
    )
    output_rows = 0
    capital_rows = 0

    try:
        with TEMP_CSV.open("w", newline="", encoding="utf-8") as csv_file:
            writer = csv.writer(csv_file, lineterminator="\n")
            writer.writerow(OUTPUT_FIELDS)

            for position, (stock_code, day_path) in enumerate(
                day_files,
                start=1,
            ):
                stock_rows, stock_capital_rows = write_stock_rows(
                    writer,
                    stock_code,
                    day_path,
                    valid_dates,
                    tq_messages,
                    capital_issues,
                    capital_issue_samples,
                )
                output_rows += stock_rows
                capital_rows += stock_capital_rows
                if position % 50 == 0 or position == len(day_files):
                    print_progress(
                        "daily files",
                        position,
                        len(day_files),
                        (
                            f"rows={output_rows}/{expected_rows} "
                            f"capital_rows={capital_rows} "
                            f"missing_capital_rows={output_rows - capital_rows}"
                        ),
                    )
    except Exception:
        TEMP_CSV.unlink(missing_ok=True)
        report_captured_output("tqcenter_fact_daily", tq_messages)
        raise
    finally:
        close_method = getattr(tq, "close", None)
        if callable(close_method):
            _, messages = capture_output(close_method)
            tq_messages.update(messages)

    if output_rows != expected_rows:
        TEMP_CSV.unlink(missing_ok=True)
        raise RuntimeError(
            f"row count mismatch: wrote {output_rows}, expected {expected_rows}"
        )

    TEMP_CSV.replace(OUTPUT_CSV)
    report_captured_output("tqcenter_fact_daily", tq_messages)
    if capital_issues:
        issue_detail = ",".join(
            f"{name}:{count}" for name, count in capital_issues.items()
        )
        sample = "; ".join(capital_issue_samples)
        print(
            "share capital coverage warning: "
            f"missing_rows={output_rows - capital_rows}; "
            f"issues={issue_detail}; sample={sample}",
            flush=True,
        )
        append_summary(
            "fact_daily_capital_coverage",
            (
                f"missing_rows={output_rows - capital_rows} "
                f"issues={issue_detail} sample={sample}"
            ),
        )
    summary = (
        f"stocks={len(day_files)} rows={output_rows} "
        f"capital_rows={capital_rows} "
        f"missing_capital_rows={output_rows - capital_rows} "
        f"changed_trade_days={changed_trade_days} expected_rows={expected_rows}"
    )
    print(
        "daily summary: "
        f"{summary}; amount_unit=10000 CNY; "
        "share_source=tqcenter.get_gb_info"
    )
    append_summary("fact_daily", summary)


if __name__ == "__main__":
    main()
