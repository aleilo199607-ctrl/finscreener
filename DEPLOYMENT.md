# FinScreener 部署指南

本文档详细说明如何将FinScreener股票筛选工具部署到生产环境。

## 架构概述

FinScreener采用前后端分离架构：

- **前端**: React + TypeScript + Vite (部署到Vercel)
- **后端**: FastAPI + Python (部署到Railway)
- **数据库**: PostgreSQL (Railway托管)
- **缓存**: Redis (Railway托管)

## 环境要求

### 必需配置
1. **Tushare Pro Token** - 用于获取A股数据
   - 注册: https://tushare.pro
   - 获取Token后配置到环境变量

2. **至少一个AI提供商API密钥** (可选，但推荐)
   - DeepSeek、OpenAI、GLM或百度文心一言

### 推荐配置
- 域名 (用于生产环境)
- SSL证书 (Vercel和Railway自动提供)
- 监控告警配置

## 部署步骤

### 第一步：准备代码仓库

```bash
# 克隆项目
git clone https://github.com/yourusername/finscreener.git
cd finscreener

# 安装前端依赖
cd frontend
npm install

# 安装后端依赖
cd ../backend
pip install -r requirements.txt
```

### 第二步：部署后端到Railway

1. **注册Railway账号**
   - 访问: https://railway.app
   - 使用GitHub登录

2. **创建新项目**
   - 点击"New Project"
   - 选择"Deploy from GitHub repo"
   - 选择你的FinScreener仓库

3. **配置环境变量**
   在Railway项目的Environment Variables中设置：

   ```
   TUSHARE_TOKEN=你的Tushare Token
   AI_PROVIDER=deepseek  # 或 openai, glm, baidu, mock
   DEEPSEEK_API_KEY=你的DeepSeek API密钥
   ENVIRONMENT=production
   CORS_ORIGINS=https://你的前端域名,http://localhost:3000
   ```

4. **等待部署完成**
   - Railway会自动检测`railway.json`配置
   - 会自动创建PostgreSQL和Redis服务
   - 部署完成后获取API URL

### 第三步：部署前端到Vercel

1. **注册Vercel账号**
   - 访问: https://vercel.com
   - 使用GitHub登录

2. **导入项目**
   - 点击"Add New" → "Project"
   - 导入你的FinScreener仓库
   - 选择`frontend`目录

3. **配置环境变量**
   在Vercel项目的Environment Variables中设置：

   ```
   VITE_API_URL=https://你的Railway API地址
   ```

4. **自定义域名** (可选)
   - 在项目设置中添加自定义域名
   - Vercel会自动配置SSL证书

### 第四步：验证部署

1. **检查后端健康状态**
   ```
   curl https://你的railway域名/health
   # 应该返回: {"status": "healthy"}
   ```

2. **检查API端点**
   ```
   curl https://你的railway域名/api/stocks
   # 应该返回股票列表
   ```

3. **访问前端网站**
   - 打开Vercel提供的URL
   - 测试筛选功能和股票详情

## 环境变量说明

### 后端环境变量 (.env.example)

```env
# 数据库配置
DATABASE_URL=postgresql://user:password@localhost:5432/finscreener

# Redis配置
REDIS_URL=redis://localhost:6379/0

# Tushare配置
TUSHARE_TOKEN=你的Tushare Token

# AI服务配置
AI_PROVIDER=deepseek  # mock, deepseek, openai, glm, baidu
DEEPSEEK_API_KEY=你的DeepSeek API密钥
OPENAI_API_KEY=你的OpenAI API密钥
GLM_API_KEY=你的GLM API密钥
BAIDU_API_KEY=你的百度API密钥

# 应用配置
ENVIRONMENT=production  # development, testing, production
CORS_ORIGINS=https://finscreener.vercel.app,http://localhost:3000
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR
CACHE_TTL=300  # 缓存过期时间(秒)

# 安全配置
SECRET_KEY=你的密钥
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 前端环境变量 (.env.example)

```env
# API配置
VITE_API_URL=http://localhost:8000  # 开发环境
# VITE_API_URL=https://finscreener-api.up.railway.app  # 生产环境

# 应用配置
VITE_APP_NAME=FinScreener
VITE_APP_VERSION=1.0.0
VITE_APP_ENV=development  # development, production
```

## 数据库迁移

如果修改了数据模型，需要执行数据库迁移：

```bash
# 进入后端目录
cd backend

# 生成迁移脚本
alembic revision --autogenerate -m "描述变更"

# 应用迁移
alembic upgrade head
```

## 监控和日志

### Railway监控
- **日志**: 在Railway控制台查看实时日志
- **指标**: Railway提供CPU、内存、请求数等指标
- **健康检查**: 自动监控服务健康状态

### Vercel监控
- **Analytics**: 访问量、性能指标
- **Logs**: 前端错误日志
- **Speed Insights**: 页面加载性能

### 自定义监控建议
1. **应用性能监控 (APM)**
   - 推荐: Sentry, Datadog, New Relic
   - 配置错误追踪和性能分析

2. **业务指标监控**
   - API响应时间
   - 筛选查询性能
   - 数据同步状态

## 备份策略

### 数据库备份
Railway自动提供PostgreSQL备份：
- 每日自动备份
- 保留7天备份
- 支持手动备份

### 恢复数据库
```bash
# 从备份恢复
railway backup:restore <backup-id>

# 导出数据
pg_dump -h localhost -U user finscreener > backup.sql

# 导入数据
psql -h localhost -U user finscreener < backup.sql
```

## 安全配置

### 1. API安全
- CORS配置只允许信任的域名
- API速率限制
- JWT身份验证（如果需要）
- 输入验证和SQL注入防护

### 2. 网络安全
- 强制HTTPS
- 安全HTTP头
- CSRF防护
- XSS防护

### 3. 数据安全
- 数据库连接使用SSL
- Redis密码保护
- 敏感数据加密存储
- API密钥安全管理

## 故障排除

### 常见问题

1. **后端启动失败**
   ```
   # 检查依赖
   pip list | grep fastapi
   
   # 检查端口占用
   lsof -i :8000
   
   # 查看日志
   railway logs
   ```

2. **数据库连接问题**
   ```
   # 测试数据库连接
   python -c "import psycopg2; print(psycopg2.connect('$DATABASE_URL'))"
   
   # 检查迁移状态
   alembic current
   ```

3. **Redis连接问题**
   ```
   # 测试Redis连接
   redis-cli -u $REDIS_URL ping
   ```

4. **前端API调用失败**
   ```
   # 检查CORS配置
   # 检查API URL配置
   # 检查网络控制台错误
   ```

### 性能优化

1. **数据库索引优化**
   ```sql
   -- 为常用查询字段创建索引
   CREATE INDEX idx_stocks_symbol ON stocks(symbol);
   CREATE INDEX idx_quotes_date ON quotes(trade_date);
   ```

2. **缓存策略优化**
   - 热点数据缓存
   - 缓存预热
   - 缓存穿透防护

3. **API性能优化**
   - 查询分页
   - 响应压缩
   - CDN缓存静态资源

## 更新部署

### 前端更新
```bash
# 提交代码到GitHub
git add .
git commit -m "更新描述"
git push origin main

# Vercel会自动部署
```

### 后端更新
```bash
# Railway会自动检测并部署
# 或手动触发部署
railway up
```

### 数据库更新
```bash
# 生成迁移
alembic revision --autogenerate -m "更新描述"

# 应用迁移
alembic upgrade head

# 回滚迁移
alembic downgrade -1
```

## 联系支持

- **问题报告**: GitHub Issues
- **紧急支持**: 项目维护者邮箱
- **文档**: 本项目README和DEPLOYMENT.md
- **社区**: 技术论坛或Slack频道

## 附录

### 部署检查清单
- [ ] 所有环境变量已配置
- [ ] 数据库迁移已应用
- [ ] SSL证书有效
- [ ] 健康检查通过
- [ ] API端点可访问
- [ ] 前端可正常加载
- [ ] 筛选功能正常工作
- [ ] 错误监控已配置
- [ ] 备份策略已实施

### 性能基准
- API响应时间: < 500ms
- 页面加载时间: < 3s
- 筛选查询: < 2s
- 同时在线用户: 1000+
- 数据更新时间: 实时+15分钟延迟

### 成本估算
- **Vercel**: 免费计划 (Hobby)
- **Railway**: $5-20/月 (Starter计划)
- **Tushare Pro**: 免费或￥199/年
- **AI API**: 按使用量计费
- **域名**: $10-20/年 (可选)