from datetime import datetime
from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field, validator
from enum import Enum

# 枚举类型
class MarketType(str, Enum):
    """市场类型"""
    SH = "SH"  # 沪市
    SZ = "SZ"  # 深市
    BJ = "BJ"  # 北交所
    ALL = "ALL"  # 全部

class SentimentType(str, Enum):
    """情感类型"""
    BULLISH = "bullish"  # 看涨
    BEARISH = "bearish"  # 看跌
    NEUTRAL = "neutral"  # 中性

class ConditionType(str, Enum):
    """条件类型"""
    PRICE = "price"  # 价格
    VOLUME = "volume"  # 成交量
    TECHNICAL = "technical"  # 技术指标
    FINANCIAL = "financial"  # 财务指标
    MARKET = "market"  # 市场表现

class ConditionOperator(str, Enum):
    """条件运算符"""
    GT = "gt"  # 大于
    LT = "lt"  # 小于
    GTE = "gte"  # 大于等于
    LTE = "lte"  # 小于等于
    EQ = "eq"  # 等于
    NEQ = "neq"  # 不等于
    BETWEEN = "between"  # 在...之间

# 基础模型
class StockBase(BaseModel):
    """股票基础模型"""
    ts_code: str = Field(..., description="Tushare代码")
    symbol: str = Field(..., description="股票代码")
    name: str = Field(..., description="股票名称")
    area: Optional[str] = Field(None, description="地区")
    industry: Optional[str] = Field(None, description="行业")
    market: Optional[str] = Field(None, description="市场")
    list_date: Optional[str] = Field(None, description="上市日期")

class StockDailyBase(BaseModel):
    """股票日行情基础模型"""
    ts_code: str = Field(..., description="Tushare代码")
    trade_date: str = Field(..., description="交易日期 YYYYMMDD")
    
    # 价格数据
    open: Optional[float] = Field(None, description="开盘价")
    high: Optional[float] = Field(None, description="最高价")
    low: Optional[float] = Field(None, description="最低价")
    close: Optional[float] = Field(None, description="收盘价")
    pre_close: Optional[float] = Field(None, description="前收盘价")
    change: Optional[float] = Field(None, description="涨跌额")
    pct_chg: Optional[float] = Field(None, description="涨跌幅")
    vol: Optional[float] = Field(None, description="成交量（手）")
    amount: Optional[float] = Field(None, description="成交额（千元）")
    
    # 技术指标
    turnover_rate: Optional[float] = Field(None, description="换手率")
    turnover_rate_f: Optional[float] = Field(None, description="流通换手率")
    volume_ratio: Optional[float] = Field(None, description="量比")
    
    # 估值指标
    pe: Optional[float] = Field(None, description="市盈率")
    pb: Optional[float] = Field(None, description="市净率")
    ps: Optional[float] = Field(None, description="市销率")
    total_share: Optional[float] = Field(None, description="总股本")
    float_share: Optional[float] = Field(None, description="流通股本")
    total_mv: Optional[float] = Field(None, description="总市值")
    circ_mv: Optional[float] = Field(None, description="流通市值")

class StockFinancialBase(BaseModel):
    """股票财务基础模型"""
    ts_code: str = Field(..., description="Tushare代码")
    report_date: str = Field(..., description="报告期 YYYYMMDD")
    
    # 盈利能力
    roe: Optional[float] = Field(None, description="净资产收益率")
    roa: Optional[float] = Field(None, description="总资产收益率")
    gross_margin: Optional[float] = Field(None, description="毛利率")
    net_margin: Optional[float] = Field(None, description="净利率")
    eps: Optional[float] = Field(None, description="每股收益")
    bvps: Optional[float] = Field(None, description="每股净资产")
    
    # 成长能力
    revenue_growth: Optional[float] = Field(None, description="营收增长率")
    profit_growth: Optional[float] = Field(None, description="净利润增长率")
    
    # 偿债能力
    debt_ratio: Optional[float] = Field(None, description="资产负债率")
    current_ratio: Optional[float] = Field(None, description="流动比率")
    quick_ratio: Optional[float] = Field(None, description="速动比率")

class StockMoneyFlowBase(BaseModel):
    """股票资金流向基础模型"""
    ts_code: str = Field(..., description="Tushare代码")
    trade_date: str = Field(..., description="交易日期 YYYYMMDD")
    
    # 小单
    buy_sm_vol: Optional[float] = Field(None, description="小单买入量")
    buy_sm_amount: Optional[float] = Field(None, description="小单买入金额")
    sell_sm_vol: Optional[float] = Field(None, description="小单卖出量")
    sell_sm_amount: Optional[float] = Field(None, description="小单卖出金额")
    
    # 中单
    buy_md_vol: Optional[float] = Field(None, description="中单买入量")
    buy_md_amount: Optional[float] = Field(None, description="中单买入金额")
    sell_md_vol: Optional[float] = Field(None, description="中单卖出量")
    sell_md_amount: Optional[float] = Field(None, description="中单卖出金额")
    
    # 大单
    buy_lg_vol: Optional[float] = Field(None, description="大单买入量")
    buy_lg_amount: Optional[float] = Field(None, description="大单买入金额")
    sell_lg_vol: Optional[float] = Field(None, description="大单卖出量")
    sell_lg_amount: Optional[float] = Field(None, description="大单卖出金额")
    
    # 特大单
    buy_elg_vol: Optional[float] = Field(None, description="特大单买入量")
    buy_elg_amount: Optional[float] = Field(None, description="特大单买入金额")
    sell_elg_vol: Optional[float] = Field(None, description="特大单卖出量")
    sell_elg_amount: Optional[float] = Field(None, description="特大单卖出金额")
    
    # 净流入
    net_mf_vol: Optional[float] = Field(None, description="净流入量")
    net_mf_amount: Optional[float] = Field(None, description="净流入金额")

# 响应模型
class StockResponse(StockBase):
    """股票响应模型"""
    id: str
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class StockDailyResponse(StockDailyBase):
    """股票日行情响应模型"""
    id: str
    created_at: datetime
    updated_at: Optional[datetime]
    
    @validator('pct_chg')
    def format_pct_chg(cls, v):
        """格式化涨跌幅"""
        if v is not None:
            return round(v, 2)
        return v
    
    class Config:
        from_attributes = True

class StockFinancialResponse(StockFinancialBase):
    """股票财务响应模型"""
    id: str
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class StockMoneyFlowResponse(StockMoneyFlowBase):
    """股票资金流向响应模型"""
    id: str
    created_at: datetime
    updated_at: Optional[datetime]
    
    @property
    def net_inflow(self) -> Optional[float]:
        """计算净流入金额（简化）"""
        if self.net_mf_amount is not None:
            return self.net_mf_amount
        return None
    
    class Config:
        from_attributes = True

# 筛选条件模型
class ScreeningCondition(BaseModel):
    """筛选条件模型"""
    id: Optional[str] = Field(None, description="条件ID")
    type: ConditionType = Field(..., description="条件类型")
    field: str = Field(..., description="字段名")
    operator: ConditionOperator = Field(..., description="运算符")
    value: Union[float, int, str, List[float], List[int]] = Field(..., description="值")
    label: str = Field(..., description="显示标签")
    unit: Optional[str] = Field(None, description="单位")
    
    @validator('value')
    def validate_value(cls, v, values):
        """验证值格式"""
        operator = values.get('operator')
        
        if operator == ConditionOperator.BETWEEN:
            if not isinstance(v, list) or len(v) != 2:
                raise ValueError('between操作符的值必须是包含两个元素的列表')
            if v[0] >= v[1]:
                raise ValueError('区间起始值必须小于结束值')
        elif operator in [ConditionOperator.EQ, ConditionOperator.NEQ] and isinstance(v, (list, dict)):
            raise ValueError(f'{operator}操作符不支持列表或字典值')
        
        return v

class ScreeningRequest(BaseModel):
    """筛选请求模型"""
    conditions: List[ScreeningCondition] = Field(..., description="筛选条件列表")
    page: int = Field(1, ge=1, description="页码")
    page_size: int = Field(20, ge=1, le=100, description="每页数量")
    market: Optional[MarketType] = Field(MarketType.ALL, description="市场类型")
    
    @validator('conditions')
    def validate_conditions(cls, v):
        """验证条件列表"""
        if not v:
            raise ValueError('筛选条件列表不能为空')
        if len(v) > 20:
            raise ValueError('筛选条件数量不能超过20个')
        return v

class ScreeningResult(BaseModel):
    """筛选结果模型"""
    total: int = Field(..., description="总记录数")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页数量")
    total_pages: int = Field(..., description="总页数")
    items: List[StockDailyResponse] = Field(..., description="股票列表")
    
    @validator('total_pages', always=True)
    def calculate_total_pages(cls, v, values):
        """计算总页数"""
        total = values.get('total', 0)
        page_size = values.get('page_size', 20)
        if total == 0:
            return 0
        return (total + page_size - 1) // page_size

# AI摘要模型
class StockSummaryRequest(BaseModel):
    """股票摘要请求模型"""
    ts_code: str = Field(..., description="股票代码")
    refresh: bool = Field(False, description="是否强制刷新")

class StockSummaryResponse(BaseModel):
    """股票摘要响应模型"""
    ts_code: str = Field(..., description="股票代码")
    
    # 各维度摘要
    technical_summary: str = Field(..., description="技术面摘要")
    fundamental_summary: str = Field(..., description="基本面摘要")
    capital_summary: str = Field(..., description="资金面摘要")
    news_summary: str = Field(..., description="消息面摘要")
    overall_summary: str = Field(..., description="整体摘要")
    
    # 情感分析
    sentiment: SentimentType = Field(..., description="情感倾向")
    confidence: float = Field(..., ge=0, le=1, description="置信度")
    
    # AI模型信息
    model_name: str = Field(..., description="模型名称")
    prompt_version: str = Field(..., description="提示词版本")
    
    # 生成时间
    generated_at: datetime = Field(..., description="生成时间")
    expires_at: datetime = Field(..., description="过期时间")
    
    # 免责声明
    disclaimer: str = Field(
        "本摘要由AI生成，仅供参考，不构成投资建议。投资有风险，决策需谨慎。",
        description="免责声明"
    )

# 市场指标模型
class MarketIndicatorResponse(BaseModel):
    """市场指标响应模型"""
    trade_date: str = Field(..., description="交易日期")
    
    # 市场概况
    sh_index: Optional[float] = Field(None, description="上证指数")
    sz_index: Optional[float] = Field(None, description="深证成指")
    cyb_index: Optional[float] = Field(None, description="创业板指")
    kcb_index: Optional[float] = Field(None, description="科创板指")
    
    # 涨跌统计
    up_count: Optional[int] = Field(None, description="上涨家数")
    down_count: Optional[int] = Field(None, description="下跌家数")
    unchanged_count: Optional[int] = Field(None, description="平盘家数")
    
    # 成交统计
    total_volume: Optional[float] = Field(None, description="总成交量")
    total_amount: Optional[float] = Field(None, description="总成交额")
    
    # 资金流向
    sh_money_in: Optional[float] = Field(None, description="沪市资金流入")
    sz_money_in: Optional[float] = Field(None, description="深市资金流入")
    total_money_in: Optional[float] = Field(None, description="总资金流入")
    
    # 计算字段
    @property
    def up_ratio(self) -> Optional[float]:
        """上涨比例"""
        if self.up_count is not None and self.down_count is not None:
            total = self.up_count + self.down_count + (self.unchanged_count or 0)
            if total > 0:
                return round(self.up_count / total * 100, 2)
        return None
    
    class Config:
        from_attributes = True

# API响应模型
class ApiResponse(BaseModel):
    """通用API响应模型"""
    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="消息")
    data: Optional[Any] = Field(None, description="数据")
    timestamp: datetime = Field(default_factory=datetime.now, description="时间戳")
    
    @classmethod
    def success_response(cls, data: Any = None, message: str = "操作成功"):
        """成功响应"""
        return cls(success=True, message=message, data=data)
    
    @classmethod
    def error_response(cls, message: str = "操作失败"):
        """错误响应"""
        return cls(success=False, message=message, data=None)