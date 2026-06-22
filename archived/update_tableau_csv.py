#!/home/wbi/job/.venv/bin/python3
"""
使用 akshare 更新 raw/index_gz/ 目录下的 CSV 指数行情文件，并自动同步到对应的 Google Sheets。

规则：
1. 仅在「CSV 最新日期 < 今天」且「北京时间 > 16:30」时才执行更新。
2. 依次尝试三个接口：stock_zh_index_daily_tx -> stock_zh_index_daily_em -> index_zh_a_hist。
   某个接口只要能返回可用数据即停止，并立即把该文件已取到的数据写回 CSV，再继续下一个文件。
3. 默认每次请求后间隔 15 秒；接口失败时重试间隔依次提升为 30 秒、60 秒；仍然失败则尝试下一个接口。
4. 仅更新 CSV 中已存在的列，不新增列，并保持原编码（utf-8-sig BOM）、表头与数值格式。
5. 本地 CSV 更新成功后，自动把该文件完整覆盖同步到对应的 Google Sheet 第一个工作表。
   对于明确标记为不需要同步的指数（如 000985_中证全指），则跳过 Google Sheet 同步。
6. 全部 9 个文件处理完毕后，仅当存在失败文件时：生成 log/日期_fail.log，并调用 archived/telegram_msg.py 发送一次汇总消息。
   若本地 CSV 更新成功但 Google Sheet 同步失败，也会汇总到失败通知中。
"""

import csv
import logging
import os
import subprocess
import sys
import time
from datetime import datetime, time as dt_time
from pathlib import Path
from zoneinfo import ZoneInfo

os.environ.setdefault("TQDM_DISABLE", "1")

import akshare as ak
import gspread
import pandas as pd
from google.oauth2.service_account import Credentials

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
RAW_DIR = PROJECT_ROOT / "raw/index_gz"
LOG_DIR = PROJECT_ROOT / "log"
TELEGRAM_SCRIPT = SCRIPT_DIR / "telegram_msg.py"
GOOGLE_SHEET_SERVICE_ACCOUNT = PROJECT_ROOT / "google_sheet_service_account.json"

ENCODING = "utf-8-sig"
DATE_FMT_FILE = "%Y-%m-%d"
DATE_FMT_API = "%Y%m%d"
DEFAULT_START_DATE = "19900101"
BJ_TZ = ZoneInfo("Asia/Shanghai")
UPDATE_AFTER = dt_time(16, 30)

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# CSV stem -> Google Spreadsheet ID 的映射
# 未在此映射中的指数默认会尝试同步；若同时出现在 NO_SYNC_STEMS 中，则明确跳过同步。
SPREADSHEET_IDS = {
    "399370_国证成长": "119PrHGTmvZT3qiYYYN2JB-mIf27ImzDdlv9aIdQbSBU",
    "399371_国证价值": "1CUI3KSLoUQaLWASHvCL4oQ7iMdlYw_Su9p2Fi5xEDT8",
    "399372_大盘成长": "1478p0lQbby82cflybIQJP_5YyoY75tWXViaK_Ne8_rU",
    "399373_大盘价值": "1FmbEZaNFzCBFg666ykYqpYotva6fPb5HCmpyazHpZyM",
    "399374_中盘成长": "1DLZlhqTqEOnOTLwPYXC9T0xMVogX85JsgbEWYCqRV5E",
    "399375_中盘价值": "1qHC3a522LGawtTwkSitHL0fWYRvnPqtiFpxyj33DRdo",
    "399376_小盘成长": "1wklNljB4r-9vJa9S3hiz-vtI9qAN1Pq3upmIZbN5uZI",
    "399377_小盘价值": "1-BDVi162yH5QWPSn7bnydUgeCnCs1sOpEJXhtUkhsh0",
}

# 明确不需要同步到 Google Sheets 的指数文件
NO_SYNC_STEMS = {
    "000985_中证全指",
}


def fetch_tx(code: str, prefix: str, start_date: str, end_date: str) -> pd.DataFrame:
    return ak.stock_zh_index_daily_tx(
        symbol=f"{prefix}{code}", start_date=start_date, end_date=end_date
    )


def fetch_em(code: str, prefix: str, start_date: str, end_date: str) -> pd.DataFrame:
    return ak.stock_zh_index_daily_em(
        symbol=f"{prefix}{code}", start_date=start_date, end_date=end_date
    )


def fetch_hist(code: str, start_date: str, end_date: str) -> pd.DataFrame:
    return ak.index_zh_a_hist(
        symbol=code, period="daily", start_date=start_date, end_date=end_date
    )


API_CONFIGS = [
    {
        "name": "stock_zh_index_daily_tx",
        "fetch": fetch_tx,
        "column_map": {
            "date": "日期",
            "open": "开盘价",
            "close": "收盘价",
            "high": "最高价",
            "low": "最低价",
            # TX 的 amount 列实际为成交量，单位：手
            "amount": "成交量(万手)",
        },
        "conversions": {
            "成交量(万手)": lambda x: x / 10000.0,
        },
    },
    {
        "name": "stock_zh_index_daily_em",
        "fetch": fetch_em,
        "column_map": {
            "date": "日期",
            "open": "开盘价",
            "close": "收盘价",
            "high": "最高价",
            "low": "最低价",
            "volume": "成交量(万手)",
        },
        "conversions": {
            "成交量(万手)": lambda x: x / 10000.0,
        },
    },
    {
        "name": "index_zh_a_hist",
        "fetch": fetch_hist,
        "column_map": {
            "日期": "日期",
            "开盘": "开盘价",
            "收盘": "收盘价",
            "最高": "最高价",
            "最低": "最低价",
            "成交量": "成交量(万手)",
        },
        "conversions": {
            "成交量(万手)": lambda x: x / 10000.0,
        },
    },
]


def setup_logging() -> Path:
    """设置日志同时输出到控制台和日期_fail.log文件；成功运行后删除该文件。"""
    LOG_DIR.mkdir(exist_ok=True)
    today_str = now_beijing().strftime("%Y%m%d")
    log_file = LOG_DIR / f"{today_str}_fail.log"
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s: %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(log_file, encoding="utf-8"),
        ],
    )
    return log_file


def now_beijing() -> datetime:
    return datetime.now(BJ_TZ)


def get_symbol_prefix(code: str) -> str:
    """根据指数代码猜测市场前缀。"""
    if code.startswith("000") or code.startswith("88") or code.startswith("95"):
        return "sh"
    return "sz"


def read_existing_csv(path: Path) -> pd.DataFrame:
    """读取已有 CSV，统一把日期列解析为 datetime。"""
    df = pd.read_csv(path, encoding=ENCODING)
    if "日期" not in df.columns:
        raise ValueError(f"{path.name} 缺少必需的 '日期' 列")
    df["日期"] = pd.to_datetime(df["日期"], errors="coerce")
    return df


def should_update(path: Path) -> tuple[bool, str]:
    """
    判断是否需要更新该文件。
    返回 (是否更新, 原因说明)。
    """
    now_bj = now_beijing()
    if now_bj.time() <= UPDATE_AFTER:
        return False, f"北京时间 {now_bj.strftime('%H:%M')} 未过 15:30"

    try:
        existing = read_existing_csv(path)
    except Exception as e:
        return True, f"读取失败，默认需要更新: {e}"

    if existing.empty:
        return True, "文件为空"

    latest_date = existing["日期"].max().date()
    today = now_bj.date()
    if latest_date >= today:
        return False, f"最新日期 {latest_date} 已是今天或更晚"
    return True, f"最新日期 {latest_date} 早于今天 {today}"


def format_value(col: str, val) -> str:
    """按原 CSV 格式输出数值。"""
    if pd.isna(val):
        return ""
    if col in ("开盘价", "收盘价", "最高价", "最低价"):
        return f"{float(val):.2f}"
    if col == "成交量(万手)":
        return f"{float(val):.1f}"
    return str(val)


def update_file(path: Path, new_df: pd.DataFrame) -> None:
    """将新数据合并到原 CSV，保持原表头、顺序与格式。"""
    file_cols = list(pd.read_csv(path, nrows=0, encoding=ENCODING).columns)

    existing = read_existing_csv(path)

    # 允许覆盖最近一天的数据（可能已有更新），删除更早的重复日期
    if not new_df.empty and "日期" in new_df.columns:
        min_new_date = new_df["日期"].min()
        existing = existing[existing["日期"] < min_new_date]

    combined = pd.concat([existing, new_df], ignore_index=True)
    combined = combined.sort_values("日期", ascending=False)
    combined["日期"] = combined["日期"].dt.strftime(DATE_FMT_FILE)

    # 保证列顺序与文件一致；API 未提供的列会用 NaN 填充
    combined = combined[[c for c in file_cols if c in combined.columns]]

    with open(path, "w", encoding=ENCODING, newline="") as f:
        writer = csv.writer(f)
        writer.writerow(file_cols)
        for _, row in combined.iterrows():
            writer.writerow([format_value(c, row.get(c, "")) for c in file_cols])


def try_update_file(path: Path, code: str, prefix: str, start_date: str, end_date: str) -> tuple[bool, str]:
    """依次尝试三个接口更新单个文件，返回 (是否成功, 使用的接口名)。"""
    file_cols = list(pd.read_csv(path, nrows=0, encoding=ENCODING).columns)
    for api in API_CONFIGS:
        # 若接口明确无法覆盖 CSV 所有列，直接跳过，避免无意义请求
        api_file_cols = set(api["column_map"].values())
        if not set(file_cols).issubset(api_file_cols):
            missing = set(file_cols) - api_file_cols
            logging.info(
                f"{path.name} [{api['name']}] 无法提供列 {sorted(missing)}，跳过"
            )
            continue

        wait = 15
        for attempt in range(3):
            if attempt > 0:
                time.sleep(wait)
            try:
                if api["name"] in ("stock_zh_index_daily_tx", "stock_zh_index_daily_em"):
                    raw_df = api["fetch"](code, prefix, start_date, end_date)
                else:
                    raw_df = api["fetch"](code, start_date, end_date)

                if raw_df is None:
                    raise ValueError("返回 None")
                if raw_df.empty:
                    logging.info(f"{path.name} [{api['name']}] 返回空数据，视为已是最新")
                    return True, api["name"]

                mapper = {k: v for k, v in api["column_map"].items() if k in raw_df.columns}
                if not mapper:
                    raise ValueError("返回数据中无可用列")

                df = raw_df[list(mapper.keys())].rename(columns=mapper)
                for col, fn in api["conversions"].items():
                    if col in df.columns:
                        df[col] = pd.to_numeric(df[col], errors="coerce").apply(fn)

                df["日期"] = pd.to_datetime(df["日期"], errors="coerce")
                df = df.dropna(subset=["日期"])

                # “完成任务”要求接口能提供 CSV 中所有已存在的列；否则尝试下一个接口
                missing_cols = [c for c in file_cols if c not in df.columns]
                if missing_cols:
                    raise ValueError(f"返回数据缺少文件列: {missing_cols}")

                # 每完成一次成功的请求就立即把数据写回 CSV
                update_file(path, df)
                logging.info(f"{path.name} 使用 {api['name']} 更新成功")

                # 成功请求后间隔 15 秒
                time.sleep(15)
                return True, api["name"]
            except Exception as e:
                logging.warning(
                    f"{path.name} [{api['name']}] 第 {attempt + 1} 次尝试失败: {e}"
                )
                if wait == 15:
                    wait = 30
                elif wait == 30:
                    wait = 60
                else:
                    # 已达 60 秒仍失败，跳出重试循环尝试下一个接口
                    break
        # 当前接口全部失败后，间隔 15 秒再尝试下一个接口
        time.sleep(15)
    return False, "all_failed"


def get_gsheet_client():
    """使用服务账号创建 gspread 客户端。"""
    if not GOOGLE_SHEET_SERVICE_ACCOUNT.exists():
        raise FileNotFoundError(f"服务账号文件不存在: {GOOGLE_SHEET_SERVICE_ACCOUNT}")
    creds = Credentials.from_service_account_file(
        str(GOOGLE_SHEET_SERVICE_ACCOUNT), scopes=SCOPES
    )
    return gspread.authorize(creds)


def sync_csv_to_gsheet(path: Path, sheet_key: str) -> tuple[bool, str]:
    """将本地 CSV 完整覆盖同步到指定 Google Sheet 的第一个工作表。"""
    try:
        client = get_gsheet_client()
        sh = client.open_by_key(sheet_key)
        ws = sh.get_worksheet(0)
        if ws is None:
            raise ValueError("未找到第一个工作表")

        df = pd.read_csv(path, encoding=ENCODING)
        values = [df.columns.tolist()] + [
            [format_value(col, row[col]) for col in df.columns]
            for _, row in df.iterrows()
        ]

        ws.clear()
        ws.update(range_name="A1", values=values, value_input_option="USER_ENTERED")
        return True, f"已同步 {len(values) - 1} 行数据"
    except Exception as e:
        return False, str(e)


def send_telegram(message: str) -> None:
    """调用项目自带的 telegram_msg.py 发送消息（不修改该脚本）。"""
    if not TELEGRAM_SCRIPT.exists():
        logging.error(f"Telegram 脚本不存在: {TELEGRAM_SCRIPT}")
        return
    try:
        subprocess.run(
            [sys.executable, str(TELEGRAM_SCRIPT), "--text", message],
            check=True,
            cwd=str(PROJECT_ROOT),
        )
        logging.info("Telegram 消息已发送")
    except Exception as e:
        logging.error(f"发送 Telegram 消息失败: {e}")


def main() -> int:
    log_file = setup_logging()

    if not RAW_DIR.exists():
        logging.error(f"raw 目录不存在: {RAW_DIR}")
        return 1

    csv_files = sorted(RAW_DIR.glob("*.csv"))
    if not csv_files:
        logging.warning(f"{RAW_DIR} 下未找到 CSV 文件")
        return 0

    failures: list[str] = []
    gsheet_failures: list[str] = []

    for idx, path in enumerate(csv_files):
        stem = path.stem
        code = stem.split("_")[0]
        prefix = get_symbol_prefix(code)

        need, reason = should_update(path)
        logging.info(
            f"[{idx + 1}/{len(csv_files)}] {path.name} ({code}) -> {reason}"
        )
        if not need:
            continue

        try:
            existing = read_existing_csv(path)
            start_date = (
                existing["日期"].max().strftime(DATE_FMT_API)
                if not existing.empty
                else DEFAULT_START_DATE
            )
        except Exception:
            start_date = DEFAULT_START_DATE

        end_date = now_beijing().strftime(DATE_FMT_API)
        success, used = try_update_file(path, code, prefix, start_date, end_date)
        if not success:
            msg = f"{path.name} 所有接口均失败"
            logging.error(msg)
            failures.append(msg)
            continue

        if stem in NO_SYNC_STEMS:
            logging.info(f"{path.name} 标记为不需要 Google Sheet 同步，跳过")
            continue

        sheet_key = SPREADSHEET_IDS.get(stem)
        if sheet_key:
            gs_success, gs_msg = sync_csv_to_gsheet(path, sheet_key)
            if gs_success:
                logging.info(f"{path.name} Google Sheet 同步成功: {gs_msg}")
            else:
                msg = f"{path.name} Google Sheet 同步失败: {gs_msg}"
                logging.warning(msg)
                gsheet_failures.append(msg)
        else:
            logging.warning(f"{path.name} 未找到对应的 Google Sheet ID，跳过同步")

    failures.extend(gsheet_failures)

    if failures:
        summary = "指数 CSV 更新失败:\n" + "\n".join(failures)
        send_telegram(summary)
        logging.info(f"失败日志已写入: {log_file}")
        return 1

    logging.info("全部文件更新完成")
    close_logging_handlers()
    log_file.unlink(missing_ok=True)
    return 0

def close_logging_handlers() -> None:
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        handler.flush()
        handler.close()
        root_logger.removeHandler(handler)

if __name__ == "__main__":
    raise SystemExit(main())
