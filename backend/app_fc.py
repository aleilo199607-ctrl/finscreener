"""
FinScreener 后端 - 阿里云函数计算版
数据源：东方财富 HTTP API（免费，无限制，国内网络极快）
部署：阿里云函数计算 FC 3.0 Web函数模式
"""

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import os
import logging
import json
import time
from datetime import datetime, timedelta
from typing import Optional
import random
import requests

# ══════════════════════════════════════════════════════════════════════════════
# 清除代理设置（阿里云FC环境无需代理，避免被本地代理干扰）
# ══════════════════════════════════════════════════════════════════════════════
for _proxy_key in ["HTTP_PROXY", "http_proxy", "HTTPS_PROXY", "https_proxy", "ALL_PROXY", "all_proxy"]:
    os.environ.pop(_proxy_key, None)

# 创建不使用代理的 requests session
_http_session = requests.Session()
_http_session.trust_env = False

# ══════════════════════════════════════════════════════════════════════════════
# 日志配置
# ══════════════════════════════════════════════════════════════════════════════
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger(__name__)

# ══════════════════════════════════════════════════════════════════════════════
# 东方财富 HTTP API（免费，无需认证，A股全量数据）
# ══════════════════════════════════════════════════════════════════════════════

EASTMONEY_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://quote.eastmoney.com/",
}

# 全量股票缓存
_STOCK_CACHE = {"data": None, "ts": 0}


def fetch_eastmoney_all_stocks() -> list:
    """
    通过东方财富 API 获取全部 A 股实时行情
    支持沪深A股 + 北交所，每次最多5000条，通过翻页获取全量
    """
    now = time.time()
    if _STOCK_CACHE["data"] is not None and now - _STOCK_CACHE["ts"] < 300:
        return _STOCK_CACHE["data"]

    all_stocks = []
    page = 1
    max_pages = 12  # 每页5000，12页=60000，覆盖全A股+退市

    while page <= max_pages:
        try:
            url = "https://push2.eastmoney.com/api/qt/clist/get"
            params = {
                "pn": page,
                "pz": 5000,
                "po": 1,
                "np": 1,
                "ut": "bd1d9ddb04089700cf9c27f6f7426281",
                "fltt": 2,
                "invt": 2,
                "fid": "f3",
                "fs": "m:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23,m:0+t:81+s:2048",
                "fields": "f2,f3,f4,f5,f6,f7,f8,f9,f10,f12,f13,f14,f15,f16,f17,f18,f20,f21,f23,f62,f115,f128,f140,f141,f136",
            }

            resp = _http_session.get(url, params=params, headers=EASTMONEY_HEADERS, timeout=15)
            data = resp.json()

            if data and data.get("data") and data["data"].get("diff"):
                items = data["data"]["diff"]
                if not items:
                    break
                all_stocks.extend(items)
                logger.info(f"东方财富第{page}页: 获取 {len(items)} 只，累计 {len(all_stocks)} 只")
                if len(items) < 5000:
                    break
            else:
                break

            page += 1
        except Exception as e:
            logger.error(f"东方财富API第{page}页请求失败: {e}")
            break

    if all_stocks:
        _STOCK_CACHE["data"] = all_stocks
        _STOCK_CACHE["ts"] = now
        logger.info(f"✅ 东方财富全量获取完成：共 {len(all_stocks)} 只股票")

    return all_stocks


def parse_eastmoney_stock(item: dict) -> dict:
    """
    将东方财富 API 返回的单条数据解析为统一格式
    f2=最新价, f3=涨跌幅, f4=涨跌额, f5=成交量, f6=成交额
    f7=振幅, f8=换手率, f9=市盈率(动态), f10=量比
    f12=代码, f13=市场(0深圳 1上海), f14=名称
    f15=最高, f16=最低, f17=今开, f18=昨收
    f20=总市值, f21=流通市值, f23=市净率
    f62=主力净流入, f115=市盈率(TTM), f128=领涨股票
    f140=涨速, f141=5分钟涨跌
    """
    code = str(item.get("f12", ""))
    market_id = item.get("f13", 0)

    # 转换为 ts_code 格式
    if market_id == 1:
        ts_code = f"{code}.SH"
        market = "主板"
        if code.startswith("68"):
            market = "科创板"
    elif market_id == 0:
        ts_code = f"{code}.SZ"
        if code.startswith("30"):
            market = "创业板"
        elif code.startswith("8") or code.startswith("4"):
            market = "北交所"
        else:
            market = "主板"
    else:
        ts_code = f"{code}.SZ"
        market = "主板"

    return {
        "ts_code": ts_code,
        "name": str(item.get("f14", "")),
        "market": market,
        "close": _safe_float(item.get("f2")),
        "pct_chg": _safe_float(item.get("f3")),
        "change": _safe_float(item.get("f4")),
        "vol": _safe_float(item.get("f5")),
        "amount": _safe_float(item.get("f6")),
        "amplitude": _safe_float(item.get("f7")),
        "turnover_rate": _safe_float(item.get("f8")),
        "pe": _safe_float(item.get("f9")) or _safe_float(item.get("f115")),
        "pb": _safe_float(item.get("f23")),
        "high": _safe_float(item.get("f15")),
        "low": _safe_float(item.get("f16")),
        "open": _safe_float(item.get("f17")),
        "pre_close": _safe_float(item.get("f18")),
        "total_mv": _safe_float(item.get("f20")),
        "circ_mv": _safe_float(item.get("f21")),
    }


def fetch_eastmoney_stock_detail(code: str) -> dict:
    """
    获取单只股票的K线数据（日K）
    code: 如 "000001.SZ"
    """
    try:
        # 东方财富日K线接口
        secid = ""
        if ".SH" in code:
            secid = f"1.{code.replace('.SH', '')}"
        elif ".SZ" in code:
            secid = f"0.{code.replace('.SZ', '')}"

        if not secid:
            return {}

        url = "https://push2his.eastmoney.com/api/qt/stock/kline/get"
        params = {
            "secid": secid,
            "fields1": "f1,f2,f3,f4,f5,f6",
            "fields2": "f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61",
            "klt": 101,  # 日K
            "fqt": 1,    # 前复权
            "beg": "0",
            "end": "20500101",
            "lmt": 120,  # 最近120天
        }

        resp = _http_session.get(url, params=params, headers=EASTMONEY_HEADERS, timeout=15)
        data = resp.json()

        if data and data.get("data") and data["data"].get("klines"):
            klines = data["data"]["klines"]
            result = []
            for line in klines:
                parts = line.split(",")
                if len(parts) >= 6:
                    result.append({
                        "date": parts[0].replace("-", ""),
                        "open": float(parts[1]) if parts[1] else 0,
                        "close": float(parts[2]) if parts[2] else 0,
                        "high": float(parts[3]) if parts[3] else 0,
                        "low": float(parts[4]) if parts[4] else 0,
                        "vol": int(float(parts[5])) if parts[5] else 0,
                        "amount": float(parts[6]) if len(parts) > 6 and parts[6] else 0,
                        "pct_chg": float(parts[8]) if len(parts) > 8 and parts[8] else 0,
                    })
            return result

    except Exception as e:
        logger.error(f"获取 {code} K线失败: {e}")

    return []


def fetch_eastmoney_indices() -> list:
    """获取主要指数实时行情"""
    indices = []
    # 上证指数, 深证成指, 创业板指, 科创50, 北证50
    index_list = [
        ("1.000001", "上证指数"),
        ("0.399001", "深证成指"),
        ("0.399006", "创业板指"),
        ("1.000688", "科创50"),
        ("0.899050", "北证50"),
    ]

    try:
        codes_str = ",".join([item[0] for item in index_list])
        url = "https://push2.eastmoney.com/api/qt/ulist.np/get"
        params = {
            "fltt": 2,
            "fields": "f1,f2,f3,f4,f6,f12,f14",
            "secids": codes_str,
        }

        resp = _http_session.get(url, params=params, headers=EASTMONEY_HEADERS, timeout=10)
        data = resp.json()

        if data and data.get("data") and data["data"].get("diff"):
            code_map = {item[0]: item[1] for item in index_list}
            for item in data["data"]["diff"]:
                secid = str(item.get("f12", ""))
                indices.append({
                    "name": code_map.get(secid, secid),
                    "code": secid,
                    "close": _safe_float(item.get("f2")),
                    "pct_chg": _safe_float(item.get("f3")),
                    "change": _safe_float(item.get("f4")),
                    "amount": _safe_float(item.get("f6")),
                })

    except Exception as e:
        logger.error(f"获取指数数据失败: {e}")

    return indices


def fetch_eastmoney_industries() -> list:
    """获取行业板块数据"""
    industries = []

    try:
        url = "https://push2.eastmoney.com/api/qt/clist/get"
        params = {
            "pn": 1,
            "pz": 50,
            "po": 1,
            "np": 1,
            "ut": "bd1d9ddb04089700cf9c27f6f7426281",
            "fltt": 2,
            "invt": 2,
            "fid": "f3",
            "fs": "m:90+t:2",
            "fields": "f2,f3,f4,f8,f12,f14,f104,f105,f128,f140,f141,f136",
        }

        resp = _http_session.get(url, params=params, headers=EASTMONEY_HEADERS, timeout=10)
        data = resp.json()

        if data and data.get("data") and data["data"].get("diff"):
            for item in data["data"]["diff"]:
                industries.append({
                    "industry": str(item.get("f14", "")),
                    "code": str(item.get("f12", "")),
                    "close": _safe_float(item.get("f2")),
                    "pct_chg": _safe_float(item.get("f3")),
                    "change": _safe_float(item.get("f4")),
                    "turnover_rate": _safe_float(item.get("f8")),
                    "stocks": _safe_int(item.get("f104")),
                    "net_flow": round(_safe_float(item.get("f62")) / 100000000, 2) if item.get("f62") else 0,
                    "up_count": _safe_int(item.get("f136")),
                })

    except Exception as e:
        logger.error(f"获取行业数据失败: {e}")

    return industries


# ══════════════════════════════════════════════════════════════════════════════
# 工具函数
# ══════════════════════════════════════════════════════════════════════════════

def _safe_float(val, default=0.0):
    try:
        if val is None or val == "-":
            return default
        return round(float(val), 4)
    except Exception:
        return default


def _safe_int(val, default=0):
    try:
        if val is None:
            return default
        return int(float(val))
    except Exception:
        return default


def _classify_market(ts_code: str) -> str:
    code_upper = ts_code.upper()
    if code_upper.endswith(".BJ"):
        return "北交所"
    pure = code_upper.split(".")[0]
    if pure.startswith("68") and code_upper.endswith(".SH"):
        return "科创板"
    if pure.startswith("30"):
        return "创业板"
    return "主板"


# ══════════════════════════════════════════════════════════════════════════════
# 模拟数据（降级兜底）
# ══════════════════════════════════════════════════════════════════════════════

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


def _gen_mock_quote(stock):
    price = round(random.uniform(5, 300), 2)
    pct = round(random.uniform(-5, 5), 2)
    return {
        "ts_code": stock["ts_code"],
        "name": stock["name"],
        "industry": stock.get("industry", "未知"),
        "market": stock.get("market", "主板"),
        "close": price,
        "change": round(price * pct / 100, 2),
        "pct_chg": pct,
        "vol": random.randint(100000, 50000000),
        "amount": random.uniform(1000, 500000),
        "pe": round(random.uniform(8, 80), 2),
        "pb": round(random.uniform(0.5, 8), 2),
        "total_mv": random.uniform(50, 20000),
        "circ_mv": random.uniform(30, 15000),
        "turnover_rate": round(random.uniform(0.5, 8), 2),
    }


# ══════════════════════════════════════════════════════════════════════════════
# FastAPI 应用
# ══════════════════════════════════════════════════════════════════════════════

app = FastAPI(
    title="FinScreener API",
    description="智能股票筛选工具 - 阿里云函数计算版",
    version="2.0.0",
    docs_url="/docs",
)

# CORS配置
cors_origins = os.environ.get("CORS_ORIGINS",
    "https://finscreener-wcxd.vercel.app,https://finscreener.vercel.app,http://localhost:3000,http://localhost:5173"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ══════════════════════════════════════════════════════════════════════════════
# API 端点
# ══════════════════════════════════════════════════════════════════════════════

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "FinScreener API",
        "version": "2.0.0",
        "platform": "aliyun-fc",
        "datasource": "eastmoney",
        "message": "东方财富数据源 - 阿里云函数计算部署",
    }


@app.get("/")
async def root():
    return {
        "message": "FinScreener API - 阿里云函数计算版",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/api/market/overview")
async def get_market_overview():
    """市场概况：主要指数"""
    indices = fetch_eastmoney_indices()

    # 获取涨跌家数
    all_stocks = fetch_eastmoney_all_stocks()
    up_count = sum(1 for s in all_stocks if s.get("f3") and float(s["f3"]) > 0)
    down_count = sum(1 for s in all_stocks if s.get("f3") and float(s["f3"]) < 0)
    flat_count = len(all_stocks) - up_count - down_count

    total = len(all_stocks) if all_stocks else 1
    return {
        "success": True,
        "data": {
            "trade_date": datetime.now().strftime("%Y%m%d"),
            "indices": indices if indices else [
                {"name": "上证指数", "code": "000001.SH", "close": 3289, "pct_chg": 0.5, "amount": 312450000},
                {"name": "深证成指", "code": "399001.SZ", "close": 10512, "pct_chg": 0.78, "amount": 423120000},
            ],
            "market_stats": {
                "up_count": up_count,
                "down_count": down_count,
                "flat_count": flat_count,
                "total": total,
                "up_ratio": round(up_count / total * 100, 1) if total > 0 else 50,
            },
            "data_source": "eastmoney" if indices else "mock",
        }
    }


@app.get("/api/market/hot")
async def get_hot_stocks(limit: int = Query(20, ge=5, le=50)):
    """热门股票：涨幅榜、跌幅榜、成交额榜"""
    all_stocks = fetch_eastmoney_all_stocks()

    gainers = []
    losers = []
    by_amount = []

    if all_stocks:
        parsed = [parse_eastmoney_stock(s) for s in all_stocks if s.get("f14")]

        # 涨幅榜
        sorted_up = sorted(parsed, key=lambda x: x["pct_chg"], reverse=True)
        gainers = sorted_up[:limit]

        # 跌幅榜
        sorted_down = sorted(parsed, key=lambda x: x["pct_chg"])
        losers = sorted_down[:limit]

        # 成交额榜
        sorted_amt = sorted(parsed, key=lambda x: x["amount"], reverse=True)
        by_amount = sorted_amt[:limit]
    else:
        mock_list = [_gen_mock_quote(s) for s in MOCK_STOCKS]
        gainers = sorted(mock_list, key=lambda x: x["pct_chg"], reverse=True)[:limit]
        losers = sorted(mock_list, key=lambda x: x["pct_chg"])[:limit]
        by_amount = sorted(mock_list, key=lambda x: x["amount"], reverse=True)[:limit]

    return {
        "success": True,
        "data": {
            "trade_date": datetime.now().strftime("%Y%m%d"),
            "gainers": gainers,
            "losers": losers,
            "by_amount": by_amount,
            "data_source": "eastmoney" if all_stocks else "mock",
        }
    }


@app.get("/api/market/industries")
async def get_industries():
    """行业板块分析"""
    industries = fetch_eastmoney_industries()

    if not industries:
        industries = [
            {"industry": "电子", "stocks": 312, "pct_chg": 1.85, "net_flow": 45.3},
            {"industry": "医药生物", "stocks": 428, "pct_chg": 0.92, "net_flow": 23.1},
            {"industry": "计算机", "stocks": 256, "pct_chg": 2.14, "net_flow": 67.8},
            {"industry": "银行", "stocks": 47, "pct_chg": 0.23, "net_flow": -12.4},
            {"industry": "食品饮料", "stocks": 95, "pct_chg": 0.67, "net_flow": 8.7},
        ]

    return {
        "success": True,
        "data": {
            "trade_date": datetime.now().strftime("%Y%m%d"),
            "industries": industries,
            "data_source": "eastmoney" if industries else "mock",
        }
    }


@app.post("/api/screening")
@app.get("/api/screening")
async def screen_stocks(
    body: dict = {},
    market: str = "",
    industry: str = "",
    page: int = 1,
    page_size: int = 50,
):
    """股票条件筛选 - 支持多条件组合"""
    # GET请求时的参数处理
    if isinstance(body, dict) and not body.get("conditions"):
        conditions = []
    else:
        conditions = body.get("conditions", []) if isinstance(body, dict) else []

    all_stocks = fetch_eastmoney_all_stocks()
    data_source = "mock"

    if all_stocks:
        parsed = [parse_eastmoney_stock(s) for s in all_stocks if s.get("f14")]

        # 按市场过滤
        if market and market not in ("全部股票", ""):
            parsed = [s for s in parsed if s.get("market") == market]

        # 按行业过滤
        if industry:
            pattern = industry.replace(",", "|").replace("，", "|")
            parsed = [s for s in parsed if s.get("industry") and any(k in s["industry"] for k in pattern.split("|"))]

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
                    parsed = [s for s in parsed if s.get(field, 0) > val]
                elif op in ["lt", "<"]:
                    parsed = [s for s in parsed if s.get(field, 0) < val]
                elif op in ["gte", ">="]:
                    parsed = [s for s in parsed if s.get(field, 0) >= val]
                elif op in ["lte", "<="]:
                    parsed = [s for s in parsed if s.get(field, 0) <= val]
            except Exception:
                pass

        total = len(parsed)
        start = (page - 1) * page_size
        results = parsed[start: start + page_size]
        data_source = "eastmoney"
    else:
        # 降级模拟数据
        mock_list = [_gen_mock_quote(s) for s in MOCK_STOCKS]
        total = len(mock_list)
        start = (page - 1) * page_size
        results = mock_list[start:start + page_size]

    return {
        "success": True,
        "data": {
            "stocks": results,
            "total": total,
            "page": page,
            "page_size": page_size,
            "trade_date": datetime.now().strftime("%Y%m%d"),
            "data_source": data_source,
        }
    }


@app.get("/api/stocks/{ts_code}")
async def get_stock_detail(ts_code: str):
    """获取单只股票详情 + K线"""
    # 从缓存的全量数据中找基本信息
    all_stocks = fetch_eastmoney_all_stocks()
    stock_info = {}

    if all_stocks:
        for item in all_stocks:
            parsed = parse_eastmoney_stock(item)
            if parsed["ts_code"] == ts_code:
                stock_info = parsed
                break

    # 获取K线数据
    kline = fetch_eastmoney_stock_detail(ts_code)

    if not stock_info:
        mock = next((s for s in MOCK_STOCKS if s["ts_code"] == ts_code), MOCK_STOCKS[0])
        stock_info = _gen_mock_quote(mock)
        if not kline:
            kline = [
                {
                    "date": (datetime.now() - timedelta(days=120 - i)).strftime("%Y%m%d"),
                    "open": round(stock_info["close"] * random.uniform(0.97, 1.03), 2),
                    "high": round(stock_info["close"] * random.uniform(1.01, 1.06), 2),
                    "low": round(stock_info["close"] * random.uniform(0.94, 0.99), 2),
                    "close": round(stock_info["close"] * random.uniform(0.97, 1.03), 2),
                    "vol": random.randint(500000, 20000000),
                    "pct_chg": round(random.uniform(-3, 3), 2),
                }
                for i in range(60)
            ]

    return {
        "success": True,
        "data": {
            "basic": {"ts_code": ts_code, "name": stock_info.get("name", ""), "market": stock_info.get("market", "")},
            "quote": stock_info,
            "kline": kline,
            "data_source": "eastmoney" if stock_info else "mock",
        }
    }


@app.get("/api/stocks")
@app.post("/api/stocks/screen")
@app.get("/api/stocks/screen")
async def stocks_alias(
    body: dict = {},
    market: str = "",
    industry: str = "",
    page: int = 1,
    page_size: int = 50,
):
    """路由别名"""
    return await screen_stocks(body=body, market=market, industry=industry, page=page, page_size=page_size)


# ══════════════════════════════════════════════════════════════════════════════
# 阿里云函数计算入口
# Web函数模式：通过环境变量 FC_SERVER_PORT 获取端口
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("FC_SERVER_PORT", "9000"))
    logger.info(f"启动 FinScreener API，端口: {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
