#!/usr/bin/env python3
"""
使用Railway API Token自动部署FinScreener
"""

import os
import sys
import json
import time
import requests
import subprocess
from pathlib import Path

# Railway API配置
RAILWAY_TOKEN = "36d71d4a-cea4-4f46-9813-92865de585ac"
RAILWAY_API_URL = "https://backboard.railway.app/graphql/v2"

# 项目配置
PROJECT_NAME = "finscreener-api"
GITHUB_REPO = "aleilo199607-ctrl/finscreener"

# 环境变量配置
ENV_VARS = {
    "TUSHARE_TOKEN": "13d6c6df74675cbb76961df7cde5c08fc73ee57a61b80636fa745e96",
    "AI_PROVIDER": "mock",
    "ENVIRONMENT": "production",
    "CORS_ORIGINS": "https://finscreener.vercel.app,http://localhost:3000",
    "LOG_LEVEL": "INFO",
    "CACHE_TTL": "300"
}

def print_header():
    """打印标题"""
    print("=" * 60)
    print("FinScreener Railway 自动化部署")
    print("=" * 60)
    print(f"Token: {RAILWAY_TOKEN[:10]}...{RAILWAY_TOKEN[-10:]}")
    print(f"项目: {PROJECT_NAME}")
    print(f"仓库: {GITHUB_REPO}")
    print("=" * 60)
    print()

def call_railway_api(query, variables=None):
    """调用Railway GraphQL API"""
    headers = {
        "Authorization": f"Bearer {RAILWAY_TOKEN}",
        "Content-Type": "application/json",
    }
    
    payload = {"query": query}
    if variables:
        payload["variables"] = variables
    
    try:
        response = requests.post(RAILWAY_API_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ API调用失败: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"响应内容: {e.response.text[:200]}")
        return None

def create_project():
    """创建Railway项目"""
    print("📦 步骤1: 创建Railway项目")
    
    query = """
    mutation {
      projectCreate(input: { name: "%s" }) {
        id
        name
        createdAt
      }
    }
    """ % PROJECT_NAME
    
    result = call_railway_api(query)
    if not result:
        print("❌ 创建项目失败")
        return None
    
    if "errors" in result:
        print(f"❌ GraphQL错误: {result['errors']}")
        return None
    
    project_data = result.get("data", {}).get("projectCreate", {})
    if not project_data:
        print("❌ 项目数据为空")
        return None
    
    project_id = project_data.get("id")
    project_name = project_data.get("name")
    
    print(f"✅ 项目创建成功!")
    print(f"   ID: {project_id}")
    print(f"   名称: {project_name}")
    print(f"   创建时间: {project_data.get('createdAt')}")
    
    return project_id

def connect_github_repo(project_id):
    """连接GitHub仓库"""
    print("\n🔗 步骤2: 连接GitHub仓库")
    
    query = """
    mutation($projectId: String!, $repo: String!) {
      gitHubRepositoryConnect(projectId: $projectId, repo: $repo) {
        id
        repo
        createdAt
      }
    }
    """
    
    variables = {
        "projectId": project_id,
        "repo": GITHUB_REPO
    }
    
    result = call_railway_api(query, variables)
    if not result:
        print("❌ 连接GitHub仓库失败")
        return False
    
    if "errors" in result:
        print(f"❌ GraphQL错误: {result['errors']}")
        return False
    
    print("✅ GitHub仓库连接成功!")
    return True

def set_environment_variables(project_id):
    """设置环境变量"""
    print("\n⚙️ 步骤3: 设置环境变量")
    
    success_count = 0
    total_count = len(ENV_VARS)
    
    for key, value in ENV_VARS.items():
        print(f"   设置 {key}...")
        
        query = """
        mutation($projectId: String!, $key: String!, $value: String!) {
          variableCreate(projectId: $projectId, key: $key, value: $value) {
            id
            key
            createdAt
          }
        }
        """
        
        variables = {
            "projectId": project_id,
            "key": key,
            "value": value
        }
        
        result = call_railway_api(query, variables)
        if result and "errors" not in result:
            success_count += 1
            print(f"   ✅ {key} 设置成功")
        else:
            print(f"   ❌ {key} 设置失败")
    
    print(f"\n📊 环境变量设置完成: {success_count}/{total_count}")
    return success_count == total_count

def trigger_deployment(project_id):
    """触发部署"""
    print("\n🚀 步骤4: 触发部署")
    
    query = """
    mutation($projectId: String!) {
      deploymentCreate(input: { projectId: $projectId }) {
        id
        status
        createdAt
      }
    }
    """
    
    variables = {"projectId": project_id}
    
    result = call_railway_api(query, variables)
    if not result:
        print("❌ 触发部署失败")
        return None
    
    if "errors" in result:
        print(f"❌ GraphQL错误: {result['errors']}")
        return None
    
    deployment_data = result.get("data", {}).get("deploymentCreate", {})
    if not deployment_data:
        print("❌ 部署数据为空")
        return None
    
    deployment_id = deployment_data.get("id")
    
    print("✅ 部署已触发!")
    print(f"   部署ID: {deployment_id}")
    print(f"   状态: {deployment_data.get('status', 'pending')}")
    
    return deployment_id

def get_project_url(project_id):
    """获取项目URL"""
    print("\n🌐 步骤5: 获取项目URL")
    
    query = """
    query($projectId: String!) {
      project(id: $projectId) {
        id
        name
        domains {
          domain
          createdAt
        }
        services {
          id
          name
          createdAt
        }
      }
    }
    """
    
    variables = {"projectId": project_id}
    
    # 尝试多次获取，因为URL可能需要一些时间生成
    for attempt in range(1, 11):
        print(f"   尝试获取URL (尝试 {attempt}/10)...")
        
        result = call_railway_api(query, variables)
        if result and "errors" not in result:
            project_data = result.get("data", {}).get("project", {})
            if project_data:
                domains = project_data.get("domains", [])
                if domains:
                    domain = domains[0].get("domain")
                    if domain:
                        url = f"https://{domain}"
                        print(f"✅ 获取URL成功!")
                        print(f"   域名: {domain}")
                        print(f"   URL: {url}")
                        return url
        
        time.sleep(5)  # 等待5秒再试
    
    print("❌ 获取URL失败，可能需要更多时间")
    return None

def deploy_with_railway_cli():
    """使用Railway CLI部署（备选方案）"""
    print("\n🔄 备选方案: 使用Railway CLI部署")
    
    # 设置环境变量
    os.environ["RAILWAY_TOKEN"] = RAILWAY_TOKEN
    
    commands = [
        ["railway", "--version"],
        ["railway", "login", "--browserless"],
        ["railway", "init", "--name", PROJECT_NAME, "--yes"],
        ["railway", "link"],
        ["railway", "up", "--detach"]
    ]
    
    # 添加环境变量设置命令
    for key, value in ENV_VARS.items():
        commands.append(["railway", "variables", "set", f"{key}={value}"])
    
    commands.append(["railway", "status"])
    
    for cmd in commands:
        print(f"执行: {' '.join(cmd)}")
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            if result.returncode == 0:
                print(f"✅ 成功")
                if result.stdout:
                    print(f"输出: {result.stdout[:200]}")
            else:
                print(f"❌ 失败 (code: {result.returncode})")
                if result.stderr:
                    print(f"错误: {result.stderr[:200]}")
        except Exception as e:
            print(f"❌ 异常: {e}")
    
    return True

def save_deployment_info(project_id, project_url):
    """保存部署信息"""
    print("\n💾 步骤6: 保存部署信息")
    
    info = {
        "project_id": project_id,
        "project_name": PROJECT_NAME,
        "railway_url": project_url,
        "github_repo": GITHUB_REPO,
        "environment_variables": ENV_VARS,
        "deployed_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "railway_token_prefix": RAILWAY_TOKEN[:8] + "..." + RAILWAY_TOKEN[-8:]
    }
    
    with open("RAILWAY_DEPLOYMENT_INFO.json", "w", encoding="utf-8") as f:
        json.dump(info, f, indent=2, ensure_ascii=False)
    
    # 也保存URL到单独文件
    if project_url:
        with open("RAILWAY_URL.txt", "w", encoding="utf-8") as f:
            f.write(project_url)
    
    print("✅ 部署信息已保存:")
    print(f"   RAILWAY_DEPLOYMENT_INFO.json - 完整部署信息")
    print(f"   RAILWAY_URL.txt - Railway后端URL")
    
    return True

def main():
    """主函数"""
    print_header()
    
    print("🔍 检查Railway Token有效性...")
    
    # 简单测试Token
    test_query = "query { me { id email } }"
    test_result = call_railway_api(test_query)
    
    if not test_result:
        print("❌ Railway Token无效或网络错误")
        print("\n🔄 尝试使用Railway CLI方法...")
        deploy_with_railway_cli()
        return 1
    
    if "errors" in test_result:
        print(f"❌ Token验证失败: {test_result['errors']}")
        print("\n🔄 尝试使用Railway CLI方法...")
        deploy_with_railway_cli()
        return 1
    
    print("✅ Token验证成功!")
    
    # 方法1: 使用GraphQL API
    print("\n🚀 开始使用Railway GraphQL API部署...")
    
    # 1. 创建项目
    project_id = create_project()
    if not project_id:
        print("❌ 创建项目失败，尝试备选方案")
        deploy_with_railway_cli()
        return 1
    
    # 2. 连接GitHub仓库
    if not connect_github_repo(project_id):
        print("⚠️ GitHub仓库连接失败，继续其他步骤...")
    
    # 3. 设置环境变量
    set_environment_variables(project_id)
    
    # 4. 触发部署
    deployment_id = trigger_deployment(project_id)
    
    # 5. 获取URL
    print("\n⏳ 等待部署完成（大约需要2-3分钟）...")
    time.sleep(30)  # 等待30秒
    
    project_url = get_project_url(project_id)
    
    if not project_url:
        print("⚠️ 未能获取URL，可能需要更长时间部署")
        project_url = f"https://{PROJECT_NAME}.up.railway.app (请稍后检查)"
    
    # 6. 保存信息
    save_deployment_info(project_id, project_url)
    
    print("\n" + "=" * 60)
    print("🎉 部署流程完成!")
    print("=" * 60)
    print()
    
    if project_url and "up.railway.app" in project_url:
        print("✅ Railway后端部署成功!")
        print(f"   🌐 后端URL: {project_url}")
        print()
        print("📋 下一步:")
        print("   1. 测试后端API:")
        print(f"      {project_url}/docs - API文档")
        print(f"      {project_url}/health - 健康检查")
        print("   2. 保存这个URL")
        print("   3. 开始Vercel前端部署")
    else:
        print("⚠️ 部署可能还在进行中")
        print("   请稍后访问Railway控制台查看:")
        print("   https://railway.app/projects")
        print()
        print("📋 后续步骤:")
        print("   1. 等待几分钟让部署完成")
        print("   2. 访问Railway控制台获取URL")
        print("   3. 告诉我你的Railway URL")
    
    print("\n⚡ 部署完成时间:", time.strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 60)
    
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⚠️ 部署被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ 部署过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)