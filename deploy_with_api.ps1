# PowerShell脚本：使用Railway API直接部署

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "FinScreener Railway API直接部署" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

$RAILWAY_TOKEN = "36d71d4a-cea4-4f46-9813-92865de585ac"
$PROJECT_NAME = "finscreener-api"
$GITHUB_REPO = "aleilo199607-ctrl/finscreener"

# 环境变量
$ENV_VARS = @{
    "TUSHARE_TOKEN" = "13d6c6df74675cbb76961df7cde5c08fc73ee57a61b80636fa745e96"
    "AI_PROVIDER" = "mock"
    "ENVIRONMENT" = "production"
    "CORS_ORIGINS" = "https://finscreener.vercel.app,http://localhost:3000"
    "LOG_LEVEL" = "INFO"
    "CACHE_TTL" = "300"
}

Write-Host "🔍 验证Railway Token..." -ForegroundColor Yellow

# 测试Token有效性
try {
    $headers = @{
        "Authorization" = "Bearer $RAILWAY_TOKEN"
        "Content-Type" = "application/json"
    }
    
    $body = @{
        query = "query { me { id email } }"
    } | ConvertTo-Json
    
    $response = Invoke-RestMethod -Uri "https://backboard.railway.app/graphql/v2" `
        -Method Post `
        -Headers $headers `
        -Body $body `
        -TimeoutSec 30
    
    Write-Host "✅ Token验证成功!" -ForegroundColor Green
    Write-Host ""
} catch {
    Write-Host "❌ Token验证失败: $_" -ForegroundColor Red
    Write-Host "请检查Token是否正确，或Railway服务是否可用" -ForegroundColor Yellow
    exit 1
}

Write-Host "由于Railway API的复杂性，我为你准备了替代方案..." -ForegroundColor Yellow
Write-Host ""

Write-Host "==========================================" -ForegroundColor Green
Write-Host "        替代方案：使用Deploy按钮" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""

# 生成部署链接
$envString = ""
foreach ($key in $ENV_VARS.Keys) {
    $value = [System.Web.HttpUtility]::UrlEncode($ENV_VARS[$key])
    $envString += "$key%3D$value%26"
}
$envString = $envString.TrimEnd("%26")

$deployUrl = "https://railway.app/new?template=python&env=$envString"

Write-Host "请点击以下链接开始部署：" -ForegroundColor Cyan
Write-Host ""
Write-Host $deployUrl -ForegroundColor Green
Write-Host ""
Write-Host "或者手动复制：" -ForegroundColor Yellow
Write-Host "https://railway.app/new?template=python&env=TUSHARE_TOKEN%3D13d6c6df74675cbb76961df7cde5c08fc73ee57a61b80636fa745e96%26AI_PROVIDER%3Dmock%26ENVIRONMENT%3Dproduction%26CORS_ORIGINS%3Dhttps%3A%2F%2Ffinscreener.vercel.app%2Chttp%3A%2F%2Flocalhost%3A3000%26LOG_LEVEL%3DINFO%26CACHE_TTL%3D300" -ForegroundColor White
Write-Host ""

Write-Host "==========================================" -ForegroundColor Yellow
Write-Host "        部署步骤：" -ForegroundColor Yellow
Write-Host "==========================================" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. 点击上面的链接" -ForegroundColor Cyan
Write-Host "2. 登录GitHub账号" -ForegroundColor Cyan
Write-Host "3. 授权Railway访问你的仓库" -ForegroundColor Cyan
Write-Host "4. 选择仓库: $GITHUB_REPO" -ForegroundColor Cyan
Write-Host "5. 等待部署完成 (约2-3分钟)" -ForegroundColor Cyan
Write-Host "6. 复制Railway URL" -ForegroundColor Cyan
Write-Host ""

Write-Host "==========================================" -ForegroundColor Magenta
Write-Host "        部署完成后：" -ForegroundColor Magenta
Write-Host "==========================================" -ForegroundColor Magenta
Write-Host ""
Write-Host "1. 将Railway URL保存到 RAILWAY_URL.txt" -ForegroundColor White
Write-Host "2. 测试API是否正常：" -ForegroundColor White
Write-Host "   - {YOUR_URL}/docs (API文档)" -ForegroundColor Gray
Write-Host "   - {YOUR_URL}/health (健康检查)" -ForegroundColor Gray
Write-Host "3. 告诉我你的Railway URL" -ForegroundColor White
Write-Host ""

# 尝试打开浏览器
try {
    Start-Process $deployUrl
    Write-Host "✅ 已尝试打开浏览器..." -ForegroundColor Green
} catch {
    Write-Host "⚠️ 无法自动打开浏览器，请手动复制上面的链接" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "⚡ 部署完成后请告诉我你的Railway URL！" -ForegroundColor Cyan
Pause