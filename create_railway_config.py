#!/usr/bin/env python3
"""
创建Railway配置文件
"""

import os
import json
import sys
from pathlib import Path

def main():
    print("创建Railway配置文件...")
    
    # Railway配置目录
    railway_dir = Path.home() / ".railway"
    config_file = railway_dir / "config.json"
    
    # 创建目录
    railway_dir.mkdir(exist_ok=True)
    
    # 配置数据
    config = {
        "token": "36d71d4a-cea4-4f46-9813-92865de585ac",
        "userId": "auto-configured-by-finscreener",
        "createdAt": "2026-03-31T13:30:00.000Z"
    }
    
    # 写入配置文件
    with open(config_file, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)
    
    print(f"✅ Railway配置文件已创建: {config_file}")
    print(f"   Token: {config['token'][:10]}...{config['token'][-10:]}")
    
    # 测试配置
    print("\n测试Railway CLI...")
    
    # 设置环境变量
    os.environ["RAILWAY_TOKEN"] = config["token"]
    
    # 尝试运行railway命令
    import subprocess
    try:
        result = subprocess.run(["railway", "status"], 
                              capture_output=True, 
                              text=True, 
                              timeout=10)
        
        if result.returncode == 0:
            print("✅ Railway CLI配置成功!")
            print(f"输出: {result.stdout[:100]}...")
            
            # 现在尝试部署
            print("\n🚀 开始部署...")
            
            # 1. 初始化项目
            subprocess.run(["railway", "init", "--name", "finscreener-api", "--yes"], 
                          timeout=30)
            
            # 2. 部署
            subprocess.run(["railway", "up", "--detach"], timeout=60)
            
            # 3. 设置环境变量
            env_vars = [
                ("TUSHARE_TOKEN", "13d6c6df74675cbb76961df7cde5c08fc73ee57a61b80636fa745e96"),
                ("AI_PROVIDER", "mock"),
                ("ENVIRONMENT", "production"),
                ("CORS_ORIGINS", "https://finscreener.vercel.app,http://localhost:3000"),
                ("LOG_LEVEL", "INFO"),
                ("CACHE_TTL", "300")
            ]
            
            for key, value in env_vars:
                subprocess.run(["railway", "variables", "set", f"{key}={value}"], 
                              timeout=10)
            
            # 4. 获取状态
            result = subprocess.run(["railway", "status"], 
                                  capture_output=True, 
                                  text=True, 
                                  timeout=10)
            
            print("\n🎉 部署完成!")
            print(f"状态: {result.stdout}")
            
            # 提取URL
            lines = result.stdout.split('\n')
            for line in lines:
                if 'up.railway.app' in line or 'railway.app' in line:
                    url = line.strip()
                    if url.startswith('http'):
                        print(f"\n🌐 你的Railway URL: {url}")
                        
                        # 保存URL
                        with open("RAILWAY_URL.txt", "w") as f:
                            f.write(url)
                        print("✅ URL已保存到: RAILWAY_URL.txt")
                        break
            
        else:
            print(f"❌ Railway CLI测试失败: {result.stderr}")
            
    except Exception as e:
        print(f"❌ 执行失败: {e}")
    
    print("\n如果上述方法失败，请使用网页部署:")
    print("https://railway.app/new?template=python&env=TUSHARE_TOKEN%3D13d6c6df74675cbb76961df7cde5c08fc73ee57a61b80636fa745e96%26AI_PROVIDER%3Dmock%26ENVIRONMENT%3Dproduction%26CORS_ORIGINS%3Dhttps%3A%2F%2Ffinscreener.vercel.app%2Chttp%3A%2F%2Flocalhost%3A3000%26LOG_LEVEL%3DINFO%26CACHE_TTL%3D300")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())