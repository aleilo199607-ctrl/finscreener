#!/usr/bin/env python3
"""
测试Railway配置是否正确
"""

import os
import sys
from pathlib import Path

def check_requirements():
    """检查requirements.txt是否存在"""
    req_file = Path("requirements.txt")
    if req_file.exists():
        print(f"✅ requirements.txt 存在")
        with open(req_file, "r") as f:
            lines = f.readlines()
            print(f"✅ 依赖数量: {len(lines)} 个")
    else:
        print(f"❌ requirements.txt 不存在")
        return False
    return True

def check_main_py():
    """检查main.py是否正确"""
    main_file = Path("main.py")
    if main_file.exists():
        print(f"✅ main.py 存在")
        
        # 检查是否能正确导入
        try:
            sys.path.insert(0, str(Path(__file__).parent / "backend"))
            from backend.main import app
            print(f"✅ 可以正确导入FastAPI应用")
        except Exception as e:
            print(f"❌ 导入应用失败: {e}")
            return False
    else:
        print(f"❌ main.py 不存在")
        return False
    return True

def check_railway_config():
    """检查railway.toml配置"""
    config_file = Path("railway.toml")
    if config_file.exists():
        print(f"✅ railway.toml 存在")
        
        with open(config_file, "r") as f:
            content = f.read()
            
        # 检查关键配置
        if "startCommand" in content:
            print(f"✅ 包含启动命令")
        else:
            print(f"⚠️  缺少启动命令")
            
        if "TUSHARE_TOKEN" in content:
            print(f"✅ 包含Tushare Token配置")
        else:
            print(f"❌ 缺少Tushare Token配置")
            return False
    else:
        print(f"❌ railway.toml 不存在")
        return False
    return True

def check_structure():
    """检查项目结构"""
    print("\n📁 项目结构检查:")
    required_dirs = ["backend", "backend/app", "backend/app/api", "backend/app/core"]
    
    for dir_path in required_dirs:
        if Path(dir_path).exists():
            print(f"✅ {dir_path}/")
        else:
            print(f"❌ {dir_path}/ 不存在")
            return False
    
    return True

def main():
    print("🔍 开始检查Railway部署配置...")
    print("=" * 50)
    
    all_passed = True
    all_passed &= check_requirements()
    all_passed &= check_main_py()
    all_passed &= check_railway_config()
    all_passed &= check_structure()
    
    print("=" * 50)
    
    if all_passed:
        print("🎉 所有检查通过！Railway部署配置正确。")
        print("\n🚀 现在可以重新尝试Railway部署：")
        print("1. 重新打开部署链接")
        print("2. 选择你的GitHub仓库")
        print("3. 等待部署完成")
    else:
        print("❌ 有些检查未通过，需要修复问题。")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)