import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

/**
 * 格式化数字为货币格式
 */
export function formatCurrency(value: number, currency: string = '¥'): string {
  if (value === null || value === undefined) return '-'
  
  // 处理大数字
  if (Math.abs(value) >= 100000000) {
    return `${currency}${(value / 100000000).toFixed(2)}亿`
  } else if (Math.abs(value) >= 10000) {
    return `${currency}${(value / 10000).toFixed(2)}万`
  }
  
  return `${currency}${value.toFixed(2)}`
}

/**
 * 格式化百分比
 */
export function formatPercentage(value: number, decimal: number = 2): string {
  if (value === null || value === undefined) return '-'
  
  const sign = value > 0 ? '+' : ''
  return `${sign}${value.toFixed(decimal)}%`
}

/**
 * 根据涨跌获取颜色类名
 */
export function getChangeColor(value: number): string {
  if (value > 0) return 'financial-up'
  if (value < 0) return 'financial-down'
  return 'financial-neutral'
}

/**
 * 格式化日期
 */
export function formatDate(dateStr: string, format: string = 'YYYY-MM-DD'): string {
  if (!dateStr) return '-'
  
  const date = new Date(dateStr.replace(/(\d{4})(\d{2})(\d{2})/, '$1-$2-$3'))
  
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  
  switch (format) {
    case 'YYYY-MM-DD':
      return `${year}-${month}-${day}`
    case 'MM-DD':
      return `${month}-${day}`
    case 'YYYY/MM/DD':
      return `${year}/${month}/${day}`
    default:
      return `${year}-${month}-${day}`
  }
}

/**
 * 格式化股票代码
 */
export function formatStockCode(tsCode: string): string {
  if (!tsCode) return '-'
  
  // 如果是Tushare格式（如000001.SZ），提取代码部分
  if (tsCode.includes('.')) {
    return tsCode.split('.')[0]
  }
  
  return tsCode
}

/**
 * 获取股票市场名称
 */
export function getMarketName(tsCode: string): string {
  if (!tsCode) return '未知'
  
  if (tsCode.endsWith('.SH')) return '沪市'
  if (tsCode.endsWith('.SZ')) return '深市'
  if (tsCode.endsWith('.BJ')) return '北交所'
  
  return '其他'
}

/**
 * 防抖函数
 */
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout
  
  return function executedFunction(...args: Parameters<T>) {
    const later = () => {
      clearTimeout(timeout)
      func(...args)
    }
    
    clearTimeout(timeout)
    timeout = setTimeout(later, wait)
  }
}

/**
 * 节流函数
 */
export function throttle<T extends (...args: any[]) => any>(
  func: T,
  limit: number
): (...args: Parameters<T>) => void {
  let inThrottle: boolean
  
  return function executedFunction(...args: Parameters<T>) {
    if (!inThrottle) {
      func(...args)
      inThrottle = true
      setTimeout(() => (inThrottle = false), limit)
    }
  }
}

/**
 * 生成随机ID
 */
export function generateId(length: number = 8): string {
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
  let result = ''
  for (let i = 0; i < length; i++) {
    result += chars.charAt(Math.floor(Math.random() * chars.length))
  }
  return result
}

/**
 * 深拷贝
 */
export function deepClone<T>(obj: T): T {
  if (obj === null || typeof obj !== 'object') {
    return obj
  }
  
  if (obj instanceof Date) {
    return new Date(obj.getTime()) as T
  }
  
  if (obj instanceof Array) {
    return obj.map(item => deepClone(item)) as T
  }
  
  if (typeof obj === 'object') {
    const clonedObj: any = {}
    for (const key in obj) {
      if (obj.hasOwnProperty(key)) {
        clonedObj[key] = deepClone(obj[key])
      }
    }
    return clonedObj
  }
  
  return obj
}

/**
 * 检查对象是否为空
 */
export function isEmpty(obj: any): boolean {
  if (obj === null || obj === undefined) return true
  if (typeof obj === 'string' && obj.trim() === '') return true
  if (Array.isArray(obj) && obj.length === 0) return true
  if (typeof obj === 'object' && Object.keys(obj).length === 0) return true
  return false
}

/**
 * 安全获取嵌套对象属性
 */
export function getSafe<T>(obj: any, path: string, defaultValue: T): T {
  return path.split('.').reduce((acc, key) => {
    if (acc && typeof acc === 'object' && key in acc) {
      return acc[key]
    }
    return defaultValue
  }, obj)
}

/**
 * 计算百分比
 */
export function calculatePercentage(part: number, total: number): number {
  if (total === 0) return 0
  return (part / total) * 100
}

/**
 * 截断文本
 */
export function truncateText(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text
  return text.substring(0, maxLength) + '...'
}