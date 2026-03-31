#!/usr/bin/env python3
"""
FinScreener Railway部署适配文件

Railway要求Python应用的入口点必须在根目录下。
此文件将正确导入backend目录下的主应用。
"""

import sys
import os
from pathlib import Path

# 添加backend目录到Python路径
sys.path.insert(0, str(Path(__file__).parent / "backend"))

# 导入真正的FastAPI应用
from backend.main import app

# 简化启动逻辑，直接返回app对象
# Railway会使用gunicorn或uvicorn自动启动
if __name__ == "__main__":
    import uvicorn
    import argparse
    
    parser = argparse.ArgumentParser(description="FinScreener API Server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    args = parser.parse_args()
    
    print(f"🚀 启动FinScreener后端服务在 {args.host}:{args.port}")
    # 注意：这里使用 'backend.main:app' 而不是 'main:app'
    uvicorn.run("backend.main:app", host=args.host, port=args.port, log_level="info")