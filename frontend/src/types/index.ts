// 股票基础类型
export interface Stock {
  ts_code: string
  symbol: string
  name: string
  area: string
  industry: string
  market: string
  list_date: string
}

// 股票行情数据
export interface StockQuote {
  ts_code: string
  name?: string       // 股票名称
  industry?: string   // 所属行业
  market?: string     // 市场板块
  trade_date: string
  open: number
  high: number
  low: number
  close: number
  pre_close: number
  change: number
  pct_chg: number
  vol: number
  amount: number
  turnover_rate?: number
  turnover_rate_f?: number
  volume_ratio?: number
  pe?: number
  pb?: number
  ps?: number
  total_share?: number
  float_share?: number
  total_mv?: number
  circ_mv?: number
}

// 技术指标
export interface TechnicalIndicators {
  macd?: {
    dif: number
    dea: number
    macd: number
  }
  kdj?: {
    k: number
    d: number
    j: number
  }
  rsi?: {
    rsi6: number
    rsi12: number
    rsi24: number
  }
  boll?: {
    upper: number
    middle: number
    lower: number
  }
  ma?: {
    ma5: number
    ma10: number
    ma20: number
    ma60: number
  }
}

// 财务指标
export interface FinancialIndicators {
  roe: number // 净资产收益率
  roa: number // 总资产收益率
  gross_margin: number // 毛利率
  net_margin: number // 净利率
  debt_ratio: number // 资产负债率
  current_ratio: number // 流动比率
  quick_ratio: number // 速动比率
  eps: number // 每股收益
  bvps: number // 每股净资产
  revenue_growth: number // 营收增长率
  profit_growth: number // 利润增长率
}

// 资金流向
export interface MoneyFlow {
  trade_date: string
  buy_sm_vol: number // 小单买入量
  buy_sm_amount: number // 小单买入金额
  sell_sm_vol: number // 小单卖出量
  sell_sm_amount: number // 小单卖出金额
  buy_md_vol: number // 中单买入量
  buy_md_amount: number // 中单买入金额
  sell_md_vol: number // 中单卖出量
  sell_md_amount: number // 中单卖出金额
  buy_lg_vol: number // 大单买入量
  buy_lg_amount: number // 大单买入金额
  sell_lg_vol: number // 大单卖出量
  sell_lg_amount: number // 大单卖出金额
  buy_elg_vol: number // 特大单买入量
  buy_elg_amount: number // 特大单买入金额
  sell_elg_vol: number // 特大单卖出量
  sell_elg_amount: number // 特大单卖出金额
  net_mf_vol: number // 净流入量
  net_mf_amount: number // 净流入金额
}

// 筛选条件
export interface ScreeningCondition {
  id: string
  type: 'price' | 'volume' | 'technical' | 'financial' | 'market'
  field: string
  operator: 'gt' | 'lt' | 'gte' | 'lte' | 'eq' | 'neq' | 'between'
  value: number | [number, number] | string
  label: string
  unit?: string
}

// 筛选结果
export interface ScreeningResult {
  total: number
  page: number
  page_size: number
  items: StockQuote[]
}

// AI摘要
export interface StockSummary {
  ts_code: string
  technical_summary: string
  fundamental_summary: string
  capital_summary: string
  news_summary: string
  overall_summary: string
  sentiment: 'bullish' | 'bearish' | 'neutral'
  confidence: number
  generated_at: string
}

// API响应
export interface ApiResponse<T> {
  success: boolean
  message: string
  data: T
  timestamp: string
}

// K线数据
export interface KLineData {
  date: string
  open: number
  high: number
  low: number
  close: number
  volume: number
  turnover?: number
}

// K线蜡烛图（KLineData别名）
export interface Candlestick extends KLineData {}

// 股票筛选条件（用于ScreeningPanel组件）
export interface StockScreeningCondition {
  id: string
  name: string
  type: 'range' | 'select' | 'boolean'
  min?: number
  max?: number
  unit?: string
  options?: Array<{ label: string; value: string }>
  value: number | [number, number] | string | boolean
  label?: string
}