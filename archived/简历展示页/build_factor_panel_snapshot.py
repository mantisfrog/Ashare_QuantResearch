from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
OUT_PATH = Path(__file__).resolve().with_name("factor_panel_data.js")

STYLE_ORDER = ["value", "quality", "growth", "momentum", "reversal", "risk"]
STYLE_NAMES = {
    "value": "\u4ef7\u503c",
    "quality": "\u8d28\u91cf",
    "growth": "\u6210\u957f",
    "momentum": "\u52a8\u91cf",
    "reversal": "\u53cd\u8f6c",
    "risk": "\u98ce\u9669",
}


def _read_diagnostics() -> pd.DataFrame:
    paths = sorted((ROOT / "data/factor/diagnostics").glob("diagnostics_*.csv"))
    if not paths:
        raise FileNotFoundError("No diagnostics_*.csv files found.")
    frames = [pd.read_csv(path) for path in paths]
    diagnostics = pd.concat(frames, ignore_index=True)
    return diagnostics.drop_duplicates(
        subset=["date_id", "factor_code", "calc_version"], keep="last"
    )


def _metric_stats(values: pd.Series) -> dict[str, Any]:
    s = values.dropna()
    if s.empty:
        return {"ic_mean": None, "ir": None, "win_rate": None, "months": 0}

    std = s.std()
    ir = None if pd.isna(std) or std == 0 else s.mean() / std
    return {
        "ic_mean": s.mean(),
        "ir": ir,
        "win_rate": (s > 0).mean(),
        "months": int(s.shape[0]),
    }


def _score_label(ir: float | None, win_rate: float | None, coverage: float | None) -> str:
    if coverage is not None and coverage < 0.9:
        return "\u8986\u76d6\u504f\u4f4e"
    if ir is None:
        return "\u5f85\u89c2\u5bdf"
    if ir >= 0.70:
        return "\u5f3a"
    if ir >= 0.45:
        return "\u7a33\u5065"
    if ir >= 0.20:
        return "\u53ef\u89c2\u5bdf"
    if ir >= 0:
        return "\u504f\u5f31"
    if win_rate is not None and win_rate < 0.5:
        return "\u9700\u590d\u6838"
    return "\u8d1f\u6548"


def _date_text(date_id: int | float | None) -> str | None:
    if date_id is None or pd.isna(date_id):
        return None
    s = str(int(date_id))
    if len(s) != 8:
        return s
    return f"{s[:4]}-{s[4:6]}-{s[6:]}"


def _recent_stats(df: pd.DataFrame, max_date: int, months: int) -> dict[str, Any]:
    dates = sorted(df.loc[df["date_id"] <= max_date, "date_id"].dropna().unique())
    selected_dates = dates[-months:]
    return _metric_stats(df.loc[df["date_id"].isin(selected_dates), "rank_ic_1m"])


def _style_sort_key(style: str) -> tuple[int, str]:
    if style in STYLE_ORDER:
        return (STYLE_ORDER.index(style), style)
    return (len(STYLE_ORDER), style)


def _build_summary(catalog: pd.DataFrame, diagnostics: pd.DataFrame) -> dict[str, Any]:
    active_codes = set(catalog["factor_code"])
    diagnostics = diagnostics[diagnostics["factor_code"].isin(active_codes)].copy()
    diagnostics = diagnostics.merge(
        catalog[["factor_code", "factor_name", "style", "direction", "unit"]],
        on="factor_code",
        how="left",
    )

    latest_coverage_date = int(diagnostics["date_id"].max())
    latest_coverage_rows = diagnostics[diagnostics["date_id"] == latest_coverage_date]
    mature = diagnostics[diagnostics["rank_ic_1m"].notna()].copy()
    latest_ic_date = int(mature["date_id"].max()) if not mature.empty else None
    latest_ic_rows = mature[mature["date_id"] == latest_ic_date] if latest_ic_date else mature

    style_counts = catalog.groupby("style")["factor_code"].count().to_dict()
    available_styles = sorted(catalog["style"].dropna().unique(), key=_style_sort_key)

    styles = []
    for style in available_styles:
        style_df = mature[mature["style"] == style]
        latest_style_coverage = latest_coverage_rows.loc[
            latest_coverage_rows["style"] == style, "coverage"
        ].mean()
        latest_style_ic = latest_ic_rows.loc[
            latest_ic_rows["style"] == style, "rank_ic_1m"
        ].mean()
        all_stats = _metric_stats(style_df["rank_ic_1m"])
        recent_12 = _recent_stats(style_df, latest_ic_date, 12) if latest_ic_date else _metric_stats(pd.Series(dtype=float))
        recent_6 = _recent_stats(style_df, latest_ic_date, 6) if latest_ic_date else _metric_stats(pd.Series(dtype=float))
        styles.append(
            {
                "style": style,
                "style_name": STYLE_NAMES.get(style, style),
                "factor_count": int(style_counts.get(style, 0)),
                "latest_coverage": latest_style_coverage,
                "latest_ic_1m": latest_style_ic,
                "ic_mean": all_stats["ic_mean"],
                "ir": all_stats["ir"],
                "win_rate": all_stats["win_rate"],
                "months": all_stats["months"],
                "recent_12m_ir": recent_12["ir"],
                "recent_6m_ir": recent_6["ir"],
                "label": _score_label(all_stats["ir"], all_stats["win_rate"], latest_style_coverage),
            }
        )

    factor_rows = []
    for _, item in catalog.sort_values(["style", "factor_code"]).iterrows():
        code = item["factor_code"]
        factor_df = mature[mature["factor_code"] == code]
        coverage = latest_coverage_rows.loc[
            latest_coverage_rows["factor_code"] == code, "coverage"
        ].mean()
        latest_ic = latest_ic_rows.loc[
            latest_ic_rows["factor_code"] == code, "rank_ic_1m"
        ].mean()
        all_stats = _metric_stats(factor_df["rank_ic_1m"])
        recent_12 = _recent_stats(factor_df, latest_ic_date, 12) if latest_ic_date else _metric_stats(pd.Series(dtype=float))
        recent_6 = _recent_stats(factor_df, latest_ic_date, 6) if latest_ic_date else _metric_stats(pd.Series(dtype=float))
        factor_rows.append(
            {
                "factor_code": code,
                "factor_name": item["factor_name"],
                "style": item["style"],
                "style_name": STYLE_NAMES.get(item["style"], item["style"]),
                "direction": int(item["direction"]),
                "unit": item["unit"],
                "latest_coverage": coverage,
                "latest_ic_1m": latest_ic,
                "ic_mean": all_stats["ic_mean"],
                "ir": all_stats["ir"],
                "win_rate": all_stats["win_rate"],
                "months": all_stats["months"],
                "recent_12m_ir": recent_12["ir"],
                "recent_6m_ir": recent_6["ir"],
                "label": _score_label(all_stats["ir"], all_stats["win_rate"], coverage),
            }
        )
    factor_rows.sort(key=lambda row: (_style_sort_key(row["style"]), -(row["ir"] or -999)))

    years = sorted(mature["date_id"].dropna().astype(int).floordiv(10000).unique())
    heatmap_rows = []
    mature = mature.assign(year=mature["date_id"].astype(int) // 10000)
    for factor in factor_rows:
        group = mature[mature["factor_code"] == factor["factor_code"]]
        by_year = {}
        for year in years:
            stats = _metric_stats(group.loc[group["year"] == year, "rank_ic_1m"])
            by_year[str(int(year))] = stats["ir"]
        heatmap_rows.append(
            {
                "factor_code": factor["factor_code"],
                "factor_name": factor["factor_name"],
                "style": factor["style"],
                "style_name": factor["style_name"],
                "values": by_year,
            }
        )

    return {
        "meta": {
            "generated_at": datetime.now().isoformat(timespec="seconds"),
            "factor_count": int(catalog.shape[0]),
            "style_count": int(len(available_styles)),
            "calc_version": sorted(diagnostics["calc_version"].dropna().unique())[-1],
            "latest_coverage_date": latest_coverage_date,
            "latest_coverage_date_text": _date_text(latest_coverage_date),
            "latest_ic_date": latest_ic_date,
            "latest_ic_date_text": _date_text(latest_ic_date),
            "latest_universe_count": int(latest_coverage_rows["universe_count"].max()),
            "latest_avg_coverage": latest_coverage_rows["coverage"].mean(),
        },
        "styles": styles,
        "factors": factor_rows,
        "heatmap": {
            "years": [str(int(year)) for year in years],
            "rows": heatmap_rows,
        },
    }


def _build_corr_pairs(catalog: pd.DataFrame) -> list[dict[str, Any]]:
    path = ROOT / "data/factor/diagnostics/rank_corr_mean.csv"
    if not path.exists():
        return []

    corr = pd.read_csv(path, index_col=0)
    active = set(catalog["factor_code"])
    names = catalog.set_index("factor_code")["factor_name"].to_dict()
    styles = catalog.set_index("factor_code")["style"].to_dict()
    pairs = []
    columns = list(corr.columns)
    for i, factor_a in enumerate(corr.index):
        if factor_a not in active:
            continue
        for factor_b in columns[i + 1 :]:
            if factor_b not in active:
                continue
            value = corr.loc[factor_a, factor_b]
            if pd.isna(value):
                continue
            pairs.append(
                {
                    "factor_a": factor_a,
                    "factor_b": factor_b,
                    "factor_a_name": names.get(factor_a, factor_a),
                    "factor_b_name": names.get(factor_b, factor_b),
                    "style_a": styles.get(factor_a),
                    "style_b": styles.get(factor_b),
                    "corr": float(value),
                }
            )

    pairs.sort(key=lambda row: abs(row["corr"]), reverse=True)
    return pairs[:10]


def _build_manifest() -> list[dict[str, Any]]:
    path = ROOT / "data/factor/manifest/factor_build_manifest.csv"
    if not path.exists():
        return []

    manifest = pd.read_csv(path)
    if manifest.empty:
        return []

    latest = manifest.groupby("layer", sort=False).tail(1)
    order = {"universe": 0, "raw": 1, "exposure": 2, "composite": 3, "diagnostics": 4}
    latest = latest.sort_values("layer", key=lambda s: s.map(order).fillna(99))
    rows = []
    for _, item in latest.iterrows():
        rows.append(
            {
                "layer": item["layer"],
                "start_date": _date_text(item["start_date_id"]),
                "end_date": _date_text(item["end_date_id"]),
                "row_count": item["row_count"],
                "valid_count": item["valid_count"],
                "coverage": item["coverage"],
                "status": item["status"],
                "created_at": item["created_at"],
            }
        )
    return rows


def _clean(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): _clean(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_clean(item) for item in value]
    if pd.isna(value):
        return None
    if hasattr(value, "item"):
        return value.item()
    return value


def main() -> None:
    catalog = pd.read_csv(ROOT / "factor/factor_catalog.csv")
    diagnostics = _read_diagnostics()
    data = _build_summary(catalog, diagnostics)
    data["corr_pairs"] = _build_corr_pairs(catalog)
    data["build_manifest"] = _build_manifest()

    payload = json.dumps(_clean(data), ensure_ascii=False, allow_nan=False, indent=2)
    OUT_PATH.write_text(f"window.factorPanelData = {payload};\n", encoding="utf-8")
    print(f"wrote {OUT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
