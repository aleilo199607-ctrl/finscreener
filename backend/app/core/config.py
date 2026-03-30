from pydantic_settings import BaseSettings
from typing import List, Optional
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class Settings(BaseSettings):
    """应用配置"""
    
    # 基础配置
    APP_NAME: str = "FinScreener"
    VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # 服务器配置
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # 数据库配置
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "postgresql+asyncpg://postgres:password@localhost:5432/finscreener"
    )
    
    # Redis配置
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    REDIS_POOL_SIZE: int = int(os.getenv("REDIS_POOL_SIZE", "10"))
    REDIS_POOL_TIMEOUT: int = int(os.getenv("REDIS_POOL_TIMEOUT", "30"))
    
    # CORS配置
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
    ]
    
    # 数据源配置
    TUSHARE_TOKEN: str = os.getenv("TUSHARE_TOKEN", "")
    AKSHARE_ENABLED: bool = os.getenv("AKSHARE_ENABLED", "True").lower() == "true"
    
    # AI配置
    AI_PROVIDER: str = os.getenv("AI_PROVIDER", "deepseek")  # deepseek, openai, glm, baidu
    DEEPSEEK_API_KEY: Optional[str] = os.getenv("DEEPSEEK_API_KEY")
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    GLM_API_KEY: Optional[str] = os.getenv("GLM_API_KEY")
    BAIDU_API_KEY: Optional[str] = os.getenv("BAIDU_API_KEY")
    
    # 缓存配置
    CACHE_ENABLED: bool = os.getenv("CACHE_ENABLED", "True").lower() == "true"
    CACHE_TTL: int = int(os.getenv("CACHE_TTL", "300"))  # 5分钟
    CACHE_MAX_SIZE: int = int(os.getenv("CACHE_MAX_SIZE", "1000"))
    
    # 限流配置
    RATE_LIMIT_ENABLED: bool = os.getenv("RATE_LIMIT_ENABLED", "True").lower() == "true"
    RATE_LIMIT_REQUESTS: int = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
    RATE_LIMIT_PERIOD: int = int(os.getenv("RATE_LIMIT_PERIOD", "60"))  # 秒
    
    # 安全配置
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # 日志配置
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = os.getenv("LOG_FORMAT", "json")
    
    # 静态文件配置
    STATIC_FILES_ENABLED: bool = os.getenv("STATIC_FILES_ENABLED", "False").lower() == "true"
    STATIC_FILES_DIR: str = os.getenv("STATIC_FILES_DIR", "static")
    
    # 数据同步配置
    DATA_SYNC_ENABLED: bool = os.getenv("DATA_SYNC_ENABLED", "True").lower() == "true"
    DATA_SYNC_INTERVAL: int = int(os.getenv("DATA_SYNC_INTERVAL", "300"))  # 5分钟
    DATA_SYNC_BATCH_SIZE: int = int(os.getenv("DATA_SYNC_BATCH_SIZE", "100"))
    
    # 监控配置
    SENTRY_DSN: Optional[str] = os.getenv("SENTRY_DSN")
    PROMETHEUS_ENABLED: bool = os.getenv("PROMETHEUS_ENABLED", "False").lower() == "true"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# 全局配置实例
settings = Settings()

# 开发环境特殊配置
if settings.ENVIRONMENT == "development":
    settings.CORS_ORIGINS.append("*")
    settings.DEBUG = True
    settings.LOG_LEVEL = "DEBUG"

# 生产环境特殊配置
if settings.ENVIRONMENT == "production":
    settings.DEBUG = False
    settings.CORS_ORIGINS = [
        "https://finscreener.com",
        "https://www.finscreener.com",
    ]
    settings.CACHE_ENABLED = True
    settings.RATE_LIMIT_ENABLED = True

# 验证必要配置
def validate_settings():
    """验证必要配置"""
    required_configs = [
        ("TUSHARE_TOKEN", settings.TUSHARE_TOKEN, "Tushare API Token"),
    ]
    
    missing_configs = []
    for key, value, description in required_configs:
        if not value:
            missing_configs.append(f"{key} ({description})")
    
    if missing_configs:
        print("⚠️ 警告：以下必要配置缺失：")
        for config in missing_configs:
            print(f"   - {config}")
        print("部分功能可能无法正常工作。")
    
    # 验证AI配置
    if settings.AI_PROVIDER == "deepseek" and not settings.DEEPSEEK_API_KEY:
        print("⚠️ 警告：DeepSeek API密钥未配置，AI摘要功能将不可用。")
    elif settings.AI_PROVIDER == "openai" and not settings.OPENAI_API_KEY:
        print("⚠️ 警告：OpenAI API密钥未配置，AI摘要功能将不可用。")
    elif settings.AI_PROVIDER == "glm" and not settings.GLM_API_KEY:
        print("⚠️ 警告：GLM API密钥未配置，AI摘要功能将不可用。")
    
    return True

# 初始化时验证配置
validate_settings()