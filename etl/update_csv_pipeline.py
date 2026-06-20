from __future__ import annotations

import argparse
import csv
import os
import re
import shutil
import struct
import subprocess
import sys
import time
import urllib.request
import zipfile
from datetime import date, datetime, timedelta
from pathlib import Path
from pathlib import PurePosixPath

import build_financial_csv
from etl_logging import append_summary
from paths import DATA_DIR, RAW_DIR


BASE_DIR = Path(__file__).resolve().parent
VIPDOC_DIR = RAW_DIR / "vipdoc"
DIM_STOCK_CSV = DATA_DIR / "dim_stock.csv"
DIM_DATE_CSV = DATA_DIR / "dim_date.csv"
DAY_DIRECTORIES = (
    VIPDOC_DIR / "sh" / "lday",
    VIPDOC_DIR / "sz" / "lday",
)
CW_DIR = VIPDOC_DIR / "cw"

DAY_RECORD = struct.Struct("<5If2I")
STOCK_FIELDS = ["stock_code", "stock_name", "tdx_sector_code"]
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

RAW_ARCHIVES = [
    (
        "hsjday.zip",
        "https://data.tdx.com.cn/vipdoc/hsjday.zip",
        RAW_DIR / "hsjday.zip",
        VIPDOC_DIR,
        "day",
    ),
    (
        "tdxfin.zip",
        "https://data.tdx.com.cn/vipdoc/tdxfin.zip",
        RAW_DIR / "tdxfin.zip",
        CW_DIR,
        "financial",
    ),
]
PROGRESS_BAR_WIDTH = 28
CURL_EXE = shutil.which("curl.exe") or shutil.which("curl")

PIPELINE_STEPS = [
    ("stock_info", "build_dim_stock.py", "update stock and industry dimensions"),
    ("daily", "build_fact_daily.py", "build daily bars"),
    ("dividend", "build_fact_dividend.py", "build dividend actions"),
    ("adjustment", "build_adjustment_factor.py", "build adjustment factor periods"),
    ("financial", "build_financial_csv.py", "build financial tables"),
]


def format_bytes(value: int) -> str:
    units = ["B", "KB", "MB", "GB"]
    number = float(value)
    for unit in units:
        if number < 1024 or unit == units[-1]:
            return f"{number:.1f}{unit}"
        number /= 1024
    return f"{number:.1f}GB"


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


def is_zip_file(path: Path) -> bool:
    with path.open("rb") as handle:
        signature = handle.read(4)
    return signature in {b"PK\x03\x04", b"PK\x05\x06", b"PK\x07\x08"}


def response_sample(path: Path, limit: int = 300) -> str:
    data = path.read_bytes()[:limit]
    return data.decode("utf-8", errors="replace").replace("\r", " ").replace("\n", " ")


def tdx_antibot_cookie(path: Path) -> str | None:
    text = path.read_text(encoding="utf-8", errors="ignore")
    if "EO_Bot_Ssid" not in text or "__tst_status" not in text:
        return None

    ssid_match = re.search(r"t,([0-9]{6,})", text)
    if ssid_match is None:
        return None

    status_parts: list[int] = []
    for key in ("WTKkN", "bOYDu", "wyeCN"):
        match = re.search(rf"{key}:([0-9]+)", text)
        if match is None:
            return None
        status_parts.append(int(match.group(1)))

    return f"__tst_status={sum(status_parts)}#; EO_Bot_Ssid={ssid_match.group(1)}"


def download_with_curl(
    url: str,
    destination: Path,
    extra_headers: dict[str, str],
) -> None:
    command = [
        CURL_EXE,
        "--location",
        "--fail",
        "--retry",
        "8",
        "--retry-all-errors",
        "--retry-delay",
        "5",
        "--connect-timeout",
        "30",
        "--speed-time",
        "60",
        "--speed-limit",
        "1024",
        "--progress-bar",
        "--user-agent",
        "Mozilla/5.0",
        "--header",
        "Accept: application/zip,application/octet-stream,*/*",
        "--output",
        str(destination),
    ]
    for key, value in extra_headers.items():
        command.extend(["--header", f"{key}: {value}"])
    command.append(url)

    print(f"downloading {destination.name.removesuffix('.tmp')} with curl")
    subprocess.run(command, cwd=BASE_DIR, check=True)


def download_with_urllib(
    url: str,
    destination: Path,
    extra_headers: dict[str, str],
) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/zip,application/octet-stream,*/*",
            **extra_headers,
        },
    )

    with urllib.request.urlopen(request, timeout=60) as response, (
        destination.open("wb")
    ) as out:
        total = int(response.headers.get("Content-Length") or 0)
        downloaded = 0
        while True:
            chunk = response.read(1024 * 1024)
            if not chunk:
                break
            out.write(chunk)
            downloaded += len(chunk)
            if total:
                print_progress(
                    f"download {destination.name.removesuffix('.tmp')}",
                    downloaded,
                    total,
                    format_bytes(downloaded),
                )
            else:
                print(
                    f"\rdownload {destination.name.removesuffix('.tmp')} "
                    f"{format_bytes(downloaded)}",
                    end="",
                    flush=True,
                )
        if not total:
            print(flush=True)


def download_to_path(url: str, destination: Path, extra_headers: dict[str, str]) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if CURL_EXE:
        download_with_curl(url, destination, extra_headers)
        return
    download_with_urllib(url, destination, extra_headers)


def download_archive(url: str, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    temp_path = destination.with_name(destination.name + ".tmp")
    challenge_path = destination.with_name(destination.name + ".challenge")
    bad_path = destination.with_name(destination.name + ".bad")
    start_time = time.monotonic()

    try:
        challenge_path.unlink(missing_ok=True)
        temp_path.unlink(missing_ok=True)
        download_to_path(url, temp_path, {})
        if not is_zip_file(temp_path):
            cookie = tdx_antibot_cookie(temp_path)
            if cookie:
                print("received TDX anti-bot challenge; retrying with cookies")
                temp_path.replace(challenge_path)
                download_to_path(url, temp_path, {"Cookie": cookie})

        if not is_zip_file(temp_path):
            bad_path.unlink(missing_ok=True)
            temp_path.replace(bad_path)
            if destination.exists() and not is_zip_file(destination):
                destination.unlink()
            raise RuntimeError(
                f"{destination.name} download did not return a zip file; "
                f"saved response to {bad_path.name}; "
                f"sample={response_sample(bad_path)!r}"
            )

        temp_path.replace(destination)
        bad_path.unlink(missing_ok=True)
        challenge_path.unlink(missing_ok=True)
    except Exception:
        temp_path.unlink(missing_ok=True)
        challenge_path.unlink(missing_ok=True)
        raise

    elapsed = format_duration(time.monotonic() - start_time)
    print(f"downloaded {destination.name} in {elapsed}")
    append_summary("raw_download", f"{destination.name} duration={elapsed}")


def normalized_zip_member(member_name: str, archive_kind: str) -> Path | None:
    parts = [
        part
        for part in PurePosixPath(member_name).parts
        if part not in {"", "."}
    ]
    if not parts or any(part == ".." for part in parts):
        return None

    lower_parts = [part.lower() for part in parts]
    if archive_kind == "day":
        for index, part in enumerate(lower_parts):
            if part in {"sh", "sz"}:
                return Path(*parts[index:])
        return Path(*parts)

    if archive_kind == "financial":
        file_name = parts[-1]
        if file_name.lower().startswith("gpcw") and file_name.lower().endswith(".dat"):
            return Path(file_name)
        if file_name.lower().endswith(".dat"):
            return Path(file_name)
        return Path(*parts)

    raise ValueError(f"unknown archive kind: {archive_kind}")


def extract_archive(archive_path: Path, target_dir: Path, archive_kind: str) -> None:
    target_dir.mkdir(parents=True, exist_ok=True)
    target_root = target_dir.resolve()
    start_time = time.monotonic()

    with zipfile.ZipFile(archive_path) as archive:
        members: list[tuple[zipfile.ZipInfo, Path]] = []
        for info in archive.infolist():
            if info.is_dir():
                continue
            relative_path = normalized_zip_member(info.filename, archive_kind)
            if relative_path is None:
                continue
            members.append((info, relative_path))

        if not members:
            raise ValueError(f"{archive_path.name} contains no extractable files")

        for position, (info, relative_path) in enumerate(members, start=1):
            destination = target_dir / relative_path
            resolved_destination = destination.resolve()
            if (
                resolved_destination != target_root
                and target_root not in resolved_destination.parents
            ):
                raise ValueError(
                    f"refusing to extract outside target directory: {info.filename}"
                )

            destination.parent.mkdir(parents=True, exist_ok=True)
            temp_destination = destination.with_name(destination.name + ".tmp")
            with archive.open(info) as source, temp_destination.open("wb") as out:
                shutil.copyfileobj(source, out)
            temp_destination.replace(destination)

            if position % 100 == 0 or position == len(members):
                print_progress(
                    f"extract {archive_path.name}",
                    position,
                    len(members),
                )

    elapsed = format_duration(time.monotonic() - start_time)
    print(f"extracted {archive_path.name} -> {target_dir} in {elapsed}")
    append_summary(
        "raw_extract",
        f"{archive_path.name} files={len(members)} target={target_dir} duration={elapsed}",
    )


def update_raw_archives() -> None:
    for position, (name, url, archive_path, target_dir, archive_kind) in enumerate(
        RAW_ARCHIVES,
        start=1,
    ):
        print(f"[raw {position}/{len(RAW_ARCHIVES)}] {name}")
        download_archive(url, archive_path)
        extract_archive(archive_path, target_dir, archive_kind)


def stock_code_from_day_path(day_path: Path) -> str | None:
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


def iter_day_files() -> list[tuple[str, Path]]:
    files: list[tuple[str, Path]] = []
    seen: set[str] = set()
    ignored: list[str] = []
    for directory in DAY_DIRECTORIES:
        if not directory.exists():
            raise FileNotFoundError(directory)
        for day_path in directory.glob("*.day"):
            stock_code = stock_code_from_day_path(day_path)
            if stock_code is None:
                ignored.append(day_path.name)
                continue
            if stock_code in seen:
                raise ValueError(f"duplicate .day file for {stock_code}")
            if day_path.stat().st_size % DAY_RECORD.size != 0:
                raise ValueError(
                    f"{day_path.name} size is not divisible by {DAY_RECORD.size}"
                )
            seen.add(stock_code)
            files.append((stock_code, day_path))
    if not files:
        raise ValueError("no .day files found under raw/vipdoc/*/lday")
    if ignored:
        sample = ", ".join(ignored[:10])
        print(
            f"ignored {len(ignored)} non-target day files; sample: {sample}"
        )
    return sorted(files)


def read_dim_stock() -> dict[str, dict[str, str]]:
    if not DIM_STOCK_CSV.exists():
        return {}
    with DIM_STOCK_CSV.open("r", newline="", encoding="utf-8-sig") as csv_file:
        reader = csv.DictReader(csv_file)
        rows: dict[str, dict[str, str]] = {}
        for row in reader:
            stock_code = row.get("stock_code", "").strip()
            if not stock_code:
                continue
            rows[stock_code] = {
                "stock_code": stock_code,
                "stock_name": row.get(
                    "stock_name",
                    row.get("name", row.get("Name", "")),
                ).strip(),
                "tdx_sector_code": row.get("tdx_sector_code", "").strip(),
            }
        return rows


def write_dim_stock(rows: list[dict[str, str]]) -> None:
    temp_path = DIM_STOCK_CSV.with_suffix(".csv.tmp")
    try:
        with temp_path.open("w", newline="", encoding="utf-8") as csv_file:
            writer = csv.DictWriter(
                csv_file,
                fieldnames=STOCK_FIELDS,
                lineterminator="\n",
            )
            writer.writeheader()
            writer.writerows(rows)
        temp_path.replace(DIM_STOCK_CSV)
    except Exception:
        temp_path.unlink(missing_ok=True)
        raise


def sync_dim_stock_codes(day_files: list[tuple[str, Path]]) -> None:
    existing = read_dim_stock()
    day_codes = [stock_code for stock_code, _ in day_files]
    rows = [
        existing.get(
            stock_code,
            {
                "stock_code": stock_code,
                "stock_name": "",
                "tdx_sector_code": "",
            },
        )
        for stock_code in day_codes
    ]
    write_dim_stock(rows)

    existing_codes = set(existing)
    day_code_set = set(day_codes)
    added = len(day_code_set - existing_codes)
    removed = len(existing_codes - day_code_set)
    print(
        f"synced dim_stock codes: total={len(rows)}, "
        f"added={added}, removed={removed}"
    )
    append_summary(
        "dim_stock_sync",
        f"total={len(rows)} added={added} removed={removed}",
    )


def read_dim_date() -> tuple[dict[int, bool], set[int]]:
    if not DIM_DATE_CSV.exists():
        return {}, set()
    existing_flags: dict[int, bool] = {}
    existing_true_trade_days: set[int] = set()
    with DIM_DATE_CSV.open("r", newline="", encoding="utf-8-sig") as csv_file:
        for row in csv.DictReader(csv_file):
            date_id = int(row["date_id"])
            is_trade_day = row["is_trade_day"].strip().lower() == "true"
            existing_flags[date_id] = is_trade_day
            if is_trade_day:
                existing_true_trade_days.add(date_id)
    return existing_flags, existing_true_trade_days


def collect_bar_dates(day_files: list[tuple[str, Path]]) -> set[int]:
    dates: set[int] = set()
    for position, (_, day_path) in enumerate(day_files, start=1):
        data = day_path.read_bytes()
        dates.update(record[0] for record in DAY_RECORD.iter_unpack(data))
        if position % 100 == 0 or position == len(day_files):
            print_progress("scan day files", position, len(day_files))
    if not dates:
        raise ValueError("no bar dates found in .day files")
    return dates


def raw_stock_map(stock_codes: set[str]) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for stock_code in stock_codes:
        raw_code = stock_code.split(".", 1)[0]
        if raw_code in mapping:
            raise ValueError(
                f"duplicate raw stock code {raw_code}: "
                f"{mapping[raw_code]} and {stock_code}"
            )
        mapping[raw_code] = stock_code
    return mapping


def collect_financial_announce_dates(stock_codes: set[str]) -> set[int]:
    mapping = raw_stock_map(stock_codes)
    dates: set[int] = set()
    if not CW_DIR.exists():
        return dates

    dat_paths = sorted(CW_DIR.glob("gpcw*.dat"))
    for position, dat_path in enumerate(dat_paths, start=1):
        if dat_path.stat().st_size <= build_financial_csv.HEADER.size:
            continue
        record_iter = build_financial_csv.iter_dat_records(dat_path)
        if record_iter is None:
            continue
        for raw_code, values in record_iter:
            if raw_code not in mapping:
                continue
            announce_id = build_financial_csv.announce_date_id(
                values[build_financial_csv.ANNOUNCE_DATE_FIELD - 1]
            )
            if announce_id is not None:
                dates.add(announce_id)
        if position % 5 == 0 or position == len(dat_paths):
            print_progress("scan financial dates", position, len(dat_paths))
    return dates


def date_id_to_date(date_id: int) -> date:
    return datetime.strptime(str(date_id), "%Y%m%d").date()


def date_to_date_id(value: date) -> int:
    return int(value.strftime("%Y%m%d"))


def write_dim_date(all_dates: set[int], trade_days: set[int]) -> None:
    if not all_dates:
        raise ValueError("cannot build dim_date without dates")
    start = min(date_id_to_date(value) for value in all_dates)
    end = max(date_id_to_date(value) for value in all_dates)
    temp_path = DIM_DATE_CSV.with_suffix(".csv.tmp")
    trade_day_indexes = {
        date_id: position
        for position, date_id in enumerate(sorted(trade_days), start=1)
    }

    try:
        with temp_path.open("w", newline="", encoding="utf-8") as csv_file:
            writer = csv.DictWriter(
                csv_file,
                fieldnames=DATE_FIELDS,
                lineterminator="\n",
            )
            writer.writeheader()
            current = end
            while current >= start:
                date_id = date_to_date_id(current)
                writer.writerow(
                    {
                        "date_id": date_id,
                        "date": current.isoformat(),
                        "year_num": current.year,
                        "quarter_num": (current.month - 1) // 3 + 1,
                        "month_num": current.month,
                        "day_week": current.isoweekday(),
                        "is_trade_day": "True" if date_id in trade_days else "False",
                        "trade_day_index": trade_day_indexes.get(date_id, ""),
                    }
                )
                current -= timedelta(days=1)
        temp_path.replace(DIM_DATE_CSV)
    except Exception:
        temp_path.unlink(missing_ok=True)
        raise


def sync_dim_date(day_files: list[tuple[str, Path]]) -> None:
    existing_flags, existing_trade_days = read_dim_date()
    bar_dates = collect_bar_dates(day_files)
    stock_codes = {stock_code for stock_code, _ in day_files}
    financial_announce_dates = collect_financial_announce_dates(stock_codes)
    all_dates = set(existing_flags) | bar_dates | financial_announce_dates
    trade_days = existing_trade_days | bar_dates

    write_dim_date(all_dates, trade_days)
    print(
        "synced dim_date: "
        f"range={min(all_dates)}..{max(all_dates)}, "
        f"natural_days={(date_id_to_date(max(all_dates)) - date_id_to_date(min(all_dates))).days + 1}, "
        f"trade_days={len(trade_days)}, "
        f"financial_announce_dates={len(financial_announce_dates)}"
    )
    append_summary(
        "dim_date_sync",
        f"range={min(all_dates)}..{max(all_dates)} "
        f"natural_days={(date_id_to_date(max(all_dates)) - date_id_to_date(min(all_dates))).days + 1} "
        f"trade_days={len(trade_days)} "
        f"financial_announce_dates={len(financial_announce_dates)}",
    )


def run_step(
    script_name: str,
    step_position: int,
    step_total: int,
    label: str,
) -> None:
    env = os.environ.copy()
    env.setdefault("TQDM_DISABLE", "1")
    command = [sys.executable, str(BASE_DIR / script_name)]
    start_time = time.monotonic()
    print(f"[csv {step_position}/{step_total}] {label}", flush=True)
    try:
        subprocess.run(command, cwd=BASE_DIR, env=env, check=True)
    except subprocess.CalledProcessError as error:
        raise SystemExit(
            f"{script_name} failed with exit code {error.returncode}"
        ) from None
    elapsed = format_duration(time.monotonic() - start_time)
    print(f"completed {script_name} in {elapsed}", flush=True)
    append_summary("csv_step", f"{script_name} duration={elapsed}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Regenerate project CSV files from updated TDX raw files."
    )
    parser.add_argument(
        "--skip-stock-info",
        action="store_true",
        help="Only sync stock codes; do not call tqcenter get_stock_info.",
    )
    parser.add_argument(
        "--skip-dividend",
        action="store_true",
        help="Skip fact_dividend.csv generation.",
    )
    parser.add_argument(
        "--skip-daily",
        action="store_true",
        help="Skip fact_daily.csv generation.",
    )
    parser.add_argument(
        "--skip-financial",
        action="store_true",
        help="Skip financial CSV generation.",
    )
    parser.add_argument(
        "--skip-adjustment",
        action="store_true",
        help="Skip adjustment factor CSV generation.",
    )
    parser.add_argument(
        "--skip-raw-download",
        action="store_true",
        help="Skip downloading and extracting TDX raw archives.",
    )
    parser.add_argument(
        "--precheck-only",
        action="store_true",
        help="Only sync dim_stock codes and dim_date, then stop.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if args.skip_raw_download:
        print("skipping raw archive download")
    else:
        update_raw_archives()

    day_files = iter_day_files()
    sync_dim_stock_codes(day_files)
    sync_dim_date(day_files)

    if args.precheck_only:
        print("precheck complete")
        return 0

    runnable_steps = [
        (step_name, script_name, label)
        for step_name, script_name, label in PIPELINE_STEPS
        if not (
            (step_name == "stock_info" and args.skip_stock_info)
            or (step_name == "daily" and args.skip_daily)
            or (step_name == "dividend" and args.skip_dividend)
            or (step_name == "adjustment" and args.skip_adjustment)
            or (step_name == "financial" and args.skip_financial)
        )
    ]

    skipped_steps = len(PIPELINE_STEPS) - len(runnable_steps)
    if skipped_steps:
        print(f"skipping {skipped_steps} CSV step(s)")

    for position, (step_name, script_name, label) in enumerate(
        runnable_steps,
        start=1,
    ):
        if step_name == "stock_info" and args.skip_stock_info:
            print("skipping stock info update")
            continue
        if step_name == "daily" and args.skip_daily:
            print("skipping daily CSV generation")
            continue
        if step_name == "dividend" and args.skip_dividend:
            print("skipping dividend CSV generation")
            continue
        if step_name == "adjustment" and args.skip_adjustment:
            print("skipping adjustment factor CSV generation")
            continue
        if step_name == "financial" and args.skip_financial:
            print("skipping financial CSV generation")
            continue
        run_step(script_name, position, len(runnable_steps), label)

    print("CSV update pipeline complete")
    append_summary("csv_pipeline", "complete")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
