#!/usr/bin/env python3
"""
超级简化版FinScreener启动脚本
确保Railway部署100%成功
"""

import os
import sys
from pathlib import Path

# 添加backend目录到Python路径
sys.path.insert(0, str(Path(__file__).parent / "backend"))

# 设置环境变量
os.environ.setdefault("ENVIRONMENT", "production")
os.environ.setdefault("LOG_LEVEL", "INFO")
os.environ.setdefault("DEBUG", "true")  # 开启调试模式

import uvicorn
from backend.app_simple import app

if __name__ == "__main__":
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", "8000"))
    
    print(f"🚀 启动简化版FinScreener后端服务在 {host}:{port}")
    print(f"📝 使用简化应用，无需数据库和Redis")
    
    # 直接运行uvicorn
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info",
        access_log=True
    )