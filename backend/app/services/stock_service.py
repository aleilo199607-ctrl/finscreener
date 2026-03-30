import asyncio
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Union
import json
import logging

import tushare as ts
import pandas as pd
import numpy as np
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
import talib

from app.core.config import settings
from app.core.redis import redis_client, cached
from app.models.stock import (
    Stock, StockDaily, StockFinancial, 
    StockMoneyFlow, StockSummary, MarketIndicator
)
from app.schemas.stock import (
    StockResponse, StockDailyResponse, StockFinancialResponse,
    StockMoneyFlowResponse, ScreeningCondition, ScreeningResult
)

# 配置日志
logger = logging.getLogger(__name__)

class StockService:
    """股票数据服务"""
    
    def __init__(self):
        self.pro = None
        self._init_tushare()
    
    def _init_tushare(self):
        """初始化Tushare"""
        try:
            # 使用环境变量中的Token
            token = settings.TUSHARE_TOKEN
            if not token:
                logger.warning("Tushare Token未配置，部分功能可能受限")
                return
            
            self.pro = ts.pro_api(token)
            logger.info("✅ Tushare Pro API初始化成功")
        except Exception as e:
            logger.error(f"❌ Tushare初始化失败: {e}")
            self.pro = None
    
    async def get_stock_list(
        self, 
        session: AsyncSession,
        market: Optional[str] = None,
        industry: Optional[str] = None,
        limit: int = 100
    ) -> List[StockResponse]:
        """获取股票列表"""
        try:
            # 构建查询条件
            query = select(Stock)
            
            if market and market != "ALL":
                query = query.where(Stock.market == market)
            
            if industry:
                query = query.where(Stock.industry == industry)
            
            query = query.limit(limit)
            
            result = await session.execute(query)
            stocks = result.scalars().all()
            
            return [StockResponse.model_validate(stock) for stock in stocks]
        except Exception as e:
            logger.error(f"获取股票列表失败: {e}")
            return []
    
    async def get_stock_detail(
        self, 
        session: AsyncSession,
        ts_code: str
    ) -> Optional[StockDailyResponse]:
        """获取股票最新详情"""
        try:
            # 构建缓存键
            cache_key = f"stock:detail:{ts_code}"
            
            # 尝试从缓存获取
            cached_data = await redis_client.get(cache_key)
            if cached_data:
                return StockDailyResponse(**cached_data)
            
            # 查询数据库
            query = select(StockDaily).where(
                StockDaily.ts_code == ts_code
            ).order_by(StockDaily.trade_date.desc()).limit(1)
            
            result = await session.execute(query)
            stock_daily = result.scalar_one_or_none()
            
            if not stock_daily:
                # 如果数据库中没有，尝试从Tushare获取
                stock_daily = await self._fetch_stock_daily_from_tushare(ts_code)
                if stock_daily:
                    # 保存到数据库
                    session.add(stock_daily)
                    await session.commit()
            
            if stock_daily:
                response = StockDailyResponse.model_validate(stock_daily)
                # 缓存结果（5分钟）
                await redis_client.set(cache_key, response.model_dump(), ttl=300)
                return response
            
            return None
        except Exception as e:
            logger.error(f"获取股票详情失败 [{ts_code}]: {e}")
            return None
    
    async def _fetch_stock_daily_from_tushare(self, ts_code: str) -> Optional[StockDaily]:
        """从Tushare获取股票日行情"""
        if not self.pro:
            logger.warning("Tushare未初始化，无法获取数据")
            return None
        
        try:
            # 获取最近一天的行情数据
            today = datetime.now().strftime("%Y%m%d")
            df = self.pro.daily(ts_code=ts_code, start_date=today, end_date=today)
            
            if df.empty:
                # 如果没有今天的数据，获取最近一天
                df = self.pro.daily(ts_code=ts_code, end_date=today).head(1)
            
            if df.empty:
                return None
            
            row = df.iloc[0]
            
            # 创建StockDaily对象
            stock_daily = StockDaily(
                ts_code=row['ts_code'],
                trade_date=str(row['trade_date']),
                open=float(row['open']),
                high=float(row['high']),
                low=float(row['low']),
                close=float(row['close']),
                pre_close=float(row['pre_close']),
                change=float(row['change']),
                pct_chg=float(row['pct_chg']),
                vol=float(row['vol']),
                amount=float(row['amount'])
            )
            
            # 获取其他指标
            await self._enrich_stock_data(stock_daily, ts_code)
            
            return stock_daily
        except Exception as e:
            logger.error(f"从Tushare获取股票数据失败 [{ts_code}]: {e}")
            return None
    
    async def _enrich_stock_data(self, stock_daily: StockDaily, ts_code: str):
        """丰富股票数据（技术指标等）"""
        try:
            # 获取更多指标（这里可以扩展）
            df = self.pro.daily_basic(ts_code=ts_code, trade_date=stock_daily.trade_date)
            
            if not df.empty:
                row = df.iloc[0]
                stock_daily.turnover_rate = float(row.get('turnover_rate', 0))
                stock_daily.turnover_rate_f = float(row.get('turnover_rate_f', 0))
                stock_daily.volume_ratio = float(row.get('volume_ratio', 0))
                stock_daily.pe = float(row.get('pe', 0))
                stock_daily.pb = float(row.get('pb', 0))
                stock_daily.ps = float(row.get('ps', 0))
                stock_daily.total_share = float(row.get('total_share', 0))
                stock_daily.float_share = float(row.get('float_share', 0))
                stock_daily.total_mv = float(row.get('total_mv', 0))
                stock_daily.circ_mv = float(row.get('circ_mv', 0))
        except Exception as e:
            logger.warning(f"丰富股票数据失败 [{ts_code}]: {e}")
    
    async def get_stock_kline(
        self,
        session: AsyncSession,
        ts_code: str,
        period: str = 'D',
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """获取股票K线数据"""
        try:
            cache_key = f"stock:kline:{ts_code}:{period}:{limit}"
            
            # 尝试从缓存获取
            cached_data = await redis_client.get(cache_key)
            if cached_data:
                return cached_data
            
            # 查询数据库
            query = select(StockDaily).where(
                StockDaily.ts_code == ts_code
            ).order_by(StockDaily.trade_date.desc()).limit(limit)
            
            result = await session.execute(query)
            daily_list = result.scalars().all()
            
            # 转换为K线格式
            kline_data = []
            for daily in daily_list:
                kline_data.append({
                    'date': daily.trade_date,
                    'open': daily.open,
                    'high': daily.high,
                    'low': daily.low,
                    'close': daily.close,
                    'volume': daily.vol,
                    'amount': daily.amount,
                    'change': daily.change,
                    'pct_chg': daily.pct_chg
                })
            
            # 反转顺序（从旧到新）
            kline_data.reverse()
            
            # 缓存结果（1分钟）
            await redis_client.set(cache_key, kline_data, ttl=60)
            
            return kline_data
        except Exception as e:
            logger.error(f"获取K线数据失败 [{ts_code}]: {e}")
            return []
    
    async def get_technical_indicators(
        self,
        ts_code: str,
        period: str = 'D',
        limit: int = 100
    ) -> Dict[str, Any]:
        """计算技术指标"""
        try:
            cache_key = f"stock:technical:{ts_code}:{period}:{limit}"
            
            cached_data = await redis_client.get(cache_key)
            if cached_data:
                return cached_data
            
            # 获取K线数据
            from app.core.database import AsyncSessionLocal
            async with AsyncSessionLocal() as session:
                kline_data = await self.get_stock_kline(session, ts_code, period, limit)
            
            if not kline_data:
                return {}
            
            # 提取价格数据
            closes = [float(d['close']) for d in kline_data]
            highs = [float(d['high']) for d in kline_data]
            lows = [float(d['low']) for d in kline_data]
            volumes = [float(d['volume']) for d in kline_data]
            
            # 转换为numpy数组
            close_array = np.array(closes, dtype=np.float64)
            high_array = np.array(highs, dtype=np.float64)
            low_array = np.array(lows, dtype=np.float64)
            volume_array = np.array(volumes, dtype=np.float64)
            
            # 计算MACD
            macd, macd_signal, macd_hist = talib.MACD(close_array)
            
            # 计算KDJ
            slowk, slowd = talib.STOCH(high_array, low_array, close_array)
            slowj = 3 * slowk - 2 * slowd
            
            # 计算RSI
            rsi6 = talib.RSI(close_array, timeperiod=6)
            rsi12 = talib.RSI(close_array, timeperiod=12)
            rsi24 = talib.RSI(close_array, timeperiod=24)
            
            # 计算布林带
            upper, middle, lower = talib.BBANDS(close_array)
            
            # 计算均线
            ma5 = talib.MA(close_array, timeperiod=5)
            ma10 = talib.MA(close_array, timeperiod=10)
            ma20 = talib.MA(close_array, timeperiod=20)
            ma60 = talib.MA(close_array, timeperiod=60)
            
            # 计算成交量均线
            volume_ma5 = talib.MA(volume_array, timeperiod=5)
            volume_ma10 = talib.MA(volume_array, timeperiod=10)
            
            # 获取最新值
            latest_idx = -1
            
            indicators = {
                'macd': {
                    'dif': float(macd[latest_idx]) if not np.isnan(macd[latest_idx]) else None,
                    'dea': float(macd_signal[latest_idx]) if not np.isnan(macd_signal[latest_idx]) else None,
                    'histogram': float(macd_hist[latest_idx]) if not np.isnan(macd_hist[latest_idx]) else None,
                },
                'kdj': {
                    'k': float(slowk[latest_idx]) if not np.isnan(slowk[latest_idx]) else None,
                    'd': float(slowd[latest_idx]) if not np.isnan(slowd[latest_idx]) else None,
                    'j': float(slowj[latest_idx]) if not np.isnan(slowj[latest_idx]) else None,
                },
                'rsi': {
                    'rsi6': float(rsi6[latest_idx]) if not np.isnan(rsi6[latest_idx]) else None,
                    'rsi12': float(rsi12[latest_idx]) if not np.isnan(rsi12[latest_idx]) else None,
                    'rsi24': float(rsi24[latest_idx]) if not np.isnan(rsi24[latest_idx]) else None,
                },
                'boll': {
                    'upper': float(upper[latest_idx]) if not np.isnan(upper[latest_idx]) else None,
                    'middle': float(middle[latest_idx]) if not np.isnan(middle[latest_idx]) else None,
                    'lower': float(lower[latest_idx]) if not np.isnan(lower[latest_idx]) else None,
                    'width': (float(upper[latest_idx]) - float(lower[latest_idx])) / float(middle[latest_idx]) 
                            if not (np.isnan(upper[latest_idx]) or np.isnan(lower[latest_idx]) or np.isnan(middle[latest_idx])) 
                            else None,
                },
                'ma': {
                    'ma5': float(ma5[latest_idx]) if not np.isnan(ma5[latest_idx]) else None,
                    'ma10': float(ma10[latest_idx]) if not np.isnan(ma10[latest_idx]) else None,
                    'ma20': float(ma20[latest_idx]) if not np.isnan(ma20[latest_idx]) else None,
                    'ma60': float(ma60[latest_idx]) if not np.isnan(ma60[latest_idx]) else None,
                },
                'volume': {
                    'volume_ma5': float(volume_ma5[latest_idx]) if not np.isnan(volume_ma5[latest_idx]) else None,
                    'volume_ma10': float(volume_ma10[latest_idx]) if not np.isnan(volume_ma10[latest_idx]) else None,
                    'volume_ratio': float(volume_array[latest_idx]) / float(volume_ma5[latest_idx]) 
                                  if not (np.isnan(volume_array[latest_idx]) or np.isnan(volume_ma5[latest_idx])) 
                                  else None,
                }
            }
            
            # 缓存结果（5分钟）
            await redis_client.set(cache_key, indicators, ttl=300)
            
            return indicators
        except Exception as e:
            logger.error(f"计算技术指标失败 [{ts_code}]: {e}")
            return {}
    
    async def screen_stocks(
        self,
        session: AsyncSession,
        conditions: List[ScreeningCondition],
        page: int = 1,
        page_size: int = 20,
        market: str = "ALL"
    ) -> ScreeningResult:
        """筛选股票"""
        try:
            # 构建缓存键
            conditions_hash = hash(json.dumps([c.model_dump() for c in conditions], sort_keys=True))
            cache_key = f"screening:{conditions_hash}:{page}:{page_size}:{market}"
            
            # 尝试从缓存获取
            cached_data = await redis_client.get(cache_key)
            if cached_data:
                return ScreeningResult(**cached_data)
            
            # 构建查询
            query = select(StockDaily).join(Stock, StockDaily.ts_code == Stock.ts_code)
            
            # 应用筛选条件
            filters = []
            for condition in conditions:
                field = condition.field
                operator = condition.operator
                value = condition.value
                
                # 获取对应的列
                if hasattr(StockDaily, field):
                    column = getattr(StockDaily, field)
                elif hasattr(Stock, field):
                    column = getattr(Stock, field)
                else:
                    continue  # 跳过不存在的字段
                
                # 构建筛选条件
                if operator == 'gt':
                    filters.append(column > value)
                elif operator == 'lt':
                    filters.append(column < value)
                elif operator == 'gte':
                    filters.append(column >= value)
                elif operator == 'lte':
                    filters.append(column <= value)
                elif operator == 'eq':
                    filters.append(column == value)
                elif operator == 'neq':
                    filters.append(column != value)
                elif operator == 'between' and isinstance(value, list) and len(value) == 2:
                    filters.append(column.between(value[0], value[1]))
            
            if filters:
                query = query.where(and_(*filters))
            
            # 应用市场筛选
            if market != "ALL":
                query = query.where(Stock.market == market)
            
            # 获取最新日期的数据
            subquery = select(
                StockDaily.ts_code,
                func.max(StockDaily.trade_date).label('max_date')
            ).group_by(StockDaily.ts_code).subquery()
            
            query = query.join(
                subquery,
                and_(
                    StockDaily.ts_code == subquery.c.ts_code,
                    StockDaily.trade_date == subquery.c.max_date
                )
            )
            
            # 计算总数
            count_query = query.with_only_columns(func.count())
            total_result = await session.execute(count_query)
            total = total_result.scalar()
            
            # 分页查询
            offset = (page - 1) * page_size
            query = query.order_by(StockDaily.pct_chg.desc()).offset(offset).limit(page_size)
            
            result = await session.execute(query)
            items = result.scalars().all()
            
            # 转换为响应模型
            stock_responses = [StockDailyResponse.model_validate(item) for item in items]
            
            screening_result = ScreeningResult(
                total=total,
                page=page,
                page_size=page_size,
                items=stock_responses
            )
            
            # 缓存结果（30秒）
            await redis_client.set(cache_key, screening_result.model_dump(), ttl=30)
            
            return screening_result
        except Exception as e:
            logger.error(f"筛选股票失败: {e}")
            return ScreeningResult(total=0, page=page, page_size=page_size, items=[])
    
    async def get_money_flow(
        self,
        session: AsyncSession,
        ts_code: str,
        days: int = 5
    ) -> List[StockMoneyFlowResponse]:
        """获取资金流向数据"""
        try:
            cache_key = f"stock:moneyflow:{ts_code}:{days}"
            
            cached_data = await redis_client.get(cache_key)
            if cached_data:
                return [StockMoneyFlowResponse(**item) for item in cached_data]
            
            query = select(StockMoneyFlow).where(
                StockMoneyFlow.ts_code == ts_code
            ).order_by(StockMoneyFlow.trade_date.desc()).limit(days)
            
            result = await session.execute(query)
            money_flows = result.scalars().all()
            
            responses = [StockMoneyFlowResponse.model_validate(flow) for flow in money_flows]
            
            # 缓存结果（2分钟）
            await redis_client.set(cache_key, [resp.model_dump() for resp in responses], ttl=120)
            
            return responses
        except Exception as e:
            logger.error(f"获取资金流向失败 [{ts_code}]: {e}")
            return []
    
    async def get_market_overview(self, session: AsyncSession) -> Dict[str, Any]:
        """获取市场概况"""
        try:
            cache_key = "market:overview"
            
            cached_data = await redis_client.get(cache_key)
            if cached_data:
                return cached_data
            
            # 获取最新市场指标
            query = select(MarketIndicator).order_by(MarketIndicator.trade_date.desc()).limit(1)
            result = await session.execute(query)
            market_indicator = result.scalar_one_or_none()
            
            if not market_indicator:
                return {}
            
            # 计算市场情绪
            if market_indicator.up_count and market_indicator.down_count:
                total = market_indicator.up_count + market_indicator.down_count + (market_indicator.unchanged_count or 0)
                up_ratio = market_indicator.up_count / total * 100
                
                if up_ratio > 60:
                    sentiment = "bullish"
                elif up_ratio < 40:
                    sentiment = "bearish"
                else:
                    sentiment = "neutral"
            else:
                sentiment = "neutral"
            
            overview = {
                'trade_date': market_indicator.trade_date,
                'sh_index': market_indicator.sh_index,
                'sz_index': market_indicator.sz_index,
                'cyb_index': market_indicator.cyb_index,
                'up_count': market_indicator.up_count,
                'down_count': market_indicator.down_count,
                'unchanged_count': market_indicator.unchanged_count,
                'total_amount': market_indicator.total_amount,
                'total_volume': market_indicator.total_volume,
                'sentiment': sentiment,
                'up_ratio': up_ratio if 'up_ratio' in locals() else None,
                'sh_money_in': market_indicator.sh_money_in,
                'sz_money_in': market_indicator.sz_money_in,
                'total_money_in': market_indicator.total_money_in,
            }
            
            # 缓存结果（1分钟）
            await redis_client.set(cache_key, overview, ttl=60)
            
            return overview
        except Exception as e:
            logger.error(f"获取市场概况失败: {e}")
            return {}
    
    async def sync_stock_data(self, session: AsyncSession, ts_codes: List[str] = None):
        """同步股票数据"""
        if not self.pro:
            logger.warning("Tushare未初始化，跳过数据同步")
            return
        
        try:
            # 如果没有指定股票代码，获取所有股票
            if not ts_codes:
                stock_query = select(Stock.ts_code).limit(100)  # 限制数量避免超时
                result = await session.execute(stock_query)
                ts_codes = [row[0] for row in result]
            
            # 获取今天的日期
            today = datetime.now().strftime("%Y%m%d")
            
            for ts_code in ts_codes:
                try:
                    # 获取日行情数据
                    df = self.pro.daily(ts_code=ts_code, start_date=today, end_date=today)
                    
                    if df.empty:
                        continue
                    
                    for _, row in df.iterrows():
                        # 检查是否已存在
                        existing_query = select(StockDaily).where(
                            and_(
                                StockDaily.ts_code == row['ts_code'],
                                StockDaily.trade_date == str(row['trade_date'])
                            )
                        )
                        existing_result = await session.execute(existing_query)
                        existing = existing_result.scalar_one_or_none()
                        
                        if existing:
                            # 更新现有记录
                            existing.open = float(row['open'])
                            existing.high = float(row['high'])
                            existing.low = float(row['low'])
                            existing.close = float(row['close'])
                            existing.pre_close = float(row['pre_close'])
                            existing.change = float(row['change'])
                            existing.pct_chg = float(row['pct_chg'])
                            existing.vol = float(row['vol'])
                            existing.amount = float(row['amount'])
                        else:
                            # 创建新记录
                            stock_daily = StockDaily(
                                ts_code=row['ts_code'],
                                trade_date=str(row['trade_date']),
                                open=float(row['open']),
                                high=float(row['high']),
                                low=float(row['low']),
                                close=float(row['close']),
                                pre_close=float(row['pre_close']),
                                change=float(row['change']),
                                pct_chg=float(row['pct_chg']),
                                vol=float(row['vol']),
                                amount=float(row['amount'])
                            )
                            session.add(stock_daily)
                    
                    logger.info(f"✅ 同步股票数据成功: {ts_code}")
                    
                except Exception as e:
                    logger.error(f"❌ 同步股票数据失败 [{ts_code}]: {e}")
                    continue
            
            await session.commit()
            logger.info("🎉 股票数据同步完成")
            
        except Exception as e:
            logger.error(f"❌ 数据同步失败: {e}")
            await session.rollback()

# 全局股票服务实例
stock_service = StockService()