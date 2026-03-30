@echo off
echo ============================================
echo FinScreener 部署进度检查工具
echo ============================================
echo.

echo [步骤1] 检查本地Git仓库状态
echo --------------------------------------------
git status
echo.

echo [步骤2] 检查Git远程连接
echo --------------------------------------------
git remote -v
echo.

echo [步骤3] 检查关键配置文件
echo --------------------------------------------
if exist "railway.json" (
  echo ✅ railway.json 存在
) else (
  echo ❌ railway.json 不存在
)

if exist "frontend\vercel.json" (
  echo ✅ vercel.json 存在
) else (
  echo ❌ vercel.json 不存在
)

if exist "deploy.sh" (
  echo ✅ deploy.sh 存在
) else (
  echo ❌ deploy.sh 不存在
)

echo.
echo [步骤4] 检查项目结构
echo --------------------------------------------
echo 前端: frontend\
if exist "frontend\package.json" echo   ✅ package.json 存在
if exist "frontend\vite.config.ts" echo   ✅ vite.config.ts 存在
if exist "frontend\src\main.tsx" echo   ✅ main.tsx 存在

echo.
echo 后端: backend\
if exist "backend\main.py" echo   ✅ main.py 存在
if exist "backend\requirements.txt" echo   ✅ requirements.txt 存在
if exist "backend\railway.json" echo   ✅ railway.json 存在

echo.
echo [步骤5] 部署状态
echo --------------------------------------------
echo 请手动检查以下内容:
echo.
echo 1. GitHub仓库是否创建: https://github.com/YOUR_USERNAME/finscreener
echo 2. Railway项目是否部署: https://railway.app
echo 3. Tushare Token是否获取: https://tushare.pro
echo.
echo 如果以上都已完成，运行:
echo   python verify_deployment.py
echo.
echo ============================================
echo 检查完成！
echo ============================================
pause