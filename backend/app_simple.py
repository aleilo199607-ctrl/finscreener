"""
简化版FastAPI应用，用于Railway部署
避免复杂的数据库和Redis初始化
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title="FinScreener API",
    description="智能股票筛选工具后端API",
    version="1.0.0",
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

# 健康检查端点
@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "service": "FinScreener API",
        "version": "1.0.0",
        "simple_mode": True,
        "message": "简化版API正常运行中",
    }

# 根路径
@app.get("/")
async def root():
    """API根路径"""
    return {
        "message": "欢迎使用FinScreener API (简化版)",
        "docs": "/docs",
        "health": "/health",
        "api_prefix": "/api",
    }

# 股票相关API（示例）
@app.get("/api/stocks")
async def get_stocks():
    """获取股票列表（示例）"""
    return {
        "stocks": [
            {"code": "000001", "name": "平安银行", "price": 10.5},
            {"code": "000002", "name": "万科A", "price": 8.3},
        ],
        "count": 2,
        "message": "数据获取成功（示例数据）",
    }

# 股票筛选（示例）
@app.post("/api/screen")
async def screen_stocks():
    """股票筛选（示例）"""
    return {
        "results": [
            {"code": "000001", "name": "平安银行", "score": 85},
            {"code": "000002", "name": "万科A", "score": 78},
        ],
        "total": 2,
        "message": "筛选完成（示例结果）",
    }