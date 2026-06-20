from __future__ import annotations

import bisect
import csv
from collections import defaultdict
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP, getcontext
from pathlib import Path

from etl_logging import append_summary, print_progress
from paths import DATA_DIR


getcontext().prec = 50

BASE_DIR = Path(__file__).resolve().parent
STOCK_CSV = DATA_DIR / "dim_stock.csv"
DAILY_CSV = DATA_DIR / "fact_daily.csv"
DIVIDEND_CSV = DATA_DIR / "fact_dividend.csv"
OUTPUT_CSV = DATA_DIR / "fact_adjustment_factor_period.csv"
TEMP_CSV = DATA_DIR / "fact_adjustment_factor_period.csv.tmp"

FACTOR_SCALE = Decimal("0.000000000001")
TEN = Decimal("10")
ONE = Decimal("1")


@dataclass(frozen=True)
class DividendEvent:
    date_id: int
    action_type: int
    bonus: Decimal
    allot_price: Decimal
    share_bonus: Decimal
    allotment: Decimal


@dataclass(frozen=True)
class DailyRow:
    date_id: int
    stock_code: str
    close: Decimal


@dataclass
class EffectiveEvent:
    source_date_id: int
    effective_date_id: int
    action_type: int
    cash: Decimal
    share: Decimal
    rights: Decimal
    rights_cost: Decimal


def parse_decimal(value: str) -> Decimal:
    text = value.strip()
    if not text:
        return Decimal("0")
    return Decimal(text)


def load_dividend_events() -> dict[str, list[DividendEvent]]:
    events: dict[str, list[DividendEvent]] = defaultdict(list)
    with DIVIDEND_CSV.open("r", newline="", encoding="utf-8-sig") as csv_file:
        for row in csv.DictReader(csv_file):
            event = DividendEvent(
                date_id=int(row["date_id"]),
                action_type=int(row["action_type"]),
                bonus=parse_decimal(row["bonus"]),
                allot_price=parse_decimal(row["allot_price"]),
                share_bonus=parse_decimal(row["share_bonus"]),
                allotment=parse_decimal(row["allotment"]),
            )
            events[row["stock_code"]].append(event)

    for stock_events in events.values():
        stock_events.sort(key=lambda item: (item.date_id, item.action_type))
    return events


def load_stock_count() -> int:
    with STOCK_CSV.open("r", newline="", encoding="utf-8-sig") as csv_file:
        return sum(
            1
            for row in csv.DictReader(csv_file)
            if row.get("stock_code", "").strip()
        )


def diagnostic_sample(rows: list[tuple[object, ...]], limit: int = 5) -> str:
    return "; ".join(", ".join(str(value) for value in row) for row in rows[:limit])


def build_effective_q_by_position(
    stock_code: str,
    daily_rows: list[DailyRow],
    dividends: list[DividendEvent],
    skipped: list[tuple[object, ...]],
    errors: list[tuple[object, ...]],
) -> dict[int, Decimal]:
    if not dividends:
        return {}

    dates = [row.date_id for row in daily_rows]
    closes = [row.close for row in daily_rows]
    grouped: dict[int, list[EffectiveEvent]] = defaultdict(list)

    for event in dividends:
        position = bisect.bisect_left(dates, event.date_id)
        if position >= len(dates):
            skipped.append(
                (
                    stock_code,
                    event.date_id,
                    event.action_type,
                    "no trading day on or after action date",
                )
            )
            continue
        if position == 0:
            skipped.append(
                (
                    stock_code,
                    event.date_id,
                    event.action_type,
                    "no previous close before effective trading day",
                )
            )
            continue

        grouped[position].append(
            EffectiveEvent(
                source_date_id=event.date_id,
                effective_date_id=dates[position],
                action_type=event.action_type,
                cash=event.bonus / TEN,
                share=event.share_bonus / TEN,
                rights=event.allotment / TEN,
                rights_cost=event.allot_price * (event.allotment / TEN),
            )
        )

    q_by_position: dict[int, Decimal] = {}
    for position, events in grouped.items():
        previous_close = closes[position - 1]
        if previous_close <= 0:
            errors.append(
                (
                    stock_code,
                    dates[position],
                    "previous close is not positive",
                    str(previous_close),
                )
            )
            continue

        ordered_events = sorted(
            events, key=lambda item: (item.source_date_id, item.action_type)
        )
        reference_price = previous_close
        q = ONE
        invalid = False
        for event in ordered_events:
            denominator = reference_price * (ONE + event.share + event.rights)
            if denominator <= 0:
                errors.append(
                    (
                        stock_code,
                        dates[position],
                        "non-positive adjustment denominator",
                        f"denominator={denominator}; source_date={event.source_date_id}; "
                        f"action_type={event.action_type}",
                    )
                )
                invalid = True
                break

            q_event = (reference_price - event.cash + event.rights_cost) / denominator
            if q_event <= 0:
                errors.append(
                    (
                        stock_code,
                        dates[position],
                        "non-positive adjustment ratio",
                        f"q={q_event}; source_date={event.source_date_id}; "
                        f"action_type={event.action_type}",
                    )
                )
                invalid = True
                break

            q *= q_event
            reference_price *= q_event

        if invalid:
            continue
        q_by_position[position] = q

    return q_by_position


def format_factor(value: Decimal) -> str:
    return format(value.quantize(FACTOR_SCALE, rounding=ROUND_HALF_UP), "f")


def write_stock_factor_periods(
    writer: csv.writer,
    stock_code: str,
    daily_rows: list[DailyRow],
    dividends: list[DividendEvent],
    skipped: list[tuple[object, ...]],
    errors: list[tuple[object, ...]],
) -> int:
    q_by_position = build_effective_q_by_position(
        stock_code,
        daily_rows,
        dividends,
        skipped,
        errors,
    )
    row_count = len(daily_rows)
    adjust_factors = [ONE] * row_count

    current = ONE
    for position in range(row_count):
        q = q_by_position.get(position)
        if q is not None:
            current *= ONE / q
        adjust_factors[position] = current

    period_start_date_id: int | None = None
    period_end_date_id: int | None = None
    period_adjust_factor: str | None = None
    period_count = 0

    for row, adjust_factor in zip(
        daily_rows,
        adjust_factors,
    ):
        adjust_factor_text = format_factor(adjust_factor)

        if period_start_date_id is None:
            period_start_date_id = row.date_id
            period_adjust_factor = adjust_factor_text
        elif adjust_factor_text != period_adjust_factor:
            writer.writerow(
                [
                    stock_code,
                    period_start_date_id,
                    period_end_date_id,
                    period_adjust_factor,
                ]
            )
            period_count += 1
            period_start_date_id = row.date_id
            period_adjust_factor = adjust_factor_text

        period_end_date_id = row.date_id

    if period_start_date_id is not None:
        writer.writerow(
            [
                stock_code,
                period_start_date_id,
                period_end_date_id,
                period_adjust_factor,
            ]
        )
        period_count += 1

    return period_count


def main() -> None:
    dividends_by_stock = load_dividend_events()
    total_stocks = load_stock_count()
    skipped: list[tuple[object, ...]] = []
    errors: list[tuple[object, ...]] = []
    output_periods = 0
    covered_daily_rows = 0
    processed_stocks = 0

    try:
        with DAILY_CSV.open("r", newline="", encoding="utf-8-sig") as daily_file, (
            TEMP_CSV.open("w", newline="", encoding="utf-8")
        ) as output_file:
            reader = csv.DictReader(daily_file)
            writer = csv.writer(output_file, lineterminator="\n")
            writer.writerow(
                [
                    "stock_code",
                    "valid_from_date_id",
                    "valid_to_date_id",
                    "adjust_factor",
                ]
            )

            current_stock: str | None = None
            stock_rows: list[DailyRow] = []
            processed_stock_codes: set[str] = set()

            def flush_stock() -> None:
                nonlocal output_periods
                nonlocal covered_daily_rows
                nonlocal processed_stocks
                nonlocal stock_rows
                nonlocal current_stock
                if current_stock is None:
                    return
                processed_stock_codes.add(current_stock)
                output_periods += write_stock_factor_periods(
                    writer,
                    current_stock,
                    stock_rows,
                    dividends_by_stock.get(current_stock, []),
                    skipped,
                    errors,
                )
                covered_daily_rows += len(stock_rows)
                processed_stocks += 1
                if processed_stocks % 50 == 0:
                    print_progress(
                        "adjustment stocks",
                        processed_stocks,
                        total_stocks,
                        (
                            f"periods={output_periods} daily_rows={covered_daily_rows} "
                            f"skipped={len(skipped)} errors={len(errors)}"
                        ),
                    )
                stock_rows = []

            for row in reader:
                stock_code = row["stock_code"]
                if current_stock is not None and stock_code != current_stock:
                    flush_stock()
                    if stock_code in processed_stock_codes:
                        raise ValueError(
                            f"{DAILY_CSV.name} must be grouped by stock_code; "
                            f"{stock_code} appeared again after another stock"
                        )
                current_stock = stock_code
                date_id = int(row["date_id"])
                if stock_rows and date_id <= stock_rows[-1].date_id:
                    raise ValueError(
                        f"{DAILY_CSV.name} dates must be strictly increasing within "
                        f"{stock_code}; got {date_id} after {stock_rows[-1].date_id}"
                    )
                stock_rows.append(
                    DailyRow(
                        date_id=date_id,
                        stock_code=stock_code,
                        close=parse_decimal(row["close"]),
                    )
                )

            flush_stock()
            print_progress(
                "adjustment stocks",
                processed_stocks,
                total_stocks,
                (
                    f"periods={output_periods} daily_rows={covered_daily_rows} "
                    f"skipped={len(skipped)} errors={len(errors)}"
                ),
            )
    except Exception:
        TEMP_CSV.unlink(missing_ok=True)
        raise

    if errors:
        TEMP_CSV.unlink(missing_ok=True)
        append_summary(
            "fact_adjustment_factor_period",
            f"errors={len(errors)} sample={diagnostic_sample(errors)}",
        )
        raise RuntimeError(
            f"{len(errors)} adjustment factor errors; "
            f"sample: {diagnostic_sample(errors)}. "
            f"{OUTPUT_CSV.name} was not replaced."
        )

    TEMP_CSV.replace(OUTPUT_CSV)
    summary = (
        f"stocks={processed_stocks} periods={output_periods} "
        f"covered_daily_rows={covered_daily_rows} "
        f"skipped_events={len(skipped)} errors={len(errors)}"
    )
    print(f"adjustment factor period summary: {summary}")
    append_summary("fact_adjustment_factor_period", summary)


if __name__ == "__main__":
    main()
