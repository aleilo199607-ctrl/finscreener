#!/bin/bash

# FinScreener 启动脚本
# 用法: ./start.sh [dev|prod|docker|test]

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_message() {
    echo -e "${GREEN}[FinScreener]${NC} $1"
}

print_error() {
    echo -e "${RED}[错误]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[警告]${NC} $1"
}

print_info() {
    echo -e "${BLUE}[信息]${NC} $1"
}

# 检查命令是否存在
check_command() {
    if ! command -v $1 &> /dev/null; then
        print_error "命令 $1 未安装，请先安装"
        exit 1
    fi
}

# 检查环境变量
check_env() {
    if [ ! -f ".env" ]; then
        print_warning "未找到 .env 文件，正在从示例文件创建..."
        cp .env.example .env
        print_message "请编辑 .env 文件配置必要的环境变量"
        exit 1
    fi
    
    # 检查必要的环境变量
    if [ -z "$TUSHARE_TOKEN" ]; then
        print_error "请设置 TUSHARE_TOKEN 环境变量"
        print_info "获取地址: https://tushare.pro"
        exit 1
    fi
}

# 开发环境启动
start_dev() {
    print_message "启动开发环境..."
    
    # 启动后端
    print_info "启动后端服务..."
    cd backend
    python -m venv venv 2>/dev/null || true
    source venv/bin/activate
    pip install -r requirements.txt
    python main.py &
    BACKEND_PID=$!
    cd ..
    
    # 启动前端
    print_info "启动前端服务..."
    cd frontend
    npm install
    npm run dev &
    FRONTEND_PID=$!
    cd ..
    
    print_message "开发环境已启动！"
    print_info "前端: http://localhost:3000"
    print_info "后端API: http://localhost:8000"
    print_info "API文档: http://localhost:8000/docs"
    
    # 等待用户中断
    trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; print_message '服务已停止'" INT
    wait
}

# 生产环境启动
start_prod() {
    print_message "启动生产环境..."
    
    check_env
    
    # 检查Docker
    check_command docker
    check_command docker-compose
    
    # 停止现有服务
    docker-compose down
    
    # 启动服务
    docker-compose up -d
    
    print_message "生产环境已启动！"
    print_info "应用: http://localhost"
    print_info "API: http://localhost/api"
    print_info "监控: http://localhost:9090 (Prometheus)"
    print_info "监控面板: http://localhost:3001 (Grafana)"
    print_info "数据库管理: http://localhost:5050 (pgAdmin)"
    
    # 查看日志
    docker-compose logs -f
}

# Docker环境启动
start_docker() {
    print_message "启动Docker开发环境..."
    
    check_command docker
    check_command docker-compose
    
    # 停止现有服务
    docker-compose -f docker-compose.dev.yml down
    
    # 启动服务
    docker-compose -f docker-compose.dev.yml up
    
    print_message "Docker开发环境已启动！"
}

# 运行测试
run_tests() {
    print_message "运行测试..."
    
    # 后端测试
    if [ -d "backend" ]; then
        print_info "运行后端测试..."
        cd backend
        python -m pytest tests/ -v
        cd ..
    fi
    
    # 前端测试
    if [ -d "frontend" ]; then
        print_info "运行前端测试..."
        cd frontend
        npm test -- --watchAll=false
        cd ..
    fi
    
    print_message "测试完成！"
}

# 初始化数据库
init_db() {
    print_message "初始化数据库..."
    
    if [ -d "backend" ]; then
        cd backend
        python -m venv venv 2>/dev/null || true
        source venv/bin/activate
        
        # 运行数据库迁移
        print_info "运行数据库迁移..."
        alembic upgrade head
        
        # 初始化数据
        print_info "初始化基础数据..."
        python -c "
from app.core.database import init_db
from app.core.config import settings
import asyncio

async def main():
    await init_db()
    print('数据库初始化完成')

asyncio.run(main())
        "
        
        cd ..
        print_message "数据库初始化完成！"
    else
        print_error "后端目录不存在"
    fi
}

# 显示帮助
show_help() {
    echo "FinScreener 启动脚本"
    echo ""
    echo "用法: $0 [命令]"
    echo ""
    echo "命令:"
    echo "  dev     启动开发环境 (默认)"
    echo "  prod    启动生产环境 (Docker Compose)"
    echo "  docker  启动Docker开发环境"
    echo "  test    运行测试"
    echo "  db      初始化数据库"
    echo "  help    显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 dev      # 启动开发环境"
    echo "  $0 prod     # 启动生产环境"
    echo "  $0 test     # 运行所有测试"
}

# 主函数
main() {
    COMMAND=${1:-dev}
    
    case $COMMAND in
        dev)
            start_dev
            ;;
        prod)
            start_prod
            ;;
        docker)
            start_docker
            ;;
        test)
            run_tests
            ;;
        db)
            init_db
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            print_error "未知命令: $COMMAND"
            show_help
            exit 1
            ;;
    esac
}

# 加载环境变量
if [ -f ".env" ]; then
    export $(grep -v '^#' .env | xargs)
fi

# 执行主函数
main "$@"