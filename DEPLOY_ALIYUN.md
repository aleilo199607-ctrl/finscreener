# FinScreener 阿里云函数计算部署指南

## 前置准备

### 1. 安装 Serverless Devs 工具

```bash
npm install -g @serverless-devs/s
```

### 2. 配置阿里云密钥

访问 https://ram.console.aliyun.com/manage/ak 创建 AccessKey，然后：

```bash
s config add
```

按提示输入：
- AccountID: 你的阿里云账号ID
- AccessKeyID: 你的AccessKey ID
- AccessKeySecret: 你的AccessKey Secret

## 部署步骤

### 方式一：命令行部署（推荐）

```bash
cd FinScreener
s deploy
```

部署成功后会输出类似这样的地址：
```
https://xxxxx.cn-hangzhou.fc.aliyuncs.com/
```

### 方式二：阿里云控制台部署

1. 登录 https://fc.console.aliyun.com
2. 创建服务：`finscreener-service`
3. 创建函数：
   - 运行时：自定义运行时（Custom Runtime）
   - 启动命令：`bash bootstrap`
   - 监听端口：9000
   - 请求处理程序：`app_fc.handler`
4. 上传代码：`backend/` 目录下的所有文件
5. 配置HTTP触发器：匿名访问，支持所有方法
6. 配置环境变量（可选）：
   ```
   CORS_ORIGINS=https://finscreener-wcxd.vercel.app,https://finscreener.vercel.app
   ```

## 部署后配置

### 更新前端API地址

部署成功后，修改 `frontend/.env.production`：

```bash
VITE_API_BASE_URL=https://你的函数计算地址
```

然后重新部署前端到 Vercel：
```bash
cd frontend
npm run build
vercel --prod
```

或在 Vercel 控制台修改环境变量 `VITE_API_BASE_URL`。

## 文件说明

```
backend/
├── app_fc.py              # FastAPI应用（阿里云FC版）
├── bootstrap              # FC启动脚本
├── requirements_fc.txt    # Python依赖
├── .fcignore              # 部署忽略文件
└── ...

s.yaml                     # Serverless Devs部署配置
```

## 免费额度

- 调用次数：100万次/月
- 执行时间：40万GB-秒/月
- 公网流量：按实际使用（约¥0.8/GB）
- 预估月费用：< ¥1（正常使用）
