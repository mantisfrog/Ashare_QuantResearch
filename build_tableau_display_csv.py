"""Build stable Tableau display-layer CSV files.

Outputs are written to ``raw/tableau_display``.  Existing Tableau CSVs remain
the canonical history: rows already present in those files are copied byte for
byte, and only genuinely new rows are appended.
"""
from __future__ import annotations

import argparse
import shutil
from dataclasses import dataclass
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parent
DEFAULT_OUTPUT_DIR = ROOT / "raw" / "tableau_display"

NAV_FILE = "nav_daily_size005_noquality_long_utf8_bom.csv"
RANK_CORR_FILE = "rank_corr_mean.csv"
DIAGNOSTICS_FILE = "diagnostics_2015_2026.csv"
STYLE_GROUP_FILE = "style_group_returns.csv"
STYLE_LONG_SHORT_FILE = "style_long_short_returns.csv"
STYLE_YEAR_IC_FILE = "style_year_ic_chart.csv"

PORTFOLIO_DAILY = (
    ROOT
    / "data"
    / "backtest"
    / "size5_growth10_quality_disabled_mcap_growth_cap10_1y_daily_returns.csv"
)
GROWTH100_INDEX = ROOT / "data" / "factor" / "980080_成长100.csv"
ALL_A_INDEX = ROOT / "raw" / "index_gz" / "000985_中证全指.csv"

LEGACY_PATHS = {
    NAV_FILE: ROOT / "data" / "factor" / NAV_FILE,
    RANK_CORR_FILE: ROOT / "data" / "factor" / "diagnostics" / RANK_CORR_FILE,
    DIAGNOSTICS_FILE: ROOT / DIAGNOSTICS_FILE,
    STYLE_GROUP_FILE: ROOT / "data" / "factor" / "style_backtest" / STYLE_GROUP_FILE,
    STYLE_LONG_SHORT_FILE: ROOT
    / "data"
    / "factor"
    / "style_backtest"
    / STYLE_LONG_SHORT_FILE,
    STYLE_YEAR_IC_FILE: ROOT / "docs" / STYLE_YEAR_IC_FILE,
}

DIAGNOSTICS_COLUMNS = [
    "date_id",
    "factor_code",
    "calc_version",
    "universe_count",
    "valid_count",
    "coverage",
    "rank_ic_1m",
    "icir_1m",
    "rank_ic_3m",
    "icir_3m",
    "rank_ic_6m",
    "icir_6m",
    "raw_rank_ic_1m",
    "raw_icir_1m",
    "raw_rank_ic_3m",
    "raw_icir_3m",
    "raw_rank_ic_6m",
    "raw_icir_6m",
]

STYLE_ORDER = ["value", "quality", "growth", "momentum", "reversal", "risk"]
STYLE_NAMES = {
    "value": "价值",
    "quality": "质量",
    "growth": "成长",
    "momentum": "动量",
    "reversal": "反转",
    "risk": "风险",
}
HORIZONS = (1, 3, 6)


@dataclass
class BuildReport:
    name: str
    output: Path
    rows: int
    frozen_rows: int = 0
    appended_rows: int = 0
    generated_overlap_diffs: int = 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build stable Tableau display CSV files under raw/tableau_display."
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Output directory. Default: raw/tableau_display.",
    )
    parser.add_argument(
        "--fetch-missing-index",
        action="store_true",
        help="Best-effort akshare fallback for missing index rows.",
    )
    return parser.parse_args()


def read_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, encoding="utf-8-sig")


def copy_csv(source: Path, output: Path, name: str) -> BuildReport:
    if not source.exists():
        raise FileNotFoundError(f"missing source CSV for {name}: {source}")
    output.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, output)
    rows = len(read_csv(output))
    return BuildReport(name=name, output=output, rows=rows, frozen_rows=rows)


def append_preserving_legacy(
    *,
    legacy_path: Path,
    output_path: Path,
    append_rows: pd.DataFrame,
    columns: list[str],
    name: str,
    float_format: str | None = None,
) -> BuildReport:
    if not legacy_path.exists():
        output_path.parent.mkdir(parents=True, exist_ok=True)
        append_rows.to_csv(
            output_path,
            index=False,
            columns=columns,
            encoding="utf-8-sig" if name == NAV_FILE else "utf-8",
            float_format=float_format,
            lineterminator="\n",
        )
        return BuildReport(name=name, output=output_path, rows=len(append_rows))

    legacy = read_csv(legacy_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(legacy_path, output_path)
    if not append_rows.empty:
        append_rows.to_csv(
            output_path,
            mode="a",
            header=False,
            index=False,
            columns=columns,
            encoding="utf-8",
            float_format=float_format,
            lineterminator="\n",
        )
    return BuildReport(
        name=name,
        output=output_path,
        rows=len(legacy) + len(append_rows),
        frozen_rows=len(legacy),
        appended_rows=len(append_rows),
    )


def count_key_diffs(
    legacy: pd.DataFrame,
    candidate: pd.DataFrame,
    key_cols: list[str],
) -> int:
    if legacy.empty or candidate.empty:
        return 0
    if legacy.duplicated(key_cols).any() or candidate.duplicated(key_cols).any():
        return 0
    value_cols = [col for col in legacy.columns if col not in key_cols]
    common = legacy.merge(candidate, on=key_cols, how="inner", suffixes=("_old", "_new"))
    if common.empty:
        return 0
    changed = pd.Series(False, index=common.index)
    for col in value_cols:
        old = common[f"{col}_old"]
        new = common[f"{col}_new"]
        equal = old.eq(new) | (old.isna() & new.isna())
        changed |= ~equal
    return int(changed.sum())


def build_diagnostics_candidate() -> pd.DataFrame:
    diag_dir = ROOT / "data" / "factor" / "diagnostics"
    paths = sorted(diag_dir.glob("diagnostics_*.csv"))
    if not paths:
        raise FileNotFoundError(f"no diagnostics_*.csv files found in {diag_dir}")

    diagnostics = pd.concat((read_csv(path) for path in paths), ignore_index=True)
    diagnostics = diagnostics.drop_duplicates(
        subset=["date_id", "factor_code", "calc_version"],
        keep="last",
    )

    for horizon in HORIZONS:
        for source_prefix, output_prefix in (
            ("rank_ic", "icir"),
            ("raw_rank_ic", "raw_icir"),
        ):
            value_col = f"{source_prefix}_{horizon}m"
            output_col = f"{output_prefix}_{horizon}m"
            diagnostics[output_col] = diagnostics.groupby("factor_code")[
                value_col
            ].transform(lambda s: s.mean(skipna=True) / s.std(skipna=True))

    for col in DIAGNOSTICS_COLUMNS:
        if col not in diagnostics.columns:
            diagnostics[col] = pd.NA
    diagnostics = diagnostics[DIAGNOSTICS_COLUMNS].sort_values(
        ["date_id", "factor_code", "calc_version"],
        kind="mergesort",
    )
    numeric_cols = diagnostics.select_dtypes(include="number").columns
    diagnostics[numeric_cols] = diagnostics[numeric_cols].round(6)
    return diagnostics


def build_diagnostics(output_dir: Path) -> BuildReport:
    name = DIAGNOSTICS_FILE
    legacy_path = LEGACY_PATHS[name]
    candidate = build_diagnostics_candidate()
    append_rows = candidate
    diffs = 0
    if legacy_path.exists():
        legacy = read_csv(legacy_path)
        max_date_id = int(legacy["date_id"].max())
        append_rows = candidate[candidate["date_id"].astype(int) > max_date_id]
        diffs = count_key_diffs(
            legacy,
            candidate[candidate["date_id"].astype(int) <= max_date_id],
            ["date_id", "factor_code", "calc_version"],
        )
    report = append_preserving_legacy(
        legacy_path=legacy_path,
        output_path=output_dir / name,
        append_rows=append_rows,
        columns=DIAGNOSTICS_COLUMNS,
        name=name,
        float_format="%.6f",
    )
    report.generated_overlap_diffs = diffs
    return report


def read_index_nav(path: Path, name: str, start_date: int) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"missing index CSV for {name}: {path}")
    raw = read_csv(path)
    required = {"日期", "收盘价"}
    missing = required - set(raw.columns)
    if missing:
        raise ValueError(f"{path} missing columns: {sorted(missing)}")
    frame = raw[["日期", "收盘价"]].copy()
    frame["date"] = pd.to_datetime(frame["日期"], errors="coerce").dt.strftime("%Y%m%d")
    frame = frame.dropna(subset=["date", "收盘价"])
    frame["date"] = frame["date"].astype("int64")
    frame["close"] = pd.to_numeric(frame["收盘价"], errors="coerce")
    frame = frame.dropna(subset=["close"]).sort_values("date", kind="mergesort")
    frame = frame[frame["date"] >= start_date].copy()
    if frame.empty:
        return pd.DataFrame(columns=["date", "name", "nav"])
    base_rows = frame.loc[frame["date"] == start_date, "close"]
    base = float(base_rows.iloc[0] if not base_rows.empty else frame["close"].iloc[0])
    result = pd.DataFrame(
        {
            "date": frame["date"].astype("int64"),
            "name": name,
            "nav": frame["close"].astype("float64") / base,
        }
    )
    return result


def maybe_fetch_missing_index_rows(enabled: bool) -> None:
    if not enabled:
        return
    try:
        import akshare as ak  # type: ignore
    except Exception as exc:  # pragma: no cover - optional local dependency
        print(f"[tableau] akshare unavailable, skip index fetch: {exc}")
        return

    # Keep this deliberately conservative.  The script can run without network;
    # local CSVs remain the canonical source when available.
    for code, path in (("980080", GROWTH100_INDEX), ("000985", ALL_A_INDEX)):
        try:
            existing = read_csv(path) if path.exists() else pd.DataFrame()
            start_date = "19900101"
            if not existing.empty and "日期" in existing.columns:
                latest = pd.to_datetime(existing["日期"], errors="coerce").max()
                if pd.notna(latest):
                    start_date = latest.strftime("%Y%m%d")
            fetched = ak.index_zh_a_hist(
                symbol=code,
                period="daily",
                start_date=start_date,
                end_date=pd.Timestamp.today().strftime("%Y%m%d"),
            )
            if fetched is None or fetched.empty:
                continue
            rename = {
                "日期": "日期",
                "开盘": "开盘价",
                "收盘": "收盘价",
                "最高": "最高价",
                "最低": "最低价",
                "成交量": "成交量(万手)",
            }
            fetched = fetched.rename(columns=rename)
            cols = ["日期", "开盘价", "收盘价", "最高价", "最低价", "成交量(万手)"]
            fetched = fetched[[col for col in cols if col in fetched.columns]]
            combined = pd.concat([existing, fetched], ignore_index=True)
            combined = combined.drop_duplicates(subset=["日期"], keep="last")
            combined = combined.sort_values("日期", ascending=False)
            path.parent.mkdir(parents=True, exist_ok=True)
            combined.to_csv(path, index=False, encoding="utf-8-sig")
        except Exception as exc:  # pragma: no cover - optional network path
            print(f"[tableau] akshare fetch failed for {code}, keep local CSV: {exc}")


def build_strategy_nav(legacy: pd.DataFrame | None) -> pd.DataFrame:
    if not PORTFOLIO_DAILY.exists():
        return pd.DataFrame(columns=["date", "name", "nav"])
    daily = read_csv(PORTFOLIO_DAILY)
    if daily.empty:
        return pd.DataFrame(columns=["date", "name", "nav"])
    date_col = "date_id" if "date_id" in daily.columns else "date"
    daily = daily[[date_col, "net_value"]].copy()
    daily["date"] = daily[date_col].astype(str).str.replace("-", "", regex=False).astype("int64")
    daily["net_value"] = pd.to_numeric(daily["net_value"], errors="coerce")
    daily = daily.dropna(subset=["net_value"]).sort_values("date", kind="mergesort")

    scale = 1.0
    if legacy is not None and not legacy.empty:
        old_strategy = legacy[legacy["name"].eq("策略组合")][["date", "nav"]].copy()
        old_strategy["date"] = old_strategy["date"].astype("int64")
        old_strategy = old_strategy.drop_duplicates(subset=["date"], keep="last")
        common = old_strategy.merge(daily[["date", "net_value"]], on="date", how="inner")
        common = common[common["net_value"].ne(0)]
        if not common.empty:
            last = common.sort_values("date").iloc[-1]
            scale = float(last["nav"]) / float(last["net_value"])
        elif not daily.empty:
            scale = 1.0 / float(daily["net_value"].iloc[0])
    elif not daily.empty:
        scale = 1.0 / float(daily["net_value"].iloc[0])

    return pd.DataFrame(
        {
            "date": daily["date"].astype("int64"),
            "name": "策略组合",
            "nav": daily["net_value"].astype("float64") * scale,
        }
    )


def restrict_to_complete_nav_dates(nav: pd.DataFrame) -> pd.DataFrame:
    if nav.empty:
        return nav
    counts = nav.groupby("date")["name"].nunique()
    complete_dates = set(counts[counts == 3].index)
    return nav[nav["date"].isin(complete_dates)].copy()


def duplicate_month_end_nav_rows(nav: pd.DataFrame) -> pd.DataFrame:
    if nav.empty:
        return nav
    dated = nav.copy()
    parsed = pd.to_datetime(dated["date"].astype(str), format="%Y%m%d", errors="coerce")
    dated["_period"] = parsed.dt.to_period("M").astype(str)
    max_dates = set(dated.groupby("_period")["date"].max())
    duplicates = dated[dated["date"].isin(max_dates)].copy()
    dated = dated.drop(columns=["_period"])
    duplicates = duplicates.drop(columns=["_period"])
    return pd.concat([dated, duplicates], ignore_index=True)


def build_nav(output_dir: Path, fetch_missing_index: bool) -> BuildReport:
    name = NAV_FILE
    legacy_path = LEGACY_PATHS[name]
    legacy = read_csv(legacy_path) if legacy_path.exists() else None
    start_date = 20250530
    max_legacy_date = None
    if legacy is not None and not legacy.empty:
        start_date = int(legacy["date"].min())
        max_legacy_date = int(legacy["date"].max())

    maybe_fetch_missing_index_rows(fetch_missing_index)
    pieces = [
        build_strategy_nav(legacy),
        read_index_nav(GROWTH100_INDEX, "成长100", start_date),
        read_index_nav(ALL_A_INDEX, "中证全指", start_date),
    ]
    candidate = pd.concat(pieces, ignore_index=True)
    candidate = restrict_to_complete_nav_dates(candidate)
    candidate = candidate.sort_values(["date", "name"], kind="mergesort")

    append_rows = candidate
    if max_legacy_date is not None:
        append_rows = candidate[candidate["date"].astype(int) > max_legacy_date].copy()
    append_rows = duplicate_month_end_nav_rows(append_rows)
    append_rows = append_rows.sort_values(["date", "name"], kind="mergesort")
    report = append_preserving_legacy(
        legacy_path=legacy_path,
        output_path=output_dir / name,
        append_rows=append_rows[["date", "name", "nav"]],
        columns=["date", "name", "nav"],
        name=name,
        float_format="%.6f",
    )
    return report


def build_style_year_ic_candidate(diagnostics: pd.DataFrame) -> pd.DataFrame:
    catalog = read_csv(ROOT / "factor" / "factor_catalog.csv")
    catalog = catalog[["factor_code", "style"]].drop_duplicates()
    factor_counts = catalog.groupby("style")["factor_code"].nunique().to_dict()

    data = diagnostics.merge(catalog, on="factor_code", how="inner")
    data["year"] = data["date_id"].astype(int) // 10000
    rows: list[dict[str, object]] = []

    for horizon in HORIZONS:
        horizon_label = f"{horizon}M"
        for signal_type, signal_name, col in (
            ("neutralized", "Neutralized", f"rank_ic_{horizon}m"),
            ("raw", "Raw", f"raw_rank_ic_{horizon}m"),
        ):
            for metric, metric_name in (("IC", "IC Mean"), ("ICIR", "ICIR")):
                for year in sorted(data["year"].dropna().unique()):
                    year_data = data[data["year"].eq(year)]
                    for style_order, style in enumerate(STYLE_ORDER, start=1):
                        style_data = year_data[year_data["style"].eq(style)]
                        if style_data.empty:
                            continue
                        monthly = style_data.groupby("date_id")[col].mean().dropna()
                        if monthly.empty:
                            continue
                        ic_mean = float(monthly.mean())
                        ic_std = float(monthly.std())
                        value = ic_mean if metric == "IC" else (
                            None if pd.isna(ic_std) or ic_std == 0 else ic_mean / ic_std
                        )
                        if value is None:
                            continue
                        rows.append(
                            {
                                "calc_version": sorted(
                                    style_data["calc_version"].dropna().astype(str).unique()
                                )[-1],
                                "year": int(year),
                                "style": style,
                                "style_name": STYLE_NAMES.get(style, style),
                                "style_order": style_order,
                                "horizon": horizon_label,
                                "horizon_months": horizon,
                                "signal_type": signal_type,
                                "signal_name": signal_name,
                                "month_count": int(len(monthly)),
                                "factor_count": int(factor_counts.get(style, 0)),
                                "factor_month_obs": int(style_data[col].notna().sum()),
                                "win_rate": float((monthly > 0).mean()),
                                "ic_std": ic_std,
                                "is_partial_year": bool(len(monthly) < 12),
                                "metric": metric,
                                "metric_name": metric_name,
                                "value": float(value),
                            }
                        )

    output = pd.DataFrame(rows)
    if output.empty:
        return output
    return output[
        [
            "calc_version",
            "year",
            "style",
            "style_name",
            "style_order",
            "horizon",
            "horizon_months",
            "signal_type",
            "signal_name",
            "month_count",
            "factor_count",
            "factor_month_obs",
            "win_rate",
            "ic_std",
            "is_partial_year",
            "metric",
            "metric_name",
            "value",
        ]
    ].round(
        {
            "win_rate": 6,
            "ic_std": 6,
            "value": 6,
        }
    )


def build_style_year_ic(output_dir: Path, diagnostics_output: Path) -> BuildReport:
    name = STYLE_YEAR_IC_FILE
    legacy_path = LEGACY_PATHS[name]
    diagnostics = read_csv(diagnostics_output)
    candidate = build_style_year_ic_candidate(diagnostics)
    append_rows = candidate
    diffs = 0
    key_cols = [
        "calc_version",
        "year",
        "style",
        "horizon",
        "signal_type",
        "metric",
    ]
    if legacy_path.exists() and not candidate.empty:
        legacy = read_csv(legacy_path)
        existing_keys = legacy[key_cols].drop_duplicates()
        candidate_keys = candidate.merge(existing_keys, on=key_cols, how="inner")
        new_keys = candidate.merge(existing_keys, on=key_cols, how="left", indicator=True)
        append_rows = new_keys[new_keys["_merge"].eq("left_only")]
        append_rows = append_rows.drop(columns=["_merge"])
        diffs = count_key_diffs(legacy, candidate_keys, key_cols)
    report = append_preserving_legacy(
        legacy_path=legacy_path,
        output_path=output_dir / name,
        append_rows=append_rows,
        columns=list(candidate.columns) if not candidate.empty else list(read_csv(legacy_path).columns),
        name=name,
        float_format="%.6f",
    )
    report.generated_overlap_diffs = diffs
    return report


def build_temporal_copy(
    *,
    source: Path,
    output_dir: Path,
    name: str,
    date_col: str,
    key_cols: list[str],
) -> BuildReport:
    if not source.exists():
        raise FileNotFoundError(f"missing source CSV for {name}: {source}")
    legacy_path = LEGACY_PATHS[name]
    candidate = read_csv(source)
    append_rows = candidate
    diffs = 0
    if legacy_path.exists():
        legacy = read_csv(legacy_path)
        max_date = int(legacy[date_col].max())
        append_rows = candidate[candidate[date_col].astype(int) > max_date].copy()
        diffs = count_key_diffs(
            legacy,
            candidate[candidate[date_col].astype(int) <= max_date],
            key_cols,
        )
    report = append_preserving_legacy(
        legacy_path=legacy_path,
        output_path=output_dir / name,
        append_rows=append_rows,
        columns=list(candidate.columns),
        name=name,
    )
    report.generated_overlap_diffs = diffs
    return report


def build_all(output_dir: Path, fetch_missing_index: bool) -> list[BuildReport]:
    output_dir.mkdir(parents=True, exist_ok=True)
    reports = [
        build_nav(output_dir, fetch_missing_index),
        copy_csv(LEGACY_PATHS[RANK_CORR_FILE], output_dir / RANK_CORR_FILE, RANK_CORR_FILE),
        build_diagnostics(output_dir),
        build_temporal_copy(
            source=LEGACY_PATHS[STYLE_GROUP_FILE],
            output_dir=output_dir,
            name=STYLE_GROUP_FILE,
            date_col="signal_date_id",
            key_cols=["signal_date_id", "style", "group_rank", "group_count"],
        ),
        build_temporal_copy(
            source=LEGACY_PATHS[STYLE_LONG_SHORT_FILE],
            output_dir=output_dir,
            name=STYLE_LONG_SHORT_FILE,
            date_col="signal_date_id",
            key_cols=["signal_date_id", "style", "group_count"],
        ),
    ]
    reports.append(build_style_year_ic(output_dir, output_dir / DIAGNOSTICS_FILE))
    return reports


def main() -> int:
    args = parse_args()
    output_dir = args.output_dir.resolve()
    reports = build_all(output_dir, args.fetch_missing_index)
    print(f"Tableau display CSVs written to {output_dir}")
    for report in reports:
        rel_output = report.output.relative_to(ROOT) if report.output.is_relative_to(ROOT) else report.output
        diff_note = (
            f" generated_overlap_diffs={report.generated_overlap_diffs}"
            if report.generated_overlap_diffs
            else ""
        )
        print(
            f"  {report.name}: rows={report.rows} "
            f"frozen={report.frozen_rows} appended={report.appended_rows}"
            f"{diff_note} -> {rel_output}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
