import { useState, useCallback, useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import { useSearchParams } from 'react-router-dom'
import { Filter, X, RefreshCw, Download, AlertCircle } from 'lucide-react'
import { toast } from 'sonner'
import { ScreeningPanel, panelConditionsToApi } from '@/components/ScreeningPanel'
import { StockTable } from '@/components/StockTable'
import { StockScreeningCondition, StockQuote } from '@/types'

const API_BASE = import.meta.env.VITE_API_URL?.replace('/api', '') || 'https://finscreener-production.up.railway.app'

interface ScreeningResult {
  stocks: StockQuote[]
  total: number
  page: number
  page_size: number
  trade_date: string
  data_source: string
}

// 市场板块 → 侧边栏 URL 参数标签映射
const MARKET_LABELS: Record<string, string> = {
  '主板': '主板',
  '创业板': '创业板',
  '科创板': '科创板',
  '北交所': '北交所',
}

const INDUSTRY_LABELS: Record<string, string> = {
  '电子': '电子',
  '医药生物': '医药生物',
  '计算机': '计算机',
  '新能源': '新能源',
  '消费': '食品饮料|消费',
}

async function fetchScreeningResults(
  conditions: StockScreeningCondition[],
  urlMarket: string,
  urlIndustry: string,
  page: number,
  pageSize: number
): Promise<ScreeningResult> {
  const panelApi = panelConditionsToApi(
    Object.fromEntries(
      conditions.map(c => [c.id, c.value])
    )
  )
  // URL 参数优先级更高（侧边栏点击）
  const market = urlMarket || panelApi.market
  const industry = urlIndustry || panelApi.industry

  const body = {
    conditions: panelApi.conditions,
    market,
    industry,
    page,
    page_size: pageSize,
  }
  const res = await fetch(`${API_BASE}/api/screening`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  const json = await res.json()
  return json.data
}

const PAGE_SIZE = 30

const ScreenerPage = () => {
  const [searchParams, setSearchParams] = useSearchParams()

  // 从 URL 读取侧边栏传来的参数
  const urlMarket = searchParams.get('market') || ''
  const urlIndustry = searchParams.get('industry') || ''

  const [conditions, setConditions] = useState<StockScreeningCondition[]>([])
  const [showPanel, setShowPanel] = useState(true)
  const [page, setPage] = useState(1)
  const [savedPresets, setSavedPresets] = useState<{ name: string; conditions: StockScreeningCondition[] }[]>([])

  // URL 参数变化时重置页码
  useEffect(() => {
    setPage(1)
    if (urlMarket) toast.info(`已筛选：${urlMarket}`)
    if (urlIndustry) toast.info(`已筛选行业：${urlIndustry}`)
  }, [urlMarket, urlIndustry])

  // 主查询 - 包含所有筛选条件（面板条件 + URL参数）
  const query = useQuery<ScreeningResult>({
    queryKey: ['screener', conditions, urlMarket, urlIndustry, page],
    queryFn: () => fetchScreeningResults(conditions, urlMarket, urlIndustry, page, PAGE_SIZE),
    staleTime: 2 * 60 * 1000,
  })

  const stocks = query.data?.stocks ?? []
  const total = query.data?.total ?? 0
  const isLoading = query.isLoading
  const isError = query.isError
  const dataSource = query.data?.data_source

  const handleApplyFilters = useCallback((conds: StockScreeningCondition[]) => {
    setConditions(conds)
    setPage(1)
    if (conds.length > 0) {
      toast.success(`已应用 ${conds.length} 个筛选条件`)
    } else if (!urlMarket && !urlIndustry) {
      toast.info('已重置，显示全部股票')
    }
  }, [urlMarket, urlIndustry])

  const handleSavePreset = useCallback((name: string, conds: StockScreeningCondition[]) => {
    setSavedPresets(prev => {
      const existing = prev.findIndex(p => p.name === name)
      if (existing >= 0) {
        const updated = [...prev]
        updated[existing] = { name, conditions: conds }
        return updated
      }
      return [...prev, { name, conditions: conds }]
    })
    toast.success(`预设 "${name}" 已保存`)
  }, [])

  // 清除 URL 筛选参数
  const clearUrlFilter = () => {
    setSearchParams({})
    setPage(1)
  }

  const totalPages = Math.ceil(total / PAGE_SIZE)

  // 当前激活的过滤标签（URL参数）
  const urlTags: { label: string; key: string }[] = []
  if (urlMarket) urlTags.push({ label: `板块：${urlMarket}`, key: 'market' })
  if (urlIndustry) urlTags.push({ label: `行业：${INDUSTRY_LABELS[urlIndustry] || urlIndustry}`, key: 'industry' })

  return (
    <div className="space-y-4">
      {/* 页面标题 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">智能股票筛选器</h1>
          <p className="text-gray-500 text-sm mt-1">
            多维度条件筛选A股市场，发现投资机会
            {dataSource === 'mock' && (
              <span className="ml-2 text-yellow-600 text-xs font-medium bg-yellow-50 px-1.5 py-0.5 rounded">演示数据</span>
            )}
            {dataSource === 'tushare' && (
              <span className="ml-2 text-green-600 text-xs font-medium bg-green-50 px-1.5 py-0.5 rounded">Tushare Pro</span>
            )}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => query.refetch()}
            className="flex items-center gap-1.5 px-3 py-2 bg-white border border-gray-200 rounded-lg hover:bg-gray-50 text-sm text-gray-600"
          >
            <RefreshCw size={14} className={query.isFetching ? 'animate-spin' : ''} />
            <span>刷新</span>
          </button>
          <button
            onClick={() => setShowPanel(!showPanel)}
            className="flex items-center gap-2 px-4 py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 text-sm"
          >
            <Filter size={16} />
            <span>{showPanel ? '隐藏筛选' : '显示筛选'}</span>
            {conditions.length > 0 && (
              <span className="bg-blue-600 text-white text-xs rounded-full w-4 h-4 flex items-center justify-center">
                {conditions.length}
              </span>
            )}
          </button>
        </div>
      </div>

      {/* 统计卡片 */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <div className="bg-white rounded-xl p-3.5 border border-gray-200">
          <div className="text-xs text-gray-500">符合条件</div>
          <div className="text-2xl font-bold text-gray-900 mt-1">
            {isLoading ? <span className="text-gray-300">...</span> : total.toLocaleString()}
          </div>
          <div className="text-[10px] text-gray-400 mt-0.5">只股票</div>
        </div>
        <div className="bg-white rounded-xl p-3.5 border border-gray-200">
          <div className="text-xs text-gray-500">当前页</div>
          <div className="text-2xl font-bold text-gray-900 mt-1">{stocks.length}</div>
          <div className="text-[10px] text-gray-400 mt-0.5">第{page}/{Math.max(totalPages, 1)}页</div>
        </div>
        <div className="bg-white rounded-xl p-3.5 border border-gray-200">
          <div className="text-xs text-gray-500">筛选条件</div>
          <div className="text-2xl font-bold text-gray-900 mt-1">{conditions.length + urlTags.length}</div>
          <div className="text-[10px] text-gray-400 mt-0.5">
            {conditions.length + urlTags.length > 0 ? '已应用' : '默认全部'}
          </div>
        </div>
        <div className="bg-white rounded-xl p-3.5 border border-gray-200">
          <div className="text-xs text-gray-500">交易日</div>
          <div className="text-sm font-bold text-gray-900 mt-1">
            {query.data?.trade_date ? query.data.trade_date.replace(/(\d{4})(\d{2})(\d{2})/, '$1-$2-$3') : '加载中'}
          </div>
          <div className="text-[10px] text-gray-400 mt-0.5">数据日期</div>
        </div>
      </div>

      <div className="flex flex-col lg:flex-row gap-4">
        {/* 筛选面板 */}
        {showPanel && (
          <div className="lg:w-72 lg:flex-shrink-0">
            <ScreeningPanel
              onApplyFilters={handleApplyFilters}
              onSavePreset={handleSavePreset}
              savedPresets={savedPresets}
              isLoading={isLoading}
            />
          </div>
        )}

        {/* 主要内容 */}
        <div className="flex-1 min-w-0">
          {/* URL 参数标签（侧边栏点击的板块/行业筛选） */}
          {urlTags.length > 0 && (
            <div className="mb-3 p-3 bg-blue-50 border border-blue-200 rounded-xl flex items-center flex-wrap gap-2">
              <span className="text-xs font-medium text-blue-700">侧边栏筛选：</span>
              {urlTags.map(tag => (
                <span key={tag.key} className="flex items-center gap-1 bg-blue-600 text-white text-xs px-2.5 py-1 rounded-full">
                  {tag.label}
                </span>
              ))}
              <button
                onClick={clearUrlFilter}
                className="ml-auto flex items-center gap-1 text-xs text-blue-600 hover:text-blue-800"
              >
                <X size={12} />
                清除板块筛选
              </button>
            </div>
          )}

          {/* 面板筛选条件标签 */}
          {conditions.length > 0 && (
            <div className="mb-3 p-3 bg-green-50 border border-green-200 rounded-xl">
              <div className="flex items-center justify-between mb-1.5">
                <span className="text-xs font-medium text-green-700">
                  面板条件 ({conditions.length})：
                </span>
                <button
                  onClick={() => handleApplyFilters([])}
                  className="text-xs text-green-600 hover:text-green-800 flex items-center gap-1"
                >
                  <X size={10} />
                  清空
                </button>
              </div>
              <div className="flex flex-wrap gap-1.5">
                {conditions.map(c => {
                  let valStr = ''
                  if (c.type === 'range') {
                    const [lo, hi] = c.value as [number, number]
                    valStr = `${lo}-${hi}${c.unit ?? ''}`
                  } else if (c.type === 'select') {
                    valStr = c.options?.find(o => o.value === c.value)?.label ?? String(c.value)
                  } else {
                    valStr = c.value ? '是' : '否'
                  }
                  return (
                    <span key={c.id} className="bg-white border border-green-200 px-2 py-0.5 rounded text-xs text-green-700">
                      {c.name}: {valStr}
                    </span>
                  )
                })}
              </div>
            </div>
          )}

          {/* 错误提示 */}
          {isError && (
            <div className="mb-3 p-3 bg-red-50 border border-red-200 rounded-xl flex items-center gap-3 text-red-600 text-sm">
              <AlertCircle size={18} />
              <span>数据加载失败</span>
              <button onClick={() => query.refetch()} className="ml-auto underline text-xs">重试</button>
            </div>
          )}

          {/* 股票表格 */}
          <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
            <div className="px-4 py-3 border-b border-gray-200 bg-gray-50 flex items-center justify-between">
              <div>
                <h2 className="text-base font-semibold text-gray-900">筛选结果</h2>
                <p className="text-gray-500 text-xs mt-0.5">
                  {isLoading ? '加载中...' : `共 ${total.toLocaleString()} 只，点击表头排序`}
                </p>
              </div>
              <button className="flex items-center gap-1.5 px-3 py-1.5 bg-white border border-gray-200 rounded-lg hover:bg-gray-50 text-xs text-gray-600">
                <Download size={12} />
                <span>导出</span>
              </button>
            </div>

            <StockTable stocks={stocks} isLoading={isLoading} />

            {/* 分页 */}
            {totalPages > 1 && (
              <div className="px-4 py-3 border-t border-gray-200 bg-gray-50 flex items-center justify-between">
                <span className="text-xs text-gray-500">
                  第 {page} / {totalPages} 页，共 {total.toLocaleString()} 条
                </span>
                <div className="flex items-center gap-1.5">
                  <button
                    onClick={() => setPage(p => Math.max(1, p - 1))}
                    disabled={page <= 1}
                    className="px-3 py-1.5 text-xs border border-gray-200 rounded-lg hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed"
                  >
                    上一页
                  </button>
                  {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                    const pageNum = Math.max(1, page - 2) + i
                    if (pageNum > totalPages) return null
                    return (
                      <button
                        key={pageNum}
                        onClick={() => setPage(pageNum)}
                        className={`px-3 py-1.5 text-xs rounded-lg ${
                          pageNum === page
                            ? 'bg-blue-600 text-white'
                            : 'border border-gray-200 hover:bg-gray-50'
                        }`}
                      >
                        {pageNum}
                      </button>
                    )
                  })}
                  <button
                    onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                    disabled={page >= totalPages}
                    className="px-3 py-1.5 text-xs border border-gray-200 rounded-lg hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed"
                  >
                    下一页
                  </button>
                </div>
              </div>
            )}
          </div>

          {/* 免责声明 */}
          <div className="mt-3 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
            <p className="text-xs text-yellow-800">
              ⚠️ 本筛选器信息仅供学习参考，不构成任何投资建议。股市有风险，投资需谨慎。
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default ScreenerPage
