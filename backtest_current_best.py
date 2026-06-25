"""
Standalone backtest for the current best strategy.

Strategy logic:
    - Universe: A-share stocks passing liquidity filter
    - Size filter: top 10% by market cap
    - Growth filter: top 10% by growth_score
    - Quality filter: exclude bottom 50% by quality_score
    - Weighting: market_cap * growth_score
    - Single-stock cap: 10%
    - Rebalancing: monthly

Backtest window: 2025-06-24 to 2026-06-24
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / "data"
FACTOR_DIR = DATA_DIR / "factor"


# ---------------------------------------------------------------------------
# Parameters
# ---------------------------------------------------------------------------
DEFAULT_START = 20250624
DEFAULT_END = 20260624

SIZE_FRAC = 0.10          # top 10% market cap
GROWTH_FRAC = 0.10        # top 10% growth score
QUALITY_BOTTOM = 0.50     # exclude bottom 50% quality
CAP = 0.10                # 10% single-stock weight cap


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Backtest current best strategy.")
    parser.add_argument("--start", type=int, default=DEFAULT_START, help="First rebalance date.")
    parser.add_argument("--end", type=int, default=DEFAULT_END, help="Last evaluation date.")
    parser.add_argument("--size-frac", type=float, default=SIZE_FRAC)
    parser.add_argument("--growth-frac", type=float, default=GROWTH_FRAC)
    parser.add_argument("--quality-bottom", type=float, default=QUALITY_BOTTOM)
    parser.add_argument("--cap", type=float, default=CAP)
    parser.add_argument("--weight", type=str, default="mcap_x_growth",
                        choices=["equal", "mcap", "growth", "mcap_x_growth"])
    parser.add_argument("--disable-quality", action="store_true",
                        help="Disable quality filter.")
    parser.add_argument("--output", type=str, default=None,
                        help="Path to output monthly NAV curve CSV.")
    parser.add_argument("--output-daily", type=str, default=None,
                        help="Path to output daily NAV curve CSV (date, nav only).")
    parser.add_argument("--output-sector", type=str, default=None,
                        help="Path to output final holding sector exposure CSV.")
    return parser.parse_args()


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------
def load_composite() -> pd.DataFrame:
    frames = []
    for year in (2025, 2026):
        path = FACTOR_DIR / "composite" / f"composite_{year}.csv"
        if path.exists():
            frames.append(pd.read_csv(path))
    return pd.concat(frames, ignore_index=True)


def load_universe() -> pd.DataFrame:
    frames = []
    for year in (2025, 2026):
        path = FACTOR_DIR / "universe" / f"universe_{year}.csv"
        if path.exists():
            frames.append(pd.read_csv(path))
    return pd.concat(frames, ignore_index=True)


def load_prices() -> pd.DataFrame:
    daily = pd.read_csv(DATA_DIR / "fact_daily.csv",
                        usecols=["date_id", "stock_code", "close", "market_cap"])
    adj = pd.read_csv(DATA_DIR / "fact_adjustment_factor_period.csv")
    daily = daily.merge(adj, on="stock_code", how="left")
    daily = daily[
        (daily["date_id"] >= daily["valid_from_date_id"])
        & (daily["date_id"] <= daily["valid_to_date_id"])
    ]
    daily["adj_close"] = daily["close"] * daily["adjust_factor"]
    return daily[["date_id", "stock_code", "adj_close", "market_cap"]]


# ---------------------------------------------------------------------------
# Stock selection
# ---------------------------------------------------------------------------
def select_stocks(
    comp: pd.DataFrame,
    uni: pd.DataFrame,
    prices: pd.DataFrame,
    date_id: int,
    size_frac: float,
    growth_frac: float,
    quality_bottom: float,
    disable_quality: bool = False,
) -> pd.DataFrame | None:
    """Return selected stocks with scores and market cap for one rebalance date."""
    scores = comp[comp["date_id"] == date_id].copy()
    if scores.empty:
        return None

    # Apply universe filter
    uni_codes = uni[(uni["date_id"] == date_id) & (uni["in_universe"].astype(bool))]["stock_code"].unique()
    scores = scores[scores["stock_code"].isin(uni_codes)].copy()
    if scores.empty:
        return None

    # Merge market cap
    mc = prices[prices["date_id"] == date_id][["stock_code", "market_cap"]]
    scores = scores.merge(mc, on="stock_code", how="inner")
    if scores.empty:
        return None

    # Size filter: top size_frac by market cap
    size_threshold = scores["market_cap"].quantile(1 - size_frac)
    selected = scores[scores["market_cap"] >= size_threshold].copy()
    if selected.empty:
        return None

    # Growth filter: top growth_frac by growth_score
    n_growth = max(1, int(len(scores) * growth_frac))
    growth_top = set(scores.nlargest(n_growth, "growth_score")["stock_code"])
    selected = selected[selected["stock_code"].isin(growth_top)].copy()
    if selected.empty:
        return None

    # Quality filter: exclude bottom quality_bottom (unless disabled)
    if not disable_quality:
        quality_threshold = scores["quality_score"].quantile(quality_bottom)
        selected = selected[selected["quality_score"] > quality_threshold].copy()
        if selected.empty:
            return None

    return selected


# ---------------------------------------------------------------------------
# Weighting
# ---------------------------------------------------------------------------
def apply_weights(df: pd.DataFrame, method: str, cap: float) -> dict[str, float]:
    if df.empty:
        return {}

    df = df.copy()
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

    # Iterative cap redistribution
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


# ---------------------------------------------------------------------------
# Portfolio return
# ---------------------------------------------------------------------------
def portfolio_return(
    prices: pd.DataFrame,
    date_t: int,
    date_t1: int,
    weights: dict[str, float],
) -> float:
    if not weights:
        return 0.0

    p0 = prices[prices["date_id"] == date_t][["stock_code", "adj_close"]].rename(columns={"adj_close": "p0"})
    p1 = prices[prices["date_id"] == date_t1][["stock_code", "adj_close"]].rename(columns={"adj_close": "p1"})
    pr = p0.merge(p1, on="stock_code", how="inner")
    pr["ret"] = pr["p1"] / pr["p0"] - 1
    pr["weight"] = pr["stock_code"].map(weights)
    pr = pr[pr["weight"].notna()].copy()
    if pr.empty:
        return 0.0
    return (pr["weight"] * pr["ret"]).sum()


def build_daily_nav(periods_df: pd.DataFrame, prices: pd.DataFrame) -> pd.DataFrame:
    """Build a daily NAV series from monthly weights and daily prices.

    Within each holding period the portfolio is buy-and-hold with fixed shares,
    so the daily portfolio value is sum(start_weight_i * price_i_t / price_i_start).
    """
    if periods_df.empty:
        return pd.DataFrame(columns=["date", "nav"])

    nav_records = []
    current_nav = 1.0

    for _, row in periods_df.iterrows():
        date_t = int(row["date_t"])
        date_t1 = int(row["date_t1"])
        weights = row["weights"]
        if not weights:
            continue

        stocks = list(weights.keys())

        # Start-of-period prices
        p_start = prices[(prices["date_id"] == date_t) & (prices["stock_code"].isin(stocks))]
        p_start = p_start.set_index("stock_code")["adj_close"]
        if p_start.empty:
            continue

        # Daily prices for the period
        period_prices = prices[
            (prices["date_id"] >= date_t) & (prices["date_id"] <= date_t1)
            & (prices["stock_code"].isin(stocks))
        ][["date_id", "stock_code", "adj_close"]].copy()

        if period_prices.empty:
            continue

        price_wide = period_prices.pivot(index="date_id", columns="stock_code", values="adj_close")

        # Portfolio value relative to start = sum(weight_i * price_t / price_start)
        # Use only stocks with valid start prices
        valid_stocks = [s for s in stocks if s in p_start.index and s in price_wide.columns]
        if not valid_stocks:
            continue

        relative_value = pd.Series(0.0, index=price_wide.index)
        for s in valid_stocks:
            relative_value += weights[s] * price_wide[s] / p_start[s]

        # Scale by current NAV
        for d, rel in relative_value.items():
            nav_records.append({"date": int(d), "nav": current_nav * rel})

        current_nav *= relative_value.iloc[-1]

    return pd.DataFrame(nav_records)


def build_sector_exposure(periods_df: pd.DataFrame) -> pd.DataFrame | None:
    """Aggregate the last portfolio weights by TDX industry sector."""
    if periods_df.empty:
        return None

    last_row = periods_df.iloc[-1]
    weights = last_row["weights"]
    if not weights:
        return None

    # Load mappings
    try:
        stock_map = pd.read_csv(DATA_DIR / "dim_stock.csv")[["stock_code", "tdx_sector_code"]]
        sector_map = pd.read_csv(DATA_DIR / "dim_tdx_industry.csv")
    except FileNotFoundError:
        print("Warning: industry mapping files not found.")
        return None

    weights_df = pd.DataFrame.from_dict(weights, orient="index", columns=["weight"]).reset_index()
    weights_df.columns = ["stock_code", "weight"]
    weights_df = weights_df.merge(stock_map, on="stock_code", how="left")
    weights_df = weights_df.merge(sector_map, on="tdx_sector_code", how="left")

    # Aggregate by sector
    sector_exp = weights_df.groupby(["tdx_sector_code", "tdx_sector_name"], as_index=False)["weight"].sum()
    sector_exp = sector_exp.sort_values("weight", ascending=False).reset_index(drop=True)
    sector_exp.columns = ["tdx_sector_code", "tdx_sector_name", "weight"]

    # Add total row
    total = pd.DataFrame({
        "tdx_sector_code": ["TOTAL"],
        "tdx_sector_name": ["TOTAL"],
        "weight": [sector_exp["weight"].sum()],
    })
    sector_exp = pd.concat([sector_exp, total], ignore_index=True)
    return sector_exp


# ---------------------------------------------------------------------------
# Backtest engine
# ---------------------------------------------------------------------------
def run_backtest(args: argparse.Namespace) -> pd.DataFrame:
    comp = load_composite()
    uni = load_universe()
    prices = load_prices()

    # Rebalance dates within window
    all_dates = sorted(comp["date_id"].unique())
    rebalance_dates = [d for d in all_dates if args.start <= d <= args.end]
    if len(rebalance_dates) < 2:
        raise ValueError(f"Need at least 2 rebalance dates between {args.start} and {args.end}")

    periods = []
    prev_weights: dict[str, float] = {}
    for i in range(len(rebalance_dates) - 1):
        date_t = rebalance_dates[i]
        date_t1 = rebalance_dates[i + 1]

        selected = select_stocks(
            comp, uni, prices, date_t,
            args.size_frac, args.growth_frac, args.quality_bottom,
            args.disable_quality,
        )
        if selected is None:
            continue

        weights = apply_weights(selected, args.weight, args.cap)
        if not weights:
            continue

        ret = portfolio_return(prices, date_t, date_t1, weights)

        # Turnover: half the sum of absolute weight changes vs previous period
        all_stocks = set(prev_weights.keys()) | set(weights.keys())
        turnover = 0.5 * sum(abs(weights.get(s, 0.0) - prev_weights.get(s, 0.0)) for s in all_stocks)

        periods.append({
            "date_t": date_t,
            "date_t1": date_t1,
            "n_stocks": len(weights),
            "ret": ret,
            "turnover": turnover,
            "weights": weights,
        })
        prev_weights = weights

    return pd.DataFrame(periods)


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------
def print_report(df: pd.DataFrame, args: argparse.Namespace, prices: pd.DataFrame) -> None:
    if df.empty:
        print("No periods to evaluate.")
        return

    df = df.copy()
    df["cum"] = (1 + df["ret"]).cumprod()
    df["nav"] = df["cum"]

    # Output monthly NAV curve CSV if requested
    if args.output:
        nav_df = df[["date_t1", "ret", "nav", "n_stocks", "turnover"]].copy()
        nav_df.columns = ["date", "period_return", "nav", "n_stocks", "turnover"]
        nav_df.to_csv(args.output, index=False, float_format="%.6f")
        print(f"Monthly NAV curve saved to: {args.output}")
        print()

    # Output daily NAV curve CSV if requested
    if args.output_daily:
        daily_nav = build_daily_nav(df, prices)
        daily_nav.to_csv(args.output_daily, index=False, float_format="%.6f")
        print(f"Daily NAV curve saved to: {args.output_daily}")
        print()

    # Output final sector exposure CSV if requested
    if args.output_sector:
        sector_df = build_sector_exposure(df)
        if sector_df is not None:
            sector_df.to_csv(args.output_sector, index=False, float_format="%.4f")
            print(f"Sector exposure saved to: {args.output_sector}")
            print(sector_df.to_string(index=False))
            print()

    print("=" * 80)
    print("CURRENT BEST STRATEGY BACKTEST")
    print("=" * 80)
    print(f"Window     : {args.start} -> {args.end}")
    quality_str = "DISABLED" if args.disable_quality else f"not bottom {args.quality_bottom:.0%}"
    print(f"Logic      : Size top {args.size_frac:.0%} AND Growth top {args.growth_frac:.0%} "
          f"AND Quality {quality_str}")
    print(f"Weighting  : {args.weight}")
    print(f"Cap        : {args.cap:.0%}")
    print(f"Rebalance  : monthly")
    print("=" * 80)
    print()

    print(df.to_string(index=False))
    print()

    ret = df["ret"]
    cum = df["cum"].iloc[-1]
    n = len(df)
    ann = cum ** (12 / n) - 1
    vol = ret.std() * np.sqrt(12)
    sharpe = (ret.mean() * 12) / vol if vol > 0 else 0
    dd = (1 - (1 + ret).cumprod() / (1 + ret).cumprod().cummax()).max()

    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Periods         : {n}")
    print(f"Cumulative ret  : {cum - 1:+.2%}")
    print(f"Annualized ret  : {ann:+.2%}")
    print(f"Annualized vol  : {vol:.2%}")
    print(f"Sharpe ratio    : {sharpe:.2f}")
    print(f"Max drawdown    : {dd:.2%}")
    print(f"Avg stocks held : {df['n_stocks'].mean():.1f}")
    print(f"Win rate        : {(ret > 0).mean():.1%}")
    print(f"Best month      : {ret.max():+.2%}")
    print(f"Worst month     : {ret.min():+.2%}")
    print(f"Avg turnover    : {df['turnover'].mean():.2%}")
    print(f"Total turnover  : {df['turnover'].sum():.2%}")
    print("=" * 80)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> int:
    args = parse_args()
    df = run_backtest(args)
    prices = load_prices()
    print_report(df, args, prices)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
