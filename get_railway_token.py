#!/usr/bin/env python3
"""
获取Railway API Token的辅助脚本
"""

import webbrowser
import time

print("=" * 60)
print("Railway API Token 获取助手")
print("=" * 60)
print()

print("由于Railway CLI需要交互式登录，我需要你手动获取API Token：")
print()

print("步骤1: 访问以下链接获取Railway API Token:")
print("  https://railway.app/account/tokens")
print()

print("步骤2: 登录后，点击'Generate Token'按钮")
print()

print("步骤3: 复制生成的API Token")
print()

print("步骤4: 将Token粘贴到下面的文件中:")
print("  C:\\Users\\42337\\WorkBuddy\\20260330172538\\FinScreener\\.railway_token")
print()

print("或者，你可以使用更简单的方法：")
print("1. 访问 https://railway.app/new")
print("2. 手动部署你的项目")
print("3. 然后告诉我你的Railway后端URL")
print()

# 尝试打开浏览器
try:
    webbrowser.open("https://railway.app/account/tokens")
    print("已尝试打开浏览器...")
except:
    print("无法自动打开浏览器，请手动复制上面的链接")

input("按Enter键继续...")