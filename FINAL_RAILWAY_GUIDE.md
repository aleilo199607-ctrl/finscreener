# Railway最终部署指南

## 问题总结
之前遇到的两个问题：
1. 一键部署表单缺少TUSHARE_TOKEN字段
2. Railway可能没有正确识别项目结构

## 解决方案
使用标准"Deploy from GitHub"方法，然后手动添加环境变量。

## 详细步骤

### 第一步：确保代码已更新
我已经为项目添加了 `railway.toml` 配置文件，这个文件会帮助Railway正确识别项目。

### 第二步：访问Railway
1. **打开**：https://railway.app
2. **登录**：使用GitHub账号登录
3. **如果还有旧项目**，先删除它

### 第三步：创建新项目
1. 点击 **"+ New Project"**（绿色按钮）
2. 选择 **"Deploy from GitHub repo"**（第一个选项）
3. 选择你的仓库：**"aleilo199607-ctrl/finscreener"**
4. 点击 **"Deploy"**

### 第四步：等待部署完成
部署过程需要2-3分钟，你会看到：
- ✓ Cloning repository
- ✓ Detecting project type
- ✓ Building...
- ✓ Starting application...
- ✓ Deployment successful!

### 第五步：添加环境变量（关键步骤！）
部署完成后：
1. 进入项目页面
2. 点击顶部菜单的 **"Variables"** 标签
3. 点击 **"+ Add Variable"** 按钮
4. **逐个添加**以下6个变量：

#### 变量1：TUSHARE_TOKEN
- **Key**: `TUSHARE_TOKEN`
- **Value**: `13d6c6df74675cbb76961df7cde5c08fc73ee57a61b80636fa745e96`
- **说明**: 这是必需的核心配置

#### 变量2：AI_PROVIDER
- **Key**: `AI_PROVIDER`
- **Value**: `mock`
- **说明**: 使用模拟AI，先确保核心功能

#### 变量3：ENVIRONMENT
- **Key**: `ENVIRONMENT`
- **Value**: `production`
- **说明**: 生产环境

#### 变量4：CORS_ORIGINS
- **Key**: `CORS_ORIGINS`
- **Value**: `https://finscreener.vercel.app,http://localhost:3000`
- **说明**: 允许的前端域名

#### 变量5：LOG_LEVEL
- **Key**: `LOG_LEVEL`
- **Value**: `INFO`
- **说明**: 日志级别

#### 变量6：CACHE_TTL
- **Key**: `CACHE_TTL`
- **Value**: `300`
- **说明**: 缓存时间（秒）

### 第六步：验证部署
添加完所有变量后：
1. Railway会自动重启应用
2. 等待1-2分钟
3. 访问：`https://你的域名.railway.app/health`
   - 应该显示：`{"status": "healthy"}`
4. 访问：`https://你的域名.railway.app/docs`
   - 应该显示API文档

### 第七步：获取后端URL
1. 点击 **"Settings"** 标签
2. 找到 **"Production Domain"**
3. 复制这个URL
4. **保存这个URL**，部署Vercel时需要

## 故障排除

### 问题1：部署失败
**可能原因**：
- 项目结构识别错误
- 依赖安装失败

**解决**：
- 检查Railway日志
- 确保 `railway.toml` 文件存在

### 问题2：应用启动失败
**可能原因**：
- 环境变量缺失
- Tushare Token无效

**解决**：
- 检查所有6个环境变量是否都已添加
- 验证TUSHARE_TOKEN是否正确

### 问题3：无法访问API
**可能原因**：
- 应用还在启动中
- 端口配置错误

**解决**：
- 等待几分钟
- 检查应用日志

## 成功标志

✅ 部署状态：Deployment successful  
✅ 应用状态：Running  
✅ 健康检查：`{"status": "healthy"}`  
✅ API文档：可以正常访问  
✅ 数据库：Railway自动创建  
✅ Redis：Railway自动创建  

## 下一步
Railway部署成功后，就可以开始部署前端到Vercel了！

**重要**：请把你的Railway后端URL告诉我，这样我就可以帮你配置Vercel了。