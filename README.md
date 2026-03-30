# FinScreener - 智能股票筛选工具

一个专业的A股股票筛选工具网站，具备多维度条件筛选和智能化股票信息卡片功能，风格参考专业金融工具（如TradingView）。

## 🚀 项目进度

### ✅ 已完成

#### 第一阶段：需求与规划
- [x] 创建详细的项目规划文档 (`PROJECT_PLAN.md`)
- [x] 定义核心功能需求
- [x] 规划页面结构和用户流程

#### 第二阶段：技术架构与实现

##### 前端 (React + TypeScript + Vite)
- [x] 项目框架搭建
- [x] 技术栈配置：
  - React 18 + TypeScript
  - Vite 构建工具
  - Tailwind CSS + shadcn/ui
  - React Router v6
  - Zustand 状态管理
  - TanStack Query (React Query)
  - Recharts 图表库
- [x] 项目结构创建
- [x] 主要组件框架：
  - 主布局组件 (`Layout.tsx`)
  - 筛选器页面 (`ScreenerPage.tsx`)
  - 工具函数库 (`utils/cn.ts`)
- [x] API服务配置 (`services/api.ts`)
- [x] TypeScript类型定义 (`types/index.ts`)

##### 后端 (Python + FastAPI)
- [x] 项目框架搭建
- [x] 技术栈配置：
  - FastAPI + Uvicorn
  - SQLAlchemy (异步ORM)
  - PostgreSQL / SQLite 支持
  - Redis 缓存
  - Tushare Pro API 集成
- [x] 核心模块实现：
  - 应用配置 (`core/config.py`)
  - 数据库配置 (`core/database.py`)
  - Redis缓存 (`core/redis.py`)
  - 数据模型定义 (`models/stock.py`)
  - Pydantic模型 (`schemas/stock.py`)
  - 股票数据服务 (`services/stock_service.py`)
  - AI摘要服务 (`services/ai_service.py`)
  - 数据同步服务 (`services/data_sync.py`)
  - API路由 (`api/routes/stock.py`)
- [x] 主应用入口 (`main.py`)
- [x] 依赖管理 (`requirements.txt`)

#### 第三阶段：测试与部署准备
- [x] 环境变量配置示例 (`.env.example`)
- [x] 项目文档

### ✅ 最新完成 (2026年3月30日更新)

#### 前端组件开发 ✅
- [x] 筛选面板组件 (`ScreeningPanel`) - 包含多维度条件筛选、预设管理、实时交互
- [x] 股票表格组件 (`StockTable`) - 支持排序、分页、市值分级、涨跌颜色标记
- [x] 股票详情页组件 (`StockDetailPage`) - 已完成基础框架
- [x] 图表组件集成 (`KLineChart`, `TechnicalIndicatorChart`) - 使用Recharts，支持K线图、技术指标分析

#### 测试套件 ✅
- [x] 前端单元测试配置 (Vitest + Testing Library)
- [x] 筛选面板组件完整测试套件
- [x] 后端测试配置 (pytest + async fixtures)
- [x] 股票API完整测试套件 (30+测试用例)
- [x] 覆盖率报告配置 (前端+后端)

#### 部署配置 ✅
- [x] Vercel部署配置 (`vercel.json`)
- [x] Railway部署配置 (`railway.json`)
- [x] 一键部署脚本 (`deploy.sh`)
- [x] 详细部署指南 (`DEPLOYMENT.md`)
- [x] 环境变量管理

## 📁 项目结构

```
FinScreener/
├── frontend/                 # React前端
│   ├── src/
│   │   ├── components/      # 可复用组件
│   │   ├── pages/          # 页面组件
│   │   ├── services/       # API服务
│   │   ├── store/          # 状态管理
│   │   ├── utils/          # 工具函数
│   │   └── types/          # TypeScript类型
│   ├── public/             # 静态资源
│   └── 配置文件...
├── backend/                 # FastAPI后端
│   ├── app/
│   │   ├── api/            # API路由
│   │   ├── core/           # 核心配置
│   │   ├── models/         # 数据模型
│   │   ├── services/       # 业务逻辑
│   │   └── schemas/        # Pydantic模型
│   ├── tests/              # 测试文件
│   └── 配置文件...
├── shared/                  # 共享代码
├── docs/                   # 项目文档
└── 配置文件...
```

## 🛠️ 快速开始

### 环境要求
- Node.js 18+ (前端)
- Python 3.10+ (后端)
- PostgreSQL 14+ 或 SQLite (数据库)
- Redis 6+ (缓存，可选)

### 后端设置
1. 进入后端目录：
   ```bash
   cd backend
   ```

2. 创建虚拟环境并安装依赖：
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. 配置环境变量：
   ```bash
   cp .env.example .env
   # 编辑 .env 文件，设置 TUSHARE_TOKEN 等必要配置
   ```

4. 启动后端服务器：
   ```bash
   python main.py
   ```

### 前端设置
1. 进入前端目录：
   ```bash
   cd frontend
   ```

2. 安装依赖：
   ```bash
   npm install
   ```

3. 配置环境变量：
   ```bash
   cp .env.example .env
   ```

4. 启动开发服务器：
   ```bash
   npm run dev
   ```

### 🚀 快速启动（推荐使用一键部署脚本）

```bash
# 1. 设置开发环境（首次运行）
chmod +x deploy.sh
./deploy.sh --setup

# 2. 启动开发服务器
./deploy.sh --dev

# 3. 运行测试
./deploy.sh --test

# 4. 部署到生产环境
./deploy.sh --prod
```

### 访问应用
- 前端：http://localhost:3000
- 后端API：http://localhost:8000
- API文档：http://localhost:8000/docs
- 测试覆盖率报告：
  - 前端：`frontend/coverage/index.html`
  - 后端：`backend/coverage_html/index.html`

## 🔧 关键技术特性

### 智能条件筛选
- 多维度条件组合（价格、技术指标、财务指标、市场表现）
- 实时筛选A股股票
- 条件保存与加载

### 数据可视化
- 交互式K线图
- 资金流向图
- 技术指标图表
- 财务数据对比

### AI智能分析
- 多维度AI摘要（技术面、基本面、资金面、消息面）
- 支持多个AI提供商（DeepSeek、OpenAI、GLM、百度文心一言）
- 情感分析和置信度评估

### 性能优化
- Redis缓存层
- 数据库连接池
- 异步API设计
- 智能数据同步

### 🔧 开发工具

#### 测试工具
- **前端测试**: Vitest + Testing Library
- **后端测试**: pytest + pytest-asyncio
- **测试覆盖率**: 前端85%+，后端80%+目标
- **E2E测试**: Playwright (规划中)

#### 代码质量
- **代码检查**: ESLint (前端), Flake8 (后端)
- **类型检查**: TypeScript (严格模式), mypy (后端)
- **格式化**: Prettier (前端), Black (后端)
- **提交检查**: Husky + lint-staged

#### 部署工具
- **一键部署脚本**: `./deploy.sh`
- **持续集成**: GitHub Actions (规划中)
- **容器化**: Docker + docker-compose
- **云部署**: Vercel (前端) + Railway (后端)

### 📡 API 文档

#### 主要API端点

| 端点 | 方法 | 描述 | 认证 |
|------|------|------|------|
| `/api/stocks` | GET | 获取股票列表 | 否 |
| `/api/stocks/{symbol}` | GET | 获取股票详情 | 否 |
| `/api/stocks/{symbol}/kline` | GET | 获取K线数据 | 否 |
| `/api/stocks/{symbol}/indicators/{indicator}` | GET | 获取技术指标 | 否 |
| `/api/stocks/screen` | POST | 筛选股票 | 否 |
| `/api/stocks/{symbol}/summary` | POST | 生成AI摘要 | 否 |
| `/api/market/overview` | GET | 获取市场概览 | 否 |
| `/health` | GET | 健康检查 | 否 |

#### 快速API测试
```bash
# 获取股票列表
curl http://localhost:8000/api/stocks

# 获取平安银行详情
curl http://localhost:8000/api/stocks/000001

# 筛选市盈率<15的股票
curl -X POST http://localhost:8000/api/stocks/screen \
  -H "Content-Type: application/json" \
  -d '{"conditions":[{"id":"pe_ratio","type":"range","value":[0,15]}]}'
```

### 🧪 测试套件

#### 前端测试
```bash
cd frontend
npm test                    # 运行测试
npm run test:coverage      # 运行测试并生成覆盖率报告
npm run test:ui            # 打开测试UI界面
npm run test:watch         # 监听模式运行测试
```

#### 后端测试
```bash
cd backend
pytest tests/ -v           # 运行所有测试
pytest tests/ --cov=app    # 运行测试并计算覆盖率
pytest tests/ -m "not slow" # 跳过慢速测试
```

#### 测试策略
- **单元测试**: 测试独立组件和函数
- **集成测试**: 测试API端点和数据库交互
- **性能测试**: 测试筛选查询性能
- **错误处理测试**: 测试异常情况处理

## 📊 数据源

- **主要数据源**：Tushare Pro API
  - 股票基本信息
  - 日行情数据
  - 财务指标
  - 资金流向
  - 市场数据

- **技术指标计算**：TA-Lib
  - MACD、KDJ、RSI
  - 布林带、均线
  - 成交量指标

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🚀 云部署指南

### 一键部署到生产环境

```bash
# 1. 准备代码仓库
git init
git add .
git commit -m "初始化FinScreener项目"

# 2. 推送到GitHub (可选)
git remote add origin https://github.com/你的用户名/finscreener.git
git push -u origin main

# 3. 使用部署脚本
./deploy.sh --setup   # 设置开发环境
./deploy.sh --test    # 运行测试
./deploy.sh --prod    # 部署到生产环境
```

### 分步部署指南

#### 后端部署 (Railway)
1. 访问 https://railway.app 并使用GitHub登录
2. 创建新项目 → 从GitHub仓库导入
3. 系统会自动检测 `railway.json` 配置文件
4. 在Environment Variables中配置：
   - `TUSHARE_TOKEN`: 你的Tushare Pro Token
   - `AI_PROVIDER`: `mock` (测试) 或 `deepseek`/`openai` (生产)
   - 其他可选环境变量
5. Railway会自动部署并创建PostgreSQL和Redis服务

#### 前端部署 (Vercel)
1. 访问 https://vercel.com 并使用GitHub登录
2. 导入项目 → 选择 `frontend` 目录
3. 在Environment Variables中配置：
   - `VITE_API_URL`: 你的Railway后端URL (如 `https://finscreener-api.up.railway.app`)
4. Vercel会自动构建和部署前端应用

#### 部署验证
```bash
# 检查后端健康状态
curl https://你的域名.railway.app/health
# 预期响应: {"status": "healthy"}

# 检查API可用性
curl https://你的域名.railway.app/api/stocks
# 预期响应: 股票列表JSON

# 访问前端网站
open https://你的域名.vercel.app
```

详细部署步骤、故障排除和最佳实践请参考 [DEPLOYMENT.md](./DEPLOYMENT.md)

### 📈 性能指标

#### 目标性能
- **API响应时间**: < 500ms (95% percentile)
- **页面加载时间**: < 3s (首屏)
- **筛选查询时间**: < 2s (1000只股票)
- **并发用户数**: 1000+
- **数据更新延迟**: < 15分钟

#### 监控建议
- **应用性能**: 使用Railway和Vercel内置监控
- **业务指标**: 实现自定义指标追踪
- **错误追踪**: 集成Sentry或类似服务
- **日志分析**: 配置结构化日志和日志聚合

## ⚠️ 免责声明

**重要提示**：本工具所有信息仅供学习参考，不构成任何投资建议。股市有风险，投资需谨慎。数据可能有延迟，投资决策请谨慎。

---

**开发团队**: FinScreener Team  
**项目状态**: ✅ 开发完成，可部署使用  
**最后更新**: 2026年3月30日  
**版本**: 1.0.0-rc1 (发布候选版)  
**部署状态**: 🟢 已准备好部署到Vercel + Railway