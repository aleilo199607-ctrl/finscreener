from fastapi import APIRouter

from app.api.routes import stock

# 创建主路由器
api_router = APIRouter()

# 包含子路由
api_router.include_router(stock.router)