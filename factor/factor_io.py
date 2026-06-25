"""CSV partitioning + manifest helpers for the factor library.

Keeps factor outputs as long-format CSVs split by year, with idempotent
"upsert by month" semantics so a moving latest-month rebalance date overwrites
the earlier same-month snapshot cleanly. Also appends one row per build to the
shared manifest.
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

    For each year touched by ``df``, existing rows whose ``date_id`` is in the
    same YYYYMM month as any new row are dropped before appending. If
    ``calc_version`` is present on both old and new rows, replacement is scoped
    to the new versions. This keeps partially updated latest-month snapshots
    from leaving stale earlier rebalance dates in monthly factor outputs.
    Returns the list of files written.
    """
    out_dir = Path(directory) if subdir is None else Path(directory) / subdir
    out_dir.mkdir(parents=True, exist_ok=True)

    order = [column for column in sort_cols if column in df.columns]
    work = df.copy()
    work["__year"] = work["date_id"].astype(int) // 10000
    output_columns = [column for column in work.columns if column != "__year"]
    written: list[Path] = []
    for year, chunk in work.groupby("__year"):
        chunk = chunk.drop(columns="__year")
        path = out_dir / f"{prefix}_{year}.csv"
        new_months = {int(value) // 100 for value in chunk["date_id"].unique()}
        if path.exists():
            existing = pd.read_csv(path)
            existing_months = pd.to_numeric(existing["date_id"], errors="coerce") // 100
            replace_mask = existing_months.isin(new_months)
            if "calc_version" in existing.columns and "calc_version" in chunk.columns:
                new_versions = {str(value) for value in chunk["calc_version"].dropna().unique()}
                replace_mask &= existing["calc_version"].astype(str).isin(new_versions)
            existing = existing[~replace_mask]
            combined = pd.concat(
                [
                    existing.reindex(columns=output_columns),
                    chunk.reindex(columns=output_columns),
                ],
                ignore_index=True,
            )
        else:
            combined = chunk.reindex(columns=output_columns)
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
    calc_version: str | None = None,
) -> pd.DataFrame:
    """Read and concatenate ``<prefix>_*.csv`` files, optionally filtered by date."""
    out_dir = Path(directory) if subdir is None else Path(directory) / subdir
    if not out_dir.exists():
        return pd.DataFrame()
    wanted = {int(value) for value in date_ids} if date_ids is not None else None
    requested_usecols = list(usecols) if usecols is not None else None
    read_usecols = requested_usecols
    if calc_version is not None and read_usecols is not None and "calc_version" not in read_usecols:
        read_usecols = [*read_usecols, "calc_version"]
    frames: list[pd.DataFrame] = []
    for path in sorted(out_dir.glob(f"{prefix}_*.csv")):
        try:
            frame = pd.read_csv(path, usecols=read_usecols)
        except ValueError:
            if calc_version is not None:
                continue
            raise
        if wanted is not None and "date_id" in frame.columns:
            frame = frame[frame["date_id"].isin(wanted)]
        if calc_version is not None:
            if "calc_version" not in frame.columns:
                continue
            frame = frame[frame["calc_version"].astype(str) == str(calc_version)]
            if requested_usecols is not None and "calc_version" not in requested_usecols:
                frame = frame.drop(columns=["calc_version"])
        if not frame.empty:
            frames.append(frame)
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


def done_date_ids(
    directory: Path,
    prefix: str,
    subdir: str | None = None,
    calc_version: str | None = None,
) -> set[int]:
    """Union of ``date_id`` values already present in matching per-year CSVs."""
    out_dir = Path(directory) if subdir is None else Path(directory) / subdir
    if not out_dir.exists():
        return set()
    ids: set[int] = set()
    for path in sorted(out_dir.glob(f"{prefix}_*.csv")):
        try:
            usecols = ["date_id", "calc_version"] if calc_version is not None else ["date_id"]
            frame = pd.read_csv(path, usecols=usecols)
        except (ValueError, KeyError):
            continue
        if calc_version is not None:
            if "calc_version" not in frame.columns:
                continue
            frame = frame[frame["calc_version"].astype(str) == str(calc_version)]
        values = frame["date_id"].unique()
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
