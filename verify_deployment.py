#!/usr/bin/env python3
"""
FinScreener 部署验证脚本
用于验证Railway后端和Vercel前端的部署状态
"""

import requests
import sys
import json
import time

def check_backend_health(backend_url):
    """检查后端健康状态"""
    try:
        print(f"🔍 检查后端健康状态: {backend_url}/health")
        response = requests.get(f"{backend_url}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "healthy":
                print("✅ 后端健康状态: 正常")
                return True
            else:
                print(f"❌ 后端健康状态异常: {data}")
                return False
        else:
            print(f"❌ 后端健康检查失败: HTTP {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ 后端连接失败: {e}")
        return False

def check_backend_api(backend_url):
    """检查后端API接口"""
    try:
        print(f"🔍 检查API接口: {backend_url}/api/stocks")
        response = requests.get(f"{backend_url}/api/stocks", timeout=10)
        if response.status_code == 200:
            data = response.json()
            stock_count = len(data.get("stocks", []))
            total = data.get("total", 0)
            print(f"✅ API接口正常 - 股票数量: {stock_count} (总计: {total})")
            return True
        else:
            print(f"❌ API接口失败: HTTP {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ API连接失败: {e}")
        return False

def check_frontend_access(frontend_url):
    """检查前端可访问性"""
    try:
        print(f"🔍 检查前端可访问性: {frontend_url}")
        response = requests.get(frontend_url, timeout=10)
        if response.status_code == 200:
            print("✅ 前端网站可访问")
            return True
        else:
            print(f"❌ 前端网站返回异常状态: HTTP {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ 前端连接失败: {e}")
        return False

def check_cors_config(backend_url, frontend_url):
    """检查CORS配置"""
    try:
        print(f"🔍 检查CORS配置: {backend_url}")
        response = requests.options(
            f"{backend_url}/api/stocks",
            headers={
                "Origin": frontend_url,
                "Access-Control-Request-Method": "GET"
            },
            timeout=10
        )
        
        # 检查CORS相关头
        cors_headers = response.headers.get("Access-Control-Allow-Origin", "")
        cors_methods = response.headers.get("Access-Control-Allow-Methods", "")
        
        if cors_headers:
            print(f"✅ CORS配置正确 - 允许来源: {cors_headers}")
            print(f"   允许方法: {cors_methods}")
            return True
        else:
            print("⚠️ CORS头未设置或配置可能有问题")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ CORS检查失败: {e}")
        return False

def check_connection_between_frontend_backend(backend_url, frontend_url):
    """检查前后端连接"""
    print(f"🔍 检查前后端连接...")
    
    # 模拟前端请求后端
    try:
        # 测试常见的API端点
        endpoints = [
            "/api/stocks",
            "/api/market/overview",
            "/health"
        ]
        
        all_success = True
        for endpoint in endpoints:
            try:
                response = requests.get(f"{backend_url}{endpoint}", timeout=10)
                if response.status_code == 200:
                    print(f"  ✅ {endpoint}: 连接成功")
                else:
                    print(f"  ❌ {endpoint}: 连接失败 (HTTP {response.status_code})")
                    all_success = False
            except Exception as e:
                print(f"  ❌ {endpoint}: 连接异常 ({e})")
                all_success = False
        
        return all_success
    except Exception as e:
        print(f"❌ 连接检查失败: {e}")
        return False

def main():
    """主函数"""
    print("=" * 50)
    print("FinScreener 部署验证脚本")
    print("=" * 50)
    print()
    
    # 配置（用户需要修改这些）
    BACKEND_URL = "https://finscreener-api.up.railway.app"  # 修改为你的实际后端URL
    FRONTEND_URL = "https://finscreener.vercel.app"  # 修改为你的实际前端URL
    
    print("📋 当前配置:")
    print(f"  后端: {BACKEND_URL}")
    print(f"  前端: {FRONTEND_URL}")
    print()
    
    # 运行检查
    checks = []
    
    print("🚀 开始验证部署...")
    print()
    
    # 检查1: 后端健康状态
    check1 = check_backend_health(BACKEND_URL)
    checks.append(("后端健康状态", check1))
    
    # 检查2: API接口
    check2 = check_backend_api(BACKEND_URL)
    checks.append(("API接口", check2))
    
    # 检查3: 前端可访问
    check3 = check_frontend_access(FRONTEND_URL)
    checks.append(("前端可访问", check3))
    
    # 检查4: CORS配置
    check4 = check_cors_config(BACKEND_URL, FRONTEND_URL)
    checks.append(("CORS配置", check4))
    
    # 检查5: 前后端连接
    check5 = check_connection_between_frontend_backend(BACKEND_URL, FRONTEND_URL)
    checks.append(("前后端连接", check5))
    
    print()
    print("=" * 50)
    print("验证结果汇总")
    print("=" * 50)
    
    total_checks = len(checks)
    passed_checks = sum(1 for _, passed in checks if passed)
    
    for name, passed in checks:
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{name}: {status}")
    
    print()
    print(f"📊 总计: {passed_checks}/{total_checks} 项检查通过")
    
    if passed_checks == total_checks:
        print("🎉 恭喜！所有检查通过，部署成功！")
        print()
        print("🔗 访问链接:")
        print(f"   前端网站: {FRONTEND_URL}")
        print(f"   后端API文档: {BACKEND_URL}/docs")
        print(f"   后端健康检查: {BACKEND_URL}/health")
        print()
        print("🚀 现在可以开始使用FinScreener了！")
        return True
    elif passed_checks >= 3:
        print("⚠️ 部分检查通过，部署基本成功但可能需要调整")
        print()
        print("💡 建议:")
        if not check1 or not check2:
            print("  - 检查Railway后端部署状态")
            print("  - 确认TUSHARE_TOKEN环境变量")
        if not check3:
            print("  - 检查Vercel前端部署状态")
        if not check4 or not check5:
            print("  - 检查CORS配置和环境变量")
        return False
    else:
        print("❌ 部署验证失败，需要重新检查部署配置")
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️ 验证被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 验证过程中出现异常: {e}")
        sys.exit(1)