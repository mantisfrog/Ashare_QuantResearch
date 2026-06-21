"""Reusable backtest script for Size-Growth-Quality strategy.

Usage examples:
    python test_strategy.py --size-frac 0.20 --growth-frac 0.10 --quality-bottom 0.50
    python test_strategy.py --size-frac 0.30 --weight-method mcap_x_growth --cap 0.10
    python test_strategy.py --rebalance quarterly
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Backtest Size-Growth-Quality strategy.")
    parser.add_argument("--size-frac", type=float, default=0.30, help="Market cap top fraction.")
    parser.add_argument("--growth-frac", type=float, default=0.10, help="Growth score top fraction.")
    parser.add_argument("--quality-bottom", type=float, default=0.50, help="Quality score bottom fraction to exclude.")
    parser.add_argument("--weight-method", type=str, default="mcap_x_growth",
                        choices=["equal", "mcap", "growth", "mcap_x_growth"],
                        help="Portfolio weighting method.")
    parser.add_argument("--cap", type=float, default=0.10, help="Single-stock weight cap.")
    parser.add_argument("--rebalance", type=str, default="monthly", choices=["monthly", "quarterly"],
                        help="Rebalancing frequency.")
    parser.add_argument("--start", type=int, default=20250530, help="First rebalance date.")
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
    return comp, uni, daily_adj


def select_stocks(
    comp: pd.DataFrame,
    uni: pd.DataFrame,
    daily_adj: pd.DataFrame,
    date_id: int,
    size_frac: float,
    growth_frac: float,
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

    n_growth = max(1, int(len(scores) * growth_frac))
    growth_top = set(scores.nlargest(n_growth, "growth_score")["stock_code"])

    quality_threshold = scores["quality_score"].quantile(quality_bottom_frac)
    quality_ok = set(scores[scores["quality_score"] > quality_threshold]["stock_code"])

    selected = size_top[
        size_top["stock_code"].isin(growth_top) & size_top["stock_code"].isin(quality_ok)
    ].copy()
    return selected


def apply_weights(selected_df: pd.DataFrame, method: str, cap: float) -> dict[str, float]:
    if selected_df.empty:
        return {}
    df = selected_df.copy()
    n = len(df)

    if method == "equal":
        df["weight"] = 1.0 / n
    elif method == "mcap":
        df["weight"] = df["market_cap"] / df["market_cap"].sum()
    elif method == "growth":
        gs = df["growth_score"]
        gs_adj = gs - gs.min() + 1e-6 if gs.min() < 0 else gs + 1e-6
        df["weight"] = gs_adj / gs_adj.sum()
    elif method == "mcap_x_growth":
        gs = df["growth_score"]
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
    # monthly
    comp = pd.concat([
        pd.read_csv("data/factor/composite/composite_2025.csv"),
        pd.read_csv("data/factor/composite/composite_2026.csv"),
    ], ignore_index=True)
    return sorted([d for d in comp["date_id"].unique() if d >= start])


def main() -> int:
    args = parse_args()
    comp, uni, daily_adj = load_data()
    rebalance_dates = get_rebalance_dates(args.rebalance, args.start)

    periods = []
    step = 1 if args.rebalance == "monthly" else 1
    for i, date_t in enumerate(rebalance_dates[:-step]):
        date_t1 = rebalance_dates[i + step]
        selected = select_stocks(
            comp, uni, daily_adj, date_t,
            args.size_frac, args.growth_frac, args.quality_bottom,
        )
        weights = apply_weights(selected, args.weight_method, args.cap)
        if not weights:
            continue
        ret = portfolio_return(daily_adj, date_t, date_t1, weights)
        periods.append({
            "date_t": date_t,
            "date_t1": date_t1,
            "n_selected": len(weights),
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
    print(f"Cumulative return: {cum - 1:.2%}")
    print(f"Annualized return: {ann:.2%}")
    print(f"Volatility (ann):  {vol:.2%}")
    print(f"Sharpe:            {sharpe:.2f}")
    print(f"Max drawdown:      {dd:.2%}")
    print(f"Avg stocks held:   {df['n_selected'].mean():.0f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
