window.portfolioPanelData = {
  "meta": {
    "generated_at": "2026-08-07T23:13:55",
    "portfolio_name": "size5_growth10_quality_disabled_mcap_growth_cap10_1y",
    "calc_version": "v1",
    "latest_rebalance_date": 20260807,
    "latest_rebalance_date_text": "2026-08-07",
    "output_files": {
      "daily_returns": "data/backtest/size5_growth10_quality_disabled_mcap_growth_cap10_1y_daily_returns.csv",
      "holdings": "data/backtest/size5_growth10_quality_disabled_mcap_growth_cap10_1y_holdings.csv",
      "rebalance_summary": "data/backtest/size5_growth10_quality_disabled_mcap_growth_cap10_1y_rebalance_summary.csv",
      "summary": "data/backtest/size5_growth10_quality_disabled_mcap_growth_cap10_1y_summary.csv",
      "latest_holdings": "data/backtest/size5_growth10_quality_disabled_mcap_growth_cap10_1y_latest_holdings.csv",
      "turnover": "data/backtest/size5_growth10_quality_disabled_mcap_growth_cap10_1y_turnover.csv",
      "sector_exposure": "data/backtest/size5_growth10_quality_disabled_mcap_growth_cap10_1y_sector_exposure.csv"
    }
  },
  "strategy": {
    "logic": "Size top 5% ∩ Growth top 10%, Quality 禁用",
    "weighting": "市值 × 成长得分",
    "max_weight": "10%",
    "rebalance_frequency": "月度",
    "description": ""
  },
  "performance": {
    "source": "data/backtest/size5_growth10_quality_disabled_mcap_growth_cap10_1y_daily_returns.csv",
    "start_date": "2025-08-07",
    "end_date": "2026-08-07",
    "trading_days": 243,
    "rebalance_count": 13,
    "holding_rows": 212,
    "avg_holding_count": 16.307692307692307,
    "total_return": 1.006412352663658,
    "annual_return": 1.0588321471474242,
    "annual_vol": 0.464909511853309,
    "sharpe_0rf": 1.7935550073264925,
    "max_drawdown": -0.41728265469289827,
    "drawdown_start_date": "2026-06-25",
    "drawdown_end_date": "2026-07-30",
    "monthly_turnover": 0.2456674860754496,
    "annual_turnover": 2.948009832905395
  },
  "metrics": [
    {
      "label": "累计收益",
      "value": "+100.64%",
      "value_class": "metric-positive",
      "note": "2025-08-07 -> 2026-08-07"
    },
    {
      "label": "夏普比率",
      "value": "1.79",
      "value_class": "",
      "note": "年化收益 / 年化波动"
    },
    {
      "label": "最大回撤",
      "value": "41.73%",
      "value_class": "metric-negative",
      "note": "2026-06-25 -> 2026-07-30"
    },
    {
      "label": "年化换手率",
      "value": "~295%",
      "value_class": "",
      "note": "月均 24.57%"
    }
  ],
  "sector": {
    "latest_rebalance_date": 20260807,
    "latest_rebalance_date_text": "2026-08-07",
    "top_sector_names": [
      "半导体",
      "通信设备",
      "消费电子"
    ],
    "top3_weight": 0.6851467817908519,
    "top3_weight_text": "68.5%",
    "description": "",
    "exposure": [
      {
        "rebalance_date_id": 20260807,
        "tdx_sector_code": 881319,
        "tdx_sector_name": "半导体",
        "weight": 0.38811880003543664
      },
      {
        "rebalance_date_id": 20260807,
        "tdx_sector_code": 881338,
        "tdx_sector_name": "通信设备",
        "weight": 0.15241376451883673
      },
      {
        "rebalance_date_id": 20260807,
        "tdx_sector_code": 881326,
        "tdx_sector_name": "消费电子",
        "weight": 0.14461421723657858
      },
      {
        "rebalance_date_id": 20260807,
        "tdx_sector_code": 881294,
        "tdx_sector_name": "通用设备",
        "weight": 0.06335035217359321
      },
      {
        "rebalance_date_id": 20260807,
        "tdx_sector_code": 881290,
        "tdx_sector_name": "航海装备",
        "weight": 0.04522960326886621
      },
      {
        "rebalance_date_id": 20260807,
        "tdx_sector_code": 881094,
        "tdx_sector_name": "玻璃玻纤",
        "weight": 0.0438477210111205
      },
      {
        "rebalance_date_id": 20260807,
        "tdx_sector_code": 881055,
        "tdx_sector_name": "农用化工",
        "weight": 0.038193402359696864
      },
      {
        "rebalance_date_id": 20260807,
        "tdx_sector_code": 881303,
        "tdx_sector_name": "专用设备",
        "weight": 0.03608272269638007
      },
      {
        "rebalance_date_id": 20260807,
        "tdx_sector_code": 881449,
        "tdx_sector_name": "航运港口",
        "weight": 0.035227090979247415
      },
      {
        "rebalance_date_id": 20260807,
        "tdx_sector_code": 881359,
        "tdx_sector_name": "云服务",
        "weight": 0.033347335663763786
      },
      {
        "rebalance_date_id": 20260807,
        "tdx_sector_code": 881275,
        "tdx_sector_name": "光伏设备",
        "weight": 0.01957499005648014
      }
    ]
  },
  "turnover": [
    {
      "rebalance_date_id": 20250731,
      "rebalance_date": "2025-07-31",
      "turnover": null
    },
    {
      "rebalance_date_id": 20250829,
      "rebalance_date": "2025-08-29",
      "turnover": 0.41858629646015255
    },
    {
      "rebalance_date_id": 20250930,
      "rebalance_date": "2025-09-30",
      "turnover": 0.21168075974799253
    },
    {
      "rebalance_date_id": 20251031,
      "rebalance_date": "2025-10-31",
      "turnover": 0.47018673082481244
    },
    {
      "rebalance_date_id": 20251128,
      "rebalance_date": "2025-11-28",
      "turnover": 0.13935514537650492
    },
    {
      "rebalance_date_id": 20251231,
      "rebalance_date": "2025-12-31",
      "turnover": 0.128773004505313
    },
    {
      "rebalance_date_id": 20260130,
      "rebalance_date": "2026-01-30",
      "turnover": 0.0910557436019423
    },
    {
      "rebalance_date_id": 20260227,
      "rebalance_date": "2026-02-27",
      "turnover": 0.06413554122348122
    },
    {
      "rebalance_date_id": 20260331,
      "rebalance_date": "2026-03-31",
      "turnover": 0.23234521912763992
    },
    {
      "rebalance_date_id": 20260430,
      "rebalance_date": "2026-04-30",
      "turnover": 0.6643563071626367
    },
    {
      "rebalance_date_id": 20260529,
      "rebalance_date": "2026-05-29",
      "turnover": 0.14195660889026052
    },
    {
      "rebalance_date_id": 20260630,
      "rebalance_date": "2026-06-30",
      "turnover": 0.15416884192370095
    },
    {
      "rebalance_date_id": 20260731,
      "rebalance_date": "2026-07-31",
      "turnover": 0.23140963406095802
    }
  ]
};
