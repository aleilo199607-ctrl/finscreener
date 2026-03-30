# Railway 部署详细步骤指南

## 当前状态检查

### ✅ 已完成
1. **Tushare Token已获取**: `13d6c6df74675cbb76961df7cde5c08fc73ee57a61b80636fa745e96`
2. **本地Git仓库已初始化**: 代码已提交
3. **所有配置文件已准备**: railway.json, railway_env_variables.txt等

### 🔄 需要完成
1. **创建GitHub仓库** (如果还没做)
2. **连接本地仓库到GitHub**
3. **部署到Railway**

## 第一步：GitHub仓库准备（如果还没做）

### A. 创建GitHub仓库
1. 打开浏览器，访问：https://github.com/new
2. 填写仓库信息：
   - **Repository name**: `finscreener`
   - **Description**: `智能股票筛选工具 - A股股票多维度条件筛选和AI分析`
   - **选择**: **Public**（必须公开，Vercel部署需要）
   - **不要**勾选任何初始化选项（README、.gitignore、许可证）
3. 点击 **"Create repository"**

### B. 连接本地仓库到GitHub
创建后，运行以下命令（在FinScreener目录中）：

```bash
# 替换YOUR_USERNAME为你的GitHub用户名
git remote add origin https://github.com/YOUR_USERNAME/finscreener.git

# 重命名分支并推送代码
git branch -M main
git push -u origin main
```

## 第二步：部署到Railway

### A. 登录Railway
1. 访问：https://railway.app
2. 点击 **"Login with GitHub"**
3. 授权Railway访问你的GitHub账户

### B. 创建新项目
1. 点击 **"New Project"**
2. 选择 **"Deploy from GitHub repo"**
3. 从列表中选择你的 **"finscreener"** 仓库
4. Railway会自动检测`railway.json`配置并开始部署

### C. 配置环境变量
部署启动后，进入项目页面：
1. 点击 **"Variables"** 标签页
2. 复制以下内容粘贴到Railway（一次全部复制）：

```
TUSHARE_TOKEN=13d6c6df74675cbb76961df7cde5c08fc73ee57a61b80636fa745e96
AI_PROVIDER=mock
ENVIRONMENT=production
CORS_ORIGINS=https://finscreener.vercel.app,http://localhost:3000
LOG_LEVEL=INFO
CACHE_TTL=300
```

**注意**：上面已经包含了你的Tushare Token。

### D. 监控部署进度
1. 回到 **"Deployments"** 标签页
2. 查看部署日志
3. 等待部署完成（通常需要2-3分钟）

## 第三步：获取Railway后端URL

部署完成后：
1. 在Railway项目页面，点击 **"Settings"**
2. 找到 **"General"** 部分
3. 复制 **"Production Domain"**（看起来像：`https://finscreener-api.up.railway.app`）

**保存这个URL**：这是你的后端API地址，下一步部署前端时需要用到。

## 第四步：验证后端部署

部署完成后，运行验证脚本：
```bash
python verify_deployment.py
```

或者在浏览器中访问：
1. **健康检查**: `https://你的后端域名.railway.app/health`
   - 应该显示: `{"status": "healthy"}`
2. **API测试**: `https://你的后端域名.railway.app/api/stocks`
   - 应该返回股票列表数据
3. **API文档**: `https://你的后端域名.railway.app/docs`
   - 可以查看所有API接口

## 故障排除

### 1. 部署失败
**可能原因**：
- Tushare Token无效
- 网络连接问题
- 依赖安装失败

**解决方案**：
- 检查Railway部署日志
- 确认Tushare Token正确
- 尝试重新部署

### 2. 健康检查失败
**可能原因**：
- 数据库连接问题
- Tushare API访问失败
- 环境变量配置错误

**解决方案**：
- 检查Railway日志
- 验证环境变量
- 检查Tushare Token有效性

### 3. API返回错误
**可能原因**：
- CORS配置问题
- 路由配置错误
- 服务未完全启动

**解决方案**：
- 等待服务完全启动
- 检查CORS_ORIGINS配置
- 查看API文档确认接口路径

## 部署成功标志

✅ **所有检查通过**：
1. 健康检查: `curl https://你的域名.railway.app/health` 返回 `{"status": "healthy"}`
2. API访问: `curl https://你的域名.railway.app/api/stocks` 返回股票数据
3. 文档访问: `https://你的域名.railway.app/docs` 可以正常访问

## 接下来

后端部署成功后，就可以开始第三步：**部署前端到Vercel**。

**记得保存好Railway后端URL**，部署Vercel时需要配置环境变量 `VITE_API_URL`。