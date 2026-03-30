import { QueryClient } from '@tanstack/react-query'
import { toast } from 'sonner'

// API基础配置
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

// 创建React Query客户端
export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5分钟
      gcTime: 10 * 60 * 1000, // 10分钟
      retry: 2,
      refetchOnWindowFocus: false,
    },
    mutations: {
      retry: 1,
    },
  },
})

// 通用请求函数
async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`
  
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers,
  }

  try {
    const response = await fetch(url, {
      ...options,
      headers,
    })

    if (!response.ok) {
      const errorText = await response.text()
      throw new Error(`API Error (${response.status}): ${errorText}`)
    }

    const data = await response.json()
    
    if (!data.success) {
      throw new Error(data.message || 'API request failed')
    }

    return data.data
  } catch (error) {
    console.error(`API请求失败 [${endpoint}]:`, error)
    
    // 显示错误提示（非生产环境可减少频率）
    if (!endpoint.includes('heartbeat')) {
      toast.error('数据获取失败，请稍后重试', {
        description: error instanceof Error ? error.message : '网络连接异常',
      })
    }
    
    throw error
  }
}

// 股票相关API
export const stockApi = {
  // 获取股票列表
  getStocks: (params?: { market?: string; industry?: string }) => 
    apiRequest<Stock[]>('/stocks', {
      method: 'POST',
      body: JSON.stringify(params || {}),
    }),

  // 获取股票详情
  getStockDetail: (tsCode: string) => 
    apiRequest<StockQuote>(`/stocks/${tsCode}`),

  // 获取股票K线数据
  getStockKline: (tsCode: string, period: 'D' | 'W' | 'M' = 'D', limit: number = 100) =>
    apiRequest<any[]>(`/stocks/${tsCode}/kline?period=${period}&limit=${limit}`),

  // 获取技术指标
  getTechnicalIndicators: (tsCode: string) =>
    apiRequest<TechnicalIndicators>(`/stocks/${tsCode}/technical`),

  // 获取财务指标
  getFinancialIndicators: (tsCode: string) =>
    apiRequest<FinancialIndicators>(`/stocks/${tsCode}/financial`),

  // 获取资金流向
  getMoneyFlow: (tsCode: string, days: number = 5) =>
    apiRequest<MoneyFlow[]>(`/stocks/${tsCode}/moneyflow?days=${days}`),

  // 获取AI摘要
  getStockSummary: (tsCode: string) =>
    apiRequest<StockSummary>(`/stocks/${tsCode}/summary`),
}

// 筛选相关API
export const screeningApi = {
  // 执行筛选
  screenStocks: (conditions: ScreeningCondition[], page: number = 1, pageSize: number = 20) =>
    apiRequest<ScreeningResult>('/screening', {
      method: 'POST',
      body: JSON.stringify({ conditions, page, page_size: pageSize }),
    }),

  // 获取筛选条件模板
  getConditionTemplates: () =>
    apiRequest<ScreeningCondition[]>('/screening/templates'),

  // 保存筛选条件
  saveCondition: (name: string, conditions: ScreeningCondition[]) =>
    apiRequest<string>('/screening/save', {
      method: 'POST',
      body: JSON.stringify({ name, conditions }),
    }),

  // 加载筛选条件
  loadCondition: (id: string) =>
    apiRequest<ScreeningCondition[]>('/screening/load', {
      method: 'POST',
      body: JSON.stringify({ id }),
    }),
}

// 市场相关API
export const marketApi = {
  // 获取市场概况
  getMarketOverview: () =>
    apiRequest<any>('/market/overview'),

  // 获取行业板块
  getIndustrySectors: () =>
    apiRequest<any[]>('/market/industries'),

  // 获取热门股票
  getHotStocks: (limit: number = 10) =>
    apiRequest<StockQuote[]>(`/market/hot?limit=${limit}`),

  // 获取涨跌榜
  getTopGainers: (limit: number = 10) =>
    apiRequest<StockQuote[]>(`/market/top/gainers?limit=${limit}`),

  // 获取跌幅榜
  getTopLosers: (limit: number = 10) =>
    apiRequest<StockQuote[]>(`/market/top/losers?limit=${limit}`),
}

// 工具函数
export const formatCurrency = (value: number): string => {
  if (value >= 100000000) {
    return `¥${(value / 100000000).toFixed(2)}亿`
  } else if (value >= 10000) {
    return `¥${(value / 10000).toFixed(2)}万`
  }
  return `¥${value.toFixed(2)}`
}

export const formatPercentage = (value: number): string => {
  const sign = value >= 0 ? '+' : ''
  return `${sign}${value.toFixed(2)}%`
}

export const getChangeColor = (value: number): string => {
  if (value > 0) return 'financial-up'
  if (value < 0) return 'financial-down'
  return 'financial-neutral'
}