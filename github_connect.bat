@echo off
echo ==========================================
echo   FinScreener GitHub仓库连接工具
echo ==========================================
echo.
echo 请先告诉我你的GitHub用户名
echo （例如：如果你的GitHub地址是 https://github.com/leozhang）
echo （那么用户名就是 leozhang）
echo.

set /p github_username="请输入你的GitHub用户名: "
if "%github_username%"=="" (
    echo 错误：必须输入用户名！
    pause
    exit /b 1
)

echo.
echo 你的GitHub用户名: %github_username%
echo 仓库地址: https://github.com/%github_username%/finscreener.git
echo.

echo [1] 检查当前Git状态...
git status
echo.

echo [2] 检查是否已有远程仓库...
git config --get remote.origin.url
if %errorlevel% equ 0 (
    echo 警告：已存在远程仓库配置！
    set /p replace="是否要替换现有配置？(y/n): "
    if /i "%replace%" neq "y" (
        echo 已取消操作
        pause
        exit /b 0
    )
    git remote remove origin
    echo 已移除现有远程仓库配置
)

echo.
echo [3] 添加新的远程仓库...
git remote add origin https://github.com/%github_username%/finscreener.git

echo.
echo [4] 重命名分支为main...
git branch -M main

echo.
echo [5] 推送代码到GitHub...
echo 这可能需要一些时间，请耐心等待...
git push -u origin main

echo.
echo ==========================================
echo   ✅ 完成！代码已成功推送到GitHub
echo ==========================================
echo.
echo 下一步：
echo 1. 访问 https://railway.app
echo 2. 用GitHub登录
echo 3. 创建新项目
echo 4. 选择你的finscreener仓库
echo 5. 配置环境变量（参考railway_env_variables.txt文件）
echo.
pause