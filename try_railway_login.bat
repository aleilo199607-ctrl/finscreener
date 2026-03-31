@echo off
echo ===============================================
echo     尝试Railway CLI登录和部署
echo ===============================================
echo.

echo 步骤1: 检查Railway CLI
railway --version
if %errorlevel% neq 0 (
    echo 错误: Railway CLI未安装或未找到
    pause
    exit /b 1
)

echo.
echo 步骤2: 尝试登录Railway
echo 注意: 这会打开浏览器进行授权
echo.
railway login
if %errorlevel% neq 0 (
    echo 登录失败，请手动操作
    pause
    exit /b 1
)

echo.
echo 步骤3: 创建新项目
echo 输入项目名称 (默认: finscreener-api):
set /p project_name=
if "%project_name%"=="" set project_name=finscreener-api

railway init --name %project_name%
if %errorlevel% neq 0 (
    echo 项目初始化失败
    pause
    exit /b 1
)

echo.
echo 步骤4: 部署项目
railway up
if %errorlevel% neq 0 (
    echo 部署失败
    pause
    exit /b 1
)

echo.
echo 步骤5: 设置环境变量
echo 正在设置TUSHARE_TOKEN...
railway variables set TUSHARE_TOKEN=13d6c6df74675cbb76961df7cde5c08fc73ee57a61b80636fa745e96

echo 正在设置AI_PROVIDER...
railway variables set AI_PROVIDER=mock

echo 正在设置ENVIRONMENT...
railway variables set ENVIRONMENT=production

echo 正在设置CORS_ORIGINS...
railway variables set CORS_ORIGINS=https://finscreener.vercel.app,http://localhost:3000

echo 正在设置LOG_LEVEL...
railway variables set LOG_LEVEL=INFO

echo 正在设置CACHE_TTL...
railway variables set CACHE_TTL=300

echo.
echo 步骤6: 获取部署状态和URL
railway status

echo.
echo ===============================================
echo        部署完成！请复制上面的URL
echo ===============================================
pause