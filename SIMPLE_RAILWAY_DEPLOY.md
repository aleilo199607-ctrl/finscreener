# 最简单的Railway部署方法

## 问题背景
网页部署失败，CLI需要交互登录。我们用一个更简单的方法。

## 解决方案：使用Railway的"Deploy Button"

### 第一步：删除旧项目（如果还有）
1. 访问 https://railway.app
2. 登录后找到旧项目
3. 删除它

### 第二步：使用一键部署按钮
我为你创建了一个一键部署按钮。你只需要：

1. **点击这个链接**（复制到浏览器中打开）：
   ```
   https://railway.app/new/template?template=https%3A%2F%2Fgithub.com%2Faleilo199607-ctrl%2Ffinscreener&plugins=postgresql%2Credis&envs=TUSHARE_TOKEN%2CAI_PROVIDER%2CENVIRONMENT%2CCORS_ORIGINS%2CLOG_LEVEL%2CCACHE_TTL&AI_PROVIDER=mock&ENVIRONMENT=production&CORS_ORIGINS=https%3A%2F%2Ffinscreener.vercel.app%2Chttp%3A%2F%2Flocalhost%3A3000&LOG_LEVEL=INFO&CACHE_TTL=300
   ```

2. **或者点击这个按钮**：
   [![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template?template=https%3A%2F%2Fgithub.com%2Faleilo199607-ctrl%2Ffinscreener&plugins=postgresql%2Credis&envs=TUSHARE_TOKEN%2CAI_PROVIDER%2CENVIRONMENT%2CCORS_ORIGINS%2CLOG_LEVEL%2CCACHE_TTL&AI_PROVIDER=mock&ENVIRONMENT=production&CORS_ORIGINS=https%3A%2F%2Ffinscreener.vercel.app%2Chttp%3A%2F%2Flocalhost%3A3000&LOG_LEVEL=INFO&CACHE_TTL=300)

### 第三步：配置Tushare Token
点击链接后，Railway会打开部署页面：
1. 你会看到一个表单
2. 在表单中找到 `TUSHARE_TOKEN` 字段
3. 输入你的Token：`13d6c6df74675cbb76961df7cde5c08fc73ee57a61b80636fa745e96`
4. 其他字段已经预填好了
5. 点击 **"Deploy"**

### 第四步：等待部署完成
Railway会自动：
1. 创建新项目
2. 部署你的代码
3. 创建PostgreSQL数据库
4. 创建Redis缓存
5. 配置所有环境变量

### 第五步：获取后端URL
部署完成后：
1. 进入Railway项目页面
2. 点击 **"Settings"**
3. 找到 **"Production Domain"**
4. 复制这个URL

## 备选方案：使用Railway模板

如果上面的一键部署不行，我们还可以：

### 方法A：使用Python模板
1. 访问 https://railway.app/templates
2. 搜索 **"Python"**
3. 选择 **"Python Starter"**
4. 部署时选择你的GitHub仓库
5. 手动配置环境变量

### 方法B：手动创建
1. 访问 https://railway.app/new
2. 选择 **"Empty Project"**
3. 然后手动配置：
   - 设置根目录为 `backend`
   - 添加环境变量
   - 配置启动命令

## 环境变量配置

无论用哪种方法，都需要这些环境变量：

```
TUSHARE_TOKEN=13d6c6df74675cbb76961df7cde5c08fc73ee57a61b80636fa745e96
AI_PROVIDER=mock
ENVIRONMENT=production
CORS_ORIGINS=https://finscreener.vercel.app,http://localhost:3000
LOG_LEVEL=INFO
CACHE_TTL=300
```

## 验证部署

部署成功后，访问：
1. `https://你的域名.railway.app/health` - 应该返回 `{"status": "healthy"}`
2. `https://你的域名.railway.app/docs` - 应该显示API文档
3. `https://你的域名.railway.app/api/stocks` - 应该返回股票数据

## 如果还是失败

请告诉我：
1. 具体的错误信息
2. 你尝试了哪种方法
3. 错误截图

我会提供更具体的解决方案。