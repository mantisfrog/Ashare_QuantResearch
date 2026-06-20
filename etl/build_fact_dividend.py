import csv
import time
from collections import Counter
from datetime import date, datetime, timedelta
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path

import pandas as pd
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
DATE_CSV = DATA_DIR / "dim_date.csv"
DATE_TEMP_CSV = DATA_DIR / "dim_date.csv.tmp"
OUTPUT_CSV = DATA_DIR / "fact_dividend.csv"
TEMP_CSV = DATA_DIR / "fact_dividend.csv.tmp"

OUTPUT_FIELDS = [
    "stock_code",
    "date_id",
    "action_type",
    "bonus",
    "allot_price",
    "share_bonus",
    "allotment",
]
VALUE_FIELDS = {
    "bonus": "Bonus",
    "allot_price": "AllotPrice",
    "share_bonus": "ShareBonus",
    "allotment": "Allotment",
}
VALID_ACTION_TYPES = {1, 11, 15}
SCALE = Decimal("0.000001")
MAX_RETRIES = 3
DATE_FIELDS = [
    "date_id",
    "date",
    "year_num",
    "quarter_num",
    "month_num",
    "day_week",
    "is_trade_day",
    "trade_day_index",
]


def load_stock_codes() -> list[str]:
    with STOCK_CSV.open("r", newline="", encoding="utf-8-sig") as csv_file:
        stock_codes = [
            row["stock_code"].strip()
            for row in csv.DictReader(csv_file)
            if row.get("stock_code", "").strip()
        ]

    if len(stock_codes) != len(set(stock_codes)):
        raise ValueError("dim_stock.csv contains duplicate stock_code values")

    return sorted(stock_codes)


def load_date_ids() -> set[int]:
    with DATE_CSV.open("r", newline="", encoding="utf-8-sig") as csv_file:
        return {
            int(row["date_id"])
            for row in csv.DictReader(csv_file)
            if row.get("date_id", "").strip()
        }


def date_id_to_date(date_id: int) -> date:
    return datetime.strptime(str(date_id), "%Y%m%d").date()


def date_to_date_id(value: date) -> int:
    return int(value.strftime("%Y%m%d"))


def extend_dim_date(missing_date_ids: set[int]) -> None:
    if not missing_date_ids:
        return

    with DATE_CSV.open("r", newline="", encoding="utf-8-sig") as csv_file:
        existing_rows = list(csv.DictReader(csv_file))

    existing_flags = {
        int(row["date_id"]): row["is_trade_day"].strip().lower() == "true"
        for row in existing_rows
    }
    all_date_ids = set(existing_flags) | missing_date_ids
    start = min(date_id_to_date(value) for value in all_date_ids)
    end = max(date_id_to_date(value) for value in all_date_ids)
    trade_days = sorted(
        date_id for date_id, is_trade_day in existing_flags.items() if is_trade_day
    )
    trade_day_indexes = {
        date_id: position
        for position, date_id in enumerate(trade_days, start=1)
    }

    try:
        with DATE_TEMP_CSV.open("w", newline="", encoding="utf-8") as csv_file:
            writer = csv.DictWriter(
                csv_file,
                fieldnames=DATE_FIELDS,
                lineterminator="\n",
            )
            writer.writeheader()
            current = end
            while current >= start:
                date_id = date_to_date_id(current)
                is_trade_day = existing_flags.get(date_id, False)
                writer.writerow(
                    {
                        "date_id": date_id,
                        "date": current.isoformat(),
                        "year_num": current.year,
                        "quarter_num": (current.month - 1) // 3 + 1,
                        "month_num": current.month,
                        "day_week": current.isoweekday(),
                        "is_trade_day": "True" if is_trade_day else "False",
                        "trade_day_index": (
                            trade_day_indexes[date_id] if is_trade_day else ""
                        ),
                    }
                )
                current -= timedelta(days=1)
        DATE_TEMP_CSV.replace(DATE_CSV)
    except Exception:
        DATE_TEMP_CSV.unlink(missing_ok=True)
        raise

    print(
        f"Extended {DATE_CSV.name} through {end.isoformat()} "
        f"for {len(missing_date_ids)} company-action date(s)"
    )


def parse_decimal(value: object, field_name: str) -> Decimal:
    text = str(value).strip()
    if not text or text.lower() in {"nan", "none", "null"}:
        return Decimal("0.000000")

    try:
        number = Decimal(text).quantize(SCALE, rounding=ROUND_HALF_UP)
    except InvalidOperation as error:
        raise ValueError(f"{field_name} is not numeric: {value!r}") from error

    if number < 0:
        raise ValueError(f"{field_name} cannot be negative: {number}")

    return number


def parse_action_type(value: object) -> int:
    try:
        number = Decimal(str(value).strip())
    except InvalidOperation as error:
        raise ValueError(f"Type is not an integer: {value!r}") from error

    if number != number.to_integral_value():
        raise ValueError(f"Type is not an integer: {value!r}")

    action_type = int(number)
    if action_type not in VALID_ACTION_TYPES:
        raise ValueError(f"unsupported Type: {action_type}")

    return action_type


def get_dividend_data(
    stock_code: str,
    tq_messages: Counter[str],
) -> pd.DataFrame:
    last_error: Exception | None = None

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            result, messages = capture_output(
                tq.get_divid_factors,
                stock_code=stock_code,
                start_time="",
                end_time="",
            )
            tq_messages.update(messages)
            return result
        except Exception as error:
            tq_messages.update(captured_output_from_error(error))
            last_error = error
            if attempt < MAX_RETRIES:
                time.sleep(attempt)

    raise RuntimeError(
        f"get_divid_factors failed after {MAX_RETRIES} attempts"
    ) from last_error


def transform_rows(
    stock_code: str,
    frame: pd.DataFrame,
    valid_date_ids: set[int],
    missing_date_ids: set[int],
) -> list[dict[str, object]]:
    if frame is None or frame.empty:
        return []

    required_columns = {"Type", *VALUE_FIELDS.values()}
    missing_columns = required_columns.difference(frame.columns)
    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(f"missing columns: {missing}")

    rows: list[dict[str, object]] = []
    for date_value, source_row in frame.iterrows():
        ex_date = pd.to_datetime(date_value, errors="raise").date()
        ex_date_id = int(ex_date.strftime("%Y%m%d"))
        if ex_date_id not in valid_date_ids:
            missing_date_ids.add(ex_date_id)

        output_row: dict[str, object] = {
            "stock_code": stock_code,
            "date_id": ex_date_id,
            "action_type": parse_action_type(source_row["Type"]),
        }
        for output_name, source_name in VALUE_FIELDS.items():
            output_row[output_name] = format(
                parse_decimal(source_row[source_name], source_name),
                "f",
            )
        rows.append(output_row)

    return sorted(
        rows,
        key=lambda row: (int(row["date_id"]), int(row["action_type"])),
    )


def error_sample(errors: list[tuple[str, str]], limit: int = 5) -> str:
    return "; ".join(f"{stock_code}: {error}" for stock_code, error in errors[:limit])


def main() -> None:
    stock_codes = load_stock_codes()
    valid_date_ids = load_date_ids()
    missing_date_ids: set[int] = set()
    seen_keys: dict[tuple[str, int, int], tuple[str, ...]] = {}
    errors: list[tuple[str, str]] = []
    output_count = 0
    tq_messages: Counter[str] = Counter()

    print(
        "querying tqcenter dividend factors; "
        "raw tqcenter messages are summarized"
    )
    _, messages = capture_output(tq.initialize, __file__)
    tq_messages.update(messages)

    try:
        with TEMP_CSV.open("w", newline="", encoding="utf-8-sig") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=OUTPUT_FIELDS)
            writer.writeheader()

            for position, stock_code in enumerate(stock_codes, start=1):
                try:
                    source_frame = get_dividend_data(stock_code, tq_messages)
                    output_rows = transform_rows(
                        stock_code,
                        source_frame,
                        valid_date_ids,
                        missing_date_ids,
                    )

                    for row in output_rows:
                        key = (
                            str(row["stock_code"]),
                            int(row["date_id"]),
                            int(row["action_type"]),
                        )
                        values = tuple(str(row[field]) for field in OUTPUT_FIELDS)
                        previous_values = seen_keys.get(key)
                        if previous_values is not None:
                            if previous_values != values:
                                raise ValueError(
                                    f"conflicting duplicate business key: {key}"
                                )
                            continue

                        seen_keys[key] = values
                        writer.writerow(row)
                        output_count += 1
                except Exception as error:
                    errors.append((stock_code, str(error)))

                if position % 20 == 0 or position == len(stock_codes):
                    print_progress(
                        "dividend stocks",
                        position,
                        len(stock_codes),
                        f"rows={output_count} errors={len(errors)}",
                    )
    finally:
        close_method = getattr(tq, "close", None)
        if callable(close_method):
            _, messages = capture_output(close_method)
            tq_messages.update(messages)

    if errors:
        TEMP_CSV.unlink(missing_ok=True)
        report_captured_output("tqcenter_fact_dividend", tq_messages)
        append_summary(
            "fact_dividend",
            f"errors={len(errors)} sample={error_sample(errors)}",
        )
        raise RuntimeError(
            f"{len(errors)} stocks failed; sample: {error_sample(errors)}. "
            f"{OUTPUT_CSV.name} was not replaced."
        )

    extend_dim_date(missing_date_ids)
    TEMP_CSV.replace(OUTPUT_CSV)
    report_captured_output("tqcenter_fact_dividend", tq_messages)
    summary = (
        f"stocks={len(stock_codes)} rows={output_count} "
        f"missing_dates={len(missing_date_ids)} errors={len(errors)}"
    )
    print(f"dividend summary: {summary}")
    append_summary("fact_dividend", summary)


if __name__ == "__main__":
    main()
