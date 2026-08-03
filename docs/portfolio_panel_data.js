window.portfolioPanelData = {
  "meta": {
    "generated_at": "2026-07-31T23:26:05",
    "portfolio_name": "size5_growth10_quality_disabled_mcap_growth_cap10_1y",
    "calc_version": "v1",
    "latest_rebalance_date": 20260731,
    "latest_rebalance_date_text": "2026-07-31",
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
    "start_date": "2025-07-31",
    "end_date": "2026-07-31",
    "trading_days": 243,
    "rebalance_count": 13,
    "holding_rows": 204,
    "avg_holding_count": 15.692307692307692,
    "total_return": 0.7721126229883124,
    "annual_return": 0.8100672110945508,
    "annual_vol": 0.45367839326090076,
    "sharpe_0rf": 1.541104108069014,
    "max_drawdown": -0.4172826546928985,
    "drawdown_start_date": "2026-06-25",
    "drawdown_end_date": "2026-07-30",
    "monthly_turnover": 0.2314583041636272,
    "annual_turnover": 2.7774996499635263
  },
  "metrics": [
    {
      "label": "累计收益",
      "value": "+77.21%",
      "value_class": "metric-positive",
      "note": "2025-07-31 -> 2026-07-31"
    },
    {
      "label": "夏普比率",
      "value": "1.54",
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
      "value": "~278%",
      "value_class": "",
      "note": "月均 23.15%"
    }
  ],
  "sector": {
    "latest_rebalance_date": 20260731,
    "latest_rebalance_date_text": "2026-07-31",
    "top_sector_names": [
      "半导体",
      "通信设备",
      "消费电子"
    ],
    "top3_weight": 0.6555053599627527,
    "top3_weight_text": "65.6%",
    "description": "",
    "exposure": [
      {
        "rebalance_date_id": 20260731,
        "tdx_sector_code": 881319,
        "tdx_sector_name": "半导体",
        "weight": 0.3694625925614845
      },
      {
        "rebalance_date_id": 20260731,
        "tdx_sector_code": 881338,
        "tdx_sector_name": "通信设备",
        "weight": 0.1457498736203993
      },
      {
        "rebalance_date_id": 20260731,
        "tdx_sector_code": 881326,
        "tdx_sector_name": "消费电子",
        "weight": 0.14029289378086898
      },
      {
        "rebalance_date_id": 20260731,
        "tdx_sector_code": 881333,
        "tdx_sector_name": "元器件",
        "weight": 0.05428230944039497
      },
      {
        "rebalance_date_id": 20260731,
        "tdx_sector_code": 881294,
        "tdx_sector_name": "通用设备",
        "weight": 0.05252838471417037
      },
      {
        "rebalance_date_id": 20260731,
        "tdx_sector_code": 881055,
        "tdx_sector_name": "农用化工",
        "weight": 0.03862420997015594
      },
      {
        "rebalance_date_id": 20260731,
        "tdx_sector_code": 881290,
        "tdx_sector_name": "航海装备",
        "weight": 0.0385353257674168
      },
      {
        "rebalance_date_id": 20260731,
        "tdx_sector_code": 881094,
        "tdx_sector_name": "玻璃玻纤",
        "weight": 0.037523380947030185
      },
      {
        "rebalance_date_id": 20260731,
        "tdx_sector_code": 881359,
        "tdx_sector_name": "云服务",
        "weight": 0.03603768422276939
      },
      {
        "rebalance_date_id": 20260731,
        "tdx_sector_code": 881449,
        "tdx_sector_name": "航运港口",
        "weight": 0.03507179686277693
      },
      {
        "rebalance_date_id": 20260731,
        "tdx_sector_code": 881303,
        "tdx_sector_name": "专用设备",
        "weight": 0.03186491286284619
      },
      {
        "rebalance_date_id": 20260731,
        "tdx_sector_code": 881275,
        "tdx_sector_name": "光伏设备",
        "weight": 0.020026635249686394
      }
    ]
  },
  "turnover": [
    {
      "rebalance_date_id": 20250630,
      "rebalance_date": "2025-06-30",
      "turnover": null
    },
    {
      "rebalance_date_id": 20250731,
      "rebalance_date": "2025-07-31",
      "turnover": 0.060899451119089794
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
    }
  ]
};
