# FinScreener 部署配置指南

## 1. 部署前准备

### 1.1 必需服务
1. **Tushare Pro Token**
   - 注册地址: https://tushare.pro
   - 免费版本：提供基础股票数据
   - 专业版本：更多数据接口和实时数据

2. **GitHub账号**
   - 用于Railway和Vercel部署
   - 将代码推送到GitHub仓库

3. **AI服务（可选但推荐）**
   - DeepSeek API: https://platform.deepseek.com/
   - OpenAI API: https://platform.openai.com/
   - 百度文心一言: https://yiyan.baidu.com/
   - GLM API: https://open.bigmodel.cn/

### 1.2 账户注册
1. **Railway** (后端): https://railway.app
   - 免费额度: $5/月
   - 包含: PostgreSQL数据库 + Redis缓存

2. **Vercel** (前端): https://vercel.com
   - 免费额度: 足够个人使用
   - 包含: 自动SSL、CDN、监控

## 2. 环境变量配置

### 2.1 Railway后端环境变量

```bash
# 必需配置
TUSHARE_TOKEN=你的Tushare Token

# AI服务配置（选一即可）
AI_PROVIDER=deepseek  # 或 openai、glm、baidu、mock
DEEPSEEK_API_KEY=你的DeepSeek API密钥

# 数据库配置（Railway自动配置）
DATABASE_URL=postgresql://railway:xxx@xxx.railway.app:5432/railway

# Redis配置（Railway自动配置）
REDIS_URL=redis://default:xxx@xxx.upstash.io:6379

# 可选配置
DEBUG=false
CORS_ORIGINS=https://你的前端域名.vercel.app
```

### 2.2 Vercel前端环境变量

```bash
# 必需配置
VITE_API_URL=https://你的后端域名.railway.app

# 可选配置
VITE_APP_TITLE=FinScreener - 智能股票筛选工具
VITE_APP_VERSION=1.0.0
```

## 3. 一键部署步骤

### 步骤1: 准备代码仓库

```bash
# 1. 初始化Git仓库
git init
git add .
git commit -m "初始提交: FinScreener股票筛选工具 v1.0.0"

# 2. 创建GitHub仓库（在网页端创建）
# 访问 https://github.com/new
# 仓库名: finscreener
# 描述: 智能股票筛选工具
# 选择: Public 或 Private

# 3. 连接到GitHub
git remote add origin https://github.com/你的用户名/finscreener.git
git branch -M main
git push -u origin main
```

### 步骤2: 部署后端到Railway

1. **访问Railway**
   - 打开 https://railway.app
   - 使用GitHub登录

2. **创建项目**
   - 点击 "New Project"
   - 选择 "Deploy from GitHub repo"
   - 授权访问GitHub
   - 选择 "finscreener" 仓库

3. **自动检测配置**
   - Railway会自动读取 `railway.json`
   - 创建PostgreSQL数据库
   - 创建Redis缓存服务

4. **配置环境变量**
   - 进入项目 → "Variables"
   - 添加环境变量（参考2.1节）
   - 保存并重新部署

5. **获取后端域名**
   - 部署完成后，获取服务域名
   - 格式: https://xxx.up.railway.app

### 步骤3: 部署前端到Vercel

1. **访问Vercel**
   - 打开 https://vercel.com
   - 使用GitHub登录

2. **导入项目**
   - 点击 "Add New..." → "Project"
   - 导入 "finscreener" 仓库
   - 配置选项:
     - Framework Preset: Vite
     - Root Directory: frontend
     - Build Command: npm run build
     - Output Directory: dist

3. **配置环境变量**
   - 进入项目 → "Settings" → "Environment Variables"
   - 添加环境变量（参考2.2节）
   - 确保 `VITE_API_URL` 指向Railway后端

4. **部署**
   - 点击 "Deploy"
   - 等待构建完成
   - 获取前端域名: https://xxx.vercel.app

### 步骤4: 验证部署

#### 后端验证
```bash
# 健康检查
curl https://你的后端域名.railway.app/health
# 预期: {"status":"healthy"}

# API测试
curl https://你的后端域名.railway.app/api/stocks
# 预期: 股票列表JSON
```

#### 前端验证
1. 访问 https://你的前端域名.vercel.app
2. 页面应正常加载
3. 测试筛选功能:
   - 选择筛选条件
   - 点击"筛选"按钮
   - 显示筛选结果

## 4. 故障排除

### 常见问题1: 后端启动失败
```bash
# 可能原因: 缺少环境变量
# 解决方案:
1. 检查Railway环境变量配置
2. 确保TUSHARE_TOKEN有效
3. 重启服务
```

### 常见问题2: 前端无法连接后端
```bash
# 可能原因: CORS配置或网络问题
# 解决方案:
1. 检查VITE_API_URL配置
2. 在Railway添加CORS_ORIGINS环境变量
3. 检查网络连通性
```

### 常见问题3: 数据库连接失败
```bash
# 可能原因: 数据库凭据错误
# 解决方案:
1. Railway会自动配置数据库
2. 检查DATABASE_URL环境变量
3. 重启数据库服务
```

## 5. 监控和维护

### 5.1 Railway监控
- 访问项目 → "Metrics"
- 查看: CPU、内存、请求数
- 日志: 实时应用日志

### 5.2 Vercel分析
- 访问项目 → "Analytics"
- 查看: 页面访问、性能指标
- 监控: 构建状态、错误率

### 5.3 数据更新
- Tushare数据自动同步
- 缓存自动过期
- 手动刷新: 重启后端服务

## 6. 升级和备份

### 6.1 升级步骤
1. 本地开发测试
2. 提交到GitHub
3. Railway和Vercel自动部署
4. 验证新版本

### 6.2 数据备份
- Railway提供自动数据库备份
- 访问项目 → "Database" → "Backups"
- 可以手动创建快照

## 7. 安全建议

### 7.1 生产环境安全
1. **API密钥保护**
   - 不要提交到代码仓库
   - 使用环境变量
   - 定期轮换

2. **访问控制**
   - 考虑添加认证
   - 限制API访问频率
   - 启用HTTPS

3. **数据安全**
   - 数据库加密连接
   - 敏感数据加密存储
   - 定期审计

### 7.2 监控告警
1. 设置服务健康检查
2. 配置错误告警
3. 监控API使用量

## 8. 成本估算

### 免费套餐
- **Railway**: $5/月免费额度
  - 后端服务
  - PostgreSQL数据库
  - Redis缓存
  
- **Vercel**: 完全免费
  - 前端托管
  - CDN和SSL
  - 基础分析

### 预计成本
- 个人使用: $0-10/月
- 团队使用: $20-50/月
- 企业级: $100+/月

## 9. 联系方式和支持

### 问题报告
- GitHub Issues: https://github.com/你的用户名/finscreener/issues
- 项目文档: 参考README.md和DEPLOYMENT.md

### 紧急支持
- Railway支持: https://railway.app/contact
- Vercel支持: https://vercel.com/support

---

**部署完成！现在可以开始使用FinScreener股票筛选工具了！**

访问你的前端网站，体验专业的股票筛选功能。如有问题，参考本文档进行故障排除。