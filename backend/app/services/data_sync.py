import asyncio
import threading
import time
from datetime import datetime, timedelta
from typing import List, Optional
import logging
import schedule

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.services.stock_service import stock_service
from app.models.stock import Stock, MarketIndicator
from app.core.config import settings

# 配置日志
logger = logging.getLogger(__name__)

class DataSyncService:
    """数据同步服务"""
    
    def __init__(self):
        self._running = False
        self._thread = None
        self.sync_interval = settings.DATA_SYNC_INTERVAL  # 秒
        
    def start(self):
        """启动数据同步服务"""
        if self._running:
            logger.warning("数据同步服务已在运行")
            return
        
        if not settings.DATA_SYNC_ENABLED:
            logger.info("数据同步服务已禁用")
            return
        
        self._running = True
        self._thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self._thread.start()
        logger.info("✅ 数据同步服务已启动")
    
    def stop(self):
        """停止数据同步服务"""
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)
        logger.info("🛑 数据同步服务已停止")
    
    def _run_scheduler(self):
        """运行调度器"""
        logger.info(f"数据同步调度器启动，同步间隔: {self.sync_interval}秒")
        
        # 设置定时任务
        schedule.every(self.sync_interval).seconds.do(self._sync_all_data)
        
        # 立即执行一次
        self._sync_all_data()
        
        # 主循环
        while self._running:
            schedule.run_pending()
            time.sleep(1)
    
    def _sync_all_data(self):
        """同步所有数据"""
        try:
            logger.info("🔄 开始同步数据...")
            
            # 创建新的事件循环
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # 同步股票数据
            loop.run_until_complete(self._sync_stock_data())
            
            # 同步市场数据
            loop.run_until_complete(self._sync_market_data())
            
            loop.close()
            
            logger.info("✅ 数据同步完成")
            
        except Exception as e:
            logger.error(f"❌ 数据同步失败: {e}")
    
    async def _sync_stock_data(self):
        """同步股票数据"""
        try:
            async with AsyncSessionLocal() as session:
                # 获取需要同步的股票列表
                query = select(Stock.ts_code).limit(settings.DATA_SYNC_BATCH_SIZE)
                result = await session.execute(query)
                ts_codes = [row[0] for row in result]
                
                if not ts_codes:
                    logger.warning("没有需要同步的股票")
                    return
                
                logger.info(f"开始同步 {len(ts_codes)} 只股票的数据")
                
                # 同步数据
                await stock_service.sync_stock_data(session, ts_codes)
                
                logger.info(f"✅ 股票数据同步完成，共 {len(ts_codes)} 只股票")
                
        except Exception as e:
            logger.error(f"❌ 股票数据同步失败: {e}")
    
    async def _sync_market_data(self):
        """同步市场数据"""
        try:
            async with AsyncSessionLocal() as session:
                # 这里应该调用Tushare的API获取市场数据
                # 暂时创建模拟数据
                today = datetime.now().strftime("%Y%m%d")
                
                # 检查今天的数据是否已存在
                from sqlalchemy import select
                query = select(MarketIndicator).where(MarketIndicator.trade_date == today)
                result = await session.execute(query)
                existing = result.scalar_one_or_none()
                
                if existing:
                    logger.info(f"市场数据已存在: {today}")
                    return
                
                # 创建模拟的市场数据
                market_data = MarketIndicator(
                    trade_date=today,
                    sh_index=3000 + (datetime.now().day % 100),  # 模拟上证指数
                    sz_index=10000 + (datetime.now().day % 200),  # 模拟深证成指
                    cyb_index=2000 + (datetime.now().day % 50),  # 模拟创业板指
                    up_count=1500,  # 模拟上涨家数
                    down_count=800,  # 模拟下跌家数
                    unchanged_count=200,  # 模拟平盘家数
                    total_volume=5000000,  # 模拟总成交量
                    total_amount=800000000,  # 模拟总成交额
                    sh_money_in=1000000,  # 模拟沪市资金流入
                    sz_money_in=800000,  # 模拟深市资金流入
                    total_money_in=1800000  # 模拟总资金流入
                )
                
                session.add(market_data)
                await session.commit()
                
                logger.info(f"✅ 市场数据同步完成: {today}")
                
        except Exception as e:
            logger.error(f"❌ 市场数据同步失败: {e}")
    
    async def sync_specific_stocks(self, ts_codes: List[str]):
        """同步指定股票的数据"""
        try:
            async with AsyncSessionLocal() as session:
                await stock_service.sync_stock_data(session, ts_codes)
                logger.info(f"✅ 指定股票数据同步完成: {ts_codes}")
        except Exception as e:
            logger.error(f"❌ 指定股票数据同步失败: {e}")
    
    async def get_sync_status(self) -> dict:
        """获取同步状态"""
        try:
            async with AsyncSessionLocal() as session:
                from sqlalchemy import func, select
                
                # 获取股票总数
                stock_count_query = select(func.count(Stock.ts_code))
                stock_count_result = await session.execute(stock_count_query)
                stock_count = stock_count_result.scalar()
                
                # 获取今日有数据的股票数
                today = datetime.now().strftime("%Y%m%d")
                today_data_query = select(func.count(StockDaily.ts_code)).where(StockDaily.trade_date == today)
                today_data_result = await session.execute(today_data_query)
                today_data_count = today_data_result.scalar()
                
                return {
                    "status": "running" if self._running else "stopped",
                    "stock_count": stock_count or 0,
                    "today_data_count": today_data_count or 0,
                    "sync_interval": self.sync_interval,
                    "last_sync_time": datetime.now().isoformat(),
                    "next_sync_time": (datetime.now() + timedelta(seconds=self.sync_interval)).isoformat()
                }
        except Exception as e:
            logger.error(f"获取同步状态失败: {e}")
            return {
                "status": "error",
                "error": str(e)
            }

# 全局数据同步服务实例
data_sync_service = DataSyncService()