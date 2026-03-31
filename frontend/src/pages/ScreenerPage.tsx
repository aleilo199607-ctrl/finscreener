import { useState, useCallback } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Filter, X, Save, RefreshCw, Download, AlertCircle } from 'lucide-react'
import { toast } from 'sonner'
import { ScreeningPanel } from '@/components/ScreeningPanel'
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

// 将 ScreeningPanel 的条件格式转换成后端需要的格式
function convertConditions(conditions: StockScreeningCondition[]) {
  const apiConditions: any[] = []
  const marketFilter = { market: '', industry: '' }

  conditions.forEach(c => {
    if (c.type === 'range') {
      const [low, high] = c.value as [number, number]
      const fieldMap: Record<string, string> = {
        price_range: 'close',
        price_change_pct: 'pct_chg',
        volume_ratio: 'vol',
        turnover_rate: 'pct_chg',
        pe_ratio: 'pe',
        pb_ratio: 'pb',
      }
      const field = fieldMap[c.id]
      if (field) {
        if (low > 0) apiConditions.push({ field, operator: 'gte', value: low })
        if (high < (c.max ?? 9999)) apiConditions.push({ field, operator: 'lte', value: high })
      }
    } else if (c.type === 'select') {
      if (c.id === 'sector') {
        const industryMap: Record<string, string> = {
          tech: '电子|计算机|通信',
          consumer: '食品饮料|商业贸易|轻工',
          healthcare: '医药',
          financial: '银行|保险|证券',
          industrial: '机械|化工|钢铁',
        }
        marketFilter.industry = industryMap[c.value as string] ?? ''
      }
    }
  })

  return { conditions: apiConditions, ...marketFilter }
}

async function fetchScreeningResults(
  conditions: StockScreeningCondition[],
  page: number,
  pageSize: number
): Promise<ScreeningResult> {
  const body = {
    ...convertConditions(conditions),
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

// 默认加载所有股票（空条件）
async function fetchDefaultStocks(): Promise<ScreeningResult> {
  return fetchScreeningResults([], 1, 30)
}

const ScreenerPage = () => {
  const [conditions, setConditions] = useState<StockScreeningCondition[]>([])
  const [appliedConditions, setAppliedConditions] = useState<StockScreeningCondition[]>([])
  const [showPanel, setShowPanel] = useState(true)
  const [page, setPage] = useState(1)
  const [savedPresets, setSavedPresets] = useState<{ name: string; conditions: StockScreeningCondition[] }[]>([])

  // 默认查询 - 无条件加载前30只股票
  const defaultQuery = useQuery<ScreeningResult>({
    queryKey: ['screener-default'],
    queryFn: fetchDefaultStocks,
    staleTime: 5 * 60 * 1000,
  })

  // 条件筛选查询
  const screenQuery = useQuery<ScreeningResult>({
    queryKey: ['screener', appliedConditions, page],
    queryFn: () => fetchScreeningResults(appliedConditions, page, 30),
    enabled: appliedConditions.length > 0,
    staleTime: 2 * 60 * 1000,
  })

  // 当前要显示的数据
  const activeData = appliedConditions.length > 0 ? screenQuery : defaultQuery
  const stocks = activeData.data?.stocks ?? []
  const total = activeData.data?.total ?? 0
  const isLoading = activeData.isLoading
  const isError = activeData.isError
  const dataSource = activeData.data?.data_source

  const handleApplyFilters = useCallback((conds: StockScreeningCondition[]) => {
    setAppliedConditions(conds)
    setPage(1)
    if (conds.length > 0) {
      toast.success(`正在筛选，已应用 ${conds.length} 个条件`)
    } else {
      toast.info('已重置，显示全部股票')
    }
  }, [])

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

  const handleRemoveAppliedCondition = (id: string) => {
    const newConds = appliedConditions.filter(c => c.id !== id)
    setAppliedConditions(newConds)
    setPage(1)
  }

  const totalPages = Math.ceil(total / 30)

  return (
    <div className="space-y-6">
      {/* 页面标题 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">智能股票筛选器</h1>
          <p className="text-gray-600 mt-2">
            通过多维度条件筛选A股市场，发现投资机会
            {dataSource === 'mock' && (
              <span className="ml-2 text-yellow-600 text-sm">（演示数据）</span>
            )}
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <button
            onClick={() => activeData.refetch()}
            className="flex items-center space-x-1 px-3 py-2 bg-white border border-gray-200 rounded-lg hover:bg-gray-50 text-sm text-gray-600"
          >
            <RefreshCw size={14} />
            <span>刷新</span>
          </button>
          <button
            onClick={() => setShowPanel(!showPanel)}
            className="flex items-center space-x-2 px-4 py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50"
          >
            <Filter size={18} />
            <span>{showPanel ? '隐藏筛选' : '显示筛选'}</span>
          </button>
        </div>
      </div>

      {/* 筛选结果统计 */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-xl p-4 border border-gray-200">
          <div className="text-sm text-gray-500">符合条件的股票</div>
          <div className="text-2xl font-bold text-gray-900 mt-1">
            {isLoading ? '...' : total.toLocaleString()}
          </div>
          <div className="text-xs text-gray-400 mt-1">
            {activeData.data?.trade_date ? `交易日 ${activeData.data.trade_date}` : '实时数据'}
          </div>
        </div>
        <div className="bg-white rounded-xl p-4 border border-gray-200">
          <div className="text-sm text-gray-500">当前页股票</div>
          <div className="text-2xl font-bold text-gray-900 mt-1">{stocks.length}</div>
          <div className="text-xs text-gray-400 mt-1">第 {page}/{Math.max(totalPages, 1)} 页</div>
        </div>
        <div className="bg-white rounded-xl p-4 border border-gray-200">
          <div className="text-sm text-gray-500">筛选条件</div>
          <div className="text-2xl font-bold text-gray-900 mt-1">{appliedConditions.length}</div>
          <div className="text-xs text-gray-400 mt-1">
            {appliedConditions.length > 0 ? '已应用' : '默认全部'}
          </div>
        </div>
        <div className="bg-white rounded-xl p-4 border border-gray-200">
          <div className="text-sm text-gray-500">数据来源</div>
          <div className="text-lg font-bold text-gray-900 mt-1">
            {dataSource === 'tushare' ? 'Tushare Pro' : dataSource === 'mock' ? '演示数据' : '加载中'}
          </div>
          <div className="text-xs text-gray-400 mt-1">实时更新</div>
        </div>
      </div>

      <div className="flex flex-col lg:flex-row gap-6">
        {/* 筛选面板 */}
        {showPanel && (
          <div className="lg:w-1/4">
            <ScreeningPanel
              onApplyFilters={handleApplyFilters}
              onSavePreset={handleSavePreset}
              savedPresets={savedPresets}
              isLoading={isLoading}
            />
          </div>
        )}

        {/* 主要内容 */}
        <div className={showPanel ? 'lg:w-3/4' : 'w-full'}>
          {/* 已应用的条件标签 */}
          {appliedConditions.length > 0 && (
            <div className="mb-4 p-4 bg-blue-50 border border-blue-200 rounded-xl">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-blue-800">
                  已应用 {appliedConditions.length} 个筛选条件：
                </span>
                <button
                  onClick={() => handleApplyFilters([])}
                  className="text-xs text-blue-600 hover:text-blue-800 flex items-center space-x-1"
                >
                  <X size={12} />
                  <span>清空全部</span>
                </button>
              </div>
              <div className="flex flex-wrap gap-2">
                {appliedConditions.map(c => {
                  let valStr = ''
                  if (c.type === 'range') {
                    const [lo, hi] = c.value as [number, number]
                    valStr = `${lo.toFixed(1)}-${hi.toFixed(1)}${c.unit ?? ''}`
                  } else if (c.type === 'select') {
                    valStr = c.options?.find(o => o.value === c.value)?.label ?? String(c.value)
                  } else {
                    valStr = c.value ? '是' : '否'
                  }
                  return (
                    <span
                      key={c.id}
                      className="flex items-center space-x-1 bg-white border border-blue-200 px-2 py-1 rounded-lg text-xs text-blue-700"
                    >
                      <span>{c.name}: {valStr}</span>
                      <button onClick={() => handleRemoveAppliedCondition(c.id)}>
                        <X size={10} />
                      </button>
                    </span>
                  )
                })}
              </div>
            </div>
          )}

          {/* 错误提示 */}
          {isError && (
            <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-xl flex items-center space-x-3 text-red-600">
              <AlertCircle size={20} />
              <span className="text-sm">数据加载失败，请点击刷新重试</span>
              <button onClick={() => activeData.refetch()} className="ml-auto text-sm underline">
                重试
              </button>
            </div>
          )}

          {/* 股票表格 */}
          <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
            <div className="px-6 py-4 border-b border-gray-200 bg-gray-50 flex items-center justify-between">
              <div>
                <h2 className="text-lg font-semibold text-gray-900">筛选结果</h2>
                <p className="text-gray-500 text-sm mt-0.5">
                  {isLoading ? '加载中...' : `共 ${total.toLocaleString()} 只股票，点击表头可排序`}
                </p>
              </div>
              <button className="flex items-center space-x-2 px-3 py-2 bg-white border border-gray-200 rounded-lg hover:bg-gray-50 text-sm text-gray-600">
                <Download size={14} />
                <span>导出</span>
              </button>
            </div>

            <StockTable stocks={stocks} isLoading={isLoading} />

            {/* 分页 */}
            {totalPages > 1 && (
              <div className="px-6 py-4 border-t border-gray-200 bg-gray-50 flex items-center justify-between">
                <span className="text-sm text-gray-500">
                  第 {page} / {totalPages} 页，共 {total.toLocaleString()} 条
                </span>
                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => setPage(p => Math.max(1, p - 1))}
                    disabled={page <= 1}
                    className="px-3 py-1.5 text-sm border border-gray-200 rounded-lg hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed"
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
                        className={`px-3 py-1.5 text-sm rounded-lg ${
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
                    className="px-3 py-1.5 text-sm border border-gray-200 rounded-lg hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed"
                  >
                    下一页
                  </button>
                </div>
              </div>
            )}
          </div>

          {/* 免责声明 */}
          <div className="mt-4 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
            <p className="text-sm text-yellow-800">
              ⚠️ <strong>重要提示：</strong>本筛选器所有信息仅供学习参考，不构成任何投资建议。
              股市有风险，投资需谨慎。数据来源：Tushare Pro API。
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default ScreenerPage
