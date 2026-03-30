@echo off
echo ===============================================
echo         FinScreener Railway 自动化部署脚本
echo ===============================================
echo.

echo 步骤1: 进入项目目录
cd /d "C:\Users\42337\WorkBuddy\20260330172538\FinScreener"

echo.
echo 步骤2: 初始化Railway项目（这需要你手动在浏览器中授权）
echo 请打开下面的链接进行授权：
echo.
echo https://railway.app/login/cli
echo.
echo 复制上面链接中的授权码，然后粘贴到这里：

railway login

echo.
echo 如果授权成功，继续下一步...
pause

echo.
echo 步骤3: 创建Railway项目
railway init

echo.
echo 步骤4: 部署项目
railway up

echo.
echo 步骤5: 添加环境变量
railway variables set TUSHARE_TOKEN=13d6c6df74675cbb76961df7cde5c08fc73ee57a61b80636fa745e96
railway variables set AI_PROVIDER=mock
railway variables set ENVIRONMENT=production
railway variables set CORS_ORIGINS=https://finscreener.vercel.app,http://localhost:3000
railway variables set LOG_LEVEL=INFO
railway variables set CACHE_TTL=300

echo.
echo 步骤6: 获取项目URL
echo 你的Railway后端URL是：
railway status

echo.
echo ===============================================
echo               部署完成！
echo ===============================================
echo.
echo 请复制上面的Railway URL，部署Vercel前端时需要用到。
pause