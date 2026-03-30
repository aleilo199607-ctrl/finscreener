#!/bin/bash

# FinScreener GitHub仓库准备脚本

set -e

echo "=========================================="
echo "FinScreener GitHub仓库准备脚本"
echo "=========================================="
echo ""

# 检查是否在FinScreener目录
if [ ! -f "deploy.sh" ]; then
    echo "错误：请确保你在FinScreener项目根目录运行此脚本"
    exit 1
fi

echo "1. 清理不必要的文件..."
echo "=========================================="

# 创建.gitignore如果不存在
if [ ! -f ".gitignore" ]; then
    echo "创建.gitignore文件..."
    cat > .gitignore << 'EOF'
# 依赖
frontend/node_modules/
frontend/.npm
frontend/dist/
backend/__pycache__/
backend/.pytest_cache/
backend/venv/
backend/.env
backend/.venv
backend/*.pyc

# 构建产物
*.log
npm-debug.log*
yarn-debug.log*
yarn-error.log*
.env.local
.env.development.local
.env.test.local
.env.production.local

# 测试覆盖率
frontend/coverage/
backend/coverage_html/
backend/coverage.xml
backend/.coverage

# IDE文件
.vscode/
.idea/
*.swp
*.swo

# 系统文件
.DS_Store
Thumbs.db

# 本地配置文件
local_config/
secrets/
*.local
EOF
    echo "✅ .gitignore文件已创建"
fi

echo ""
echo "2. 检查项目结构..."
echo "=========================================="

# 检查关键文件
required_files=(
    "README.md"
    "deploy.sh"
    "frontend/package.json"
    "frontend/vite.config.ts"
    "frontend/src/main.tsx"
    "backend/main.py"
    "backend/requirements.txt"
    "backend/railway.json"
    "frontend/vercel.json"
)

for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file"
    else
        echo "❌ $file (缺失)"
    fi
done

echo ""
echo "3. 初始化Git仓库..."
echo "=========================================="

if [ ! -d ".git" ]; then
    echo "初始化Git仓库..."
    git init
    echo "✅ Git仓库已初始化"
else
    echo "⚠️ Git仓库已存在，跳过初始化"
fi

echo ""
echo "4. 添加文件到Git..."
echo "=========================================="

# 添加所有文件
git add .

echo "查看待提交文件："
git status --short

echo ""
echo "5. 提交更改..."
echo "=========================================="

echo "请输入提交信息 (默认为 '初始提交: FinScreener v1.0.0')："
read -r commit_message
commit_message=${commit_message:-"初始提交: FinScreener v1.0.0"}

git commit -m "$commit_message"

echo ""
echo "6. 创建GitHub仓库说明..."
echo "=========================================="

echo "🎯 下一步："
echo ""
echo "1. 在浏览器中打开 https://github.com/new"
echo "2. 填写仓库信息："
echo "   - Repository name: finscreener"
echo "   - Description: 智能股票筛选工具"
echo "   - 选择: Public (Vercel部署需要公开仓库)"
echo "   - 不要初始化README、.gitignore或许可证"
echo ""
echo "3. 创建仓库后，运行以下命令："
echo ""
echo "   # 连接到GitHub远程仓库"
echo "   git remote add origin https://github.com/YOUR_USERNAME/finscreener.git"
echo "   git branch -M main"
echo "   git push -u origin main"
echo ""
echo "4. 然后按照 QUICK_DEPLOY_GUIDE.md 进行部署"
echo ""
echo "=========================================="
echo "准备完成！现在去GitHub创建仓库吧！ 🚀"
echo "=========================================="