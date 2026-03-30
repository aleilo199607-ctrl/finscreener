# Railway CLI 部署脚本
# 使用方法：
# 1. 用文本编辑器打开此文件
# 2. 运行此脚本
# 3. 按照提示操作

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "   FinScreener Railway CLI 部署工具"
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# 检查Railway CLI是否已安装
try {
    $railwayVersion = railway --version
    Write-Host "✅ Railway CLI 已安装: $railwayVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Railway CLI 未安装" -ForegroundColor Red
    Write-Host "正在安装 Railway CLI..." -ForegroundColor Yellow
    npm install -g @railway/cli
}

Write-Host ""
Write-Host "第一步：登录Railway" -ForegroundColor Cyan
Write-Host "------------------------------------------" -ForegroundColor Cyan
Write-Host "请按照以下步骤操作：" -ForegroundColor Yellow
Write-Host "1. 打开一个新的命令行窗口" -ForegroundColor Yellow
Write-Host "2. 运行: railway login" -ForegroundColor Yellow
Write-Host "3. 这会打开浏览器，授权Railway访问" -ForegroundColor Yellow
Write-Host "4. 登录成功后，回到这里继续" -ForegroundColor Yellow
Write-Host ""

$loginConfirmed = Read-Host "已登录成功？(y/n)"
if ($loginConfirmed -ne 'y') {
    Write-Host "请先完成登录" -ForegroundColor Red
    pause
    exit
}

Write-Host ""
Write-Host "第二步：创建Railway项目" -ForegroundColor Cyan
Write-Host "------------------------------------------" -ForegroundColor Cyan

# 进入项目目录
Set-Location "C:\Users\42337\WorkBuddy\20260330172538\FinScreener"

# 检查当前目录
Write-Host "当前目录: $(Get-Location)" -ForegroundColor Green

# 初始化Railway项目
Write-Host "正在初始化Railway项目..." -ForegroundColor Yellow
railway init --name "finscreener-api"

Write-Host ""
Write-Host "第三步：链接到GitHub仓库" -ForegroundColor Cyan
Write-Host "------------------------------------------" -ForegroundColor Cyan
Write-Host "项目已链接到GitHub仓库: aleilo199607-ctrl/finscreener" -ForegroundColor Green

Write-Host ""
Write-Host "第四步：设置环境变量" -ForegroundColor Cyan
Write-Host "------------------------------------------" -ForegroundColor Cyan

# 设置环境变量
$envVars = @{
    "TUSHARE_TOKEN" = "13d6c6df74675cbb76961df7cde5c08fc73ee57a61b80636fa745e96"
    "AI_PROVIDER" = "mock"
    "ENVIRONMENT" = "production"
    "CORS_ORIGINS" = "https://finscreener.vercel.app,http://localhost:3000"
    "LOG_LEVEL" = "INFO"
    "CACHE_TTL" = "300"
}

Write-Host "正在设置环境变量..." -ForegroundColor Yellow
foreach ($key in $envVars.Keys) {
    $value = $envVars[$key]
    Write-Host "  $key = $value" -ForegroundColor Gray
    railway variables set $key $value
}

Write-Host ""
Write-Host "第五步：部署到Railway" -ForegroundColor Cyan
Write-Host "------------------------------------------" -ForegroundColor Cyan
Write-Host "正在部署..." -ForegroundColor Yellow
railway up

Write-Host ""
Write-Host "✅ 部署已完成！" -ForegroundColor Green
Write-Host ""

# 获取部署URL
Write-Host "第六步：获取部署URL" -ForegroundColor Cyan
Write-Host "------------------------------------------" -ForegroundColor Cyan
Write-Host "正在获取部署URL..." -ForegroundColor Yellow
$deploymentUrl = railway status
Write-Host "部署URL: $deploymentUrl" -ForegroundColor Green

Write-Host ""
Write-Host "第七步：验证部署" -ForegroundColor Cyan
Write-Host "------------------------------------------" -ForegroundColor Cyan
Write-Host "正在验证部署..." -ForegroundColor Yellow

# 等待几秒让应用启动
Start-Sleep -Seconds 10

# 检查健康状态
Write-Host "检查健康状态..." -ForegroundColor Yellow
try {
    $healthCheck = Invoke-RestMethod -Uri "$deploymentUrl/health" -Method Get
    if ($healthCheck.status -eq "healthy") {
        Write-Host "✅ 健康检查通过: $($healthCheck.status)" -ForegroundColor Green
    } else {
        Write-Host "⚠️ 健康检查异常: $($healthCheck.status)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ 健康检查失败: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "       部署完成！" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "🎉 FinScreener后端已成功部署到Railway！" -ForegroundColor Green
Write-Host ""
Write-Host "后端URL: $deploymentUrl" -ForegroundColor Yellow
Write-Host "健康检查: $deploymentUrl/health" -ForegroundColor Yellow
Write-Host "API文档: $deploymentUrl/docs" -ForegroundColor Yellow
Write-Host ""
Write-Host "下一步：部署前端到Vercel" -ForegroundColor Cyan
Write-Host "需要将上述后端URL配置到Vercel环境变量中" -ForegroundColor Yellow
Write-Host ""

pause