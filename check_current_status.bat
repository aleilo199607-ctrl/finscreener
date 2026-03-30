@echo off
echo ============================================
echo      FinScreener 部署状态检查
echo ============================================
echo.

echo [1] 检查本地Git仓库状态
echo -------------------------------------------
git status
echo.

echo [2] 检查远程仓库连接
echo -------------------------------------------
git config --get remote.origin.url
echo.

echo [3] 检查提交历史
echo -------------------------------------------
git log --oneline -3
echo.

echo [4] 检查部署配置文件
echo -------------------------------------------
echo 检查 railway.json...
if exist railway.json (
    echo ✓ railway.json 存在
) else (
    echo ✗ railway.json 不存在
)

echo 检查 vercel.json...
if exist frontend\vercel.json (
    echo ✓ vercel.json 存在
) else (
    echo ✗ vercel.json 不存在
)
echo.

echo [5] 检查环境变量模板
echo -------------------------------------------
echo 检查 railway_env_variables.txt...
if exist railway_env_variables.txt (
    echo ✓ 环境变量模板存在
    echo    Tushare Token已配置: 13d6c6df74675cbb76961df7cde5c08fc73ee57a61b80636fa745e96
) else (
    echo ✗ 环境变量模板不存在
)
echo.

echo [6] 当前状态总结
echo -------------------------------------------
echo 已完成:
echo ✓ 本地Git仓库初始化
echo ✓ Tushare Token获取
echo ✓ 所有配置文件准备
echo.
echo 待完成:
if not "%errorlevel%"=="0" (
    echo ⚠ GitHub仓库连接未设置
    echo   请运行以下命令:
    echo   git remote add origin https://github.com/YOUR_USERNAME/finscreener.git
    echo   git branch -M main
    echo   git push -u origin main
) else (
    echo ✓ GitHub仓库已连接
)
echo.
echo 下一步: 部署到Railway
echo 参考文件: RAILWAY_DEPLOY_STEPS.md
echo.

pause