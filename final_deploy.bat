@echo off
echo ===============================================
echo     FinScreener Railway 最终部署脚本
echo ===============================================
echo.

echo 步骤1: 设置Railway Token环境变量
set RAILWAY_TOKEN=36d71d4a-cea4-4f46-9813-92865de585ac

echo 步骤2: 验证Railway CLI
railway --version
if %errorlevel% neq 0 (
    echo 错误: Railway CLI未安装
    echo 正在安装Railway CLI...
    npm install -g @railway/cli
    railway --version
    if %errorlevel% neq 0 (
        echo 安装失败，请手动安装
        pause
        exit /b 1
    )
)

echo.
echo 步骤3: 使用Token登录Railway
echo 注意: 这会将Token保存到Railway配置文件
railway login --browserless --token %RAILWAY_TOKEN%
if %errorlevel% neq 0 (
    echo 登录失败，尝试其他方法...
    goto :web_deploy
)

echo.
echo 步骤4: 创建项目
railway init --name finscreener-api --yes
if %errorlevel% neq 0 (
    echo 项目创建失败
    goto :web_deploy
)

echo.
echo 步骤5: 部署项目
railway up --detach
if %errorlevel% neq 0 (
    echo 部署失败
    goto :web_deploy
)

echo.
echo 步骤6: 设置环境变量
railway variables set TUSHARE_TOKEN=13d6c6df74675cbb76961df7cde5c08fc73ee57a61b80636fa745e96
railway variables set AI_PROVIDER=mock
railway variables set ENVIRONMENT=production
railway variables set CORS_ORIGINS=https://finscreener.vercel.app,http://localhost:3000
railway variables set LOG_LEVEL=INFO
railway variables set CACHE_TTL=300

echo.
echo 步骤7: 获取项目状态
railway status

echo.
echo ===============================================
echo        Railway CLI部署完成！
echo ===============================================
echo.
echo 请复制上面的URL，保存到RAILWAY_URL.txt文件中
echo.
pause
exit /b 0

:web_deploy
echo.
echo ===============================================
echo     切换到网页部署方案
echo ===============================================
echo.
echo 由于CLI部署失败，请使用网页部署：
echo.
echo 请访问以下链接：
echo https://railway.app/new?template=python^&env=TUSHARE_TOKEN%3D13d6c6df74675cbb76961df7cde5c08fc73ee57a61b80636fa745e96%26AI_PROVIDER%3Dmock%26ENVIRONMENT%3Dproduction%26CORS_ORIGINS%3Dhttps%3A%2F%2Ffinscreener.vercel.app%2Chttp%3A%2F%2Flocalhost%3A3000%26LOG_LEVEL%3DINFO%26CACHE_TTL%3D300
echo.
echo 部署步骤：
echo 1. 点击上面的链接
echo 2. 登录GitHub
echo 3. 选择仓库: aleilo199607-ctrl/finscreener
echo 4. 等待部署完成
echo 5. 复制Railway URL
echo.
echo 部署完成后，请将URL保存到RAILWAY_URL.txt
echo.
pause