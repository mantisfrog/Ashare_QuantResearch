"""CSV partitioning + manifest helpers for the factor library.

Keeps factor outputs as long-format CSVs split by year, with idempotent
"upsert by date_id" semantics so re-running a month overwrites cleanly. Also
appends one row per build to the shared manifest.
"""
from __future__ import annotations

import csv
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd

_ETL_DIR = Path(__file__).resolve().parents[1] / "etl"
if str(_ETL_DIR) not in sys.path:
    sys.path.insert(0, str(_ETL_DIR))

from paths import FACTOR_MANIFEST_DIR

MANIFEST_COLUMNS = [
    "run_id", "calc_version", "layer", "factor_code",
    "start_date_id", "end_date_id", "row_count", "valid_count",
    "coverage", "status", "created_at",
]


def year_of(date_id: int) -> int:
    return int(date_id) // 10000


def write_year_partitioned_csv(
    df: pd.DataFrame,
    directory: Path,
    prefix: str,
    subdir: str | None = None,
    sort_cols: tuple[str, ...] = ("date_id", "stock_code"),
) -> list[Path]:
    """Write ``df`` to ``<directory>/[subdir/]<prefix>_<year>.csv`` per year.

    For each year touched by ``df``, existing rows whose ``date_id`` is present
    in ``df`` are dropped before appending, so re-computing a month is
    idempotent. Returns the list of files written.
    """
    out_dir = Path(directory) if subdir is None else Path(directory) / subdir
    out_dir.mkdir(parents=True, exist_ok=True)

    order = [column for column in sort_cols if column in df.columns]
    work = df.copy()
    work["__year"] = work["date_id"].astype(int) // 10000
    written: list[Path] = []
    for year, chunk in work.groupby("__year"):
        chunk = chunk.drop(columns="__year")
        path = out_dir / f"{prefix}_{year}.csv"
        new_dates = {int(value) for value in chunk["date_id"].unique()}
        if path.exists():
            existing = pd.read_csv(path)
            columns = list(existing.columns)
            existing = existing[~existing["date_id"].isin(new_dates)]
            combined = pd.concat(
                [existing, chunk.reindex(columns=columns)], ignore_index=True
            )
        else:
            combined = chunk
        if order:
            combined = combined.sort_values(order)
        combined = combined.reset_index(drop=True)
        combined.to_csv(path, index=False)
        written.append(path)
    return written


def read_year_partitioned_csv(
    directory: Path,
    prefix: str,
    subdir: str | None = None,
    date_ids=None,
    usecols=None,
) -> pd.DataFrame:
    """Read and concatenate ``<prefix>_*.csv`` files, optionally filtered by date."""
    out_dir = Path(directory) if subdir is None else Path(directory) / subdir
    if not out_dir.exists():
        return pd.DataFrame()
    wanted = {int(value) for value in date_ids} if date_ids is not None else None
    frames: list[pd.DataFrame] = []
    for path in sorted(out_dir.glob(f"{prefix}_*.csv")):
        frame = pd.read_csv(path, usecols=usecols)
        if wanted is not None and "date_id" in frame.columns:
            frame = frame[frame["date_id"].isin(wanted)]
        if not frame.empty:
            frames.append(frame)
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


def done_date_ids(directory: Path, prefix: str, subdir: str | None = None) -> set[int]:
    """Union of ``date_id`` values already present in matching per-year CSVs."""
    out_dir = Path(directory) if subdir is None else Path(directory) / subdir
    if not out_dir.exists():
        return set()
    ids: set[int] = set()
    for path in sorted(out_dir.glob(f"{prefix}_*.csv")):
        try:
            values = pd.read_csv(path, usecols=["date_id"])["date_id"].unique()
        except (ValueError, KeyError):
            continue
        ids |= {int(value) for value in values}
    return ids


def append_manifest(**fields: object) -> None:
    """Append one build record to ``factor_build_manifest.csv``."""
    FACTOR_MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
    path = FACTOR_MANIFEST_DIR / "factor_build_manifest.csv"
    record = {column: fields.get(column, "") for column in MANIFEST_COLUMNS}
    if not record["created_at"]:
        record["created_at"] = datetime.now().isoformat(timespec="seconds")
    write_header = not path.exists()
    with path.open("a", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=MANIFEST_COLUMNS)
        if write_header:
            writer.writeheader()
        writer.writerow(record)
