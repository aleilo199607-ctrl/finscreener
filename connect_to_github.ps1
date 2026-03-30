# PowerShell脚本：连接到GitHub仓库
# 使用方法：
# 1. 用文本编辑器打开此文件
# 2. 在第10行替换 YOUR_GITHUB_USERNAME 为你的GitHub用户名
# 3. 保存文件
# 4. 右键点击此文件，选择"使用PowerShell运行"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "   FinScreener GitHub仓库连接工具"
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# 请修改这里的GitHub用户名
$githubUsername = "YOUR_GITHUB_USERNAME"  # 请替换为你的GitHub用户名

# 检查是否已设置用户名
if ($githubUsername -eq "YOUR_GITHUB_USERNAME") {
    Write-Host "❌ 错误：请先修改脚本中的GitHub用户名" -ForegroundColor Red
    Write-Host ""
    Write-Host "修改方法：" -ForegroundColor Yellow
    Write-Host "1. 用记事本打开此文件" -ForegroundColor Yellow
    Write-Host "2. 找到第10行: `$githubUsername = `"YOUR_GITHUB_USERNAME`"`" -ForegroundColor Yellow
    Write-Host "3. 替换 YOUR_GITHUB_USERNAME 为你的实际GitHub用户名" -ForegroundColor Yellow
    Write-Host "4. 保存文件" -ForegroundColor Yellow
    Write-Host "5. 再次运行此脚本" -ForegroundColor Yellow
    pause
    exit
}

# 设置GitHub仓库URL
$githubRepoUrl = "https://github.com/$githubUsername/finscreener.git"

Write-Host "正在连接到GitHub仓库..." -ForegroundColor Green
Write-Host "仓库地址: $githubRepoUrl" -ForegroundColor Yellow
Write-Host ""

# 检查是否已有远程仓库
$currentRemote = git config --get remote.origin.url
if ($currentRemote) {
    Write-Host "⚠️ 警告：已存在远程仓库配置" -ForegroundColor Yellow
    Write-Host "当前远程仓库: $currentRemote" -ForegroundColor Yellow
    Write-Host ""
    
    $choice = Read-Host "是否要替换现有配置？(y/n)"
    if ($choice -ne 'y') {
        Write-Host "已取消操作" -ForegroundColor Red
        pause
        exit
    }
    
    # 移除现有远程仓库
    git remote remove origin
    Write-Host "✅ 已移除现有远程仓库配置" -ForegroundColor Green
}

# 添加新的远程仓库
Write-Host "正在添加新的远程仓库..." -ForegroundColor Green
git remote add origin $githubRepoUrl

# 重命名分支
Write-Host "正在重命名分支为main..." -ForegroundColor Green
git branch -M main

# 推送代码到GitHub
Write-Host "正在推送代码到GitHub..." -ForegroundColor Green
git push -u origin main

Write-Host ""
Write-Host "✅ 完成！代码已成功推送到GitHub" -ForegroundColor Green
Write-Host "✅ 远程仓库已设置: $githubRepoUrl" -ForegroundColor Green
Write-Host ""
Write-Host "下一步：部署到Railway" -ForegroundColor Cyan
Write-Host "1. 访问 https://railway.app" -ForegroundColor Yellow
Write-Host "2. 登录并创建新项目" -ForegroundColor Yellow
Write-Host "3. 选择你的finscreener仓库" -ForegroundColor Yellow
Write-Host "4. 配置环境变量（参考railway_env_variables.txt）" -ForegroundColor Yellow
Write-Host ""

pause