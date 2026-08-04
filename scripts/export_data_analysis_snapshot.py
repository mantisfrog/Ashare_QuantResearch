"""Export the DataAnalysis Streamlit semantic layer for the static portfolio site.

The source database and CSV files are read-only.  The generated ``data.js`` is a
browser-friendly snapshot consumed by ``docs/data_analysis/app.js``.
"""
from __future__ import annotations

import argparse
import importlib
import json
import logging
import math
import sys
from pathlib import Path
from typing import Any

import duckdb
import numpy as np
import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = REPO_ROOT.parent / "DataAnalysis" / "CODEX-APP"
DEFAULT_OUTPUT = REPO_ROOT / "docs" / "data_analysis" / "data.js"


def frame_records(frame: pd.DataFrame) -> list[dict[str, Any]]:
    return clean(frame.to_dict(orient="records"))


def clean(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, dict):
        return {str(key): clean(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [clean(item) for item in value]
    if isinstance(value, (pd.Timestamp, pd.Period)):
        return str(value)
    if isinstance(value, np.datetime64):
        return str(pd.Timestamp(value))
    if isinstance(value, np.generic):
        value = value.item()
    if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
        return None
    return value


def read_csv(pbi_dir: Path, name: str) -> pd.DataFrame:
    return pd.read_csv(pbi_dir / f"{name}.csv", encoding="utf-8-sig")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    source = args.source.resolve()
    source_root = source.parent
    db_path = source_root / "data" / "retail_demo.duckdb"
    pbi_dir = source_root / "data" / "pbi"
    if not db_path.exists():
        raise FileNotFoundError(f"Missing source database: {db_path}")

    if str(source) not in sys.path:
        sys.path.insert(0, str(source))
    logging.getLogger("streamlit").setLevel(logging.ERROR)
    semantic = importlib.import_module("lib.data")

    con = duckdb.connect(str(db_path), read_only=True)
    query = con.execute

    calendar = query(
        """
        SELECT strftime(CAST(snapshot_date AS DATE), '%Y-%m') AS month,
               CAST(snapshot_date AS DATE) AS snapshot_date
        FROM fact_holding_snapshot
        GROUP BY month, snapshot_date ORDER BY snapshot_date
        """
    ).df()
    months = calendar["month"].astype(str).tolist()
    snapshots = dict(zip(calendar["month"].astype(str), calendar["snapshot_date"].astype(str)))

    products = query(
        """
        SELECT fund_code, fund_name, is_own_product, fund_type_l1, fund_type_l2,
               risk_level, mgmt_fee_rate, latest_aum_yi
        FROM dim_product ORDER BY is_own_product DESC, fund_name
        """
    ).df()
    product_codes = products["fund_code"].astype(str).tolist()
    scopes = ["ALL", *product_codes]

    holdings = query(
        """
        WITH detail AS (
          SELECT strftime(CAST(snapshot_date AS DATE), '%Y-%m') AS month,
                 product_code AS scope,
                 SUM(market_value) AS aum,
                 COUNT(DISTINCT customer_id) AS holding_customers
          FROM fact_holding_snapshot GROUP BY month, product_code
        ), total AS (
          SELECT strftime(CAST(snapshot_date AS DATE), '%Y-%m') AS month,
                 'ALL' AS scope,
                 SUM(market_value) AS aum,
                 COUNT(DISTINCT customer_id) AS holding_customers
          FROM fact_holding_snapshot GROUP BY month
        )
        SELECT * FROM total UNION ALL SELECT * FROM detail
        """
    ).df()
    flows = query(
        """
        WITH detail AS (
          SELECT strftime(CAST(date AS DATE), '%Y-%m') AS month,
                 product_code AS scope,
                 SUM(subscribe_amount) AS subscribe,
                 SUM(redeem_amount) AS redeem,
                 SUM(net_inflow) AS net,
                 SUM(nav_change_effect) AS nav
          FROM fact_aum_change_daily GROUP BY month, product_code
        ), total AS (
          SELECT strftime(CAST(date AS DATE), '%Y-%m') AS month,
                 'ALL' AS scope,
                 SUM(subscribe_amount) AS subscribe,
                 SUM(redeem_amount) AS redeem,
                 SUM(net_inflow) AS net,
                 SUM(nav_change_effect) AS nav
          FROM fact_aum_change_daily GROUP BY month
        )
        SELECT * FROM total UNION ALL SELECT * FROM detail
        """
    ).df()
    new_customers = query(
        """
        WITH first_product AS (
          SELECT customer_id, product_code,
                 MIN(CAST(confirm_date AS DATE)) AS first_date
          FROM fact_fund_transaction
          WHERE txn_type <> 'REDEMPTION'
          GROUP BY customer_id, product_code
        ), detail AS (
          SELECT strftime(first_date, '%Y-%m') AS month,
                 product_code AS scope, COUNT(*) AS new_customers
          FROM first_product GROUP BY month, product_code
        ), total AS (
          SELECT strftime(CAST(confirm_date AS DATE), '%Y-%m') AS month,
                 'ALL' AS scope,
                 COUNT(DISTINCT customer_id) AS new_customers
          FROM fact_fund_transaction
          WHERE is_first_purchase GROUP BY month
        )
        SELECT * FROM total UNION ALL SELECT * FROM detail
        """
    ).df()
    high_value = query(
        """
        WITH total_aum AS (
          SELECT strftime(CAST(snapshot_date AS DATE), '%Y-%m') AS month,
                 customer_id, SUM(market_value) AS total_aum
          FROM fact_holding_snapshot GROUP BY month, customer_id
        ), holders AS (
          SELECT DISTINCT strftime(CAST(snapshot_date AS DATE), '%Y-%m') AS month,
                 customer_id, product_code
          FROM fact_holding_snapshot WHERE market_value > 0
        ), detail AS (
          SELECT h.month, h.product_code AS scope, COUNT(*) AS high_value_customers
          FROM holders h JOIN total_aum t USING (month, customer_id)
          WHERE t.total_aum >= 500000 GROUP BY h.month, h.product_code
        ), total AS (
          SELECT month, 'ALL' AS scope, COUNT(*) AS high_value_customers
          FROM total_aum WHERE total_aum >= 500000 GROUP BY month
        )
        SELECT * FROM total UNION ALL SELECT * FROM detail
        """
    ).df()
    fees = query(
        """
        WITH detail AS (
          SELECT strftime(CAST(s.snapshot_date AS DATE), '%Y-%m') AS month,
                 s.product_code AS scope,
                 SUM(CASE WHEN p.is_own_product
                          THEN s.market_value * p.mgmt_fee_rate / 100.0 ELSE 0 END) AS fee_annual
          FROM fact_holding_snapshot s JOIN dim_product p ON p.fund_code = s.product_code
          GROUP BY month, s.product_code
        ), total AS (
          SELECT month, 'ALL' AS scope, SUM(fee_annual) AS fee_annual
          FROM detail GROUP BY month
        )
        SELECT * FROM total UNION ALL SELECT * FROM detail
        """
    ).df()
    churn = query(
        """
        WITH cal AS (
          SELECT CAST(snapshot_date AS DATE) AS snapshot_date,
                 strftime(CAST(snapshot_date AS DATE), '%Y-%m') AS month,
                 ROW_NUMBER() OVER (ORDER BY CAST(snapshot_date AS DATE)) AS seq
          FROM (SELECT DISTINCT snapshot_date FROM fact_holding_snapshot)
        ), holding AS (
          SELECT CAST(snapshot_date AS DATE) AS snapshot_date, customer_id,
                 product_code, SUM(market_value) AS aum
          FROM fact_holding_snapshot GROUP BY snapshot_date, customer_id, product_code
        )
        SELECT curr_cal.month, prior.product_code AS scope,
               COUNT(*) FILTER (WHERE prior.aum > 0) AS churn_base,
               COUNT(*) FILTER (WHERE prior.aum > 0 AND COALESCE(curr.aum, 0) < 1000) AS churned
        FROM holding prior
        JOIN cal prior_cal ON prior.snapshot_date = prior_cal.snapshot_date
        JOIN cal curr_cal ON curr_cal.seq = prior_cal.seq + 1
        LEFT JOIN holding curr ON curr.snapshot_date = curr_cal.snapshot_date
          AND curr.customer_id = prior.customer_id AND curr.product_code = prior.product_code
        GROUP BY curr_cal.month, prior.product_code
        """
    ).df()
    churn["product_churn"] = churn["churned"] / churn["churn_base"].replace(0, np.nan)

    grid = pd.MultiIndex.from_product([months, scopes], names=["month", "scope"]).to_frame(index=False)
    kpis = grid.merge(holdings, on=["month", "scope"], how="left")
    for table in (flows, new_customers, high_value, fees, churn[["month", "scope", "product_churn"]]):
        kpis = kpis.merge(table, on=["month", "scope"], how="left")
    fill_zero = [
        "aum", "holding_customers", "subscribe", "redeem", "net", "nav",
        "new_customers", "high_value_customers", "fee_annual",
    ]
    kpis[fill_zero] = kpis[fill_zero].fillna(0)
    kpis = kpis.sort_values(["scope", "month"])
    kpis["aum_mom"] = kpis.groupby("scope")["aum"].pct_change(fill_method=None)
    kpis["snapshot"] = kpis["month"].map(snapshots)

    alert_log = read_csv(pbi_dir, "alert_log")
    red = alert_log[alert_log["level"] == "红"].copy()
    red["month"] = pd.to_datetime(red["window_end"]).dt.strftime("%Y-%m")
    red_total = red.groupby("month", as_index=False).agg(
        red_alert_records=("alert_id", "count"),
        red_alert_entities=("entity_id", lambda s: red.loc[s.index, ["entity_type", "entity_id"]].drop_duplicates().shape[0]),
    )
    red_total["scope"] = "ALL"
    red_product = (
        red[red["entity_type"] == "产品"]
        .groupby(["month", "entity_id"], as_index=False)
        .agg(red_alert_records=("alert_id", "count"), red_alert_entities=("entity_id", "nunique"))
        .rename(columns={"entity_id": "scope"})
    )
    red_stats = pd.concat([red_total, red_product], ignore_index=True)
    kpis = kpis.merge(red_stats, on=["month", "scope"], how="left")
    kpis[["red_alert_records", "red_alert_entities"]] = kpis[["red_alert_records", "red_alert_entities"]].fillna(0)

    dim_channels = read_csv(pbi_dir, "dim_channel")
    overall_channels = read_csv(pbi_dir, "channel_monthly")
    overall_channels["scope"] = "ALL"
    overall_channels = overall_channels.merge(
        dim_channels[["channel_code", "channel_type_cn"]], on="channel_code", how="left"
    )
    overall_channels = overall_channels.rename(columns={"申购": "subscribe", "赎回": "redeem"})

    product_holding_channels = query(
        """
        SELECT strftime(CAST(snapshot_date AS DATE), '%Y-%m') AS month,
               product_code AS scope, channel_code,
               SUM(market_value) AS aum_end,
               COUNT(DISTINCT customer_id) AS customers
        FROM fact_holding_snapshot GROUP BY month, product_code, channel_code
        """
    ).df()
    product_flow_channels = query(
        """
        SELECT strftime(CAST(date AS DATE), '%Y-%m') AS month,
               product_code AS scope, channel_code,
               SUM(subscribe_amount) AS subscribe, SUM(redeem_amount) AS redeem,
               SUM(net_inflow) AS net_inflow
        FROM fact_aum_change_daily GROUP BY month, product_code, channel_code
        """
    ).df()
    product_channel_churn = query(
        """
        WITH cal AS (
          SELECT CAST(snapshot_date AS DATE) AS snapshot_date,
                 strftime(CAST(snapshot_date AS DATE), '%Y-%m') AS month,
                 ROW_NUMBER() OVER (ORDER BY CAST(snapshot_date AS DATE)) AS seq
          FROM (SELECT DISTINCT snapshot_date FROM fact_holding_snapshot)
        ), holding AS (
          SELECT CAST(snapshot_date AS DATE) AS snapshot_date, customer_id,
                 product_code, channel_code, SUM(market_value) AS aum
          FROM fact_holding_snapshot GROUP BY snapshot_date, customer_id, product_code, channel_code
        )
        SELECT curr_cal.month, prior.product_code AS scope, prior.channel_code,
               COUNT(*) FILTER (WHERE prior.aum > 0) AS base,
               COUNT(*) FILTER (WHERE prior.aum > 0 AND COALESCE(curr.aum, 0) < 1000) AS churned
        FROM holding prior
        JOIN cal prior_cal ON prior.snapshot_date = prior_cal.snapshot_date
        JOIN cal curr_cal ON curr_cal.seq = prior_cal.seq + 1
        LEFT JOIN holding curr ON curr.snapshot_date = curr_cal.snapshot_date
          AND curr.customer_id = prior.customer_id
          AND curr.product_code = prior.product_code
          AND curr.channel_code = prior.channel_code
        GROUP BY curr_cal.month, prior.product_code, prior.channel_code
        """
    ).df()
    product_channel_churn["月流失率"] = product_channel_churn["churned"] / product_channel_churn["base"].replace(0, np.nan)
    product_channels = product_holding_channels.merge(
        product_flow_channels, on=["month", "scope", "channel_code"], how="outer"
    ).merge(
        product_channel_churn[["month", "scope", "channel_code", "月流失率"]],
        on=["month", "scope", "channel_code"], how="left",
    ).merge(
        dim_channels[["channel_code", "channel_name", "channel_type_cn", "trail_commission_bps"]],
        on="channel_code", how="left",
    ).rename(columns={"customers": "客户数", "trail_commission_bps": "尾随佣金_bps"})
    for col in ["aum_end", "subscribe", "redeem", "net_inflow", "客户数"]:
        product_channels[col] = product_channels[col].fillna(0)
    product_channels["户均_aum"] = product_channels["aum_end"] / product_channels["客户数"].replace(0, np.nan)

    channel_columns = [
        "month", "scope", "channel_code", "channel_name", "channel_type_cn", "aum_end",
        "subscribe", "redeem", "net_inflow", "客户数", "户均_aum", "尾随佣金_bps", "月流失率",
    ]
    channels = pd.concat([
        overall_channels[channel_columns], product_channels[channel_columns]
    ], ignore_index=True)
    channels["aum_share"] = channels["aum_end"] / channels.groupby(["month", "scope"])["aum_end"].transform("sum").replace(0, np.nan)
    channels = channels.sort_values(["scope", "channel_code", "month"])
    channels["net_3m"] = (
        channels.groupby(["scope", "channel_code"])["net_inflow"]
        .rolling(3, min_periods=1).sum().reset_index(level=[0, 1], drop=True)
    )

    tier_mix = query(
        """
        WITH company AS (
          SELECT strftime(CAST(snapshot_date AS DATE), '%Y-%m') AS month,
                 customer_id, SUM(market_value) AS total_aum
          FROM fact_holding_snapshot GROUP BY month, customer_id
        ), all_channel AS (
          SELECT strftime(CAST(snapshot_date AS DATE), '%Y-%m') AS month,
                 customer_id, channel_code, SUM(market_value) AS aum
          FROM fact_holding_snapshot GROUP BY month, customer_id, channel_code
        ), product_exposure AS (
          SELECT DISTINCT strftime(CAST(snapshot_date AS DATE), '%Y-%m') AS month,
                 customer_id, product_code AS scope, channel_code
          FROM fact_holding_snapshot WHERE market_value > 0
        ), all_rows AS (
          SELECT month, 'ALL' AS scope, channel_code,
                 CASE WHEN aum < 10000 THEN 'T1' WHEN aum < 50000 THEN 'T2'
                      WHEN aum < 200000 THEN 'T3' WHEN aum < 1000000 THEN 'T4' ELSE 'T5' END AS tier,
                 COUNT(*) AS customers
          FROM all_channel GROUP BY month, channel_code, tier
        ), product_rows AS (
          SELECT e.month, e.scope, e.channel_code,
                 CASE WHEN c.total_aum < 10000 THEN 'T1' WHEN c.total_aum < 50000 THEN 'T2'
                      WHEN c.total_aum < 200000 THEN 'T3' WHEN c.total_aum < 1000000 THEN 'T4' ELSE 'T5' END AS tier,
                 COUNT(*) AS customers
          FROM product_exposure e JOIN company c USING (month, customer_id)
          GROUP BY e.month, e.scope, e.channel_code, tier
        )
        SELECT * FROM all_rows UNION ALL SELECT * FROM product_rows
        """
    ).df()

    health_by_month: dict[str, list[dict[str, Any]]] = {}
    risk_by_month: dict[str, list[dict[str, Any]]] = {}
    for month in months:
        health_by_month[month] = frame_records(semantic.product_health(month))
        risk_by_month[month] = frame_records(semantic.risk_return(month))

    nav = query(
        """SELECT fund_code, CAST(trade_date AS DATE) AS date, unit_nav, data_source
           FROM fact_fund_nav_daily ORDER BY fund_code, date"""
    ).df()
    weekly_flow = query(
        """
        SELECT product_code AS fund_code,
               CAST(DATE_TRUNC('week', CAST(confirm_date AS DATE)) AS DATE) AS week,
               SUM(CASE WHEN txn_type = 'REDEMPTION' THEN -confirm_amount ELSE confirm_amount END) AS net_flow
        FROM fact_fund_transaction GROUP BY product_code, week ORDER BY product_code, week
        """
    ).df()
    scale_sample = query(
        """
        SELECT quarter_id, is_own_product, SUM(aum_yi) AS aum_yi
        FROM fact_fund_scale_quarterly GROUP BY quarter_id, is_own_product
        ORDER BY quarter_id, is_own_product
        """
    ).df()
    amac = query("SELECT * FROM fact_amac_aum_ranking ORDER BY period_id, rank").df()

    status_path = source / "state" / "alert_status.csv"
    if status_path.exists() and status_path.stat().st_size:
        status = pd.read_csv(status_path, encoding="utf-8-sig")
        status_keep = [c for c in ["alert_id", "status", "owner", "note", "updated_at"] if c in status]
        alert_log = alert_log.merge(status[status_keep], on="alert_id", how="left")
    for column, default in {"status": "未处理", "owner": "", "note": "", "updated_at": ""}.items():
        if column not in alert_log:
            alert_log[column] = default
        alert_log[column] = alert_log[column].fillna(default)

    channel_alert_flows: dict[str, list[dict[str, Any]]] = {}
    for row in alert_log[alert_log["entity_type"] == "渠道"].itertuples():
        channel_alert_flows[row.alert_id] = frame_records(
            semantic.channel_flow_by_product(row.entity_id, str(row.window_start), str(row.window_end))
        )

    dormant = {month: clean(semantic.dormant_large(month)) for month in months}
    campaigns = semantic.campaign_performance()
    direct_retention = semantic.direct_app_retention()

    migration = read_csv(pbi_dir, "tier_migration_matrix")
    migration_detail = read_csv(pbi_dir, "tier_migration_detail")
    con.register("migration_matrix_export", migration)
    con.register("migration_detail_export", migration_detail)
    migration_redemptions = query(
        """
        WITH periods AS (
          SELECT DISTINCT month, prev_snapshot_date, curr_snapshot_date
          FROM migration_matrix_export
        )
        SELECT d.month, d.prev_tier, d.curr_tier, t.product_code, p.fund_name,
               COUNT(DISTINCT t.customer_id) AS customers,
               SUM(t.confirm_amount) AS redeem_amount
        FROM migration_detail_export d
        JOIN periods m USING (month)
        JOIN fact_fund_transaction t
          ON CAST(t.customer_id AS VARCHAR) = CAST(d.customer_id AS VARCHAR)
         AND t.txn_type = 'REDEMPTION'
         AND CAST(t.confirm_date AS DATE) > CAST(m.prev_snapshot_date AS DATE)
         AND CAST(t.confirm_date AS DATE) <= CAST(m.curr_snapshot_date AS DATE)
        JOIN dim_product p ON p.fund_code = t.product_code
        GROUP BY d.month, d.prev_tier, d.curr_tier, t.product_code, p.fund_name
        ORDER BY d.month, d.prev_tier, d.curr_tier, customers DESC, redeem_amount DESC
        """
    ).df()
    cohort = read_csv(pbi_dir, "cohort_retention")
    cohort["cohort"] = cohort["cohort_month"].astype(str) + " × " + cohort["channel"].astype(str)

    payload = {
        "meta": {
            "schema_version": "retail-static-v1",
            "generated_at": pd.Timestamp.now(tz="Asia/Shanghai").isoformat(timespec="seconds"),
            "latest_snapshot": snapshots[months[-1]],
            "data_property": "模拟客户经营数据",
        },
        "months": months,
        "snapshots": snapshots,
        "products": frame_records(products),
        "kpis": frame_records(kpis),
        "channels": frame_records(channels),
        "tier_mix": frame_records(tier_mix),
        "health_by_month": health_by_month,
        "risk_by_month": risk_by_month,
        "nav": frame_records(nav),
        "weekly_flow": frame_records(weekly_flow),
        "scale_sample": frame_records(scale_sample),
        "amac": frame_records(amac),
        "alerts": frame_records(alert_log),
        "alert_rules": frame_records(read_csv(pbi_dir, "alert_rule")),
        "channel_alert_flows": channel_alert_flows,
        "migration": frame_records(migration),
        "migration_detail": frame_records(migration_detail),
        "migration_redemptions": frame_records(migration_redemptions),
        "dormant": dormant,
        "cohort": frame_records(cohort),
        "precursor": frame_records(read_csv(pbi_dir, "precursor_timeline")),
        "churn_list": frame_records(read_csv(pbi_dir, "hnw_churn_list")),
        "campaigns": frame_records(campaigns),
        "direct_app_retention": clean(direct_retention),
        "tier_order": semantic.TIER_ORDER,
        "tier_labels": semantic.TIER_LABELS,
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    encoded = json.dumps(clean(payload), ensure_ascii=False, separators=(",", ":"))
    args.output.write_text(f"window.RETAIL_DATA={encoded};\n", encoding="utf-8")
    con.close()
    print(f"Wrote {args.output} ({args.output.stat().st_size / 1024 / 1024:.2f} MiB)")


if __name__ == "__main__":
    main()
