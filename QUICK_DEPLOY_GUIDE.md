# FinScreener 快速部署指南

## 🚀 10分钟完成部署！

本指南帮助你快速将FinScreener部署到Railway（后端）和Vercel（前端）。

## 第一步：准备工作

### 1.1 获取Tushare Token
1. 访问 https://tushare.pro
2. 注册账号
3. 在个人中心获取Token
4. 保存Token：`tushare_token_xxxxxxxxxxxxxx`

### 1.2 注册账户（已有则跳过）
- **Railway**: https://railway.app (后端部署)
- **Vercel**: https://vercel.com (前端部署)
- **GitHub**: https://github.com (代码托管)

## 第二步：准备代码仓库

### 2.1 本地准备
```bash
# 进入项目目录
cd FinScreener

# 初始化Git
git init
git add .
git commit -m "初始提交: FinScreener v1.0.0"
```

### 2.2 创建GitHub仓库
1. 访问 https://github.com/new
2. 填写信息：
   - Repository name: `finscreener`
   - Description: `智能股票筛选工具`
   - 选择: **Public** (Vercel部署需要)
   - 不勾选任何模板
3. 点击 "Create repository"

### 2.3 推送代码
```bash
# 连接远程仓库
git remote add origin https://github.com/YOUR_USERNAME/finscreener.git

# 推送代码
git branch -M main
git push -u origin main
```

## 第三步：部署后端到Railway (5分钟)

### 3.1 访问Railway
1. 打开 https://railway.app
2. 点击 "Login with GitHub"

### 3.2 创建项目
1. 点击 "New Project"
2. 选择 "Deploy from GitHub repo"
3. 授权访问你的GitHub账户
4. 选择 "finscreener" 仓库

### 3.3 自动配置
Railway会自动：
- ✅ 检测 `railway.json` 配置
- ✅ 创建PostgreSQL数据库
- ✅ 创建Redis缓存服务
- ✅ 部署Python后端

### 3.4 配置环境变量
1. 在项目页面点击 "Variables"
2. 添加以下环境变量：
   ```
   TUSHARE_TOKEN=你的Tushare Token
   AI_PROVIDER=mock
   ```
3. 点击 "Save" 保存

### 3.5 获取后端URL
1. 部署完成后，点击 "Settings" → "Domains"
2. 复制你的后端域名：
   `https://finscreener-api.up.railway.app`

## 第四步：部署前端到Vercel (3分钟)

### 4.1 访问Vercel
1. 打开 https://vercel.com
2. 点击 "Login with GitHub"

### 4.2 导入项目
1. 点击 "Add New..." → "Project"
2. 选择 "finscreener" 仓库
3. 配置选项：
   - Framework Preset: **Vite**
   - Root Directory: **frontend**
   - 其他保持默认

### 4.3 配置环境变量
1. 在部署页面，点击 "Environment Variables"
2. 添加：
   ```
   VITE_API_URL=你的Railway后端URL
   ```
3. 点击 "Save"

### 4.4 开始部署
1. 点击 "Deploy"
2. 等待构建完成（约1分钟）
3. 获取前端域名：
   `https://finscreener.vercel.app`

## 第五步：验证部署 (2分钟)

### 5.1 测试后端
```bash
# 健康检查
curl https://finscreener-api.up.railway.app/health
# 预期：{"status": "healthy"}

# API测试
curl https://finscreener-api.up.railway.app/api/stocks
# 预期：股票列表JSON
```

### 5.2 访问网站
1. 打开浏览器
2. 访问：`https://finscreener.vercel.app`
3. 应该看到FinScreener首页

### 5.3 测试功能
1. 在筛选面板选择条件
2. 点击"筛选"按钮
3. 查看筛选结果
4. 点击股票查看详情和图表

## 第六步：高级配置（可选）

### 6.1 配置AI分析
在Railway添加：
```
AI_PROVIDER=deepseek
DEEPSEEK_API_KEY=你的DeepSeek密钥
```

### 6.2 配置自定义域名
**Railway**:
1. Settings → Domains → Add Domain
2. 输入：`api.yourdomain.com`

**Vercel**:
1. Settings → Domains → Add Domain
2. 输入：`app.yourdomain.com`

### 6.3 配置CORS
在Railway添加：
```
CORS_ORIGINS=https://finscreener.vercel.app,https://app.yourdomain.com
```

## 第七步：监控和维护

### 7.1 Railway监控
- 访问项目 → "Metrics"
- 查看CPU、内存使用
- 查看请求日志

### 7.2 Vercel分析
- 访问项目 → "Analytics"
- 查看访问量
- 查看性能指标

### 7.3 数据更新
- Tushare数据自动同步
- 手动刷新：重启Railway服务

## 故障排除

### 问题1：后端启动失败
**解决方案**：
1. 检查Railway日志
2. 确认TUSHARE_TOKEN正确
3. 重启服务

### 问题2：前端无法连接后端
**解决方案**：
1. 确认VITE_API_URL正确
2. 检查网络连通性
3. 验证CORS配置

### 问题3：页面显示空白
**解决方案**：
1. 检查浏览器控制台错误
2. 确认JavaScript加载正常
3. 清除浏览器缓存

## 成本说明

### 免费套餐
- **Railway**: $5/月免费额度（足够使用）
- **Vercel**: 完全免费

### 预估使用量
- 个人使用：0成本
- 团队使用（10人）：$10-20/月
- 企业使用：$50+/月

## 技术支持

### 文档
- 完整文档：README.md
- 部署文档：DEPLOYMENT.md
- 快速指南：本文件

### 问题反馈
1. GitHub Issues: 提交问题
2. Railway支持: 在线客服
3. Vercel支持: 社区论坛

### 紧急联系方式
- 项目维护者：Leo先生
- 技术支持：皮卡丘 (AI助手)

## 恭喜！ 🎉

你已经成功部署了FinScreener股票筛选工具！

**访问地址**：
- 前端: https://finscreener.vercel.app
- 后端API: https://finscreener-api.up.railway.app
- API文档: https://finscreener-api.up.railway.app/docs

**功能特性**：
- ✅ 多维度股票筛选
- ✅ 专业K线图表
- ✅ AI智能分析
- ✅ 实时数据更新
- ✅ 响应式设计

开始使用你的智能股票筛选工具吧！