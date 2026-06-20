from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR / "etl"))

from etl_logging import append_summary

LOG_DIR = BASE_DIR / "log"


def format_duration(seconds: float) -> str:
    if seconds < 60:
        return f"{seconds:.1f}s"
    minutes, remaining = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return f"{hours}h{minutes:02d}m{remaining:02d}s"
    return f"{minutes}m{remaining:02d}s"


def run_step(
    step_no: int,
    total_steps: int,
    label: str,
    command: list[str],
    env: dict[str, str],
) -> None:
    print("", flush=True)
    print(f"==> [{step_no}/{total_steps}] {label}", flush=True)
    start_time = time.monotonic()
    append_summary("etl", f"start step={step_no}/{total_steps} label={label}")
    try:
        subprocess.run(command, cwd=BASE_DIR, check=True, env=env)
    except subprocess.CalledProcessError as error:
        command_name = Path(command[1]).name if len(command) > 1 else command[0]
        raise SystemExit(
            f"{command_name} failed with exit code {error.returncode}"
        ) from None
    elapsed = format_duration(time.monotonic() - start_time)
    print(
        f"completed in {elapsed}",
        flush=True,
    )
    append_summary("etl", f"complete step={step_no}/{total_steps} label={label} duration={elapsed}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the full raw -> CSV -> PostgreSQL ETL pipeline."
    )
    parser.add_argument(
        "--database",
        help="Target PostgreSQL database name. Overrides .env POSTGRES_DB.",
    )
    parser.add_argument(
        "--create-db",
        action="store_true",
        help="Create target database if it does not already exist.",
    )
    parser.add_argument(
        "--allow-postgres-db",
        action="store_true",
        help="Allow loading into the default postgres database.",
    )
    parser.add_argument(
        "--skip-db",
        action="store_true",
        help="Generate CSV only; do not rebuild PostgreSQL.",
    )
    parser.add_argument(
        "--no-db-reset",
        action="store_true",
        help="Do not pass --reset to build_postgres_from_csv.py.",
    )
    parser.add_argument(
        "--skip-db-validate",
        action="store_true",
        help="Do not run validate-only after database build.",
    )

    parser.add_argument(
        "--skip-raw-download",
        action="store_true",
        help="Skip downloading and extracting TDX raw archives.",
    )
    parser.add_argument(
        "--skip-stock-info",
        action="store_true",
        help="Only sync stock codes; do not call tqcenter get_stock_info.",
    )
    parser.add_argument(
        "--skip-daily",
        action="store_true",
        help="Skip fact_daily.csv generation.",
    )
    parser.add_argument(
        "--skip-dividend",
        action="store_true",
        help="Skip fact_dividend.csv generation.",
    )
    parser.add_argument(
        "--skip-adjustment",
        action="store_true",
        help="Skip adjustment factor CSV generation.",
    )
    parser.add_argument(
        "--skip-financial",
        action="store_true",
        help="Skip financial CSV generation.",
    )
    parser.add_argument(
        "--precheck-only",
        action="store_true",
        help="Only sync dim_stock codes and dim_date, then stop.",
    )
    return parser.parse_args()


def pipeline_args(args: argparse.Namespace) -> list[str]:
    result: list[str] = []
    for flag in [
        "skip_raw_download",
        "skip_stock_info",
        "skip_daily",
        "skip_dividend",
        "skip_adjustment",
        "skip_financial",
        "precheck_only",
    ]:
        if getattr(args, flag):
            result.append("--" + flag.replace("_", "-"))
    return result


def db_args(args: argparse.Namespace) -> list[str]:
    result: list[str] = []
    if args.database:
        result.extend(["--database", args.database])
    if args.create_db:
        result.append("--create-db")
    if args.allow_postgres_db:
        result.append("--allow-postgres-db")
    return result


def main() -> int:
    args = parse_args()
    skip_db = args.skip_db or args.precheck_only
    validate_db = not args.skip_db_validate
    LOG_DIR.mkdir(exist_ok=True)
    log_path = LOG_DIR / f"etl_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    os.environ["ETL_SUMMARY_LOG"] = str(log_path)
    env = os.environ.copy()
    append_summary("etl", "run_start")
    print(f"summary log: {log_path}", flush=True)

    total_steps = 1
    if not skip_db:
        total_steps += 1
        if validate_db:
            total_steps += 1

    step_no = 1
    run_step(
        step_no,
        total_steps,
        "Download raw archives and regenerate CSV files",
        [
            sys.executable,
            str(BASE_DIR / "etl" / "update_csv_pipeline.py"),
            *pipeline_args(args),
        ],
        env,
    )
    step_no += 1

    if skip_db:
        print("", flush=True)
        print("ETL finished: CSV pipeline complete; PostgreSQL build skipped.")
        return 0

    build_args = db_args(args)
    if not args.no_db_reset:
        build_args.append("--reset")
    run_step(
        step_no,
        total_steps,
        "Build PostgreSQL database from CSV files",
        [
            sys.executable,
            str(BASE_DIR / "etl" / "build_postgres_from_csv.py"),
            *build_args,
        ],
        env,
    )
    step_no += 1

    if validate_db:
        run_step(
            step_no,
            total_steps,
            "Validate PostgreSQL database",
            [
                sys.executable,
                str(BASE_DIR / "etl" / "build_postgres_from_csv.py"),
                *db_args(args),
                "--validate-only",
            ],
            env,
        )

    print("", flush=True)
    print("Full ETL pipeline complete.")
    append_summary("etl", "run_complete")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
