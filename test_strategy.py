"""Reusable backtest script for Size-Growth-Quality strategy and style overlays.

Usage examples:
    # Baseline optimal
    python test_strategy.py --size-frac 0.20 --growth-frac 0.10 --quality-bottom 0.50

    # With style satellite
    python test_strategy.py --satellite-style reversal --satellite-frac 0.10

    # Risk-off overlay
    python test_strategy.py --risk-overlay

    # IC contrarian overlay
    python test_strategy.py --ic-contrarian

    # Sequential filtering
    python test_strategy.py --size-frac 0.20 --growth-frac 0.10 --quality-bottom 0.50 --sequential
"""
from __future__ import annotations

import argparse

import numpy as np
import pandas as pd


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Backtest Size-Growth-Quality strategy.")
    parser.add_argument("--size-frac", type=float, default=0.30, help="Market cap top fraction.")
    parser.add_argument("--growth-frac", type=float, default=0.10, help="Growth score top fraction.")
    parser.add_argument("--quality-bottom", type=float, default=0.50, help="Quality score bottom fraction to exclude.")
    parser.add_argument("--value-bottom", type=float, default=None, help="Optional value score bottom fraction to exclude.")
    parser.add_argument("--weight-method", type=str, default="mcap_x_growth",
                        choices=["equal", "mcap", "growth", "mcap_x_growth"],
                        help="Portfolio weighting method.")
    parser.add_argument("--cap", type=float, default=0.10, help="Single-stock weight cap.")
    parser.add_argument("--rebalance", type=str, default="monthly", choices=["monthly", "quarterly"],
                        help="Rebalancing frequency.")
    parser.add_argument("--start", type=int, default=20250530, help="First rebalance date.")
    parser.add_argument("--sequential", action="store_true",
                        help="Use sequential filtering: size -> growth -> quality, recalculating ranks at each step.")
    parser.add_argument("--satellite-style", type=str, default=None,
                        choices=["value", "quality", "growth", "momentum", "reversal", "risk"],
                        help="Satellite style to blend with core growth strategy.")
    parser.add_argument("--satellite-frac", type=float, default=0.10, help="Fraction allocated to satellite style.")
    parser.add_argument("--risk-overlay", action="store_true",
                        help="When previous month market return < -5%, shift 20% to risk style.")
    parser.add_argument("--ic-contrarian", action="store_true",
                        help="If growth IC rank <=2 over past 2m, shift 20% to worst recent non-growth style.")
    return parser.parse_args()


def load_data():
    comp = pd.concat([
        pd.read_csv("data/factor/composite/composite_2025.csv"),
        pd.read_csv("data/factor/composite/composite_2026.csv"),
    ], ignore_index=True)

    uni = pd.concat([
        pd.read_csv("data/factor/universe/universe_2025.csv"),
        pd.read_csv("data/factor/universe/universe_2026.csv"),
    ], ignore_index=True)

    daily = pd.read_csv("data/fact_daily.csv", usecols=["date_id", "stock_code", "close", "market_cap"])
    adj = pd.read_csv("data/fact_adjustment_factor_period.csv")
    daily_adj = daily.merge(adj, on="stock_code", how="left")
    daily_adj = daily_adj[
        (daily_adj["date_id"] >= daily_adj["valid_from_date_id"])
        & (daily_adj["date_id"] <= daily_adj["valid_to_date_id"])
    ]
    daily_adj["adj_close"] = daily_adj["close"] * daily_adj["adjust_factor"]
    daily_adj = daily_adj[["date_id", "stock_code", "adj_close", "market_cap"]].copy()

    diag = pd.concat([
        pd.read_csv("data/factor/diagnostics/diagnostics_2025.csv"),
        pd.read_csv("data/factor/diagnostics/diagnostics_2026.csv"),
    ], ignore_index=True)

    style_map = {
        'ep_ttm': 'value', 'bp_mrq': 'value', 'sp_ttm': 'value', 'cfp_ttm': 'value', 'div_yield_ttm': 'value',
        'roe_ttm': 'quality', 'gross_margin': 'quality', 'accruals': 'quality',
        'revenue_growth_yoy': 'growth', 'profit_growth_yoy': 'growth',
        'gross_margin_yoy_chg_2q_avg': 'growth', 'earnings_accel_2q_avg': 'growth',
        'mom_12_1': 'momentum', 'reversal_1m': 'reversal',
        'volatility_252d': 'risk', 'turnover_21d': 'risk',
    }
    diag["style"] = diag["factor_code"].map(style_map)
    style_ic = diag.groupby(["date_id", "style"])["rank_ic_1m"].mean().unstack()
    style_ic = style_ic[["value", "quality", "growth", "momentum", "reversal", "risk"]]

    return comp, uni, daily_adj, style_ic


def select_stocks(
    comp: pd.DataFrame,
    uni: pd.DataFrame,
    daily_adj: pd.DataFrame,
    date_id: int,
    style: str,
    size_frac: float,
    style_frac: float,
    quality_bottom_frac: float,
) -> pd.DataFrame:
    scores = comp[comp["date_id"] == date_id].copy()
    uni_t = uni[(uni["date_id"] == date_id) & (uni["in_universe"].astype(bool))]["stock_code"].unique()
    scores = scores[scores["stock_code"].isin(uni_t)].copy()
    if scores.empty:
        return pd.DataFrame()

    mc = daily_adj[daily_adj["date_id"] == date_id][["stock_code", "market_cap"]]
    scores = scores.merge(mc, on="stock_code", how="inner")
    if scores.empty:
        return pd.DataFrame()

    size_threshold = scores["market_cap"].quantile(1 - size_frac)
    size_top = scores[scores["market_cap"] >= size_threshold]

    style_col = f"{style}_score"
    n_style = max(1, int(len(scores) * style_frac))
    style_top = set(scores.nlargest(n_style, style_col)["stock_code"])

    quality_threshold = scores["quality_score"].quantile(quality_bottom_frac)
    quality_ok = set(scores[scores["quality_score"] > quality_threshold]["stock_code"])

    selected = size_top[size_top["stock_code"].isin(style_top) & size_top["stock_code"].isin(quality_ok)].copy()
    return selected


def select_stocks_sequential(
    comp: pd.DataFrame,
    uni: pd.DataFrame,
    daily_adj: pd.DataFrame,
    date_id: int,
    size_frac: float,
    growth_frac: float,
    quality_bottom_frac: float,
    value_bottom_frac: float | None = None,
) -> pd.DataFrame:
    scores = comp[comp["date_id"] == date_id].copy()
    uni_t = uni[(uni["date_id"] == date_id) & (uni["in_universe"].astype(bool))]["stock_code"].unique()
    scores = scores[scores["stock_code"].isin(uni_t)].copy()
    if scores.empty:
        return pd.DataFrame()

    mc = daily_adj[daily_adj["date_id"] == date_id][["stock_code", "market_cap"]]
    scores = scores.merge(mc, on="stock_code", how="inner")
    if scores.empty:
        return pd.DataFrame()

    size_threshold = scores["market_cap"].quantile(1 - size_frac)
    candidates = scores[scores["market_cap"] >= size_threshold].copy()
    if candidates.empty:
        return pd.DataFrame()

    n_growth = max(1, int(len(candidates) * growth_frac))
    candidates = candidates.nlargest(n_growth, "growth_score").copy()
    if candidates.empty:
        return pd.DataFrame()

    n_quality = max(1, int(len(candidates) * (1 - quality_bottom_frac)))
    candidates = candidates.nlargest(n_quality, "quality_score").copy()
    if candidates.empty:
        return pd.DataFrame()

    if value_bottom_frac is not None:
        n_value = max(1, int(len(candidates) * (1 - value_bottom_frac)))
        selected = candidates.nlargest(n_value, "value_score").copy()
    else:
        selected = candidates.copy()
    return selected


def apply_weights(selected_df: pd.DataFrame, method: str, cap: float, style: str = "growth") -> dict[str, float]:
    if selected_df.empty:
        return {}
    df = selected_df.copy()
    n = len(df)
    style_col = f"{style}_score"

    if method == "equal":
        df["weight"] = 1.0 / n
    elif method == "mcap":
        df["weight"] = df["market_cap"] / df["market_cap"].sum()
    elif method == "growth":
        gs = df[style_col]
        gs_adj = gs - gs.min() + 1e-6 if gs.min() < 0 else gs + 1e-6
        df["weight"] = gs_adj / gs_adj.sum()
    elif method == "mcap_x_growth":
        gs = df[style_col]
        gs_adj = gs - gs.min() + 1e-6 if gs.min() < 0 else gs + 1e-6
        score = df["market_cap"] * gs_adj
        df["weight"] = score / score.sum()
    else:
        raise ValueError(method)

    weights = df.set_index("stock_code")["weight"].copy()
    while True:
        over = weights > cap
        if not over.any():
            break
        excess = (weights[over] - cap).sum()
        weights[over] = cap
        under = weights < cap
        if under.sum() == 0:
            break
        weights[under] += weights[under] / weights[under].sum() * excess
    return weights.to_dict()


def combine_weights(weights_list: list[tuple[dict[str, float], float]], cap: float) -> dict[str, float]:
    combined: dict[str, float] = {}
    for weights, frac in weights_list:
        for s, w in weights.items():
            combined[s] = combined.get(s, 0.0) + w * frac

    weights = pd.Series(combined)
    while True:
        over = weights > cap
        if not over.any():
            break
        excess = (weights[over] - cap).sum()
        weights[over] = cap
        under = weights < cap
        if under.sum() == 0:
            break
        weights[under] += weights[under] / weights[under].sum() * excess
    return weights.to_dict()


def portfolio_return(daily_adj: pd.DataFrame, date_t: int, date_t1: int, weights: dict[str, float]) -> float:
    if not weights:
        return 0.0
    p0 = daily_adj[daily_adj["date_id"] == date_t][["stock_code", "adj_close"]].rename(columns={"adj_close": "p0"})
    p1 = daily_adj[daily_adj["date_id"] == date_t1][["stock_code", "adj_close"]].rename(columns={"adj_close": "p1"})
    pr = p0.merge(p1, on="stock_code", how="inner")
    pr["ret"] = pr["p1"] / pr["p0"] - 1
    pr["weight"] = pr["stock_code"].map(weights)
    pr = pr[pr["weight"].notna()].copy()
    if pr.empty:
        return 0.0
    return (pr["weight"] * pr["ret"]).sum()


def get_rebalance_dates(rebalance: str, start: int) -> list[int]:
    if rebalance == "quarterly":
        return [d for d in [20250530, 20250829, 20251128, 20260227, 20260529] if d >= start]
    comp = pd.concat([
        pd.read_csv("data/factor/composite/composite_2025.csv"),
        pd.read_csv("data/factor/composite/composite_2026.csv"),
    ], ignore_index=True)
    return sorted([d for d in comp["date_id"].unique() if d >= start])


def get_recent_ic(style_ic: pd.DataFrame, date_id: int, lookback: int) -> pd.Series | None:
    ic_dates = sorted(style_ic.index)
    prior = [d for d in ic_dates if d < date_id]
    if len(prior) < lookback:
        return None
    return style_ic.loc[prior[-lookback:]].mean()


def main() -> int:
    args = parse_args()
    comp, uni, daily_adj, style_ic = load_data()
    rebalance_dates = get_rebalance_dates(args.rebalance, args.start)

    # Precompute market returns for risk overlay
    market_rets: dict[int, float] = {}
    for i, date_t in enumerate(rebalance_dates[:-1]):
        date_t1 = rebalance_dates[i + 1]
        p0 = daily_adj[daily_adj["date_id"] == date_t][["stock_code", "adj_close"]].rename(columns={"adj_close": "p0"})
        p1 = daily_adj[daily_adj["date_id"] == date_t1][["stock_code", "adj_close"]].rename(columns={"adj_close": "p1"})
        pr = p0.merge(p1, on="stock_code", how="inner")
        pr["ret"] = pr["p1"] / pr["p0"] - 1
        market_rets[date_t1] = pr["ret"].mean()

    periods = []
    for i, date_t in enumerate(rebalance_dates[:-1]):
        date_t1 = rebalance_dates[i + 1]

        if args.sequential:
            core_selected = select_stocks_sequential(
                comp, uni, daily_adj, date_t,
                args.size_frac, args.growth_frac, args.quality_bottom, args.value_bottom,
            )
        else:
            core_selected = select_stocks(
                comp, uni, daily_adj, date_t, "growth",
                args.size_frac, args.growth_frac, args.quality_bottom,
            )
        core_weights = apply_weights(core_selected, args.weight_method, args.cap, "growth")

        satellite_frac = 0.0
        satellite_style = args.satellite_style

        if args.satellite_style:
            satellite_frac = args.satellite_frac
        elif args.risk_overlay:
            prev_ret = market_rets.get(date_t, 0.0)
            if prev_ret < -0.05:
                satellite_style = "risk"
                satellite_frac = 0.20
        elif args.ic_contrarian:
            recent_ic = get_recent_ic(style_ic, date_t, 2)
            if recent_ic is not None and recent_ic.rank()["growth"] <= 2:
                satellite_style = recent_ic.drop("growth").idxmin()
                satellite_frac = 0.20

        weights_list: list[tuple[dict[str, float], float]] = [(core_weights, 1 - satellite_frac)]
        if satellite_style and satellite_frac > 0:
            sat_selected = select_stocks(
                comp, uni, daily_adj, date_t, satellite_style,
                args.size_frac, args.growth_frac, args.quality_bottom,
            )
            sat_weights = apply_weights(sat_selected, args.weight_method, args.cap, satellite_style)
            weights_list.append((sat_weights, satellite_frac))

        weights = combine_weights(weights_list, args.cap)
        if not weights:
            continue

        ret = portfolio_return(daily_adj, date_t, date_t1, weights)
        periods.append({
            "date_t": date_t,
            "date_t1": date_t1,
            "n_selected": len(weights),
            "satellite_style": satellite_style if satellite_frac > 0 else "none",
            "satellite_frac": satellite_frac,
            "ret_strategy": ret,
        })

    df = pd.DataFrame(periods)
    if df.empty:
        print("No periods to evaluate.")
        return 0

    df["cum_strategy"] = (1 + df["ret_strategy"]).cumprod()
    print(df.to_string(index=False))

    ret = df["ret_strategy"]
    cum = df["cum_strategy"].iloc[-1]
    n = len(df)
    if args.rebalance == "monthly":
        ann = cum ** (12 / n) - 1
        vol = ret.std() * np.sqrt(12)
    else:
        ann = cum ** (4 / n) - 1
        vol = ret.std() * np.sqrt(4)
    sharpe = (ret.mean() * (12 if args.rebalance == "monthly" else 4)) / vol if vol > 0 else 0
    dd = (1 - (1 + ret).cumprod() / (1 + ret).cumprod().cummax()).max()

    print("\n=== SUMMARY ===")
    print(f"Parameters: size_frac={args.size_frac}, growth_frac={args.growth_frac}, "
          f"quality_bottom={args.quality_bottom}, weight={args.weight_method}, cap={args.cap}, rebalance={args.rebalance}")
    if args.satellite_style:
        print(f"Satellite: {args.satellite_style} {args.satellite_frac:.0%}")
    if args.risk_overlay:
        print("Risk overlay: enabled")
    if args.ic_contrarian:
        print("IC contrarian overlay: enabled")
    print(f"Cumulative return: {cum - 1:.2%}")
    print(f"Annualized return: {ann:.2%}")
    print(f"Volatility (ann):  {vol:.2%}")
    print(f"Sharpe:            {sharpe:.2f}")
    print(f"Max drawdown:      {dd:.2%}")
    print(f"Avg stocks held:   {df['n_selected'].mean():.0f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
