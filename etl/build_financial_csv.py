import csv
import math
import re
import struct
import time
from collections import defaultdict
from datetime import datetime
from pathlib import Path

from etl_logging import append_summary
from paths import DATA_DIR, RAW_DIR, KNOWLEDGE_DIR


BASE_DIR = Path(__file__).resolve().parent
CW_DIR = RAW_DIR / "vipdoc" / "cw"
FINVALUE_CSV_PATH = KNOWLEDGE_DIR / "FINVALUE.csv"
DIM_STOCK_PATH = DATA_DIR / "dim_stock.csv"
DIM_DATE_PATH = DATA_DIR / "dim_date.csv"

METRIC_CSV = DATA_DIR / "dim_financial_metric.csv"
REPORT_CSV = DATA_DIR / "fact_financial_report.csv"
VALUE_CSV = DATA_DIR / "fact_financial_value.csv"
BRIDGE_CSV = DATA_DIR / "bridge_trade_day_financial_report.csv"

HEADER = struct.Struct("<6H2I")
INDEX_ENTRY = struct.Struct("<7sI")
FLOAT_COUNT = 584
FLOAT_BLOCK = struct.Struct(f"<{FLOAT_COUNT}f")
ANNOUNCE_DATE_FIELD = 314
PROGRESS_BAR_WIDTH = 28


def format_duration(seconds: float) -> str:
    if seconds < 60:
        return f"{seconds:.1f}s"
    minutes, remaining = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return f"{hours}h{minutes:02d}m{remaining:02d}s"
    return f"{minutes}m{remaining:02d}s"


def print_progress(
    label: str,
    current: int,
    total: int,
    detail: str = "",
) -> None:
    if total > 0:
        ratio = min(max(current / total, 0), 1)
        filled = int(PROGRESS_BAR_WIDTH * ratio)
        bar = "#" * filled + "-" * (PROGRESS_BAR_WIDTH - filled)
        text = f"\r{label} [{bar}] {current}/{total} {ratio:6.2%}"
    else:
        text = f"\r{label} {current}"
    if detail:
        text += f" {detail}"
    print(text, end="", flush=True)
    if total > 0 and current >= total:
        print(flush=True)


def load_metric_definitions() -> dict[str, str]:
    required_columns = {
        "finvalue_id",
        "metric_code",
        "record_index",
        "field_kind",
        "metric_name",
    }
    metrics: dict[str, str] = {}
    with FINVALUE_CSV_PATH.open("r", newline="", encoding="utf-8-sig") as csv_file:
        reader = csv.DictReader(csv_file)
        fieldnames = set(reader.fieldnames or [])
        missing_columns = required_columns.difference(fieldnames)
        if missing_columns:
            missing = ", ".join(sorted(missing_columns))
            raise ValueError(f"{FINVALUE_CSV_PATH.name} missing columns: {missing}")

        for line_number, row in enumerate(reader, start=2):
            if row["field_kind"].strip() != "metric":
                continue

            metric_code = row["metric_code"].strip()
            metric_name = row["metric_name"].strip()
            if not re.fullmatch(r"FN[0-9]+", metric_code):
                raise ValueError(
                    f"{FINVALUE_CSV_PATH.name}:{line_number}: "
                    f"invalid metric_code {metric_code!r}"
                )
            if not metric_name:
                raise ValueError(
                    f"{FINVALUE_CSV_PATH.name}:{line_number}: empty metric_name"
                )

            finvalue_id = int(row["finvalue_id"])
            metric_number = int(metric_code.removeprefix("FN"))
            record_index = int(row["record_index"])
            if metric_number != finvalue_id:
                raise ValueError(
                    f"{FINVALUE_CSV_PATH.name}:{line_number}: "
                    f"{metric_code} does not match finvalue_id {finvalue_id}"
                )
            if not 1 <= metric_number <= FLOAT_COUNT:
                raise ValueError(
                    f"{FINVALUE_CSV_PATH.name}:{line_number}: "
                    f"metric id {metric_number} outside 1..{FLOAT_COUNT}"
                )
            if record_index != metric_number - 1:
                raise ValueError(
                    f"{FINVALUE_CSV_PATH.name}:{line_number}: "
                    f"record_index {record_index} does not match {metric_code}"
                )
            if metric_code in metrics:
                raise ValueError(
                    f"{FINVALUE_CSV_PATH.name}:{line_number}: "
                    f"duplicate metric_code {metric_code}"
                )

            metrics[metric_code] = metric_name

    if not metrics:
        raise ValueError("no financial metric definitions found")

    return dict(
        sorted(
            metrics.items(),
            key=lambda item: int(item[0].removeprefix("FN")),
        )
    )


def load_stock_map() -> dict[str, str]:
    mapping: dict[str, str] = {}
    with DIM_STOCK_PATH.open("r", newline="", encoding="utf-8-sig") as csv_file:
        for row in csv.DictReader(csv_file):
            stock_code = row["stock_code"].strip()
            raw_code = stock_code.split(".")[0]
            if raw_code in mapping:
                raise ValueError(f"duplicate raw stock code in dim_stock: {raw_code}")
            mapping[raw_code] = stock_code
    return mapping


def load_dates() -> tuple[set[int], list[int]]:
    date_ids: set[int] = set()
    trade_days: list[int] = []
    with DIM_DATE_PATH.open("r", newline="", encoding="utf-8-sig") as csv_file:
        for row in csv.DictReader(csv_file):
            date_id = int(row["date_id"])
            date_ids.add(date_id)
            if row["is_trade_day"].strip().lower() == "true":
                trade_days.append(date_id)
    return date_ids, sorted(trade_days)


def report_period_from_path(path: Path) -> str:
    match = re.fullmatch(r"gpcw([0-9]{8})", path.stem)
    if not match:
        raise ValueError(f"invalid financial file name: {path.name}")
    return datetime.strptime(match.group(1), "%Y%m%d").strftime("%Y-%m-%d")


def announce_date_id(value: float) -> int | None:
    if not math.isfinite(value):
        return None
    numeric_value = int(round(value))
    if numeric_value <= 0:
        return None
    short_date = f"{numeric_value:06d}"
    try:
        return int(datetime.strptime(short_date, "%y%m%d").strftime("%Y%m%d"))
    except ValueError:
        return None


def iter_dat_records(path: Path):
    data = path.read_bytes()
    if len(data) <= HEADER.size:
        return

    (
        version,
        _max_field_number,
        _unknown,
        stock_count,
        _reserved_1,
        index_size,
        record_size,
        _reserved_2,
    ) = HEADER.unpack_from(data)

    if len(data) == HEADER.size and stock_count == 0:
        return
    if version != 1:
        raise ValueError(f"{path.name}: unsupported version {version}")
    if index_size != INDEX_ENTRY.size:
        raise ValueError(f"{path.name}: unexpected index size {index_size}")
    if record_size != FLOAT_BLOCK.size:
        raise ValueError(f"{path.name}: unexpected record size {record_size}")

    index_start = HEADER.size
    index_end = index_start + stock_count * index_size
    if index_end > len(data):
        raise ValueError(f"{path.name}: index exceeds file size")

    for position in range(stock_count):
        code_bytes, block_offset = INDEX_ENTRY.unpack_from(
            data,
            index_start + position * index_size,
        )
        raw_code = code_bytes.split(b"\0", 1)[0].decode("ascii")
        if block_offset + record_size > len(data):
            raise ValueError(
                f"{path.name}: block for {raw_code} exceeds file size"
            )
        values = FLOAT_BLOCK.unpack_from(data, block_offset)
        yield raw_code, values


def write_metrics(metrics: dict[str, str]) -> None:
    with METRIC_CSV.open("w", newline="", encoding="utf-8-sig") as csv_file:
        writer = csv.writer(csv_file, lineterminator="\n")
        writer.writerow(["metric_code", "metric_name"])
        writer.writerows(metrics.items())


def diagnostic_sample(rows: list[tuple[str, str, str]], limit: int = 3) -> str:
    return "; ".join(" | ".join(row) for row in rows[:limit])


def build_financial_csvs(
    metrics: dict[str, str],
    stock_map: dict[str, str],
    valid_date_ids: set[int],
) -> tuple[int, int, list[tuple[str, str, str]], dict[str, list[tuple[int, int]]]]:
    metric_indexes = [
        (code, int(code.removeprefix("FN")) - 1)
        for code in metrics
    ]
    errors: list[tuple[str, str, str]] = []
    skipped: list[tuple[str, str, str]] = []
    report_count = 0
    value_count = 0
    report_timeline: dict[str, list[tuple[int, int]]] = defaultdict(list)
    seen_reports: dict[tuple[str, str], tuple[int, int]] = {}

    with REPORT_CSV.open("w", newline="", encoding="utf-8-sig") as report_file, (
        VALUE_CSV.open("w", newline="", encoding="utf-8-sig")
    ) as value_file:
        report_writer = csv.writer(report_file, lineterminator="\n")
        value_writer = csv.writer(value_file, lineterminator="\n")
        report_writer.writerow(
            ["report_id", "stock_code", "report_period", "announce_date_id"]
        )
        value_writer.writerow(["report_id", "metric_code", "metric_value"])

        dat_paths = [
            path
            for path in sorted(CW_DIR.glob("gpcw*.dat"))
            if path.stat().st_size > HEADER.size
        ]
        start_time = time.monotonic()
        for position, path in enumerate(dat_paths, start=1):

            report_period = report_period_from_path(path)
            try:
                record_iter = iter_dat_records(path)
                if record_iter is None:
                    continue
                for raw_code, values in record_iter:
                    stock_code = stock_map.get(raw_code)
                    if stock_code is None:
                        skipped.append((path.name, raw_code, "stock_code not in dim_stock"))
                        continue

                    announcement_id = announce_date_id(values[ANNOUNCE_DATE_FIELD - 1])
                    if announcement_id is None:
                        errors.append((path.name, stock_code, "invalid announce date"))
                        continue
                    if announcement_id not in valid_date_ids:
                        errors.append(
                            (path.name, stock_code, f"announce date {announcement_id} missing from dim_date")
                        )
                        continue

                    key = (stock_code, report_period)
                    previous = seen_reports.get(key)
                    if previous is not None:
                        previous_report_id, previous_announcement_id = previous
                        if previous_announcement_id != announcement_id:
                            errors.append(
                                (
                                    path.name,
                                    stock_code,
                                    f"duplicate report period with different announce date; existing report_id={previous_report_id}",
                                )
                            )
                        continue

                    report_count += 1
                    report_id = report_count
                    seen_reports[key] = (report_id, announcement_id)
                    report_timeline[stock_code].append((announcement_id, report_id))
                    report_writer.writerow(
                        [report_id, stock_code, report_period, announcement_id]
                    )

                    for metric_code, index in metric_indexes:
                        value = values[index]
                        if not math.isfinite(value):
                            continue
                        value_writer.writerow([report_id, metric_code, f"{value:.6f}"])
                        value_count += 1
            except Exception as error:
                errors.append((path.name, "", str(error)))

            if position % 1 == 0 or position == len(dat_paths):
                print_progress(
                    "financial dat files",
                    position,
                    len(dat_paths),
                    (
                        f"reports={report_count} values={value_count} "
                        f"errors={len(errors)} skipped={len(skipped)}"
                    ),
                )

        print(
            "financial dat scan completed in "
            f"{format_duration(time.monotonic() - start_time)}"
        )

    return report_count, value_count, errors, skipped, report_timeline


def write_bridge_csv(
    report_timeline: dict[str, list[tuple[int, int]]],
    trade_days: list[int],
) -> int:
    row_count = 0
    stock_codes = sorted(report_timeline)
    start_time = time.monotonic()
    with BRIDGE_CSV.open("w", newline="", encoding="utf-8-sig") as csv_file:
        writer = csv.writer(csv_file, lineterminator="\n")
        writer.writerow(["date_id", "stock_code", "report_id"])

        for stock_position, stock_code in enumerate(stock_codes, start=1):
            timeline = sorted(
                report_timeline[stock_code],
                key=lambda item: (item[0], item[1]),
            )
            timeline_position = 0
            current_report_id: int | None = None

            for date_id in trade_days:
                while (
                    timeline_position < len(timeline)
                    and timeline[timeline_position][0] <= date_id
                ):
                    current_report_id = timeline[timeline_position][1]
                    timeline_position += 1

                if current_report_id is not None:
                    writer.writerow([date_id, stock_code, current_report_id])
                    row_count += 1

            if stock_position % 100 == 0 or stock_position == len(stock_codes):
                print_progress(
                    "financial bridge",
                    stock_position,
                    len(stock_codes),
                    f"rows={row_count}",
                )

    print(
        "financial bridge completed in "
        f"{format_duration(time.monotonic() - start_time)}"
    )

    return row_count


def main() -> None:
    metrics = load_metric_definitions()
    stock_map = load_stock_map()
    valid_date_ids, trade_days = load_dates()

    write_metrics(metrics)
    report_count, value_count, errors, skipped, report_timeline = build_financial_csvs(
        metrics,
        stock_map,
        valid_date_ids,
    )
    bridge_count = write_bridge_csv(report_timeline, trade_days)

    summary = (
        f"metrics={len(metrics)} reports={report_count} values={value_count} "
        f"bridge_rows={bridge_count} errors={len(errors)} skipped={len(skipped)}"
    )
    print(f"financial summary: {summary}")
    detail = summary
    if errors:
        detail += f" error_sample={diagnostic_sample(errors)}"
    if skipped:
        detail += f" skipped_sample={diagnostic_sample(skipped)}"
    append_summary("financial", detail)


if __name__ == "__main__":
    main()
