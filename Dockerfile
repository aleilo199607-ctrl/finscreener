# FinScreener 后端 Dockerfile
FROM python:3.10-slim as backend

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY backend/requirements.txt .

# 安装Python依赖
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# 复制后端代码
COPY backend/ .

# 创建非root用户
RUN useradd -m -u 1000 finuser && chown -R finuser:finuser /app
USER finuser

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["python", "main.py"]

# =============================================

# FinScreener 前端 Dockerfile (多阶段构建)
FROM node:18-alpine as frontend-builder

# 设置工作目录
WORKDIR /app

# 复制前端依赖文件
COPY frontend/package*.json ./

# 安装依赖
RUN npm ci --only=production

# 复制前端源代码
COPY frontend/ .

# 构建前端
RUN npm run build

# =============================================

# 生产环境Nginx镜像
FROM nginx:alpine as production

# 复制前端构建文件到Nginx
COPY --from=frontend-builder /app/dist /usr/share/nginx/html

# 复制Nginx配置
COPY nginx.conf /etc/nginx/nginx.conf

# 暴露端口
EXPOSE 80

# 启动Nginx
CMD ["nginx", "-g", "daemon off;"]