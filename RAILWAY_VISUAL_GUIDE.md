# Railway 可视化部署指南

## 🚀 第一步：登录Railway

### 1.1 访问Railway网站
**网址**: https://railway.app
**操作**: 在浏览器中打开这个地址

### 1.2 点击登录按钮
你会看到这样的界面：
```
┌─────────────────────────────────────┐
│              RAILWAY                │
│                                     │
│   🚂 Railway - Deploy anything.     │
│                                     │
│   ┌─────────────────────────────┐   │
│   │    Login with GitHub        │   │
│   └─────────────────────────────┘   │
│                                     │
│   ┌─────────────────────────────┐   │
│   │    Login with GitLab        │   │
│   └─────────────────────────────┘   │
│                                     │
└─────────────────────────────────────┘
```

**点击**: **"Login with GitHub"** 按钮

### 1.3 GitHub授权
Railway会要求访问你的GitHub账户：
1. 点击 **"Authorize railway"** 按钮
2. 可能需要输入GitHub密码确认

## 🚀 第二步：创建新项目

### 2.1 进入Railway控制台
登录成功后，你会看到Railway控制台：
```
┌─────────────────────────────────────┐
│   Dashboard                         │
│                                     │
│   ┌─────────────────────────────┐   │
│   │    + New Project            │   │
│   └─────────────────────────────┘   │
│                                     │
└─────────────────────────────────────┘
```

**点击**: **"+ New Project"** 按钮

### 2.2 选择部署方式
你会看到几个选项：
```
┌─────────────────────────────────────┐
│   Create a new project              │
│                                     │
│   ○ Deploy from GitHub repo         │
│   ○ Start with a Template          │
│   ○ Deploy from Docker Hub         │
│   ○ Empty project                  │
│                                     │
└─────────────────────────────────────┘
```

**选择**: **"Deploy from GitHub repo"**（第一个选项）

### 2.3 选择GitHub仓库
Railway会显示你的GitHub仓库列表：
```
┌─────────────────────────────────────┐
│   Select a repository               │
│                                     │
│   🔍 Search repositories...         │
│                                     │
│   □ aleilo199607-ctrl/finscreener   │
│   □ ...（其他仓库）                  │
│                                     │
│   ┌─────────────────────────────┐   │
│   │        Deploy               │   │
│   └─────────────────────────────┘   │
│                                     │
└─────────────────────────────────────┘
```

**勾选**: **"aleilo199607-ctrl/finscreener"**
**点击**: **"Deploy"** 按钮

## 🚀 第三步：Railway自动部署

### 3.1 查看部署进度
部署开始后，你会看到：
```
┌─────────────────────────────────────┐
│   Project: finscreener              │
│                                     │
│   ┌─────────────────────────────┐   │
│   │   Deployment #1             │   │
│   │   🟡 Building...            │   │
│   │   └─────────────┘           │   │
│   └─────────────────────────────┘   │
│                                     │
│   [部署日志会实时显示在这里]          │
│                                     │
└─────────────────────────────────────┘
```

### 3.2 部署日志示例
正常的部署日志看起来像这样：
```
✓ Cloned repository
✓ Detected Python project
✓ Installing dependencies...
✓ Installing Python 3.13
✓ Installing pip packages...
✓ Building project...
✓ Starting application...
✓ Deployment successful!
```

**等待**: 直到看到 **"Deployment successful!"**

## 🚀 第四步：配置环境变量

### 4.1 进入变量配置页面
部署完成后，在项目页面：
1. 点击顶部菜单的 **"Variables"** 标签
2. 或者找到 **"Environment Variables"** 部分

界面看起来像：
```
┌─────────────────────────────────────┐
│   Variables                         │
│                                     │
│   ┌─────────────────────────────┐   │
│   │   Key            Value      │   │
│   ├─────────────────────────────┤   │
│   │   [空]           [空]       │   │
│   └─────────────────────────────┘   │
│                                     │
│   ┌─────────────────────────────┐   │
│   │   + Add Variable            │   │
│   └─────────────────────────────┘   │
│                                     │
└─────────────────────────────────────┘
```

### 4.2 添加环境变量
**一次性复制以下所有内容**（我为你准备的）：

```
TUSHARE_TOKEN=13d6c6df74675cbb76961df7cde5c08fc73ee57a61b80636fa745e96
AI_PROVIDER=mock
ENVIRONMENT=production
CORS_ORIGINS=https://finscreener.vercel.app,http://localhost:3000
LOG_LEVEL=INFO
CACHE_TTL=300
```

### 4.3 在Railway中粘贴
1. 点击 **"+ Add Variable"** 按钮
2. 选择 **"Bulk Add"** 选项（如果可用）
3. 粘贴上面的所有内容
4. 点击 **"Save"** 或 **"Add"**

**注意**：如果你的Railway没有"Bulk Add"，需要逐个添加：
1. **第一个变量**: Key=`TUSHARE_TOKEN`, Value=`13d6c6df74675cbb76961df7cde5c08fc73ee57a61b80636fa745e96`
2. **第二个变量**: Key=`AI_PROVIDER`, Value=`mock`
3. **第三个变量**: Key=`ENVIRONMENT`, Value=`production`
4. **第四个变量**: Key=`CORS_ORIGINS`, Value=`https://finscreener.vercel.app,http://localhost:3000`
5. **第五个变量**: Key=`LOG_LEVEL`, Value=`INFO`
6. **第六个变量**: Key=`CACHE_TTL`, Value=`300`

## 🚀 第五步：获取后端URL

### 5.1 找到你的域名
配置完成后，回到项目概览页：
1. 点击 **"Settings"** 标签
2. 找到 **"General"** 部分
3. 查找 **"Production Domain"**

看起来像：
```
┌─────────────────────────────────────┐
│   Settings                          │
│                                     │
│   General                           │
│   ┌─────────────────────────────┐   │
│   │   Project Name: finscreener │   │
│   │                             │   │
│   │   Production Domain:        │   │
│   │   https://finscreener-xxx   │   │
│   │   .up.railway.app           │   │
│   └─────────────────────────────┘   │
│                                     │
└─────────────────────────────────────┘
```

### 5.2 复制后端URL
**复制**这个URL（看起来像）：
`https://finscreener-xxxxxxxx.up.railway.app`

**保存好这个URL**，下一步部署Vercel时需要！

## 🚀 第六步：验证部署

### 6.1 运行验证脚本
回到你的电脑，运行我创建的验证脚本：
```bash
cd "C:\Users\42337\WorkBuddy\20260330172538\FinScreener"
python verify_deployment.py
```

### 6.2 或在浏览器中测试
1. **健康检查**: 访问 `https://你的域名.railway.app/health`
   - 应该显示: `{"status": "healthy"}`
2. **API测试**: 访问 `https://你的域名.railway.app/api/stocks`
   - 应该返回股票数据
3. **API文档**: 访问 `https://你的域名.railway.app/docs`
   - 可以查看所有API接口

## 🚨 故障排除

### 问题1：部署失败
**症状**: 部署日志显示错误
**解决**：
1. 检查Railway日志中的具体错误信息
2. 最常见的错误：Tushare Token无效
3. 重新部署：点击 **"Redeploy"** 按钮

### 问题2：应用启动失败
**症状**: 部署成功但应用无法启动
**解决**：
1. 检查环境变量是否正确配置
2. 确认TUSHARE_TOKEN变量已添加
3. 查看应用日志：点击 **"Logs"** 标签

### 问题3：无法访问API
**症状**: 健康检查返回错误
**解决**：
1. 等待几分钟让应用完全启动
2. 检查Railway服务状态
3. 尝试重启服务

## ✅ 部署成功标志

完成所有步骤后，你应该看到：

### 在Railway控制台
- ✅ 部署状态: **Deployment successful**
- ✅ 服务状态: **Running**
- ✅ 日志显示应用已启动

### 在浏览器测试
- ✅ `https://你的域名.railway.app/health` → `{"status": "healthy"}`
- ✅ `https://你的域名.railway.app/api/stocks` → 返回股票数据
- ✅ `https://你的域名.railway.app/docs` → 显示API文档

## 🎯 下一步：部署Vercel前端

Railway后端部署成功后，我们就可以开始第三步：**部署前端到Vercel**。

**重要**：请把你的Railway后端URL告诉我，这样我就可以帮你配置Vercel了！

---
**提示**：如果任何步骤不清楚，可以随时截图给我看，我会详细指导你！