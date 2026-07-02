"""Build latest Tableau display-layer CSV files.

Outputs are written to ``raw/tableau_display``.  Each run reconstructs the
display files from the current upstream CSVs; existing display outputs are not
used as canonical history.
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
GROWTH100_INDEX = ROOT / "raw" / "index_gz" / "980080_成长100.csv"
ALL_A_INDEX = ROOT / "raw" / "index_gz" / "000985_中证全指.csv"
RANK_CORR_SOURCE = ROOT / "data" / "factor" / "diagnostics" / RANK_CORR_FILE
STYLE_GROUP_SOURCE = ROOT / "data" / "factor" / "style_backtest" / STYLE_GROUP_FILE
STYLE_LONG_SHORT_SOURCE = ROOT / "data" / "factor" / "style_backtest" / STYLE_LONG_SHORT_FILE

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

STYLE_YEAR_COLUMNS = [
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
    detail: str = ""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build latest Tableau display CSV files under raw/tableau_display."
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


def write_csv(
    frame: pd.DataFrame,
    output: Path,
    name: str,
    *,
    columns: list[str] | None = None,
    float_format: str | None = None,
    encoding: str = "utf-8",
    detail: str = "",
) -> BuildReport:
    output.parent.mkdir(parents=True, exist_ok=True)
    temp_output = output.with_name(f".{output.name}.tmp")
    frame.to_csv(
        temp_output,
        index=False,
        columns=columns,
        encoding=encoding,
        float_format=float_format,
        lineterminator="\n",
    )
    replace_output(temp_output, output)
    return BuildReport(name=name, output=output, rows=len(frame), detail=detail)


def copy_current_csv(source: Path, output: Path, name: str) -> BuildReport:
    if not source.exists():
        raise FileNotFoundError(f"missing source CSV for {name}: {source}")
    output.parent.mkdir(parents=True, exist_ok=True)
    temp_output = output.with_name(f".{output.name}.tmp")
    shutil.copyfile(source, temp_output)
    replace_output(temp_output, output)
    frame = read_csv(output)
    return BuildReport(name=name, output=output, rows=len(frame), detail=date_detail(frame))


def replace_output(temp_output: Path, output: Path) -> None:
    try:
        temp_output.replace(output)
    except PermissionError as exc:
        temp_output.unlink(missing_ok=True)
        raise PermissionError(
            f"cannot replace {output}; close any Tableau/Excel/preview process using it and rerun"
        ) from exc


def date_detail(frame: pd.DataFrame) -> str:
    for col in ("date", "date_id", "exit_date_id", "signal_date_id", "year", "日期"):
        if col not in frame.columns or frame.empty:
            continue
        values = frame[col].dropna()
        if values.empty:
            continue
        return f"{col}={values.min()}..{values.max()}"
    return ""


def safe_icir(series: pd.Series) -> float:
    std = series.std(skipna=True)
    if pd.isna(std) or float(std) == 0.0:
        return float("nan")
    return float(series.mean(skipna=True) / std)


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
            ].transform(safe_icir)

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
    candidate = build_diagnostics_candidate()
    return write_csv(
        candidate,
        output_dir / DIAGNOSTICS_FILE,
        DIAGNOSTICS_FILE,
        columns=DIAGNOSTICS_COLUMNS,
        float_format="%.6f",
        detail=date_detail(candidate),
    )


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
    frame["close"] = pd.to_numeric(frame["收盘价"], errors="coerce")
    frame = frame.dropna(subset=["date", "close"])
    frame["date"] = frame["date"].astype("int64")
    frame = frame.sort_values("date", kind="mergesort").drop_duplicates(
        subset=["date"],
        keep="last",
    )
    frame = frame[frame["date"] >= start_date].copy()
    if frame.empty:
        return pd.DataFrame(columns=["date", "name", "nav"])

    base_rows = frame.loc[frame["date"].eq(start_date), "close"]
    base = float(base_rows.iloc[0] if not base_rows.empty else frame["close"].iloc[0])
    if base == 0.0:
        raise ValueError(f"{path} has zero base close for {name}")
    return pd.DataFrame(
        {
            "date": frame["date"].astype("int64"),
            "name": name,
            "nav": frame["close"].astype("float64") / base,
        }
    )


def maybe_fetch_missing_index_rows(enabled: bool) -> None:
    if not enabled:
        return
    try:
        import akshare as ak  # type: ignore
    except Exception as exc:  # pragma: no cover - optional local dependency
        print(f"[tableau] akshare unavailable, skip index fetch: {exc}")
        return

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


def build_strategy_nav() -> pd.DataFrame:
    if not PORTFOLIO_DAILY.exists():
        raise FileNotFoundError(f"missing portfolio daily CSV: {PORTFOLIO_DAILY}")
    daily = read_csv(PORTFOLIO_DAILY)
    if daily.empty:
        raise ValueError(f"portfolio daily CSV is empty: {PORTFOLIO_DAILY}")
    date_col = "date_id" if "date_id" in daily.columns else "date"
    missing = {date_col, "net_value"} - set(daily.columns)
    if missing:
        raise ValueError(f"{PORTFOLIO_DAILY} missing columns: {sorted(missing)}")

    daily = daily[[date_col, "net_value"]].copy()
    daily["date"] = pd.to_numeric(
        daily[date_col].astype(str).str.replace("-", "", regex=False).str.slice(0, 8),
        errors="coerce",
    )
    daily["net_value"] = pd.to_numeric(daily["net_value"], errors="coerce")
    daily = daily.dropna(subset=["date", "net_value"]).sort_values("date", kind="mergesort")
    daily["date"] = daily["date"].astype("int64")
    daily = daily.drop_duplicates(subset=["date"], keep="last")
    if daily.empty:
        raise ValueError(f"no valid portfolio daily rows found in {PORTFOLIO_DAILY}")

    base = float(daily["net_value"].iloc[0])
    if base == 0.0:
        raise ValueError(f"{PORTFOLIO_DAILY} has zero initial net_value")
    return pd.DataFrame(
        {
            "date": daily["date"].astype("int64"),
            "name": "策略组合",
            "nav": daily["net_value"].astype("float64") / base,
        }
    )


def restrict_to_complete_nav_dates(nav: pd.DataFrame) -> pd.DataFrame:
    if nav.empty:
        return nav
    counts = nav.groupby("date")["name"].nunique()
    complete_dates = set(counts[counts == 3].index)
    return nav[nav["date"].isin(complete_dates)].copy()


def build_nav(output_dir: Path, fetch_missing_index: bool) -> BuildReport:
    maybe_fetch_missing_index_rows(fetch_missing_index)
    strategy = build_strategy_nav()
    start_date = int(strategy["date"].min())
    pieces = [
        strategy,
        read_index_nav(GROWTH100_INDEX, "成长100", start_date),
        read_index_nav(ALL_A_INDEX, "中证全指", start_date),
    ]
    candidate = pd.concat(pieces, ignore_index=True)
    candidate = restrict_to_complete_nav_dates(candidate)
    candidate = candidate.sort_values(["date", "name"], kind="mergesort")
    candidate = candidate[["date", "name", "nav"]].reset_index(drop=True)
    if candidate.empty:
        raise ValueError("nav candidate is empty after aligning strategy and benchmarks")
    duplicate_count = int(candidate.duplicated(["date", "name"]).sum())
    if duplicate_count:
        raise ValueError(f"nav candidate has duplicate date/name rows: {duplicate_count}")

    return write_csv(
        candidate,
        output_dir / NAV_FILE,
        NAV_FILE,
        columns=["date", "name", "nav"],
        float_format="%.6f",
        encoding="utf-8-sig",
        detail=date_detail(candidate),
    )


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
        return pd.DataFrame(columns=STYLE_YEAR_COLUMNS)
    return output[STYLE_YEAR_COLUMNS].round(
        {
            "win_rate": 6,
            "ic_std": 6,
            "value": 6,
        }
    )


def build_style_year_ic(output_dir: Path, diagnostics: pd.DataFrame) -> BuildReport:
    candidate = build_style_year_ic_candidate(diagnostics)
    return write_csv(
        candidate,
        output_dir / STYLE_YEAR_IC_FILE,
        STYLE_YEAR_IC_FILE,
        columns=STYLE_YEAR_COLUMNS,
        float_format="%.6f",
        detail=date_detail(candidate),
    )


def build_all(output_dir: Path, fetch_missing_index: bool) -> list[BuildReport]:
    output_dir.mkdir(parents=True, exist_ok=True)
    diagnostics = build_diagnostics_candidate()
    reports = [
        build_nav(output_dir, fetch_missing_index),
        copy_current_csv(RANK_CORR_SOURCE, output_dir / RANK_CORR_FILE, RANK_CORR_FILE),
        write_csv(
            diagnostics,
            output_dir / DIAGNOSTICS_FILE,
            DIAGNOSTICS_FILE,
            columns=DIAGNOSTICS_COLUMNS,
            float_format="%.6f",
            detail=date_detail(diagnostics),
        ),
        copy_current_csv(STYLE_GROUP_SOURCE, output_dir / STYLE_GROUP_FILE, STYLE_GROUP_FILE),
        copy_current_csv(
            STYLE_LONG_SHORT_SOURCE,
            output_dir / STYLE_LONG_SHORT_FILE,
            STYLE_LONG_SHORT_FILE,
        ),
        build_style_year_ic(output_dir, diagnostics),
    ]
    return reports


def main() -> int:
    args = parse_args()
    output_dir = args.output_dir.resolve()
    reports = build_all(output_dir, args.fetch_missing_index)
    print(f"Tableau display CSVs written to {output_dir}")
    for report in reports:
        rel_output = report.output.relative_to(ROOT) if report.output.is_relative_to(ROOT) else report.output
        detail = f" {report.detail}" if report.detail else ""
        print(f"  {report.name}: rows={report.rows}{detail} -> {rel_output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
