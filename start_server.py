#!/usr/bin/env python3
"""
简化版FinScreener启动脚本
Railway专用，避免复杂的生命周期管理问题
"""

import os
import sys
from pathlib import Path

# 添加backend目录到Python路径
sys.path.insert(0, str(Path(__file__).parent / "backend"))

# 设置环境变量
os.environ.setdefault("ENVIRONMENT", "production")
os.environ.setdefault("LOG_LEVEL", "INFO")
os.environ.setdefault("DEBUG", "false")

import uvicorn

if __name__ == "__main__":
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", "8000"))
    
    print(f"🚀 启动FinScreener后端服务在 {host}:{port}")
    print(f"📝 Python路径: {sys.path}")
    
    # 直接运行uvicorn，使用正确的模块路径
    uvicorn.run(
        "backend.main:app",
        host=host,
        port=port,
        log_level="info",
        workers=1,  # Railway推荐使用1个worker
        access_log=True
    )