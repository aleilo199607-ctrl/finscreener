import asyncio
from typing import Optional, Any, Union
import json
from datetime import timedelta

import redis.asyncio as redis
from redis.asyncio import Redis, ConnectionPool

from app.core.config import settings

class RedisClient:
    """Redis客户端封装"""
    
    def __init__(self):
        self.pool: Optional[ConnectionPool] = None
        self.client: Optional[Redis] = None
        self._initialized = False
    
    async def initialize(self):
        """初始化Redis连接"""
        if self._initialized:
            return
        
        try:
            self.pool = ConnectionPool.from_url(
                settings.REDIS_URL,
                max_connections=settings.REDIS_POOL_SIZE,
                socket_connect_timeout=settings.REDIS_POOL_TIMEOUT,
                socket_timeout=settings.REDIS_POOL_TIMEOUT,
                decode_responses=True,
            )
            
            self.client = Redis.from_pool(self.pool)
            
            # 测试连接
            await self.client.ping()
            self._initialized = True
            print("✅ Redis连接初始化成功")
            
        except Exception as e:
            print(f"❌ Redis连接初始化失败: {e}")
            self._initialized = False
    
    async def close(self):
        """关闭Redis连接"""
        if self.client:
            await self.client.close()
        if self.pool:
            await self.pool.disconnect()
        self._initialized = False
        print("🛑 Redis连接已关闭")
    
    async def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        if not self._initialized or not settings.CACHE_ENABLED:
            return None
        
        try:
            value = await self.client.get(key)
            if value:
                try:
                    return json.loads(value)
                except json.JSONDecodeError:
                    return value
        except Exception as e:
            print(f"❌ Redis获取失败 [{key}]: {e}")
            return None
    
    async def set(
        self, 
        key: str, 
        value: Any, 
        ttl: Optional[int] = None
    ) -> bool:
        """设置缓存值"""
        if not self._initialized or not settings.CACHE_ENABLED:
            return False
        
        try:
            if isinstance(value, (dict, list, tuple)):
                value = json.dumps(value, ensure_ascii=False)
            
            ttl = ttl or settings.CACHE_TTL
            await self.client.setex(key, ttl, value)
            return True
        except Exception as e:
            print(f"❌ Redis设置失败 [{key}]: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """删除缓存"""
        if not self._initialized:
            return False
        
        try:
            result = await self.client.delete(key)
            return result > 0
        except Exception as e:
            print(f"❌ Redis删除失败 [{key}]: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """检查键是否存在"""
        if not self._initialized:
            return False
        
        try:
            result = await self.client.exists(key)
            return result > 0
        except Exception as e:
            print(f"❌ Redis检查失败 [{key}]: {e}")
            return False
    
    async def incr(self, key: str, amount: int = 1) -> Optional[int]:
        """递增计数"""
        if not self._initialized:
            return None
        
        try:
            return await self.client.incrby(key, amount)
        except Exception as e:
            print(f"❌ Redis递增失败 [{key}]: {e}")
            return None
    
    async def decr(self, key: str, amount: int = 1) -> Optional[int]:
        """递减计数"""
        if not self._initialized:
            return None
        
        try:
            return await self.client.decrby(key, amount)
        except Exception as e:
            print(f"❌ Redis递减失败 [{key}]: {e}")
            return None
    
    async def hget(self, key: str, field: str) -> Optional[Any]:
        """获取哈希字段值"""
        if not self._initialized:
            return None
        
        try:
            value = await self.client.hget(key, field)
            if value:
                try:
                    return json.loads(value)
                except json.JSONDecodeError:
                    return value
        except Exception as e:
            print(f"❌ Redis哈希获取失败 [{key}:{field}]: {e}")
            return None
    
    async def hset(self, key: str, field: str, value: Any) -> bool:
        """设置哈希字段值"""
        if not self._initialized:
            return False
        
        try:
            if isinstance(value, (dict, list, tuple)):
                value = json.dumps(value, ensure_ascii=False)
            
            result = await self.client.hset(key, field, value)
            return result > 0
        except Exception as e:
            print(f"❌ Redis哈希设置失败 [{key}:{field}]: {e}")
            return False
    
    async def hdel(self, key: str, field: str) -> bool:
        """删除哈希字段"""
        if not self._initialized:
            return False
        
        try:
            result = await self.client.hdel(key, field)
            return result > 0
        except Exception as e:
            print(f"❌ Redis哈希删除失败 [{key}:{field}]: {e}")
            return False
    
    async def keys(self, pattern: str = "*") -> list:
        """获取匹配的键列表"""
        if not self._initialized:
            return []
        
        try:
            return await self.client.keys(pattern)
        except Exception as e:
            print(f"❌ Redis获取键列表失败: {e}")
            return []
    
    async def flush(self) -> bool:
        """清空当前数据库"""
        if not self._initialized:
            return False
        
        try:
            await self.client.flushdb()
            return True
        except Exception as e:
            print(f"❌ Redis清空失败: {e}")
            return False
    
    async def info(self) -> dict:
        """获取Redis服务器信息"""
        if not self._initialized:
            return {}
        
        try:
            info = await self.client.info()
            return {
                "version": info.get("redis_version"),
                "connected_clients": info.get("connected_clients"),
                "used_memory": info.get("used_memory_human"),
                "total_commands_processed": info.get("total_commands_processed"),
                "uptime_in_seconds": info.get("uptime_in_seconds"),
            }
        except Exception as e:
            print(f"❌ Redis信息获取失败: {e}")
            return {}

# 全局Redis客户端实例
redis_client = RedisClient()

# 缓存装饰器
def cache_key_builder(func_name: str, *args, **kwargs) -> str:
    """构建缓存键"""
    key_parts = [func_name]
    
    # 添加位置参数
    for arg in args:
        if isinstance(arg, (str, int, float, bool)):
            key_parts.append(str(arg))
    
    # 添加关键字参数
    for k, v in sorted(kwargs.items()):
        if isinstance(v, (str, int, float, bool)):
            key_parts.append(f"{k}:{v}")
    
    return ":".join(key_parts)

def cached(ttl: int = None):
    """缓存装饰器"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            if not settings.CACHE_ENABLED:
                return await func(*args, **kwargs)
            
            # 构建缓存键
            key = cache_key_builder(func.__name__, *args, **kwargs)
            
            # 尝试从缓存获取
            cached_value = await redis_client.get(key)
            if cached_value is not None:
                return cached_value
            
            # 执行函数
            result = await func(*args, **kwargs)
            
            # 缓存结果
            if result is not None:
                await redis_client.set(key, result, ttl)
            
            return result
        
        return wrapper
    
    return decorator