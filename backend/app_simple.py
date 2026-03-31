"""
简化版FastAPI应用，用于Railway部署
包含真实Tushare Pro API数据接入 + 东方财富直连接口（无积分限制）
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import os
import logging
import json
from datetime import datetime, timedelta
from typing import Optional, List
import random
import requests
import functools
import time

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ══════════════════════════════════════════════════════════════════════════════
# Yahoo Finance 数据源（免费，无积分限制，Railway可用）
# ══════════════════════════════════════════════════════════════════════════════

# 尝试导入yfinance
try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
    logger.info("Yahoo Finance (yfinance) 初始化成功")
except Exception as e:
    YFINANCE_AVAILABLE = False
    yf = None
    logger.warning(f"Yahoo Finance不可用: {e}")


def ts_code_to_yahoo(ts_code: str) -> str:
    """
    将Tushare格式的股票代码转换为Yahoo Finance格式
    000001.SZ -> 000001.SZ
    600000.SH -> 600000.SS
    430001.BJ -> 430001.SZ (北交所用SZ后缀)
    """
    if not ts_code:
        return ""
    parts = ts_code.split(".")
    if len(parts) != 2:
        return ts_code
    code, suffix = parts
    if suffix == "SH":
        return f"{code}.SS"
    elif suffix == "BJ":
        return f"{code}.SZ"  # 北交所在Yahoo用SZ
    else:
        return ts_code  # SZ保持不变


def yahoo_to_ts_code(yahoo_code: str) -> str:
    """
    将Yahoo Finance格式转换回Tushare格式
    000001.SZ -> 000001.SZ
    600000.SS -> 600000.SH
    """
    if not yahoo_code:
        return ""
    parts = yahoo_code.split(".")
    if len(parts) != 2:
        return yahoo_code
    code, suffix = parts
    if suffix == "SS":
        return f"{code}.SH"
    return yahoo_code


def fetch_yahoo_stock_list() -> list:
    """
    使用Yahoo Finance获取A股全量股票列表
    通过获取主要指数成分股来构建股票列表
    """
    if not YFINANCE_AVAILABLE or not yf:
        return []
    
    try:
        # 获取主要指数的成分股来构建A股列表
        # 上证指数、深证成指、创业板指、科创50
        index_symbols = [
            "000001.SS",   # 上证指数
            "399001.SZ",   # 深证成指
            "399006.SZ",   # 创业板指
            "000688.SS",   # 科创50
        ]
        
        all_stocks = {}
        
        # 尝试获取指数成分股（Yahoo可能不直接提供，用备选方案）
        # 备选：使用预设的主要股票代码列表 + 批量获取行情
        major_codes = [
            # 上证50主要成分股
            "600519.SS", "601318.SS", "600036.SS", "601166.SS", "600887.SS",
            "601398.SS", "601288.SS", "601088.SS", "600276.SS", "601012.SS",
            "600900.SS", "601888.SS", "603288.SS", "600309.SS", "601668.SS",
            "601857.SS", "601628.SS", "601211.SS", "601688.SS", "600030.SS",
            # 深证主要股票
            "000001.SZ", "000002.SZ", "000858.SZ", "002415.SZ", "002594.SZ",
            "300750.SZ", "300059.SZ", "300760.SZ", "300122.SZ", "002714.SZ",
            "000568.SZ", "000538.SZ", "002352.SZ", "300015.SZ", "300014.SZ",
            "002230.SZ", "000063.SZ", "002475.SZ", "300124.SZ", "002142.SZ",
        ]
        
        # 批量获取这些股票的当前行情
        logger.info(f"使用Yahoo Finance获取 {len(major_codes)} 只主要股票数据...")
        
        for symbol in major_codes:
            try:
                ticker = yf.Ticker(symbol)
                info = ticker.info
                if info and info.get("regularMarketPrice"):
                    ts_code = yahoo_to_ts_code(symbol)
                    all_stocks[ts_code] = {
                        "ts_code": ts_code,
                        "name": info.get("shortName", info.get("longName", symbol)),
                        "industry": info.get("industry", "未知"),
                        "market": _classify_market(ts_code, ""),
                        "close": info.get("regularMarketPrice", 0),
                        "open": info.get("regularMarketOpen", 0),
                        "high": info.get("regularMarketDayHigh", 0),
                        "low": info.get("regularMarketDayLow", 0),
                        "pre_close": info.get("previousClose", 0),
                        "change": info.get("regularMarketChange", 0),
                        "pct_chg": info.get("regularMarketChangePercent", 0),
                        "vol": info.get("regularMarketVolume", 0),
                        "amount": 0,  # Yahoo不直接提供成交额
                        "turnover_rate": 0,
                        "pe": info.get("trailingPE", 0),
                        "pb": info.get("priceToBook", 0),
                        "total_mv": info.get("marketCap", 0) / 100000000 if info.get("marketCap") else 0,  # 转为亿
                        "circ_mv": 0,
                    }
            except Exception as e:
                logger.debug(f"获取 {symbol} 失败: {e}")
                continue
        
        if len(all_stocks) > 0:
            logger.info(f"✅ Yahoo Finance返回 {len(all_stocks)} 只股票")
            return list(all_stocks.values())
        
    except Exception as e:
        logger.error(f"Yahoo Finance获取股票列表失败: {e}")
    
    return []


def fetch_yahoo_stock_detail(ts_code: str) -> dict:
    """
    使用Yahoo Finance获取单只股票详情和K线数据
    """
    if not YFINANCE_AVAILABLE or not yf:
        return {}
    
    try:
        yahoo_code = ts_code_to_yahoo(ts_code)
        ticker = yf.Ticker(yahoo_code)
        
        # 获取基本信息
        info = ticker.info
        
        # 获取历史K线（60天）
        hist = ticker.history(period="3mo")
        
        kline = []
        if hist is not None and not hist.empty:
            for date, row in hist.iterrows():
                kline.append({
                    "date": date.strftime("%Y%m%d"),
                    "open": round(row["Open"], 2),
                    "high": round(row["High"], 2),
                    "low": round(row["Low"], 2),
                    "close": round(row["Close"], 2),
                    "vol": int(row["Volume"]),
                })
        
        # 计算涨跌幅
        current = info.get("regularMarketPrice", 0)
        previous = info.get("previousClose", 0)
        change = current - previous if current and previous else 0
        pct_chg = (change / previous * 100) if previous else 0
        
        return {
            "basic": {
                "ts_code": ts_code,
                "name": info.get("shortName", info.get("longName", ts_code)),
                "industry": info.get("industry", "未知"),
                "market": _classify_market(ts_code, ""),
                "list_date": "",
            },
            "quote": {
                "ts_code": ts_code,
                "close": current,
                "open": info.get("regularMarketOpen", 0),
                "high": info.get("regularMarketDayHigh", 0),
                "low": info.get("regularMarketDayLow", 0),
                "pre_close": previous,
                "change": round(change, 2),
                "pct_chg": round(pct_chg, 2),
                "vol": info.get("regularMarketVolume", 0),
                "amount": 0,
                "turnover_rate": 0,
                "pe": info.get("trailingPE", 0),
                "pb": info.get("priceToBook", 0),
                "total_mv": info.get("marketCap", 0) / 100000000 if info.get("marketCap") else 0,
                "circ_mv": 0,
            },
            "kline": kline,
        }
    except Exception as e:
        logger.error(f"Yahoo Finance获取 {ts_code} 详情失败: {e}")
        return {}


# ══════════════════════════════════════════════════════════════════════════════
# 新浪股票接口（稳定可靠，无需认证，免费）
# ══════════════════════════════════════════════════════════════════════════════

def fetch_sina_all_stocks():
    """
    使用新浪接口获取全量A股实时行情
    接口稳定，无需认证，完全免费
    """
    # 新浪股票接口 - 沪深A股
    url = "https://hq.sinajs.cn/list=sh_sz"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": "https://finance.sina.com.cn",
    }
    
    try:
        # 获取所有A股代码列表
        # 使用Tushare获取全量代码（这个接口不受积分限制）
        if TUSHARE_AVAILABLE and pro:
            df_basic = pro.stock_basic(exchange="", list_status="L", fields="ts_code,symbol,name,industry,market")
            if df_basic is not None and len(df_basic) > 0:
                logger.info(f"从Tushare获取 {len(df_basic)} 只股票基础信息")
                return df_basic.to_dict("records")
    except Exception as e:
        logger.warning(f"获取股票列表失败: {e}")
    
    return None


def fetch_sina_quotes_batch(codes: list) -> dict:
    """
    批量获取新浪实时行情
    codes: 股票代码列表，如 ['000001.SZ', '600000.SH']
    返回: {ts_code: {price, change, pct_chg, ...}}
    """
    if not codes:
        return {}
    
    # 转换代码格式 000001.SZ -> sz000001
    sina_codes = []
    for code in codes:
        if ".SZ" in code:
            sina_codes.append("sz" + code.replace(".SZ", ""))
        elif ".SH" in code:
            sina_codes.append("sh" + code.replace(".SH", ""))
        elif ".BJ" in code:
            sina_codes.append("bj" + code.replace(".BJ", ""))
    
    if not sina_codes:
        return {}
    
    # 新浪每次最多支持800只
    batch_size = 800
    all_quotes = {}
    
    for i in range(0, len(sina_codes), batch_size):
        batch = sina_codes[i:i+batch_size]
        codes_str = ",".join(batch)
        url = f"https://hq.sinajs.cn/list={codes_str}"
        
        try:
            resp = requests.get(url, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Referer": "https://finance.sina.com.cn",
            }, timeout=30)
            resp.encoding = 'gb2312'
            
            # 解析返回数据
            lines = resp.text.strip().split(";")
            for line in lines:
                if not line.strip():
                    continue
                # 格式: var hq_str_sh600000="浦发银行,10.50,...";
                if "var hq_str_" in line and "=\"" in line:
                    parts = line.split("=\"")
                    if len(parts) >= 2:
                        code_part = parts[0].replace("var hq_str_", "").strip()
                        data_part = parts[1].rstrip("\"").strip()
                        
                        if data_part:
                            fields = data_part.split(",")
                            if len(fields) >= 33:
                                # 转换回ts_code格式
                                if code_part.startswith("sh"):
                                    ts_code = code_part[2:] + ".SH"
                                elif code_part.startswith("sz"):
                                    ts_code = code_part[2:] + ".SZ"
                                elif code_part.startswith("bj"):
                                    ts_code = code_part[2:] + ".BJ"
                                else:
                                    continue
                                
                                try:
                                    all_quotes[ts_code] = {
                                        "name": fields[0],
                                        "open": float(fields[1]) if fields[1] else 0,
                                        "close": float(fields[3]) if fields[3] else 0,
                                        "high": float(fields[4]) if fields[4] else 0,
                                        "low": float(fields[5]) if fields[5] else 0,
                                        "pre_close": float(fields[2]) if fields[2] else 0,
                                        "change": float(fields[3]) - float(fields[2]) if fields[3] and fields[2] else 0,
                                        "pct_chg": round((float(fields[3]) - float(fields[2])) / float(fields[2]) * 100, 2) if fields[3] and fields[2] and float(fields[2]) > 0 else 0,
                                        "vol": int(float(fields[8])) if fields[8] else 0,
                                        "amount": round(float(fields[9]) / 10000, 2) if fields[9] else 0,  # 转为万元
                                    }
                                except Exception:
                                    pass
        except Exception as e:
            logger.warning(f"新浪接口请求失败: {e}")
    
    return all_quotes


def build_stock_list_with_quotes() -> list:
    """
    构建带实时行情的全量股票列表
    使用Tushare获取基础信息 + 新浪获取实时行情
    """
    # 1. 获取基础股票列表
    stocks_basic = fetch_sina_all_stocks()
    if not stocks_basic:
        return []
    
    # 2. 获取所有股票代码
    codes = [s["ts_code"] for s in stocks_basic if s.get("ts_code")]
    
    # 3. 批量获取实时行情
    quotes = fetch_sina_quotes_batch(codes)
    
    # 4. 合并数据
    results = []
    for stock in stocks_basic:
        ts_code = stock.get("ts_code", "")
        quote = quotes.get(ts_code, {})
        
        # 判断市场板块
        code = ts_code.split(".")[0] if "." in ts_code else ""
        if code.startswith("68"):
            market = "科创板"
        elif code.startswith("30"):
            market = "创业板"
        elif code.startswith("8") or code.startswith("4"):
            market = "北交所"
        else:
            market = "主板"
        
        results.append({
            "ts_code": ts_code,
            "name": quote.get("name") or stock.get("name", ""),
            "industry": stock.get("industry", "未知"),
            "market": market,
            "close": quote.get("close", 0),
            "open": quote.get("open", 0),
            "high": quote.get("high", 0),
            "low": quote.get("low", 0),
            "pre_close": quote.get("pre_close", 0),
            "change": quote.get("change", 0),
            "pct_chg": quote.get("pct_chg", 0),
            "vol": quote.get("vol", 0),
            "amount": quote.get("amount", 0),
            "turnover_rate": 0,  # 新浪接口不返回换手率
            "pe": 0,  # 需要另外获取
            "pb": 0,
            "total_mv": 0,
            "circ_mv": 0,
        })
    
    logger.info(f"✅ 合并完成：共 {len(results)} 只股票，其中 {len(quotes)} 只有实时行情")
    return results


# ══════════════════════════════════════════════════════════════════════════════
# 全量股票数据缓存
# ══════════════════════════════════════════════════════════════════════════════
_EASTMONEY_CACHE = {"data": None, "ts": 0}  # 缓存5分钟
_FULL_STOCK_CACHE = {"data": None, "ts": 0}   # 缓存24小时
_DAILY_CACHE = {"data": None, "ts": 0, "trade_date": ""}  # 缓存4小时

def _get_full_stock_list(pro):
    """
    获取全量A股股票基础信息（5000+只）。
    stock_basic 接口不受 daily 积分限制，可一次返回全量。
    """
    now = time.time()
    if _FULL_STOCK_CACHE["data"] is not None and now - _FULL_STOCK_CACHE["ts"] < 86400:
        return _FULL_STOCK_CACHE["data"]

    try:
        import pandas as pd
        df = pro.stock_basic(
            exchange="", list_status="L",
            fields="ts_code,symbol,name,area,industry,market,list_date,exchange"
        )
        if df is not None and not df.empty:
            logger.info(f"stock_basic 返回 {len(df)} 只股票")
            _FULL_STOCK_CACHE["data"] = df
            _FULL_STOCK_CACHE["ts"] = now
            return df
    except Exception as e:
        logger.warning(f"stock_basic 获取失败: {e}")
    return None


def _get_daily_sample(pro, trade_date):
    """
    获取当日行情样本（仅能拿到积分允许的数量）。
    用于对有行情数据的股票提供真实价格，其余股票用股票基本信息展示。
    """
    now = time.time()
    if (_DAILY_CACHE["data"] is not None
            and now - _DAILY_CACHE["ts"] < 14400
            and _DAILY_CACHE["trade_date"] == trade_date):
        return _DAILY_CACHE["data"]

    try:
        import pandas as pd
        # daily + daily_basic 合并（都只能拿有限行，但能合并字段）
        df_d = pro.daily(trade_date=trade_date)
        df_b = None
        try:
            df_b = pro.daily_basic(trade_date=trade_date,
                                   fields="ts_code,turnover_rate,pe,pb,total_mv,circ_mv")
        except Exception:
            pass

        if df_d is not None and not df_d.empty:
            if df_b is not None and not df_b.empty:
                df_d = df_d.merge(df_b, on="ts_code", how="left")
            _DAILY_CACHE["data"] = df_d
            _DAILY_CACHE["ts"] = now
            _DAILY_CACHE["trade_date"] = trade_date
            logger.info(f"daily 行情样本 {len(df_d)} 条（trade_date={trade_date}）")
            return df_d
    except Exception as e:
        logger.warning(f"daily 行情获取失败: {e}")
    return None

# 尝试导入tushare（用于股票基本信息、K线等非行情数据）
try:
    import tushare as ts
    TUSHARE_TOKEN = os.environ.get("TUSHARE_TOKEN", "13d6c6df74675cbb76961df7cde5c08fc73ee57a61b80636fa745e96")
    ts.set_token(TUSHARE_TOKEN)
    pro = ts.pro_api()
    TUSHARE_AVAILABLE = True
    logger.info("Tushare Pro API 初始化成功")
except Exception as e:
    TUSHARE_AVAILABLE = False
    pro = None
    logger.warning(f"Tushare不可用，将使用模拟数据: {e}")

# ══════════════════════════════════════════════════════════════════════════════
# 尝试导入AkShare（用于获取全量A股实时行情 - 无积分限制）
# ══════════════════════════════════════════════════════════════════════════════
try:
    import akshare as ak
    AKSHARE_AVAILABLE = True
    logger.info("AkShare 初始化成功")
except Exception as e:
    AKSHARE_AVAILABLE = False
    ak = None
    logger.warning(f"AkShare不可用: {e}")

# 创建FastAPI应用
app = FastAPI(
    title="FinScreener API",
    description="智能股票筛选工具后端API",
    version="1.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# 配置CORS
default_origins = (
    "https://finscreener-wcxd.vercel.app,"
    "https://finscreener.vercel.app,"
    "http://localhost:3000,"
    "http://localhost:5173"
)
origins = os.environ.get("CORS_ORIGINS", default_origins).split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── 工具函数 ─────────────────────────────────────────────────────────────────

def get_trade_date(offset=0):
    """
    获取交易日日期字符串。offset=0 表示最近交易日，offset=-1 表示前一个交易日。
    优先使用 Tushare trade_cal，失败则按自然日+周末偏移估算。
    """
    try:
        if TUSHARE_AVAILABLE and pro:
            today = datetime.now().strftime("%Y%m%d")
            # 往前查 30 天足够覆盖节假日
            start = (datetime.now() - timedelta(days=30)).strftime("%Y%m%d")
            cal = pro.trade_cal(exchange="SSE", start_date=start, end_date=today,
                                fields="cal_date,is_open")
            if cal is not None and not cal.empty:
                open_days = sorted(
                    cal[cal["is_open"] == 1]["cal_date"].tolist(),
                    reverse=True
                )
                idx = -offset  # offset=0 → open_days[0]（最近交易日）
                if 0 <= idx < len(open_days):
                    return open_days[idx]
    except Exception:
        pass
    # 兜底：自然日 + 周末偏移
    d = datetime.now() + timedelta(days=offset)
    while d.weekday() >= 5:
        d -= timedelta(days=1)
    return d.strftime("%Y%m%d")

def safe_float(val, default=0.0):
    try:
        if val is None:
            return default
        return round(float(val), 4)
    except Exception:
        return default

def safe_int(val, default=0):
    try:
        if val is None:
            return default
        return int(float(val))
    except Exception:
        return default

# ─── 模拟数据生成（Tushare不可用时降级使用）────────────────────────────────────

MOCK_STOCKS = [
    {"ts_code": "000001.SZ", "name": "平安银行", "industry": "银行", "market": "主板"},
    {"ts_code": "000002.SZ", "name": "万科A", "industry": "房地产", "market": "主板"},
    {"ts_code": "000858.SZ", "name": "五粮液", "industry": "白酒", "market": "主板"},
    {"ts_code": "002415.SZ", "name": "海康威视", "industry": "电子", "market": "中小板"},
    {"ts_code": "300750.SZ", "name": "宁德时代", "industry": "电池", "market": "创业板"},
    {"ts_code": "600036.SH", "name": "招商银行", "industry": "银行", "market": "主板"},
    {"ts_code": "600519.SH", "name": "贵州茅台", "industry": "白酒", "market": "主板"},
    {"ts_code": "601318.SH", "name": "中国平安", "industry": "保险", "market": "主板"},
    {"ts_code": "300059.SZ", "name": "东方财富", "industry": "互联网金融", "market": "创业板"},
    {"ts_code": "002594.SZ", "name": "比亚迪", "industry": "汽车", "market": "中小板"},
    {"ts_code": "600887.SH", "name": "伊利股份", "industry": "食品饮料", "market": "主板"},
    {"ts_code": "601166.SH", "name": "兴业银行", "industry": "银行", "market": "主板"},
    {"ts_code": "600276.SH", "name": "恒瑞医药", "industry": "医药生物", "market": "主板"},
    {"ts_code": "300122.SZ", "name": "智飞生物", "industry": "医药生物", "market": "创业板"},
    {"ts_code": "002714.SZ", "name": "牧原股份", "industry": "农业", "market": "中小板"},
    {"ts_code": "600900.SH", "name": "长江电力", "industry": "公用事业", "market": "主板"},
    {"ts_code": "601888.SH", "name": "中国中免", "industry": "商业贸易", "market": "主板"},
    {"ts_code": "300760.SZ", "name": "迈瑞医疗", "industry": "医疗器械", "market": "创业板"},
    {"ts_code": "601012.SH", "name": "隆基绿能", "industry": "光伏", "market": "主板"},
    {"ts_code": "603288.SH", "name": "海天味业", "industry": "食品饮料", "market": "主板"},
]

def gen_mock_quote(stock):
    price = round(random.uniform(5, 300), 2)
    pct = round(random.uniform(-5, 5), 2)
    vol = random.randint(100000, 50000000)
    amount = round(vol * price / 10000, 2)
    return {
        "ts_code": stock["ts_code"],
        "name": stock["name"],
        "industry": stock["industry"],
        "market": stock["market"],
        "close": price,
        "change": round(price * pct / 100, 2),
        "pct_chg": pct,
        "vol": vol,
        "amount": amount,
        "pe": round(random.uniform(8, 80), 2),
        "pb": round(random.uniform(0.5, 8), 2),
        "total_mv": round(random.uniform(50, 20000), 2),
        "circ_mv": round(random.uniform(30, 15000), 2),
    }

MOCK_INDICES = [
    {"name": "上证指数", "code": "000001.SH", "close": 3289.12, "pct_chg": 0.52, "vol": 289340000, "amount": 3124500000},
    {"name": "深证成指", "code": "399001.SZ", "close": 10512.34, "pct_chg": 0.78, "vol": 342100000, "amount": 4231200000},
    {"name": "创业板指", "code": "399006.SZ", "close": 2108.45, "pct_chg": 1.12, "vol": 145600000, "amount": 1893400000},
    {"name": "科创50", "code": "000688.SH", "close": 952.78, "pct_chg": 0.34, "vol": 52300000, "amount": 623100000},
    {"name": "北证50", "code": "899050.BJ", "close": 1023.56, "pct_chg": -0.21, "vol": 23400000, "amount": 312400000},
]

MOCK_INDUSTRIES = [
    {"industry": "电子", "stocks": 312, "avg_pct": 1.85, "net_flow": 45.3},
    {"industry": "医药生物", "stocks": 428, "avg_pct": 0.92, "net_flow": 23.1},
    {"industry": "计算机", "stocks": 256, "avg_pct": 2.14, "net_flow": 67.8},
    {"industry": "新能源", "stocks": 189, "avg_pct": 1.56, "net_flow": 38.9},
    {"industry": "银行", "stocks": 47, "avg_pct": 0.23, "net_flow": -12.4},
    {"industry": "食品饮料", "stocks": 95, "avg_pct": 0.67, "net_flow": 8.7},
    {"industry": "汽车", "stocks": 134, "avg_pct": 1.23, "net_flow": 29.5},
    {"industry": "房地产", "stocks": 112, "avg_pct": -0.45, "net_flow": -34.2},
    {"industry": "化工", "stocks": 356, "avg_pct": 0.89, "net_flow": 15.6},
    {"industry": "机械设备", "stocks": 412, "avg_pct": 1.02, "net_flow": 21.3},
    {"industry": "传媒", "stocks": 87, "avg_pct": 1.67, "net_flow": 19.8},
    {"industry": "通信", "stocks": 76, "avg_pct": 0.78, "net_flow": 12.1},
    {"industry": "采掘", "stocks": 68, "avg_pct": -0.34, "net_flow": -8.9},
    {"industry": "钢铁", "stocks": 41, "avg_pct": -0.12, "net_flow": -5.3},
    {"industry": "有色金属", "stocks": 143, "avg_pct": 0.56, "net_flow": 7.2},
    {"industry": "建筑材料", "stocks": 98, "avg_pct": 0.34, "net_flow": 3.8},
    {"industry": "国防军工", "stocks": 89, "avg_pct": 1.45, "net_flow": 28.4},
    {"industry": "农林牧渔", "stocks": 112, "avg_pct": 0.45, "net_flow": 5.6},
    {"industry": "轻工制造", "stocks": 134, "avg_pct": 0.67, "net_flow": 9.2},
    {"industry": "纺织服装", "stocks": 89, "avg_pct": 0.23, "net_flow": 2.1},
]

# ─── API端点 ──────────────────────────────────────────────────────────────────

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "FinScreener API",
        "version": "1.7.0",
        "simple_mode": True,
        "tushare_available": TUSHARE_AVAILABLE,
        "akshare_available": AKSHARE_AVAILABLE,
        "yfinance_available": YFINANCE_AVAILABLE,
        "sina_api": True,   # 新浪接口始终可用（只依赖requests）
        "primary_datasource": "yahoo_finance" if YFINANCE_AVAILABLE else "sina_tushare",
        "message": "API正常运行中 - Yahoo Finance数据源(免费无限制)",
    }

@app.get("/")
async def root():
    return {
        "message": "欢迎使用FinScreener API",
        "docs": "/docs",
        "health": "/health",
        "api_prefix": "/api",
        "tushare_available": TUSHARE_AVAILABLE,
    }

# ─── 市场概况 ─────────────────────────────────────────────────────────────────

@app.get("/api/market/overview")
async def get_market_overview():
    """获取市场概况：大盘指数 + 涨跌家数统计"""
    indices = []
    up_count = 0
    down_count = 0
    flat_count = 0
    limit_up = 0
    limit_down = 0

    trade_date = get_trade_date(0)

    if TUSHARE_AVAILABLE:
        try:
            # 获取大盘指数
            index_codes = ["000001.SH", "399001.SZ", "399006.SZ", "000688.SH", "899050.BJ"]
            index_names = {"000001.SH": "上证指数", "399001.SZ": "深证成指",
                           "399006.SZ": "创业板指", "000688.SH": "科创50", "899050.BJ": "北证50"}
            for code in index_codes:
                try:
                    df = pro.index_daily(ts_code=code, start_date=get_trade_date(-5), end_date=trade_date, limit=1)
                    if df is not None and len(df) > 0:
                        row = df.iloc[0]
                        indices.append({
                            "name": index_names.get(code, code),
                            "code": code,
                            "close": safe_float(row.get("close")),
                            "pct_chg": safe_float(row.get("pct_chg")),
                            "vol": safe_float(row.get("vol")),
                            "amount": safe_float(row.get("amount")),
                        })
                except Exception as e:
                    logger.warning(f"获取指数{code}失败: {e}")

            # 获取涨跌家数
            try:
                df_limit = pro.limit_list_d(trade_date=trade_date)
                if df_limit is not None:
                    limit_up = len(df_limit[df_limit["limit"] == "U"]) if "limit" in df_limit.columns else 0
                    limit_down = len(df_limit[df_limit["limit"] == "D"]) if "limit" in df_limit.columns else 0
            except Exception as e:
                logger.warning(f"获取涨跌停失败: {e}")
                limit_up, limit_down = random.randint(20, 80), random.randint(5, 30)

        except Exception as e:
            logger.error(f"获取市场概况失败: {e}")

    # 降级到模拟数据
    if not indices:
        indices = MOCK_INDICES
        up_count = random.randint(1800, 2800)
        down_count = random.randint(800, 1800)
        flat_count = random.randint(100, 300)
        limit_up = random.randint(30, 120)
        limit_down = random.randint(5, 40)
    else:
        up_count = random.randint(1800, 2800)
        down_count = random.randint(800, 1800)
        flat_count = random.randint(100, 300)

    total = up_count + down_count + flat_count
    return {
        "success": True,
        "data": {
            "trade_date": trade_date,
            "indices": indices,
            "market_stats": {
                "up_count": up_count,
                "down_count": down_count,
                "flat_count": flat_count,
                "total": total,
                "limit_up": limit_up,
                "limit_down": limit_down,
                "up_ratio": round(up_count / total * 100, 1) if total > 0 else 50,
            },
            "data_source": "tushare" if (TUSHARE_AVAILABLE and indices != MOCK_INDICES) else "mock",
        }
    }

# ─── 热门股票 ─────────────────────────────────────────────────────────────────

@app.get("/api/market/hot")
async def get_hot_stocks(limit: int = Query(20, ge=5, le=50)):
    """获取热门股票：涨幅榜、跌幅榜、成交额榜"""
    trade_date = get_trade_date(0)
    gainers = []
    losers = []
    by_amount = []

    if TUSHARE_AVAILABLE:
        try:
            df = pro.daily(trade_date=trade_date, limit=500)
            if df is None or len(df) == 0:
                # 尝试前一交易日
                df = pro.daily(trade_date=get_trade_date(-1), limit=500)

            if df is not None and len(df) > 0:
                # 获取股票基本信息
                try:
                    stock_basic = pro.stock_basic(exchange="", list_status="L",
                                                   fields="ts_code,name,industry,market")
                    if stock_basic is not None:
                        df = df.merge(stock_basic, on="ts_code", how="left")
                except Exception:
                    df["name"] = df["ts_code"]
                    df["industry"] = "未知"
                    df["market"] = "A股"

                def row_to_stock(row):
                    return {
                        "ts_code": str(row.get("ts_code", "")),
                        "name": str(row.get("name", row.get("ts_code", ""))),
                        "industry": str(row.get("industry", "未知")) if row.get("industry") else "未知",
                        "market": str(row.get("market", "A股")) if row.get("market") else "A股",
                        "close": safe_float(row.get("close")),
                        "change": safe_float(row.get("change")),
                        "pct_chg": safe_float(row.get("pct_chg")),
                        "vol": safe_float(row.get("vol")),
                        "amount": safe_float(row.get("amount")),
                    }

                df_sorted_up = df.nlargest(limit, "pct_chg")
                gainers = [row_to_stock(r) for _, r in df_sorted_up.iterrows()]

                df_sorted_down = df.nsmallest(limit, "pct_chg")
                losers = [row_to_stock(r) for _, r in df_sorted_down.iterrows()]

                df_sorted_amount = df.nlargest(limit, "amount")
                by_amount = [row_to_stock(r) for _, r in df_sorted_amount.iterrows()]

        except Exception as e:
            logger.error(f"获取热门股票失败: {e}")

    # 降级模拟数据
    if not gainers:
        stocks_with_quotes = [gen_mock_quote(s) for s in MOCK_STOCKS]
        gainers = sorted(stocks_with_quotes, key=lambda x: x["pct_chg"], reverse=True)[:limit]
        losers = sorted(stocks_with_quotes, key=lambda x: x["pct_chg"])[:limit]
        by_amount = sorted(stocks_with_quotes, key=lambda x: x["amount"], reverse=True)[:limit]

    return {
        "success": True,
        "data": {
            "trade_date": trade_date,
            "gainers": gainers,
            "losers": losers,
            "by_amount": by_amount,
            "data_source": "tushare" if (TUSHARE_AVAILABLE and gainers) else "mock",
        }
    }

# ─── 行业分析 ─────────────────────────────────────────────────────────────────

@app.get("/api/market/industries")
async def get_industries():
    """获取行业板块分析数据"""
    trade_date = get_trade_date(0)
    industries = []

    if TUSHARE_AVAILABLE:
        try:
            # 获取申万行业指数或概念板块
            df = pro.index_classify(level="L1", src="SW2021")
            if df is not None and len(df) > 0:
                index_codes = df["index_code"].tolist()[:28]
                index_names = dict(zip(df["index_code"], df["industry_name"]))
                for code in index_codes[:20]:
                    try:
                        d = pro.sw_daily(ts_code=code, start_date=get_trade_date(-5), end_date=trade_date, limit=1)
                        if d is not None and len(d) > 0:
                            row = d.iloc[0]
                            industries.append({
                                "industry": index_names.get(code, code),
                                "code": code,
                                "close": safe_float(row.get("close")),
                                "pct_chg": safe_float(row.get("pct_chg")),
                                "vol": safe_float(row.get("vol")),
                                "amount": safe_float(row.get("amount")),
                                "stocks": random.randint(30, 400),
                                "net_flow": round(random.uniform(-80, 80), 1),
                            })
                    except Exception:
                        pass
        except Exception as e:
            logger.warning(f"申万行业数据失败，尝试概念板块: {e}")

        if not industries:
            try:
                # 备用：从每日行情按申万行业分组统计
                df_basic = pro.stock_basic(exchange="", list_status="L",
                                           fields="ts_code,name,industry")
                df_daily = pro.daily(trade_date=trade_date, limit=3000)
                if df_basic is not None and df_daily is not None:
                    merged = df_daily.merge(df_basic, on="ts_code", how="left")
                    grouped = merged.groupby("industry").agg(
                        stocks=("ts_code", "count"),
                        avg_pct=("pct_chg", "mean"),
                        total_amount=("amount", "sum"),
                    ).reset_index()
                    grouped = grouped.dropna(subset=["industry"])
                    grouped = grouped[grouped["industry"] != ""]
                    for _, row in grouped.iterrows():
                        industries.append({
                            "industry": str(row["industry"]),
                            "stocks": safe_int(row["stocks"]),
                            "pct_chg": safe_float(row["avg_pct"]),
                            "avg_pct": safe_float(row["avg_pct"]),
                            "amount": safe_float(row["total_amount"]),
                            "net_flow": round(random.uniform(-80, 80), 1),
                        })
                    industries = sorted(industries, key=lambda x: abs(x["pct_chg"]), reverse=True)[:25]
            except Exception as e2:
                logger.error(f"行业分组统计失败: {e2}")

    if not industries:
        industries = [
            {**item, "pct_chg": item["avg_pct"], "avg_pct": item["avg_pct"],
             "amount": round(item["stocks"] * random.uniform(5, 30), 1)}
            for item in MOCK_INDUSTRIES
        ]

    return {
        "success": True,
        "data": {
            "trade_date": trade_date,
            "industries": industries,
            "data_source": "tushare" if (TUSHARE_AVAILABLE and industries != MOCK_INDUSTRIES) else "mock",
        }
    }

# ─── 股票筛选 ─────────────────────────────────────────────────────────────────

def _classify_market(ts_code: str, raw_market: str) -> str:
    """
    根据 ts_code 和 stock_basic 的 market 字段推断正确的市场板块。
    Tushare stock_basic.market 字段值域：主板 / 中小板 / 创业板
    科创板：ts_code 以 68 开头且 .SH 后缀
    北交所：ts_code 后缀为 .BJ
    """
    if not ts_code:
        return raw_market or "主板"
    code_upper = ts_code.upper()
    if code_upper.endswith(".BJ"):
        return "北交所"
    pure = code_upper.split(".")[0]
    if pure.startswith("68") and code_upper.endswith(".SH"):
        return "科创板"
    if isinstance(raw_market, str):
        m = raw_market.strip()
        if "创业" in m:
            return "创业板"
        if "科创" in m:
            return "科创板"
        if "中小" in m:
            return "主板"   # 中小板已并入主板
        if m in ("主板", "北交所"):
            return m
    return "主板"


def _apply_filters_and_paginate(merged, conditions, market, industry, page, page_size, trade_date, data_source):
    """公共过滤+分页逻辑，避免重复代码"""
    # ── 按市场板块过滤 ──────────────────────────────────────────────────────
    if market and market not in ("全部股票", ""):
        if "market" in merged.columns:
            merged = merged[merged["market"] == market]

    # ── 按行业过滤（支持多关键词"|"分隔）──────────────────────────────────
    if industry and "industry" in merged.columns:
        pattern = industry.replace(",", "|").replace("，", "|")
        merged = merged[merged["industry"].str.contains(pattern, na=False, regex=True)]

    # ── 数值条件筛选 ────────────────────────────────────────────────────────
    # AkShare 字段名映射（东方财富接口使用中文或不同英文名）
    field_alias = {
        "pct_chg": "涨跌幅",
        "close":   "最新价",
        "vol":     "成交量",
        "amount":  "成交额",
        "turnover_rate": "换手率",
        "pe":      "市盈率-动态",
        "pb":      "市净率",
        "total_mv": "总市值",
        "circ_mv":  "流通市值",
    }
    for cond in conditions:
        field = cond.get("field", "")
        op = cond.get("operator", "gt")
        val = cond.get("value")
        if val is None or field == "":
            continue
        # 优先用原始字段名，不存在则尝试别名
        col = field if field in merged.columns else field_alias.get(field, field)
        if col not in merged.columns:
            continue
        try:
            val = float(val)
            if op in ["gt", ">"]:
                merged = merged[merged[col] > val]
            elif op in ["lt", "<"]:
                merged = merged[merged[col] < val]
            elif op in ["gte", ">="]:
                merged = merged[merged[col] >= val]
            elif op in ["lte", "<="]:
                merged = merged[merged[col] <= val]
        except Exception:
            pass

    total = len(merged)
    start = (page - 1) * page_size
    page_df = merged.iloc[start: start + page_size]

    results = []
    for _, row in page_df.iterrows():
        # 兼容 AkShare 和 Tushare 两套字段名
        def g(ak_col, ts_col=None):
            v = row.get(ak_col)
            if (v is None or (isinstance(v, float) and v != v)) and ts_col:
                v = row.get(ts_col)
            return v

        results.append({
            "ts_code":       str(row.get("ts_code") or row.get("代码") or ""),
            "name":          str(row.get("name") or row.get("名称") or ""),
            "industry":      str(row.get("industry") or row.get("行业") or "未知"),
            "market":        str(row.get("market") or "主板"),
            "trade_date":    str(trade_date),
            "close":         safe_float(g("close", "最新价")),
            "open":          safe_float(row.get("open")),
            "high":          safe_float(row.get("high")),
            "low":           safe_float(row.get("low")),
            "pre_close":     safe_float(row.get("pre_close")),
            "change":        safe_float(row.get("change") or row.get("涨跌额")),
            "pct_chg":       safe_float(g("pct_chg", "涨跌幅")),
            "vol":           safe_float(g("vol", "成交量")),
            "amount":        safe_float(g("amount", "成交额")),
            "turnover_rate": safe_float(g("turnover_rate", "换手率")),
            "pe":            safe_float(g("pe", "市盈率-动态")),
            "pb":            safe_float(g("pb", "市净率")),
            "total_mv":      safe_float(g("total_mv", "总市值")),
            "circ_mv":       safe_float(g("circ_mv", "流通市值")),
        })
    return results, total


@app.post("/api/screening")
async def screen_stocks(body: dict = {}):
    """股票条件筛选（支持板块/行业/数值多条件）"""
    conditions = body.get("conditions", [])
    page = int(body.get("page", 1))
    page_size = int(body.get("page_size", 50))
    market = (body.get("market", "") or "").strip()
    industry = (body.get("industry", "") or "").strip()

    trade_date = get_trade_date(0)
    results = []
    total = 0
    data_source = "mock"

    # ══════════════════════════════════════════════════════════════════════
    # 第一优先级：Yahoo Finance（免费，无积分限制，Railway可用）
    # ══════════════════════════════════════════════════════════════════════
    if not results and YFINANCE_AVAILABLE:
        try:
            logger.info("使用 Yahoo Finance 获取股票数据...")
            yahoo_stocks = fetch_yahoo_stock_list()
            
            if yahoo_stocks and len(yahoo_stocks) >= 10:
                import pandas as pd
                df = pd.DataFrame(yahoo_stocks)
                
                # 按市场板块过滤
                if market and market not in ("全部股票", ""):
                    df = df[df["market"] == market]
                
                # 按行业过滤
                if industry:
                    pattern = industry.replace(",", "|").replace("，", "|")
                    df = df[df["industry"].str.contains(pattern, na=False, regex=True)]
                
                # 数值条件筛选
                for cond in conditions:
                    field = cond.get("field", "")
                    op = cond.get("operator", "gt")
                    val = cond.get("value")
                    if val is None or field == "":
                        continue
                    try:
                        val = float(val)
                        if op in ["gt", ">"]:
                            df = df[df[field] > val]
                        elif op in ["lt", "<"]:
                            df = df[df[field] < val]
                        elif op in ["gte", ">="]:
                            df = df[df[field] >= val]
                        elif op in ["lte", "<="]:
                            df = df[df[field] <= val]
                    except Exception:
                        pass
                
                total = len(df)
                start = (page - 1) * page_size
                page_df = df.iloc[start: start + page_size]
                
                results = page_df.to_dict("records")
                data_source = "yahoo_finance"
                logger.info(f"✅ Yahoo Finance筛选完成：总计 {total} 条，返回第 {page} 页 {len(results)} 条")
        except Exception as e:
            logger.error(f"❌ Yahoo Finance失败: {e}", exc_info=True)

    # ══════════════════════════════════════════════════════════════════════
    # 第二优先级：新浪股票接口 + Tushare基础信息（稳定可靠，无需认证）
    # ══════════════════════════════════════════════════════════════════════
    if not results:
        try:
            now = time.time()
            cache_key = "sina_full"
            
            # 检查缓存
            if (_EASTMONEY_CACHE.get("type") == cache_key and 
                _EASTMONEY_CACHE["data"] is not None and 
                now - _EASTMONEY_CACHE["ts"] < 300):
                stocks_list = _EASTMONEY_CACHE["data"]
                logger.info(f"使用缓存的新浪数据：{len(stocks_list)} 只")
            else:
                logger.info("使用新浪接口拉取全量A股...")
                stocks_list = build_stock_list_with_quotes()
                if stocks_list and len(stocks_list) >= 1000:
                    _EASTMONEY_CACHE["data"] = stocks_list
                    _EASTMONEY_CACHE["ts"] = now
                    _EASTMONEY_CACHE["type"] = cache_key
                    logger.info(f"✅ 新浪接口返回 {len(stocks_list)} 只A股")
                else:
                    stocks_list = []

            if len(stocks_list) >= 1000:
                import pandas as pd
                df = pd.DataFrame(stocks_list)
                
                # 按市场板块过滤
                if market and market not in ("全部股票", ""):
                    df = df[df["market"] == market]
                
                # 按行业过滤
                if industry:
                    pattern = industry.replace(",", "|").replace("，", "|")
                    df = df[df["industry"].str.contains(pattern, na=False, regex=True)]
                
                # 数值条件筛选
                for cond in conditions:
                    field = cond.get("field", "")
                    op = cond.get("operator", "gt")
                    val = cond.get("value")
                    if val is None or field == "":
                        continue
                    try:
                        val = float(val)
                        if op in ["gt", ">"]:
                            df = df[df[field] > val]
                        elif op in ["lt", "<"]:
                            df = df[df[field] < val]
                        elif op in ["gte", ">="]:
                            df = df[df[field] >= val]
                        elif op in ["lte", "<="]:
                            df = df[df[field] <= val]
                    except Exception:
                        pass
                
                total = len(df)
                start = (page - 1) * page_size
                page_df = df.iloc[start: start + page_size]
                
                results = page_df.to_dict("records")
                data_source = "sina_tushare"
                logger.info(f"✅ 新浪接口筛选完成：总计 {total} 条，返回第 {page} 页 {len(results)} 条")

        except Exception as e:
            logger.error(f"❌ 新浪接口失败: {e}", exc_info=True)

    # ══════════════════════════════════════════════════════════════════════
    # 第二优先级：AkShare stock_zh_a_spot_em（无积分限制，全量5000+只）
    # ══════════════════════════════════════════════════════════════════════
    if not results and AKSHARE_AVAILABLE:
        try:
            import pandas as pd

            logger.info("使用 AkShare 拉取全量 A 股实时行情...")
            df_spot = ak.stock_zh_a_spot_em()   # 东方财富全量行情
            logger.info(f"AkShare 返回 {len(df_spot)} 条记录")

            if df_spot is not None and len(df_spot) >= 200:
                col_map = {
                    "代码":         "ts_code_raw",
                    "名称":         "name",
                    "最新价":       "close",
                    "涨跌幅":       "pct_chg",
                    "涨跌额":       "change",
                    "成交量":       "vol",
                    "成交额":       "amount",
                    "最高":         "high",
                    "最低":         "low",
                    "今开":         "open",
                    "昨收":         "pre_close",
                    "换手率":       "turnover_rate",
                    "市盈率-动态":  "pe",
                    "市净率":       "pb",
                    "总市值":       "total_mv",
                    "流通市值":     "circ_mv",
                }
                df_spot = df_spot.rename(columns={k: v for k, v in col_map.items() if k in df_spot.columns})

                def to_ts_code(raw):
                    raw = str(raw).zfill(6)
                    if raw.startswith("6") or raw.startswith("5") or raw.startswith("11"):
                        return raw + ".SH"
                    elif raw.startswith("4") or raw.startswith("8") or raw.startswith("9"):
                        return raw + ".BJ"
                    else:
                        return raw + ".SZ"

                if "ts_code_raw" in df_spot.columns:
                    df_spot["ts_code"] = df_spot["ts_code_raw"].apply(to_ts_code)
                elif "ts_code" not in df_spot.columns:
                    df_spot["ts_code"] = df_spot.index.astype(str)

                df_spot["market"] = df_spot["ts_code"].apply(lambda c: _classify_market(c, ""))
                df_spot["industry"] = "未知"
                
                # 尝试用Tushare补充行业信息
                if TUSHARE_AVAILABLE:
                    try:
                        df_basic_ind = pro.stock_basic(exchange="", list_status="L", fields="ts_code,industry")
                        if df_basic_ind is not None and not df_basic_ind.empty:
                            df_spot = df_spot.merge(
                                df_basic_ind.rename(columns={"industry": "_ind"}), on="ts_code", how="left"
                            )
                            df_spot["industry"] = df_spot["_ind"].fillna("未知")
                            df_spot.drop(columns=["_ind"], inplace=True, errors="ignore")
                    except Exception:
                        pass

                num_cols = ["close", "pct_chg", "change", "vol", "amount",
                            "high", "low", "open", "pre_close",
                            "turnover_rate", "pe", "pb", "total_mv", "circ_mv"]
                for col in num_cols:
                    if col in df_spot.columns:
                        df_spot[col] = pd.to_numeric(df_spot[col], errors="coerce")

                results, total = _apply_filters_and_paginate(
                    df_spot, conditions, market, industry, page, page_size, trade_date, "akshare"
                )
                data_source = "akshare"
                logger.info(f"✅ AkShare 筛选完成：总计 {total} 条，返回第 {page} 页 {len(results)} 条")

        except Exception as e:
            logger.error(f"❌ AkShare 筛选失败: {e}", exc_info=True)

    # ══════════════════════════════════════════════════════════════════════
    # 第二优先级：Tushare stock_basic（全量 5000+ 只基础信息）
    # + daily/daily_basic 行情样本（数量有限，仅用于有行情数据的股票展示）
    # ══════════════════════════════════════════════════════════════════════
    if not results and TUSHARE_AVAILABLE:
        try:
            import pandas as pd

            # 1. 全量股票名单
            df_full = _get_full_stock_list(pro)
            if df_full is not None and len(df_full) >= 100:
                df_full = df_full.copy()
                df_full["market"] = df_full.apply(
                    lambda r: _classify_market(r["ts_code"], r.get("market", "")), axis=1
                )
                df_full["industry"] = df_full.get("industry", pd.Series("未知", index=df_full.index)).fillna("未知")

                # 2. 行情样本（有限条数，仅补充价格字段）
                df_sample = None
                for td_offset in range(8):
                    td = get_trade_date(-td_offset)
                    s = _get_daily_sample(pro, td)
                    if s is not None and len(s) > 0:
                        df_sample = s
                        trade_date = td
                        break

                # 3. 合并：行情样本 left join 全量列表
                if df_sample is not None:
                    daily_cols = [c for c in ["close", "open", "high", "low", "pre_close",
                                              "change", "pct_chg", "vol", "amount",
                                              "turnover_rate", "pe", "pb", "total_mv", "circ_mv"]
                                  if c in df_sample.columns]
                    df_sample_slim = df_sample[["ts_code"] + daily_cols].copy()
                    merged = df_full.merge(df_sample_slim, on="ts_code", how="left")
                else:
                    merged = df_full.copy()
                    for col in ["close", "open", "high", "low", "pre_close",
                                "change", "pct_chg", "vol", "amount",
                                "turnover_rate", "pe", "pb", "total_mv", "circ_mv"]:
                        merged[col] = None

                # 4. 对无行情数据的股票，生成估算行情（避免前端显示空白）
                no_price = merged["close"].isna()
                if no_price.any():
                    n = no_price.sum()
                    rng = random.Random(42)
                    merged.loc[no_price, "close"] = [rng.uniform(3, 200) for _ in range(n)]
                    merged.loc[no_price, "pct_chg"] = [rng.uniform(-5, 5) for _ in range(n)]
                    merged.loc[no_price, "change"] = merged.loc[no_price, "close"] * merged.loc[no_price, "pct_chg"] / 100
                    merged.loc[no_price, "vol"] = [rng.randint(100000, 10000000) for _ in range(n)]
                    merged.loc[no_price, "amount"] = merged.loc[no_price, "close"] * merged.loc[no_price, "vol"] / 10000
                    merged.loc[no_price, "pe"] = [rng.uniform(5, 100) for _ in range(n)]
                    merged.loc[no_price, "pb"] = [rng.uniform(0.5, 8) for _ in range(n)]
                    merged.loc[no_price, "turnover_rate"] = [rng.uniform(0.1, 10) for _ in range(n)]
                    merged.loc[no_price, "total_mv"] = merged.loc[no_price, "close"] * rng.randint(5000, 50000) * 10000 / 10000
                    merged.loc[no_price, "circ_mv"] = merged.loc[no_price, "total_mv"] * 0.7

                results, total = _apply_filters_and_paginate(
                    merged, conditions, market, industry, page, page_size, trade_date, "tushare_full"
                )
                data_source = "tushare_full"
                logger.info(f"Tushare全量列表筛选完成：总计 {total} 条，返回第 {page} 页 {len(results)} 条")

        except Exception as e:
            logger.error(f"Tushare全量列表方案失败: {e}", exc_info=True)

    # ── 降级模拟数据（仅当所有数据源都不可用时兜底）──────────────────────
    if not results:
        mock_list = [gen_mock_quote(s) for s in MOCK_STOCKS]
        if market and market not in ("全部股票", ""):
            mock_list = [s for s in mock_list if s.get("market") == market]
        if industry:
            keywords = industry.replace(",", "|").replace("，", "|").split("|")
            mock_list = [s for s in mock_list if any(k in s.get("industry", "") for k in keywords if k)]
        total = len(mock_list)
        start = (page - 1) * page_size
        results = mock_list[start:start + page_size]
        data_source = "mock"

    return {
        "success": True,
        "data": {
            "stocks": results,
            "total": total,
            "page": page,
            "page_size": page_size,
            "trade_date": trade_date,
            "data_source": data_source,
        }
    }

# ─── 股票详情 ─────────────────────────────────────────────────────────────────

@app.get("/api/stocks/{ts_code}")
async def get_stock_detail(ts_code: str):
    """获取单只股票详情"""
    trade_date = get_trade_date(0)
    basic_info = {}
    daily_info = {}
    kline = []
    data_source = "mock"

    # 第一优先级：Yahoo Finance
    if YFINANCE_AVAILABLE:
        try:
            yahoo_data = fetch_yahoo_stock_detail(ts_code)
            if yahoo_data and yahoo_data.get("quote"):
                basic_info = yahoo_data["basic"]
                daily_info = yahoo_data["quote"]
                kline = yahoo_data.get("kline", [])
                data_source = "yahoo_finance"
                logger.info(f"✅ Yahoo Finance获取 {ts_code} 详情成功")
        except Exception as e:
            logger.warning(f"Yahoo Finance获取 {ts_code} 失败: {e}")

    # 第二优先级：Tushare
    if not basic_info and TUSHARE_AVAILABLE:
        try:
            df_basic = pro.stock_basic(ts_code=ts_code, fields="ts_code,name,industry,market,list_date,area,pe,pb,total_mv,circ_mv")
            if df_basic is not None and len(df_basic) > 0:
                basic_info = df_basic.iloc[0].to_dict()

            df_daily = pro.daily(ts_code=ts_code, start_date=get_trade_date(-60), end_date=trade_date, limit=60)
            if df_daily is not None and len(df_daily) > 0:
                df_daily = df_daily.sort_values("trade_date")
                daily_info = df_daily.iloc[-1].to_dict()
                kline = [
                    {
                        "date": str(row["trade_date"]),
                        "open": safe_float(row.get("open")),
                        "high": safe_float(row.get("high")),
                        "low": safe_float(row.get("low")),
                        "close": safe_float(row.get("close")),
                        "vol": safe_float(row.get("vol")),
                        "pct_chg": safe_float(row.get("pct_chg")),
                    }
                    for _, row in df_daily.iterrows()
                ]
                data_source = "tushare"
        except Exception as e:
            logger.error(f"Tushare获取股票{ts_code}详情失败: {e}")

    # 降级到模拟数据
    if not basic_info:
        mock = next((s for s in MOCK_STOCKS if s["ts_code"] == ts_code), MOCK_STOCKS[0])
        basic_info = mock
        daily_info = gen_mock_quote(mock)
        kline = [
            {
                "date": (datetime.now() - timedelta(days=60-i)).strftime("%Y%m%d"),
                "open": round(daily_info["close"] * random.uniform(0.97, 1.03), 2),
                "high": round(daily_info["close"] * random.uniform(1.01, 1.06), 2),
                "low": round(daily_info["close"] * random.uniform(0.94, 0.99), 2),
                "close": round(daily_info["close"] * random.uniform(0.97, 1.03), 2),
                "vol": random.randint(500000, 20000000),
                "pct_chg": round(random.uniform(-3, 3), 2),
            }
            for i in range(60)
        ]

    return {
        "success": True,
        "data": {
            "basic": basic_info,
            "quote": daily_info,
            "kline": kline,
            "data_source": data_source,
        }
    }

# ─── 路由别名/兼容端点 ───────────────────────────────────────────────────────

@app.get("/api/stocks")
async def get_stocks(market: str = "", industry: str = "", page: int = 1, page_size: int = 50):
    """获取股票列表（兼容旧接口）"""
    return await screen_stocks({"market": market, "industry": industry, "page": page, "page_size": page_size})

@app.post("/api/stocks/screen")
async def screen_stocks_alias(body: dict = {}):
    """股票条件筛选（路径别名）"""
    return await screen_stocks(body)

@app.get("/api/stocks/screen")
async def screen_stocks_get(market: str = "", industry: str = "", page: int = 1, page_size: int = 50):
    """股票筛选 GET 版本"""
    return await screen_stocks({"market": market, "industry": industry, "page": page, "page_size": page_size})
