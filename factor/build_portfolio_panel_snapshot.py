"""Build the static portfolio snapshot consumed by docs/index.html.

Strategy locked for the public page:
  - Size top 5% intersect Growth top 10%
  - Quality filter disabled
  - raw weight = market_cap * growth_score
  - 10% single-name cap
  - monthly rebalance
"""
from __future__ import annotations

import json
import math
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd

import backtest_portfolio as bt


ROOT = Path(__file__).resolve().parents[1]
DOCS_DIR = ROOT / "docs"
OUT_PATH = DOCS_DIR / "portfolio_panel_data.js"
DISPLAY_NAV_CANDIDATES = (
    ROOT / "raw" / "tableau_display" / "nav_daily_size005_noquality_long_utf8_bom.csv",
    ROOT / "data" / "factor" / "nav_daily_size005_noquality_long_utf8_bom.csv",
)

PORTFOLIO_NAME = "size5_growth10_quality_disabled_mcap_growth_cap10_1y"
LOOKBACK_DAYS = 365
MARKET_CAP_TOP = 0.05
GROWTH_TOP = 0.10
MAX_WEIGHT = 0.10
WEIGHTING = "market_cap_growth_capped"
TRADING_DAYS_PER_YEAR = 252.0
MONTHS_PER_YEAR = 12.0


def date_text(date_id: int | float | None) -> str | None:
    if date_id is None or pd.isna(date_id):
        return None
    text = str(int(date_id))
    if len(text) != 8:
        return text
    return f"{text[:4]}-{text[4:6]}-{text[6:]}"


def format_percent(value: float | None, digits: int = 2) -> str:
    if value is None or not math.isfinite(float(value)):
        return "--"
    return f"{float(value) * 100:.{digits}f}%"


def format_signed_percent(value: float | None, digits: int = 2) -> str:
    if value is None or not math.isfinite(float(value)):
        return "--"
    sign = "+" if float(value) > 0 else ""
    return f"{sign}{float(value) * 100:.{digits}f}%"


def format_number(value: float | None, digits: int = 2) -> str:
    if value is None or not math.isfinite(float(value)):
        return "--"
    return f"{float(value):.{digits}f}"


def metric_class(value: float | None) -> str:
    if value is None or not math.isfinite(float(value)) or float(value) == 0:
        return ""
    return "metric-positive" if float(value) > 0 else "metric-negative"


def compute_turnover(holdings: pd.DataFrame) -> tuple[pd.DataFrame, float | None, float | None]:
    rows: list[dict[str, Any]] = []
    previous: pd.Series | None = None
    for rebalance_date_id, group in holdings.groupby("rebalance_date_id", sort=True):
        weights = group.set_index("stock_code")["weight"].astype("float64")
        if previous is None:
            turnover = None
        else:
            aligned = pd.concat([previous, weights], axis=1).fillna(0.0)
            aligned.columns = ["previous_weight", "current_weight"]
            turnover = float((aligned["current_weight"] - aligned["previous_weight"]).abs().sum() / 2.0)
        rows.append({
            "rebalance_date_id": int(rebalance_date_id),
            "rebalance_date": date_text(int(rebalance_date_id)),
            "turnover": turnover,
        })
        previous = weights

    turnover_df = pd.DataFrame(rows)
    valid = pd.to_numeric(turnover_df["turnover"], errors="coerce").dropna()
    if valid.empty:
        return turnover_df, None, None
    monthly_turnover = float(valid.mean())
    return turnover_df, monthly_turnover, float(monthly_turnover * MONTHS_PER_YEAR)


def max_drawdown_window(daily: pd.DataFrame) -> dict[str, Any]:
    net_value = daily["net_value"].astype("float64")
    drawdown = net_value / net_value.cummax() - 1.0
    trough_index = drawdown.idxmin()
    peak_index = net_value.loc[:trough_index].idxmax()
    return {
        "max_drawdown": float(drawdown.loc[trough_index]),
        "start_date": str(daily.loc[peak_index, "date"]),
        "end_date": str(daily.loc[trough_index, "date"]),
    }


def display_nav_performance() -> dict[str, Any] | None:
    path = next((candidate for candidate in DISPLAY_NAV_CANDIDATES if candidate.exists()), None)
    if path is None:
        return None

    nav = pd.read_csv(path, encoding="utf-8-sig")
    required = {"date", "name", "nav"}
    if not required.issubset(nav.columns):
        return None

    strategy = nav.loc[nav["name"].eq("策略组合"), ["date", "nav"]].copy()
    strategy["date_id"] = strategy["date"].astype("int64")
    strategy["date"] = strategy["date_id"].map(date_text)
    strategy["net_value"] = pd.to_numeric(strategy["nav"], errors="coerce")
    strategy = strategy.dropna(subset=["net_value"])
    strategy = strategy.drop_duplicates(subset=["date_id"], keep="last")
    strategy = strategy.sort_values("date_id", kind="mergesort").reset_index(drop=True)
    if strategy.empty:
        return None

    returns = strategy["net_value"].pct_change().dropna()
    trading_days = int(len(strategy))
    total_return = float(strategy["net_value"].iloc[-1] / strategy["net_value"].iloc[0] - 1.0)
    annual_return = (
        float((1.0 + total_return) ** (TRADING_DAYS_PER_YEAR / trading_days) - 1.0)
        if trading_days > 0 and total_return > -1.0
        else float("nan")
    )
    annual_vol = float(returns.std(ddof=1) * math.sqrt(TRADING_DAYS_PER_YEAR)) if len(returns) > 1 else float("nan")
    sharpe = (
        float(returns.mean() / returns.std(ddof=1) * math.sqrt(TRADING_DAYS_PER_YEAR))
        if len(returns) > 1 and returns.std(ddof=1) > 0
        else float("nan")
    )
    drawdown_info = max_drawdown_window(strategy.rename(columns={"date_id": "date_id"}))
    return {
        "source": rel(path),
        "start_date_id": int(strategy["date_id"].iloc[0]),
        "end_date_id": int(strategy["date_id"].iloc[-1]),
        "start_date": str(strategy["date"].iloc[0]),
        "end_date": str(strategy["date"].iloc[-1]),
        "trading_days": trading_days,
        "total_return": total_return,
        "annual_return": annual_return,
        "annual_vol": annual_vol,
        "sharpe_0rf": sharpe,
        "max_drawdown": float(drawdown_info["max_drawdown"]),
        "drawdown_start_date": drawdown_info["start_date"],
        "drawdown_end_date": drawdown_info["end_date"],
    }


def build_sector_exposure(holdings: pd.DataFrame) -> pd.DataFrame:
    latest_rebalance_date_id = int(holdings["rebalance_date_id"].max())
    latest = holdings[holdings["rebalance_date_id"].eq(latest_rebalance_date_id)].copy()
    stocks = pd.read_csv(
        ROOT / "data" / "dim_stock.csv",
        usecols=["stock_code", "tdx_sector_code"],
        dtype={"stock_code": "string"},
    )
    sectors = pd.read_csv(ROOT / "data" / "dim_tdx_industry.csv")
    stocks["tdx_sector_code"] = pd.to_numeric(
        stocks["tdx_sector_code"],
        errors="coerce",
    ).astype("Int64")
    sectors["tdx_sector_code"] = pd.to_numeric(
        sectors["tdx_sector_code"],
        errors="coerce",
    ).astype("Int64")

    merged = latest.merge(stocks, on="stock_code", how="left")
    merged = merged.merge(sectors, on="tdx_sector_code", how="left")
    merged["tdx_sector_name"] = merged["tdx_sector_name"].fillna("未知")
    exposure = (
        merged.groupby(["tdx_sector_code", "tdx_sector_name"], dropna=False)["weight"]
        .sum()
        .reset_index()
        .sort_values("weight", ascending=False)
    )
    exposure.insert(0, "rebalance_date_id", latest_rebalance_date_id)
    return exposure.reset_index(drop=True)


def build_latest_target_holdings(
    composite: pd.DataFrame,
    market_cap_snapshots: pd.DataFrame,
    latest_rebalance_date_id: int,
    tops: dict[str, float],
) -> pd.DataFrame:
    latest_schedule = pd.DataFrame([{
        "rebalance_date_id": latest_rebalance_date_id,
        "entry_date_id": latest_rebalance_date_id,
        "exit_date_id": latest_rebalance_date_id,
    }])
    latest_holdings, latest_summary = bt.select_holdings(
        composite[composite["date_id"].eq(latest_rebalance_date_id)],
        market_cap_snapshots,
        latest_schedule,
        tops,
    )
    latest_prices = bt.load_daily_prices(
        ROOT / "data" / "fact_daily.csv",
        stock_codes=set(latest_holdings["stock_code"].astype(str)),
        start_date_id=latest_rebalance_date_id,
        end_date_id=latest_rebalance_date_id,
        chunksize=1_000_000,
    )
    latest_holdings, _ = bt.apply_holding_weights(
        latest_holdings,
        latest_summary,
        latest_prices,
        weighting=WEIGHTING,
        max_weight=MAX_WEIGHT,
    )
    return latest_holdings


def build_backtest() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    tops = {
        "market_cap": MARKET_CAP_TOP,
        "growth": GROWTH_TOP,
    }
    calendar = bt.load_trade_calendar(ROOT / "data" / "dim_date.csv")
    window = bt.resolve_window(
        calendar,
        start=None,
        end=None,
        lookback_days=LOOKBACK_DAYS,
    )
    trade_ids = calendar["date_id"].to_numpy(dtype="int64")
    composite = bt.load_composite(
        ROOT / "data" / "factor" / "composite",
        start_year=window.start_date_id // 10000 - 1,
        end_year=window.end_date_id // 10000,
        calc_version=bt.CALC_VERSION,
    )
    composite = composite[composite["date_id"] <= window.end_date_id].copy()
    schedule = bt.build_signal_schedule(
        composite["date_id"].unique(),
        trade_ids=trade_ids,
        start_date_id=window.start_date_id,
        end_date_id=window.end_date_id,
    )
    latest_rebalance_date_id = int(composite["date_id"].max())
    earliest_signal = int(schedule["rebalance_date_id"].min())
    price_start = min(window.price_start_date_id, earliest_signal)
    candidate_stock_codes = set(composite["stock_code"].astype(str))
    snapshot_dates = set(int(value) for value in schedule["rebalance_date_id"].unique())
    snapshot_dates.add(latest_rebalance_date_id)
    market_cap_snapshots = bt.load_market_cap_snapshots(
        ROOT / "data" / "fact_daily.csv",
        stock_codes=candidate_stock_codes,
        date_ids=snapshot_dates,
        chunksize=1_000_000,
    )
    latest_holdings = build_latest_target_holdings(
        composite,
        market_cap_snapshots,
        latest_rebalance_date_id,
        tops,
    )
    holdings, rebalance_summary = bt.select_holdings(
        composite,
        market_cap_snapshots,
        schedule,
        tops,
    )
    stock_codes = set(holdings["stock_code"].astype(str))
    daily_prices = bt.load_daily_prices(
        ROOT / "data" / "fact_daily.csv",
        stock_codes=stock_codes,
        start_date_id=price_start,
        end_date_id=window.end_date_id,
        chunksize=1_000_000,
    )
    holdings, rebalance_summary = bt.apply_holding_weights(
        holdings,
        rebalance_summary,
        daily_prices,
        weighting=WEIGHTING,
        max_weight=MAX_WEIGHT,
    )
    adjusted_prices = bt.add_adjusted_close(
        daily_prices,
        adjustment_path=ROOT / "data" / "fact_adjustment_factor_period.csv",
        stock_codes=stock_codes,
    )
    stock_returns = bt.build_return_matrix(
        adjusted_prices,
        trade_ids=trade_ids,
        price_start_date_id=price_start,
        end_date_id=window.end_date_id,
    )
    daily = bt.compute_portfolio_returns(
        stock_returns,
        holdings,
        calendar,
        schedule,
        start_date_id=window.start_date_id,
        end_date_id=window.end_date_id,
    )
    summary = bt.summarize_performance(
        daily,
        holdings,
        rebalance_summary,
        tops=tops,
        calc_version=bt.CALC_VERSION,
        weighting=WEIGHTING,
        max_weight=MAX_WEIGHT,
    )
    return daily, holdings, rebalance_summary, summary, latest_holdings


def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT).as_posix()


def panel_payload(
    daily: pd.DataFrame,
    holdings: pd.DataFrame,
    rebalance_summary: pd.DataFrame,
    summary: pd.DataFrame,
    turnover: pd.DataFrame,
    sector_exposure: pd.DataFrame,
    paths: dict[str, Path],
    monthly_turnover: float | None,
    annual_turnover: float | None,
) -> dict[str, Any]:
    values = dict(zip(summary["metric"], summary["value"], strict=False))
    display_perf = display_nav_performance()
    mdd = (
        {
            "max_drawdown": display_perf["max_drawdown"],
            "start_date": display_perf["drawdown_start_date"],
            "end_date": display_perf["drawdown_end_date"],
        }
        if display_perf
        else max_drawdown_window(daily)
    )
    latest_rebalance_date_id = int(sector_exposure["rebalance_date_id"].max())
    sector_top = sector_exposure.head(3).copy()
    top_sector_names = sector_top["tdx_sector_name"].astype(str).tolist()
    top3_weight = float(sector_top["weight"].sum()) if not sector_top.empty else None

    if display_perf:
        total_return = float(display_perf["total_return"])
        sharpe = float(display_perf["sharpe_0rf"])
        max_drawdown = float(display_perf["max_drawdown"])
        performance_start = display_perf["start_date"]
        performance_end = display_perf["end_date"]
    else:
        total_return = float(values["total_return"])
        sharpe = float(values["sharpe_0rf"])
        max_drawdown = float(values["max_drawdown"])
        performance_start = date_text(values["start_date_id"])
        performance_end = date_text(values["end_date_id"])
    metrics = [
        {
            "label": "累计收益",
            "value": format_signed_percent(total_return),
            "value_class": metric_class(total_return),
            "note": f"{performance_start} -> {performance_end}",
        },
        {
            "label": "夏普比率",
            "value": format_number(sharpe),
            "value_class": "",
            "note": "年化收益 / 年化波动",
        },
        {
            "label": "最大回撤",
            "value": format_percent(abs(max_drawdown)),
            "value_class": "metric-negative" if max_drawdown < 0 else "",
            "note": f"{mdd['start_date']} -> {mdd['end_date']}",
        },
        {
            "label": "年化换手率",
            "value": f"~{format_percent(annual_turnover, digits=0)}",
            "value_class": "",
            "note": f"月均 {format_percent(monthly_turnover)}",
        },
    ]

    return {
        "meta": {
            "generated_at": datetime.now().isoformat(timespec="seconds"),
            "portfolio_name": PORTFOLIO_NAME,
            "calc_version": bt.CALC_VERSION,
            "latest_rebalance_date": latest_rebalance_date_id,
            "latest_rebalance_date_text": date_text(latest_rebalance_date_id),
            "output_files": {name: rel(path) for name, path in paths.items()},
        },
        "strategy": {
            "logic": "Size top 5% ∩ Growth top 10%, Quality 禁用",
            "weighting": "市值 × 成长得分",
            "max_weight": "10%",
            "rebalance_frequency": "月度",
            "description": "",
        },
        "performance": {
            "source": display_perf["source"] if display_perf else "backtest",
            "start_date": performance_start,
            "end_date": performance_end,
            "trading_days": (
                int(display_perf["trading_days"])
                if display_perf
                else int(float(values["trading_days"]))
            ),
            "rebalance_count": int(float(values["rebalance_count"])),
            "holding_rows": int(float(values["holding_rows"])),
            "avg_holding_count": float(values["avg_holding_count"]),
            "total_return": total_return,
            "annual_return": (
                float(display_perf["annual_return"])
                if display_perf
                else float(values["annual_return"])
            ),
            "annual_vol": (
                float(display_perf["annual_vol"])
                if display_perf
                else float(values["annual_vol"])
            ),
            "sharpe_0rf": sharpe,
            "max_drawdown": max_drawdown,
            "drawdown_start_date": mdd["start_date"],
            "drawdown_end_date": mdd["end_date"],
            "monthly_turnover": monthly_turnover,
            "annual_turnover": annual_turnover,
        },
        "metrics": metrics,
        "sector": {
            "latest_rebalance_date": latest_rebalance_date_id,
            "latest_rebalance_date_text": date_text(latest_rebalance_date_id),
            "top_sector_names": top_sector_names,
            "top3_weight": top3_weight,
            "top3_weight_text": format_percent(top3_weight, digits=1),
            "description": "",
            "exposure": sector_exposure.to_dict(orient="records"),
        },
        "turnover": turnover.to_dict(orient="records"),
    }


def clean(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): clean(v) for k, v in value.items()}
    if isinstance(value, list):
        return [clean(item) for item in value]
    if hasattr(value, "item"):
        return clean(value.item())
    if isinstance(value, float) and not math.isfinite(value):
        return None
    if pd.isna(value):
        return None
    return value


def main() -> int:
    daily, holdings, rebalance_summary, summary, latest_holdings = build_backtest()
    turnover, monthly_turnover, annual_turnover = compute_turnover(holdings)
    sector_exposure = build_sector_exposure(latest_holdings)

    output_dir = ROOT / "data" / "backtest"
    output_paths = bt.output_paths(output_dir, PORTFOLIO_NAME)
    extra_paths = {
        "latest_holdings": output_dir / f"{PORTFOLIO_NAME}_latest_holdings.csv",
        "turnover": output_dir / f"{PORTFOLIO_NAME}_turnover.csv",
        "sector_exposure": output_dir / f"{PORTFOLIO_NAME}_sector_exposure.csv",
    }
    bt.write_outputs(daily, holdings, rebalance_summary, summary, output_paths)
    latest_holdings.to_csv(extra_paths["latest_holdings"], index=False)
    turnover.to_csv(extra_paths["turnover"], index=False)
    sector_exposure.to_csv(extra_paths["sector_exposure"], index=False)

    paths = {
        "daily_returns": output_paths.daily_returns,
        "holdings": output_paths.holdings,
        "rebalance_summary": output_paths.rebalance_summary,
        "summary": output_paths.summary,
        **extra_paths,
    }
    payload = panel_payload(
        daily,
        holdings,
        rebalance_summary,
        summary,
        turnover,
        sector_exposure,
        paths,
        monthly_turnover,
        annual_turnover,
    )
    OUT_PATH.write_text(
        f"window.portfolioPanelData = {json.dumps(clean(payload), ensure_ascii=False, allow_nan=False, indent=2)};\n",
        encoding="utf-8",
    )
    print(f"wrote {rel(OUT_PATH)}")
    for name, path in paths.items():
        print(f"wrote {name}: {rel(path)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
