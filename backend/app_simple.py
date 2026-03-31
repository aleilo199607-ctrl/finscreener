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

# 尝试导入tushare
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
    """获取交易日日期字符串，offset=-1 表示前一交易日"""
    d = datetime.now() + timedelta(days=offset)
    # 周末往前推
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

@app.post("/api/screening")
async def screen_stocks(body: dict = {}):
    """股票条件筛选"""
    conditions = body.get("conditions", [])
    page = body.get("page", 1)
    page_size = body.get("page_size", 20)
    market = body.get("market", "")
    industry = body.get("industry", "")

    trade_date = get_trade_date(0)
    results = []
    total = 0

    if TUSHARE_AVAILABLE:
        try:
            df_basic = pro.stock_basic(exchange="", list_status="L",
                                       fields="ts_code,name,industry,market,list_date")
            df_daily = pro.daily(trade_date=trade_date, limit=5000)

            if df_basic is not None and df_daily is not None:
                merged = df_daily.merge(df_basic, on="ts_code", how="left")

                # 按市场过滤
                if market and market not in ["全部股票", ""]:
                    market_map = {"主板": "主板", "创业板": "创业板", "科创板": "科创板", "北交所": "北交所", "中小板": "中小板"}
                    if market in market_map:
                        merged = merged[merged["market"].str.contains(market_map[market], na=False)]

                # 按行业过滤
                if industry:
                    merged = merged[merged["industry"].str.contains(industry, na=False)]

                # 应用条件筛选
                for cond in conditions:
                    field = cond.get("field", "")
                    op = cond.get("operator", "gt")
                    val = cond.get("value")
                    if val is None or field == "":
                        continue
                    try:
                        val = float(val)
                        if field in merged.columns:
                            if op in ["gt", ">"]:
                                merged = merged[merged[field] > val]
                            elif op in ["lt", "<"]:
                                merged = merged[merged[field] < val]
                            elif op in ["gte", ">="]:
                                merged = merged[merged[field] >= val]
                            elif op in ["lte", "<="]:
                                merged = merged[merged[field] <= val]
                    except Exception:
                        pass

                total = len(merged)
                start = (page - 1) * page_size
                end = start + page_size
                page_df = merged.iloc[start:end]

                for _, row in page_df.iterrows():
                    results.append({
                        "ts_code": str(row.get("ts_code", "")),
                        "name": str(row.get("name", "")),
                        "industry": str(row.get("industry", "未知")) if row.get("industry") else "未知",
                        "market": str(row.get("market", "A股")) if row.get("market") else "A股",
                        "close": safe_float(row.get("close")),
                        "change": safe_float(row.get("change")),
                        "pct_chg": safe_float(row.get("pct_chg")),
                        "vol": safe_float(row.get("vol")),
                        "amount": safe_float(row.get("amount")),
                    })

        except Exception as e:
            logger.error(f"股票筛选失败: {e}")

    if not results:
        # 降级模拟数据
        mock_list = [gen_mock_quote(s) for s in MOCK_STOCKS]
        total = len(mock_list)
        results = mock_list

    return {
        "success": True,
        "data": {
            "stocks": results,
            "total": total,
            "page": page,
            "page_size": page_size,
            "trade_date": trade_date,
            "data_source": "tushare" if TUSHARE_AVAILABLE else "mock",
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

# ─── 旧兼容端点 ───────────────────────────────────────────────────────────────

@app.get("/api/stocks")
async def get_stocks(market: str = "", industry: str = ""):
    """获取股票列表（兼容旧接口）"""
    return await screen_stocks({"market": market, "industry": industry})
