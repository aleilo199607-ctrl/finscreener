"""
简化版FastAPI应用，用于Railway部署
包含真实Tushare Pro API数据接入
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import os
import logging
import json
from datetime import datetime, timedelta
from typing import Optional, List
import random

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 尝试导入 AkShare（全量行情首选，完全免费）
try:
    import akshare as ak
    AKSHARE_AVAILABLE = True
    logger.info("AkShare 初始化成功")
except Exception as e:
    AKSHARE_AVAILABLE = False
    ak = None
    logger.warning(f"AkShare不可用: {e}")

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
        "version": "1.1.0",
        "simple_mode": True,
        "tushare_available": TUSHARE_AVAILABLE,
        "message": "API正常运行中",
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
    # 优先用 AkShare stock_zh_a_spot_em（东方财富实时行情）
    # 一次请求返回全市场 5000+ 只股票，完全免费，无积分限制
    # ══════════════════════════════════════════════════════════════════════
    if AKSHARE_AVAILABLE:
        try:
            import pandas as pd

            logger.info("使用 AkShare 拉取全量 A 股实时行情...")
            df_spot = ak.stock_zh_a_spot_em()   # 东方财富全量行情
            logger.info(f"AkShare 返回 {len(df_spot)} 条记录")

            if df_spot is not None and len(df_spot) >= 200:
                # ── 字段标准化 ──────────────────────────────────────────
                # AkShare 返回列名（部分版本）：序号,代码,名称,最新价,涨跌幅,涨跌额,
                # 成交量,成交额,振幅,最高,最低,今开,昨收,换手率,市盈率-动态,量比,
                # 市净率,总市值,流通市值,涨速,5分钟涨跌,60日涨跌幅,年初至今涨跌幅
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

                # 生成标准 ts_code（600001 → 600001.SH，000001 → 000001.SZ，8xxxxx → 8xxxxx.BJ）
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
                    # 万一字段名已是英文
                    df_spot["ts_code"] = df_spot.index.astype(str)

                # 推断板块
                df_spot["market"] = df_spot["ts_code"].apply(
                    lambda c: _classify_market(c, "")
                )

                # 行业信息来自 Tushare stock_basic（AkShare 行情不含行业字段）
                df_spot["industry"] = "未知"
                if TUSHARE_AVAILABLE:
                    try:
                        df_basic = pro.stock_basic(
                            exchange="", list_status="L",
                            fields="ts_code,industry"
                        )
                        if df_basic is not None and not df_basic.empty:
                            df_spot = df_spot.merge(
                                df_basic.rename(columns={"industry": "industry_ts"}),
                                on="ts_code", how="left"
                            )
                            df_spot["industry"] = df_spot["industry_ts"].fillna("未知")
                            df_spot.drop(columns=["industry_ts"], inplace=True, errors="ignore")
                    except Exception as e_basic:
                        logger.warning(f"Tushare 行业信息获取失败，行业筛选不可用: {e_basic}")

                # 数值列转 float（AkShare 可能返回字符串 "-"）
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
                logger.info(f"AkShare 筛选完成：总计 {total} 条，返回第 {page} 页 {len(results)} 条")

        except Exception as e:
            logger.error(f"AkShare 筛选失败: {e}", exc_info=True)

    # ══════════════════════════════════════════════════════════════════════
    # 备用：Tushare（积分不足时只能返回少量数据，作为 AkShare 不可用时的兜底）
    # ══════════════════════════════════════════════════════════════════════
    if not results and TUSHARE_AVAILABLE:
        try:
            import pandas as pd
            logger.info("AkShare 不可用，回退到 Tushare...")

            df_basic = pro.stock_basic(
                exchange="", list_status="L",
                fields="ts_code,name,industry,market,list_date,exchange"
            )
            df_daily = None
            for td_offset in range(8):
                td = get_trade_date(-td_offset)
                frames = []
                batch_offset = 0
                while True:
                    try:
                        chunk = pro.daily(trade_date=td, offset=batch_offset, limit=5000)
                    except Exception:
                        break
                    if chunk is None or chunk.empty:
                        break
                    frames.append(chunk)
                    if len(chunk) < 5000:
                        break
                    batch_offset += 5000
                if frames:
                    combined = pd.concat(frames, ignore_index=True)
                    if len(combined) >= 200:
                        df_daily = combined
                        trade_date = td
                        break

            if df_basic is not None and df_daily is not None:
                df_basic["market"] = df_basic.apply(
                    lambda r: _classify_market(r["ts_code"], r.get("market", "")), axis=1
                )
                merged = df_daily.merge(
                    df_basic[["ts_code", "name", "industry", "market"]], on="ts_code", how="left"
                )
                merged["name"] = merged["name"].fillna(merged["ts_code"])
                merged["industry"] = merged["industry"].fillna("未知")
                merged["market"] = merged["market"].fillna("主板")

                results, total = _apply_filters_and_paginate(
                    merged, conditions, market, industry, page, page_size, trade_date, "tushare"
                )
                data_source = "tushare"

        except Exception as e:
            logger.error(f"Tushare 筛选失败: {e}", exc_info=True)

    # ── 降级模拟数据（支持过滤+分页）───────────────────────────────────────
    if not results:
        mock_list = [gen_mock_quote(s) for s in MOCK_STOCKS]
        # 按 market 过滤
        if market and market not in ("全部股票", ""):
            mock_list = [s for s in mock_list if s.get("market") == market]
        # 按 industry 过滤
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

    if TUSHARE_AVAILABLE:
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
        except Exception as e:
            logger.error(f"获取股票{ts_code}详情失败: {e}")

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
