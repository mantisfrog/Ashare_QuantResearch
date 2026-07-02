window.portfolioPanelData = {
  "meta": {
    "generated_at": "2026-07-02T16:44:16",
    "portfolio_name": "size5_growth10_quality_disabled_mcap_growth_cap10_1y",
    "calc_version": "v1",
    "latest_rebalance_date": 20260701,
    "latest_rebalance_date_text": "2026-07-01",
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
    "description": "这是一个 Size top 5% ∩ Growth top 10% 的示例组合，Quality 过滤禁用；原始权重使用市值 × 成长得分，并设置 10% 单票上限，按月调仓。"
  },
  "performance": {
    "start_date": "2025-07-01",
    "end_date": "2026-07-01",
    "trading_days": 243,
    "rebalance_count": 13,
    "holding_rows": 204,
    "avg_holding_count": 15.692307692307692,
    "total_return": 2.344560024440214,
    "annual_return": 2.497509939316473,
    "annual_vol": 0.376941108323231,
    "sharpe_0rf": 3.5162766215600207,
    "max_drawdown": -0.16266901501732223,
    "drawdown_start_date": "2025-10-29",
    "drawdown_end_date": "2025-11-24",
    "monthly_turnover": 0.2314583659029167,
    "annual_turnover": 2.7775003908350007
  },
  "metrics": [
    {
      "label": "累计收益",
      "value": "+234.46%",
      "value_class": "metric-positive",
      "note": "2025-07-01 -> 2026-07-01"
    },
    {
      "label": "夏普比率",
      "value": "3.52",
      "value_class": "",
      "note": "年化收益 / 年化波动"
    },
    {
      "label": "最大回撤",
      "value": "16.27%",
      "value_class": "metric-negative",
      "note": "2025-10-29 -> 2025-11-24"
    },
    {
      "label": "年化换手率",
      "value": "~278%",
      "value_class": "",
      "note": "月均 23.15%"
    }
  ],
  "sector": {
    "latest_rebalance_date": 20260701,
    "latest_rebalance_date_text": "2026-07-01",
    "top_sector_names": [
      "半导体",
      "通信设备",
      "消费电子"
    ],
    "top3_weight": 0.7103969473240501,
    "top3_weight_text": "71.0%",
    "description": "上图展示的是最后一期截面持仓的行业敞口，数据截至调仓日 2026-07-01。行业分类采用通达信（TDX）行业标准。组合当前主要集中于半导体、通信设备、消费电子，前三大行业合计占比 71.0%。",
    "exposure": [
      {
        "rebalance_date_id": 20260701,
        "tdx_sector_code": 881319,
        "tdx_sector_name": "半导体",
        "weight": 0.4158151241671466
      },
      {
        "rebalance_date_id": 20260701,
        "tdx_sector_code": 881338,
        "tdx_sector_name": "通信设备",
        "weight": 0.1534010057243606
      },
      {
        "rebalance_date_id": 20260701,
        "tdx_sector_code": 881326,
        "tdx_sector_name": "消费电子",
        "weight": 0.1411808174325429
      },
      {
        "rebalance_date_id": 20260701,
        "tdx_sector_code": 881294,
        "tdx_sector_name": "通用设备",
        "weight": 0.0523701802101714
      },
      {
        "rebalance_date_id": 20260701,
        "tdx_sector_code": 881094,
        "tdx_sector_name": "玻璃玻纤",
        "weight": 0.04917166691568885
      },
      {
        "rebalance_date_id": 20260701,
        "tdx_sector_code": 881303,
        "tdx_sector_name": "专用设备",
        "weight": 0.033765323219486644
      },
      {
        "rebalance_date_id": 20260701,
        "tdx_sector_code": 881055,
        "tdx_sector_name": "农用化工",
        "weight": 0.027993510523014343
      },
      {
        "rebalance_date_id": 20260701,
        "tdx_sector_code": 881336,
        "tdx_sector_name": "其他电子",
        "weight": 0.027289376267918938
      },
      {
        "rebalance_date_id": 20260701,
        "tdx_sector_code": 881290,
        "tdx_sector_name": "航海装备",
        "weight": 0.024106886327037492
      },
      {
        "rebalance_date_id": 20260701,
        "tdx_sector_code": 881449,
        "tdx_sector_name": "航运港口",
        "weight": 0.02293425667671916
      },
      {
        "rebalance_date_id": 20260701,
        "tdx_sector_code": 881082,
        "tdx_sector_name": "稀有金属",
        "weight": 0.02101945287198604
      },
      {
        "rebalance_date_id": 20260701,
        "tdx_sector_code": 881275,
        "tdx_sector_name": "光伏设备",
        "weight": 0.01620958049016487
      },
      {
        "rebalance_date_id": 20260701,
        "tdx_sector_code": 881262,
        "tdx_sector_name": "电池",
        "weight": 0.014742819173762132
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
      "turnover": 0.15416958279517515
    }
  ]
};
