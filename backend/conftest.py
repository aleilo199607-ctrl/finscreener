"""
测试配置文件，用于设置测试环境和fixtures
"""
import pytest
from typing import AsyncGenerator, Generator
from unittest.mock import AsyncMock, MagicMock, patch

from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.core.database import Base, get_db
from app.main import app

# 测试数据库URL
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

# 创建测试数据库引擎
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    future=True,
)

# 测试会话工厂
TestingSessionLocal = sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

@pytest.fixture(scope="session")
def event_loop():
    """创建事件循环fixture"""
    import asyncio
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session", autouse=True)
async def setup_test_database():
    """设置测试数据库"""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """创建数据库会话fixture"""
    async with TestingSessionLocal() as session:
        try:
            yield session
        finally:
            await session.rollback()

@pytest.fixture
def test_client(db_session: AsyncSession):
    """创建测试客户端fixture"""
    
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    # 覆盖依赖
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as client:
        yield client
    
    # 清理覆盖
    app.dependency_overrides.clear()

@pytest.fixture
def mock_redis():
    """创建Redis mock fixture"""
    with patch("app.core.redis.redis_client") as mock:
        redis_mock = AsyncMock()
        mock.return_value = redis_mock
        yield redis_mock

@pytest.fixture
def mock_tushare():
    """创建Tushare mock fixture"""
    with patch("app.services.stock_service.tushare") as mock:
        tushare_mock = MagicMock()
        
        # 模拟股票基本信息
        tushare_mock.stock_basic.return_value = {
            "ts_code": ["000001.SZ", "000002.SZ"],
            "symbol": ["000001", "000002"],
            "name": ["平安银行", "万科A"],
            "area": ["深圳", "深圳"],
            "industry": ["银行", "房地产"],
            "market": ["主板", "主板"],
            "list_date": ["19910403", "19910129"],
        }
        
        # 模拟日行情数据
        tushare_mock.daily.return_value = {
            "ts_code": ["000001.SZ", "000001.SZ"],
            "trade_date": ["20240115", "20240116"],
            "open": [10.5, 10.6],
            "high": [10.8, 10.9],
            "low": [10.3, 10.4],
            "close": [10.6, 10.7],
            "pre_close": [10.4, 10.5],
            "change": [0.2, 0.1],
            "pct_chg": [1.92, 0.95],
            "vol": [1000000, 1200000],
            "amount": [10600000, 12840000],
        }
        
        # 模拟财务数据
        tushare_mock.income.return_value = {
            "ts_code": ["000001.SZ"],
            "ann_date": ["20231030"],
            "end_date": ["20230930"],
            "revenue": [10000000000],
            "operate_profit": [2000000000],
            "total_profit": [2100000000],
            "n_income": [1800000000],
            "basic_eps": [0.92],
        }
        
        mock.return_value = tushare_mock
        yield tushare_mock

@pytest.fixture
def mock_ai_service():
    """创建AI服务mock fixture"""
    with patch("app.services.ai_service.get_ai_provider") as mock:
        ai_mock = AsyncMock()
        ai_mock.generate_summary.return_value = "这是一只优秀的股票，具有良好的基本面和成长性。"
        mock.return_value = ai_mock
        yield ai_mock

@pytest.fixture
def sample_stock_data():
    """提供样本股票数据fixture"""
    return {
        "symbol": "000001",
        "name": "平安银行",
        "exchange": "SZ",
        "industry": "银行",
        "area": "深圳",
        "list_date": "1991-04-03",
        "market_cap": 300000000000,
        "pe_ratio": 8.5,
        "pb_ratio": 0.9,
        "dividend_yield": 3.2,
        "roe": 12.5,
    }

@pytest.fixture
def sample_kline_data():
    """提供样本K线数据fixture"""
    return [
        {
            "date": "2024-01-15",
            "open": 10.5,
            "high": 10.8,
            "low": 10.3,
            "close": 10.6,
            "volume": 1000000,
            "turnover": 10600000,
        },
        {
            "date": "2024-01-16",
            "open": 10.6,
            "high": 10.9,
            "low": 10.4,
            "close": 10.7,
            "volume": 1200000,
            "turnover": 12840000,
        },
    ]

@pytest.fixture
def sample_screening_conditions():
    """提供样本筛选条件fixture"""
    return [
        {
            "id": "pe_ratio",
            "name": "市盈率",
            "type": "range",
            "value": [0, 15],
        },
        {
            "id": "roe",
            "name": "净资产收益率",
            "type": "range", 
            "value": [10, 30],
        },
    ]

# 测试配置覆盖
@pytest.fixture(scope="session", autouse=True)
def override_settings():
    """覆盖应用设置用于测试"""
    original_settings = settings.copy()
    
    settings.DATABASE_URL = TEST_DATABASE_URL
    settings.REDIS_URL = "redis://localhost:6379/1"
    settings.TUSHARE_TOKEN = "test_token"
    settings.AI_PROVIDER = "mock"
    settings.ENVIRONMENT = "testing"
    
    yield
    
    # 恢复原始设置
    for key, value in original_settings.items():
        setattr(settings, key, value)