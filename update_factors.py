"""Entry point for the monthly factor library.

Mirrors update_etl.py: runs each stage as a subprocess step with timing and
summary logging. Stages: universe -> raw -> exposure -> composite ->
diagnostics -> (optional) PostgreSQL load.

Examples
--------
    python update_factors.py --skip-db                 # CSV only
    python update_factors.py --start 201501 --end 202506
    python update_factors.py --start 201501 --end 202506 --rebuild
"""
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
sys.path.insert(0, str(BASE_DIR / "factor"))

from etl_logging import append_summary
from factor_config import factor_config_snapshot_lines

LOG_DIR = BASE_DIR / "log"
FACTOR_DIR = BASE_DIR / "factor"


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
    append_summary("factor", f"start step={step_no}/{total_steps} label={label}")
    try:
        subprocess.run(command, cwd=BASE_DIR, check=True, env=env)
    except subprocess.CalledProcessError as error:
        command_name = Path(command[1]).name if len(command) > 1 else command[0]
        raise SystemExit(
            f"{command_name} failed with exit code {error.returncode}"
        ) from None
    elapsed = format_duration(time.monotonic() - start_time)
    print(f"completed in {elapsed}", flush=True)
    append_summary(
        "factor",
        f"complete step={step_no}/{total_steps} label={label} duration={elapsed}",
    )


def append_config_snapshot() -> None:
    append_summary(
        "factor_config",
        "current config\n" + "\n".join(factor_config_snapshot_lines()),
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build the monthly factor library "
        "(universe -> raw -> exposure -> composite -> diagnostics -> PostgreSQL)."
    )
    parser.add_argument("--start", default="201501", help="First rebalance month YYYYMM.")
    parser.add_argument("--end", default="latest", help="Last rebalance month YYYYMM or 'latest'.")
    parser.add_argument("--factors", default="all", help="Comma-separated factor_code list, or 'all'.")
    parser.add_argument("--calc-version", default="v1", help="calc_version stamp on outputs.")
    parser.add_argument("--rebuild", action="store_true", help="Recompute all months instead of incremental.")
    parser.add_argument("--skip-db", action="store_true", help="Generate CSV only; do not load PostgreSQL.")
    parser.add_argument("--database", help="Target PostgreSQL database for the load step.")
    return parser.parse_args()


def step_args(args: argparse.Namespace) -> list[str]:
    result = [
        "--start", args.start,
        "--end", args.end,
        "--factors", args.factors,
        "--calc-version", args.calc_version,
    ]
    if args.rebuild:
        result.append("--rebuild")
    return result


def main() -> int:
    args = parse_args()
    if args.factors != "all":
        raise SystemExit(
            "--factors is only supported on individual factor build scripts. "
            "The full update_factors.py pipeline builds composite/diagnostics "
            "and requires --factors all."
        )
    LOG_DIR.mkdir(exist_ok=True)
    log_path = LOG_DIR / f"factor_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    os.environ["ETL_SUMMARY_LOG"] = str(log_path)
    env = os.environ.copy()
    append_summary("factor", "run_start")
    append_config_snapshot()
    print(f"summary log: {log_path}", flush=True)

    steps = [
        ("Build monthly stock universe", "build_universe.py"),
        ("Build raw factor values", "build_factor_raw.py"),
        ("Build factor exposures", "build_factor_exposure.py"),
        ("Build composite style scores", "build_factor_composite.py"),
        ("Build factor diagnostics", "build_factor_diagnostics.py"),
    ]
    total_steps = len(steps) + (0 if args.skip_db else 1)

    for index, (label, script) in enumerate(steps, start=1):
        run_step(
            index,
            total_steps,
            label,
            [sys.executable, str(FACTOR_DIR / script), *step_args(args)],
            env,
        )

    if args.skip_db:
        print("", flush=True)
        print("Factor build finished: CSV outputs complete; PostgreSQL load skipped.")
        return 0

    db_command = [sys.executable, str(FACTOR_DIR / "build_factor_postgres.py")]
    if args.database:
        db_command.extend(["--database", args.database])
    run_step(len(steps) + 1, total_steps, "Load factor tables into PostgreSQL", db_command, env)

    print("", flush=True)
    print("Factor build complete.")
    append_summary("factor", "run_complete")
    return 0


if __name__ == "__main__":
    sys.exit(main())
