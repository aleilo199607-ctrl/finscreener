# PowerShell脚本：直接通过Railway API部署

Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "     FinScreener Railway API直接部署" -ForegroundColor Cyan
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "步骤1: 你需要先获取Railway API Token" -ForegroundColor Yellow
Write-Host "1. 访问: https://railway.app" -ForegroundColor Yellow
Write-Host "2. 登录你的账号" -ForegroundColor Yellow
Write-Host "3. 点击右上角头像 → Settings → Tokens" -ForegroundColor Yellow
Write-Host "4. 创建一个新Token，复制它" -ForegroundColor Yellow
Write-Host ""
Write-Host "或者，你可以使用更简单的方法..." -ForegroundColor Green
Write-Host ""
Write-Host "===============================================" -ForegroundColor Green
Write-Host "        更简单的方法：使用Deploy按钮" -ForegroundColor Green
Write-Host "===============================================" -ForegroundColor Green
Write-Host ""
Write-Host "1. 访问下面的链接：" -ForegroundColor Cyan
Write-Host "https://railway.app/new?template=python&envs=TUSHARE_TOKEN%2CAI_PROVIDER%2CENVIRONMENT%2CCORS_ORIGINS%2CLOG_LEVEL%2CCACHE_TTL" -ForegroundColor Green
Write-Host ""
Write-Host "2. 选择你的GitHub仓库: aleilo199607-ctrl/finscreener" -ForegroundColor Cyan
Write-Host ""
Write-Host "3. 在环境变量表单中填写：" -ForegroundColor Cyan
Write-Host "   TUSHARE_TOKEN: 13d6c6df74675cbb76961df7cde5c08fc73ee57a61b80636fa745e96" -ForegroundColor Yellow
Write-Host "   AI_PROVIDER: mock" -ForegroundColor Yellow
Write-Host "   ENVIRONMENT: production" -ForegroundColor Yellow
Write-Host "   CORS_ORIGINS: https://finscreener.vercel.app,http://localhost:3000" -ForegroundColor Yellow
Write-Host "   LOG_LEVEL: INFO" -ForegroundColor Yellow
Write-Host "   CACHE_TTL: 300" -ForegroundColor Yellow
Write-Host ""
Write-Host "4. 点击Deploy按钮" -ForegroundColor Cyan
Write-Host ""
Write-Host "5. 等待部署完成，复制Production Domain" -ForegroundColor Cyan
Write-Host ""

Write-Host "===============================================" -ForegroundColor Green
Write-Host "             备用方案：手动部署" -ForegroundColor Green
Write-Host "===============================================" -ForegroundColor Green
Write-Host ""
Write-Host "如果上述方法都不可行，请按以下步骤操作：" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. 访问: https://railway.app" -ForegroundColor Cyan
Write-Host "2. 点击 '+ New Project'" -ForegroundColor Cyan
Write-Host "3. 选择 'Deploy from GitHub repo'" -ForegroundColor Cyan
Write-Host "4. 选择你的 'finscreener' 仓库" -ForegroundColor Cyan
Write-Host "5. 部署完成后，手动添加环境变量（见下面）" -ForegroundColor Cyan
Write-Host ""

Write-Host "需要添加的环境变量：" -ForegroundColor Yellow
Write-Host "TUSHARE_TOKEN=13d6c6df74675cbb76961df7cde5c08fc73ee57a61b80636fa745e96" -ForegroundColor White -BackgroundColor DarkBlue
Write-Host "AI_PROVIDER=mock" -ForegroundColor White -BackgroundColor DarkBlue
Write-Host "ENVIRONMENT=production" -ForegroundColor White -BackgroundColor DarkBlue
Write-Host "CORS_ORIGINS=https://finscreener.vercel.app,http://localhost:3000" -ForegroundColor White -BackgroundColor DarkBlue
Write-Host "LOG_LEVEL=INFO" -ForegroundColor White -BackgroundColor DarkBlue
Write-Host "CACHE_TTL=300" -ForegroundColor White -BackgroundColor DarkBlue
Write-Host ""

Pause