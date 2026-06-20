# ETL 更新流程

## 项目结构

- 入口脚本 `update_etl.py` 位于项目根目录，是唯一对外入口。
- 具体实现脚本位于 `etl/`：`update_csv_pipeline.py`、`build_dim_stock.py`、
  `build_fact_daily.py`、`build_fact_dividend.py`、`build_adjustment_factor.py`、
  `build_financial_csv.py`、`build_postgres_from_csv.py`、`etl_logging.py`、`paths.py`。
- 生成的 CSV 输出到 `data/`，已在 `.gitignore` 中忽略。
- 原始 TDX 数据在 `raw/`、日志在 `log/`，均不纳入 git（`raw/index_gz` 除外）。
- 所有脚本通过 `etl/paths.py` 统一解析项目根、`data/`、`raw/`、`log/` 等路径。

## 一键完整更新

激活 `.venv` 后，在项目根目录执行：

```powershell
python update_etl.py
```

默认会执行完整 ETL：

1. 下载 `https://data.tdx.com.cn/vipdoc/hsjday.zip` 到 `raw/hsjday.zip`。
2. 解压 `hsjday.zip` 到 `raw/vipdoc/`，生成或覆盖 `sh/lday`、`sz/lday` 下的 `.day` 文件。
3. 下载 `https://data.tdx.com.cn/vipdoc/tdxfin.zip` 到 `raw/tdxfin.zip`。
4. 解压 `tdxfin.zip` 到 `raw/vipdoc/cw/`，生成或覆盖 `gpcw*.dat` 文件。
5. 运行 CSV 生成管道。
6. 用当前 CSV 执行 PostgreSQL 全量重建，默认传入 `--reset`。
7. 对重建后的 PostgreSQL 数据库执行 `--validate-only` 校验。

raw 下载优先使用系统 `curl.exe`，包含重试、连接超时和低速超时；如果 TDX
触发反爬 challenge，脚本会先解析 cookie，再自动重试下载真实 zip。

每次运行会在 `log/` 目录生成一份 summary log，例如
`log/etl_20260617_123456.log`。终端只显示阶段汇总和耗时任务进度，详细的
每阶段汇总会追加到该 log 文件。

脚本会捕获 tqcenter 接口内部输出，例如初始化成功、服务端返回空值等重复
消息。终端只在阶段结束时展示去重后的摘要，完整摘要会写入 summary log；
致命错误仍会中断当前 ETL 并给出股票代码和样例。

脚本不再生成诊断型 CSV，例如 `*_errors.csv`、`*_skipped.csv`。错误数量、
跳过数量和少量样例会写入 summary log；致命错误仍会直接中断当前 ETL。

数据库连接信息来自项目根目录 `.env`。如果 `.env` 中没有 `POSTGRES_DB`，
可以临时指定数据库名：

```powershell
python update_etl.py --database tdx_quant
```

如果数据库不存在并且希望脚本创建：

```powershell
python update_etl.py --database tdx_quant --create-db
```

## CSV 生成顺序

`update_csv_pipeline.py` 会按以下顺序执行：

1. 更新 raw 文件。
2. 从 `.day` 文件名同步 `dim_stock.csv` 的 `stock_code` 列。
   - 已有股票信息会保留。
   - 只保留 `6xxxxx.SH`、`0xxxxx.SZ`、`30xxxx.SZ`。
   - 新增股票先写空的 `stock_name`、`tdx_sector_code`。
   - 已不在 `.day` 文件中的代码会从 `dim_stock.csv` 移除。
3. 从 `.day` 文件记录和 `gpcw*.dat` 财务公告日期同步 `dim_date.csv`。
   - 保证日期维度覆盖所有日线交易日期和财务公告日期。
   - `is_trade_day=True` 来自 `.day` 中实际出现过的日期。
   - `trade_day_index` 是交易日按日期升序排列的序号，从 1 开始。
   - 非交易日的 `trade_day_index` 留空，导入 PostgreSQL 后为 `NULL`。
   - 文件按日期倒序保存。
4. 运行 `build_dim_stock.py`。
   - 调用 `tq.get_stock_info` 补充 `stock_name`、`tdx_sector_code`。
   - 生成 `dim_tdx_industry.csv`，股票维度不重复保存行业名称。
   - 股票详情补充属于可选元数据增强；如果 tqcenter 连续返回空值，脚本会熔断
     后续详情查询，保留已有字段或空值继续生成 CSV。
5. 运行 `build_fact_daily.py`。
   - 从 `.day` 二进制文件重建 `fact_daily.csv`。
   - 对每只股票调用一次 `tq.get_gb_info`，覆盖该股票本地 `.day` 中全部交易日期。
   - 写入 `total_shares`、`float_shares`、`market_cap`、`float_market_cap`。
   - 市值单位为万元，按不复权收盘价和股本计算；股本缺失时四列同时留空，
     并在 summary log 中记录覆盖率 warning。
6. 运行 `build_fact_dividend.py`。
   - 调用 `tq.get_divid_factors` 重建 `fact_dividend.csv`。
7. 运行 `build_adjustment_factor.py`。
   - 只使用 `fact_daily.csv` 的不复权收盘价和 `fact_dividend.csv` 的公司行为。
   - 重建 `fact_adjustment_factor_period.csv`，每行表示一只证券在一个交易日区间内不变的后复权因子 `adjust_factor`。
   - 无法落到当前日线区间的公司行为数量和样例写入 summary log。
8. 运行 `build_financial_csv.py`。
   - 从 `gpcw*.dat` 重建：
     - `dim_financial_metric.csv`
     - `fact_financial_report.csv`
     - `fact_financial_value.csv`
     - `bridge_trade_day_financial_report.csv`
   - 财务指标定义来自 `knowledge/FINVALUE.csv` 中 `field_kind=metric` 的行。
   - 不在 `dim_stock.csv` 中的 raw 代码数量和样例写入 summary log。

## 常用参数

跳过 raw 下载，直接使用本地已有 raw 文件：

```powershell
python update_etl.py --skip-raw-download
```

只同步前置维度，不重建大型事实表，也不重建 PostgreSQL：

```powershell
python update_etl.py --precheck-only
```

只生成 CSV，不重建 PostgreSQL：

```powershell
python update_etl.py --skip-db
```

重建 PostgreSQL 时不使用 `--reset`：

```powershell
python update_etl.py --no-db-reset
```

跳过数据库重建后的校验：

```powershell
python update_etl.py --skip-db-validate
```

`build_postgres_from_csv.py` 在加载数据库前会先检查所有 CSV 表头。若当前
CSV 仍是旧 schema，脚本会在连接和删表前失败，并提示需要先重建对应 CSV。

跳过某个 CSV 阶段：

```powershell
python update_etl.py --skip-stock-info
python update_etl.py --skip-daily
python update_etl.py --skip-dividend
python update_etl.py --skip-adjustment
python update_etl.py --skip-financial
```

参数可以组合，例如只更新 raw、维度、分红、复权和财务，不重建日线：

```powershell
python update_etl.py --skip-daily
```
