from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn

from app.api.routes import api_router
from app.core.config import settings
from app.core.database import engine, Base
from app.core.redis import redis_client
from app.services.data_sync import DataSyncService

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    print("🚀 启动FinScreener后端服务...")
    
    # 创建数据库表
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # 初始化Redis连接
    await redis_client.initialize()
    
    # 启动数据同步服务（后台任务）
    data_sync_service = DataSyncService()
    data_sync_service.start()
    
    yield
    
    # 关闭时清理
    print("🛑 关闭FinScreener后端服务...")
    data_sync_service.stop()
    await redis_client.close()

# 创建FastAPI应用
app = FastAPI(
    title="FinScreener API",
    description="智能股票筛选工具后端API",
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan,
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件（可选，用于生产环境）
if settings.STATIC_FILES_ENABLED:
    app.mount("/static", StaticFiles(directory="static"), name="static")

# 挂载API路由
app.include_router(api_router, prefix="/api")

# 健康检查端点
@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "service": "FinScreener API",
        "version": "1.0.0",
        "timestamp": "2026-03-30T22:59:00Z"
    }

# 根路径重定向
@app.get("/")
async def root():
    """API根路径"""
    return {
        "message": "欢迎使用FinScreener API",
        "docs": "/docs" if settings.DEBUG else None,
        "health": "/health",
        "api_prefix": "/api",
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info" if settings.DEBUG else "warning",
    )