#!/bin/bash

# FinScreener 一键部署脚本
# 作者: FinScreener Team
# 版本: 1.0.0

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查命令是否存在
check_command() {
    if ! command -v $1 &> /dev/null; then
        log_error "命令 $1 未找到，请先安装"
        exit 1
    fi
}

# 显示帮助
show_help() {
    echo "FinScreener 部署脚本"
    echo ""
    echo "用法: ./deploy.sh [选项]"
    echo ""
    echo "选项:"
    echo "  -h, --help          显示帮助信息"
    echo "  -d, --dev           部署到开发环境"
    echo "  -p, --prod          部署到生产环境"
    echo "  -t, --test          运行测试"
    echo "  -b, --build         构建项目"
    echo "  -c, --clean         清理构建产物"
    echo "  -s, --setup         设置开发环境"
    echo ""
    echo "示例:"
    echo "  ./deploy.sh --setup   设置开发环境"
    echo "  ./deploy.sh --dev     启动开发环境"
    echo "  ./deploy.sh --prod    部署到生产环境"
    echo "  ./deploy.sh --test    运行所有测试"
}

# 设置开发环境
setup_development() {
    log_info "开始设置开发环境..."
    
    # 检查必要的命令
    check_command node
    check_command npm
    check_command python
    check_command pip
    
    # 前端设置
    log_info "设置前端..."
    cd frontend
    npm install
    cd ..
    
    # 后端设置
    log_info "设置后端..."
    cd backend
    pip install -r requirements.txt
    
    # 创建环境变量文件
    if [ ! -f .env ]; then
        log_info "创建后端环境变量文件..."
        cp .env.example .env
        log_warning "请编辑 backend/.env 文件，配置必要的环境变量"
    fi
    
    cd ..
    
    # 前端环境变量
    cd frontend
    if [ ! -f .env ]; then
        log_info "创建前端环境变量文件..."
        cp .env.example .env.local
    fi
    cd ..
    
    log_success "开发环境设置完成！"
    echo ""
    echo "下一步："
    echo "1. 配置 backend/.env 文件（特别是 TUSHARE_TOKEN）"
    echo "2. 运行 ./deploy.sh --dev 启动开发服务器"
    echo "3. 访问 http://localhost:3000"
}

# 启动开发环境
start_development() {
    log_info "启动开发环境..."
    
    # 检查环境变量
    if [ ! -f "backend/.env" ]; then
        log_error "请先运行 ./deploy.sh --setup 设置环境"
        exit 1
    fi
    
    # 启动后端
    log_info "启动后端服务器..."
    cd backend
    uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
    BACKEND_PID=$!
    cd ..
    
    # 启动前端
    log_info "启动前端开发服务器..."
    cd frontend
    npm run dev &
    FRONTEND_PID=$!
    cd ..
    
    log_success "开发服务器已启动！"
    echo ""
    echo "访问以下地址："
    echo "- 前端: http://localhost:3000"
    echo "- 后端API: http://localhost:8000"
    echo "- API文档: http://localhost:8000/docs"
    echo ""
    echo "按 Ctrl+C 停止所有服务"
    
    # 等待用户中断
    wait $BACKEND_PID $FRONTEND_PID
}

# 构建项目
build_project() {
    log_info "开始构建项目..."
    
    # 前端构建
    log_info "构建前端..."
    cd frontend
    npm run build
    cd ..
    
    # 后端检查
    log_info "检查后端..."
    cd backend
    python -c "import sys; sys.path.insert(0, '.'); from main import app; print('后端导入成功')"
    cd ..
    
    log_success "项目构建完成！"
}

# 运行测试
run_tests() {
    log_info "开始运行测试..."
    
    # 前端测试
    log_info "运行前端测试..."
    cd frontend
    if npm run test:coverage; then
        log_success "前端测试通过！"
    else
        log_error "前端测试失败"
        exit 1
    fi
    cd ..
    
    # 后端测试
    log_info "运行后端测试..."
    cd backend
    if python -m pytest tests/ -v --cov=app --cov-report=term-missing; then
        log_success "后端测试通过！"
    else
        log_error "后端测试失败"
        exit 1
    fi
    cd ..
    
    log_success "所有测试通过！"
}

# 清理构建产物
clean_project() {
    log_info "开始清理..."
    
    # 前端清理
    if [ -d "frontend/dist" ]; then
        log_info "清理前端构建产物..."
        rm -rf frontend/dist
    fi
    
    if [ -d "frontend/node_modules" ]; then
        log_info "清理前端依赖..."
        rm -rf frontend/node_modules
    fi
    
    # 后端清理
    if [ -d "backend/__pycache__" ]; then
        log_info "清理Python缓存..."
        find backend -name "__pycache__" -type d -exec rm -rf {} +
        find backend -name "*.pyc" -delete
    fi
    
    if [ -d "backend/.pytest_cache" ]; then
        log_info "清理测试缓存..."
        rm -rf backend/.pytest_cache
    fi
    
    if [ -d "backend/coverage_html" ]; then
        log_info "清理覆盖率报告..."
        rm -rf backend/coverage_html
        rm -f backend/coverage.xml
    fi
    
    if [ -d "frontend/coverage" ]; then
        log_info "清理前端覆盖率报告..."
        rm -rf frontend/coverage
    fi
    
    log_success "清理完成！"
}

# 部署到生产环境
deploy_production() {
    log_info "开始部署到生产环境..."
    
    # 检查Git状态
    if ! git status --porcelain | grep -q "^[^?]"; then
        log_info "代码已提交，继续部署..."
    else
        log_warning "有未提交的更改，建议先提交代码"
        read -p "是否继续部署？(y/n): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_info "部署已取消"
            exit 0
        fi
    fi
    
    # 运行测试
    run_tests
    
    # 构建项目
    build_project
    
    log_success "项目已准备好部署！"
    echo ""
    echo "====================================================="
    echo "                 部署指南"
    echo "====================================================="
    echo ""
    echo "🚀 第一步：部署后端到 Railway"
    echo "-----------------------------------------"
    echo "1. 访问 https://railway.app"
    echo "2. 使用GitHub登录"
    echo "3. 点击 'New Project' → 'Deploy from GitHub repo'"
    echo "4. 授权访问你的GitHub仓库"
    echo "5. 选择你的FinScreener仓库"
    echo "6. Railway会自动检测 railway.json 配置"
    echo "7. 在 'Variables' 标签页添加环境变量："
    echo "   - TUSHARE_TOKEN: 你的Tushare Pro Token"
    echo "   - AI_PROVIDER: mock (测试) 或 deepseek (生产)"
    echo "   - (可选) 其他AI服务API密钥"
    echo ""
    echo "🎨 第二步：部署前端到 Vercel"
    echo "-----------------------------------------"
    echo "1. 访问 https://vercel.com"
    echo "2. 使用GitHub登录"
    echo "3. 点击 'Add New...' → 'Project'"
    echo "4. 导入你的FinScreener项目"
    echo "5. 在 'Root Directory' 选择 'frontend'"
    echo "6. 在 'Environment Variables' 添加："
    echo "   - VITE_API_URL: 你的Railway后端URL"
    echo "   - (例如: https://finscreener-api.up.railway.app)"
    echo "7. 点击 'Deploy'"
    echo ""
    echo "🔧 第三步：配置连接"
    echo "-----------------------------------------"
    echo "1. 获取Railway后端URL"
    echo "2. 更新Vercel前端环境变量"
    echo "3. 重新部署前端应用"
    echo ""
    echo "✅ 第四步：验证部署"
    echo "-----------------------------------------"
    echo "1. 后端健康检查:"
    echo "   curl https://你的后端域名.railway.app/health"
    echo "2. API测试:"
    echo "   curl https://你的后端域名.railway.app/api/stocks"
    echo "3. 访问前端网站:"
    echo "   打开 https://你的前端域名.vercel.app"
    echo "4. 测试筛选功能"
    echo ""
    echo "📋 部署检查清单："
    echo "-----------------------------------------"
    echo "☑️ 1. Railway后端已部署并运行"
    echo "☑️ 2. Vercel前端已部署并运行"
    echo "☑️ 3. 数据库和Redis服务正常运行"
    echo "☑️ 4. 环境变量配置正确"
    echo "☑️ 5. 前端能访问后端API"
    echo "☑️ 6. 筛选功能正常工作"
    echo ""
    echo "详细步骤请参考 DEPLOYMENT.md"
    echo ""
    echo "💡 提示：项目包含一键部署配置，Railway和Vercel都能自动检测配置！"

# 主函数
main() {
    # 如果没有参数，显示帮助
    if [ $# -eq 0 ]; then
        show_help
        exit 0
    fi
    
    # 解析参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -s|--setup)
                setup_development
                exit 0
                ;;
            -d|--dev)
                start_development
                exit 0
                ;;
            -p|--prod)
                deploy_production
                exit 0
                ;;
            -t|--test)
                run_tests
                exit 0
                ;;
            -b|--build)
                build_project
                exit 0
                ;;
            -c|--clean)
                clean_project
                exit 0
                ;;
            *)
                log_error "未知选项: $1"
                show_help
                exit 1
                ;;
        esac
        shift
    done
}

# 运行主函数
main "$@"