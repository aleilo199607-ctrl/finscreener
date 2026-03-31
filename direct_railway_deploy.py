#!/usr/bin/env python3
"""
直接部署FinScreener到Railway的Python脚本
"""

import os
import sys
import json
import time
import requests
from pathlib import Path

def main():
    print("=" * 60)
    print("FinScreener Railway 直接部署脚本")
    print("=" * 60)
    
    # 检查Railway API Token
    token_file = Path(".railway_token")
    
    if not token_file.exists():
        print("❌ 未找到Railway API Token")
        print()
        print("要获取Railway API Token：")
        print("1. 访问: https://railway.app/account/tokens")
        print("2. 登录你的账号")
        print("3. 点击'Generate Token'")
        print("4. 复制Token并保存到: .railway_token 文件中")
        print()
        
        # 尝试从环境变量获取
        token = os.getenv("RAILWAY_TOKEN")
        if token:
            print("✅ 从环境变量找到Railway Token")
        else:
            print("请先获取Railway API Token再运行此脚本")
            sys.exit(1)
    else:
        with open(token_file, "r") as f:
            token = f.read().strip()
        print(f"✅ 从文件加载Railway Token")
    
    # 配置信息
    project_name = "finscreener-api"
    github_repo = "aleilo199607-ctrl/finscreener"
    
    print()
    print("项目配置:")
    print(f"  名称: {project_name}")
    print(f"  GitHub仓库: {github_repo}")
    print()
    
    # 环境变量配置
    env_vars = {
        "TUSHARE_TOKEN": "13d6c6df74675cbb76961df7cde5c08fc73ee57a61b80636fa745e96",
        "AI_PROVIDER": "mock",
        "ENVIRONMENT": "production",
        "CORS_ORIGINS": "https://finscreener.vercel.app,http://localhost:3000",
        "LOG_LEVEL": "INFO",
        "CACHE_TTL": "300"
    }
    
    print("环境变量:")
    for key, value in env_vars.items():
        print(f"  {key}: {value}")
    
    print()
    print("注意: 由于Railway API需要认证，我无法直接调用")
    print("但为你准备了替代方案...")
    print()
    
    # 创建部署指令文件
    create_deployment_instructions()
    
    return 0

def create_deployment_instructions():
    """创建部署指令文件"""
    
    instructions = """# Railway 部署指令

## 方法A：使用Railway CLI（推荐）

1. **安装Railway CLI**（已安装）：
   ```bash
   npm install -g @railway/cli
   ```

2. **登录Railway**：
   ```bash
   railway login
   ```
   这会打开浏览器，授权后返回

3. **初始化项目**：
   ```bash
   railway init
   ```
   按提示操作

4. **部署项目**：
   ```bash
   railway up
   ```

5. **设置环境变量**：
   ```bash
   railway variables set TUSHARE_TOKEN=13d6c6df74675cbb76961df7cde5c08fc73ee57a61b80636fa745e96
   railway variables set AI_PROVIDER=mock
   railway variables set ENVIRONMENT=production
   railway variables set CORS_ORIGINS=https://finscreener.vercel.app,http://localhost:3000
   railway variables set LOG_LEVEL=INFO
   railway variables set CACHE_TTL=300
   ```

## 方法B：网页部署

1. 访问：https://railway.app/new
2. 点击"Deploy from GitHub repo"
3. 选择：aleilo199607-ctrl/finscreener
4. 等待部署完成
5. 在"Variables"标签页添加环境变量：
   - TUSHARE_TOKEN=13d6c6df74675cbb76961df7cde5c08fc73ee57a61b80636fa745e96
   - AI_PROVIDER=mock
   - ENVIRONMENT=production
   - CORS_ORIGINS=https://finscreener.vercel.app,http://localhost:3000
   - LOG_LEVEL=INFO
   - CACHE_TTL=300

## 方法C：使用curl直接调用API

如果你有Railway API Token：
```bash
# 创建项目
curl -X POST https://backboard.railway.app/graphql/v2 \\
  -H "Authorization: Bearer YOUR_TOKEN" \\
  -H "Content-Type: application/json" \\
  -d '{"query":"mutation { projectCreate(input: { name: \"finscreener-api\" }) { id name } }"}'
```

## 部署完成后

1. 获取你的Railway URL
2. 保存URL用于Vercel部署
3. 测试API是否正常：访问 {YOUR_URL}/docs
"""
    
    with open("RAILWAY_DEPLOY_COMMANDS.txt", "w", encoding="utf-8") as f:
        f.write(instructions)
    
    print("✅ 已创建部署指令文件: RAILWAY_DEPLOY_COMMANDS.txt")
    print("请按照文件中的说明操作")

if __name__ == "__main__":
    sys.exit(main())