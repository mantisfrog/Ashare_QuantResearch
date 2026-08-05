# Retail Analytics 静态前端

该页面把 `DataAnalysis/CODEX-APP` 的 Streamlit 看板迁移为作品集可直接托管的纯 HTML/CSS/JS 版本，并沿用财富管理页面的视觉体系。

首屏提供动态领导摘要、六类零售业务场景入口和生产化补数清单。渠道价值地图使用颜色与形状双重编码区分银行、互联网和直销，相关图表均带显式图例。

移动端沿用财富管理页的顶部文档流导航，并切换为紧凑 SVG 几何、单列筛选和可触控布局；预警处置表转为字段卡片，客户迁移矩阵保留有边界的横向滚动。

## 更新数据快照

在 `Gongzuo` 仓库根目录运行：

```powershell
& C:\Users\87913\Desktop\DataAnalysis\.venv\Scripts\python.exe .\scripts\export_data_analysis_snapshot.py
```

导出器以只读方式读取相邻 `DataAnalysis` 项目的 DuckDB 与 PBI CSV，生成 `data.js`。页面不会在浏览器中加载 DuckDB 或原始交易明细。

## 静态版边界

- 预警状态、Owner 和备注保存在浏览器 `localStorage`，不会修改原始预警日志，也不会跨设备同步。
- 月报由浏览器基于当前月份与产品切片生成 Markdown 下载。
- 客户经营数据及客户编号均为模拟数据；界面默认对编号做掩码。

## 验证

```powershell
node .\tests\smoke_data_analysis_frontend.mjs
```

测试覆盖 7 个工作区、顶部导航、渠道图例、移动端紧凑渲染、核心二级页签、产品切片、预警下钻与关键业务数值锚点。
