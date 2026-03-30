from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, JSON, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from app.core.database import Base

class Stock(Base):
    """股票基本信息模型"""
    __tablename__ = "stocks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ts_code = Column(String(20), unique=True, nullable=False, index=True)  # Tushare代码
    symbol = Column(String(10), nullable=False, index=True)  # 股票代码
    name = Column(String(50), nullable=False)  # 股票名称
    area = Column(String(50))  # 地区
    industry = Column(String(50))  # 行业
    market = Column(String(20))  # 市场（主板/创业板/科创板）
    list_date = Column(String(10))  # 上市日期
    is_hs = Column(String(2))  # 是否沪深港通标的
    list_status = Column(String(2), default="L")  # 上市状态 L上市 D退市 P暂停上市
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 索引
    __table_args__ = (
        Index("idx_stocks_market", "market"),
        Index("idx_stocks_industry", "industry"),
        Index("idx_stocks_area", "area"),
    )

class StockDaily(Base):
    """股票日行情数据模型"""
    __tablename__ = "stock_daily"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ts_code = Column(String(20), nullable=False, index=True)
    trade_date = Column(String(10), nullable=False, index=True)  # 交易日期 YYYYMMDD
    
    # 价格数据
    open = Column(Float)  # 开盘价
    high = Column(Float)  # 最高价
    low = Column(Float)  # 最低价
    close = Column(Float)  # 收盘价
    pre_close = Column(Float)  # 前收盘价
    change = Column(Float)  # 涨跌额
    pct_chg = Column(Float)  # 涨跌幅
    vol = Column(Float)  # 成交量（手）
    amount = Column(Float)  # 成交额（千元）
    
    # 技术指标
    turnover_rate = Column(Float)  # 换手率
    turnover_rate_f = Column(Float)  # 流通换手率
    volume_ratio = Column(Float)  # 量比
    
    # 估值指标
    pe = Column(Float)  # 市盈率
    pb = Column(Float)  # 市净率
    ps = Column(Float)  # 市销率
    total_share = Column(Float)  # 总股本
    float_share = Column(Float)  # 流通股本
    total_mv = Column(Float)  # 总市值
    circ_mv = Column(Float)  # 流通市值
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 复合唯一索引
    __table_args__ = (
        Index("idx_stock_daily_code_date", "ts_code", "trade_date", unique=True),
        Index("idx_stock_daily_date", "trade_date"),
    )

class StockFinancial(Base):
    """股票财务数据模型"""
    __tablename__ = "stock_financial"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ts_code = Column(String(20), nullable=False, index=True)
    report_date = Column(String(10), nullable=False, index=True)  # 报告期 YYYYMMDD
    
    # 盈利能力
    roe = Column(Float)  # 净资产收益率
    roa = Column(Float)  # 总资产收益率
    gross_margin = Column(Float)  # 毛利率
    net_margin = Column(Float)  # 净利率
    eps = Column(Float)  # 每股收益
    bvps = Column(Float)  # 每股净资产
    
    # 成长能力
    revenue_growth = Column(Float)  # 营收增长率
    profit_growth = Column(Float)  # 净利润增长率
    
    # 偿债能力
    debt_ratio = Column(Float)  # 资产负债率
    current_ratio = Column(Float)  # 流动比率
    quick_ratio = Column(Float)  # 速动比率
    
    # 运营能力
    inventory_turnover = Column(Float)  # 存货周转率
    accounts_receivable_turnover = Column(Float)  # 应收账款周转率
    
    # 现金流
    operating_cash_flow = Column(Float)  # 经营活动现金流
    investing_cash_flow = Column(Float)  # 投资活动现金流
    financing_cash_flow = Column(Float)  # 筹资活动现金流
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    __table_args__ = (
        Index("idx_stock_financial_code_date", "ts_code", "report_date", unique=True),
    )

class StockMoneyFlow(Base):
    """股票资金流向模型"""
    __tablename__ = "stock_money_flow"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ts_code = Column(String(20), nullable=False, index=True)
    trade_date = Column(String(10), nullable=False, index=True)
    
    # 小单
    buy_sm_vol = Column(Float)  # 小单买入量
    buy_sm_amount = Column(Float)  # 小单买入金额
    sell_sm_vol = Column(Float)  # 小单卖出量
    sell_sm_amount = Column(Float)  # 小单卖出金额
    
    # 中单
    buy_md_vol = Column(Float)  # 中单买入量
    buy_md_amount = Column(Float)  # 中单买入金额
    sell_md_vol = Column(Float)  # 中单卖出量
    sell_md_amount = Column(Float)  # 中单卖出金额
    
    # 大单
    buy_lg_vol = Column(Float)  # 大单买入量
    buy_lg_amount = Column(Float)  # 大单买入金额
    sell_lg_vol = Column(Float)  # 大单卖出量
    sell_lg_amount = Column(Float)  # 大单卖出金额
    
    # 特大单
    buy_elg_vol = Column(Float)  # 特大单买入量
    buy_elg_amount = Column(Float)  # 特大单买入金额
    sell_elg_vol = Column(Float)  # 特大单卖出量
    sell_elg_amount = Column(Float)  # 特大单卖出金额
    
    # 净流入
    net_mf_vol = Column(Float)  # 净流入量
    net_mf_amount = Column(Float)  # 净流入金额
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    __table_args__ = (
        Index("idx_stock_money_flow_code_date", "ts_code", "trade_date", unique=True),
    )

class StockSummary(Base):
    """股票AI摘要模型"""
    __tablename__ = "stock_summary"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ts_code = Column(String(20), nullable=False, index=True)
    
    # 各维度摘要
    technical_summary = Column(String(1000))  # 技术面摘要
    fundamental_summary = Column(String(1000))  # 基本面摘要
    capital_summary = Column(String(1000))  # 资金面摘要
    news_summary = Column(String(1000))  # 消息面摘要
    overall_summary = Column(String(2000))  # 整体摘要
    
    # 情感分析
    sentiment = Column(String(20))  # bullish/bearish/neutral
    confidence = Column(Float)  # 置信度 0-1
    
    # AI模型信息
    model_name = Column(String(50))
    prompt_version = Column(String(20))
    
    # 生成时间
    generated_at = Column(DateTime(timezone=True))
    expires_at = Column(DateTime(timezone=True))  # 摘要过期时间
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    __table_args__ = (
        Index("idx_stock_summary_code", "ts_code", unique=True),
        Index("idx_stock_summary_expires", "expires_at"),
    )

class ScreeningCondition(Base):
    """筛选条件模型"""
    __tablename__ = "screening_conditions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String(50), nullable=False, index=True)  # 用户ID（可以为匿名）
    name = Column(String(100), nullable=False)  # 条件名称
    description = Column(String(500))  # 描述
    
    # 条件配置
    conditions = Column(JSON, nullable=False)  # JSON格式的筛选条件
    
    # 使用统计
    usage_count = Column(Integer, default=0)
    last_used_at = Column(DateTime(timezone=True))
    
    # 是否公开
    is_public = Column(Boolean, default=False)
    
    # 标签
    tags = Column(JSON)  # 标签列表
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    __table_args__ = (
        Index("idx_screening_user_id", "user_id"),
        Index("idx_screening_public", "is_public"),
    )

class MarketIndicator(Base):
    """市场指标模型"""
    __tablename__ = "market_indicators"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    trade_date = Column(String(10), nullable=False, index=True)
    
    # 市场概况
    sh_index = Column(Float)  # 上证指数
    sz_index = Column(Float)  # 深证成指
    cyb_index = Column(Float)  # 创业板指
    kcb_index = Column(Float)  # 科创板指
    
    # 涨跌统计
    up_count = Column(Integer)  # 上涨家数
    down_count = Column(Integer)  # 下跌家数
    unchanged_count = Column(Integer)  # 平盘家数
    
    # 成交统计
    total_volume = Column(Float)  # 总成交量
    total_amount = Column(Float)  # 总成交额
    
    # 资金流向
    sh_money_in = Column(Float)  # 沪市资金流入
    sz_money_in = Column(Float)  # 深市资金流入
    total_money_in = Column(Float)  # 总资金流入
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        Index("idx_market_indicator_date", "trade_date", unique=True),
    )