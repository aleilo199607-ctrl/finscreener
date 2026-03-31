import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { RefreshCw, AlertCircle, TrendingUp, TrendingDown } from 'lucide-react'
import { cn } from '@/utils/cn'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts'

const API_BASE = import.meta.env.VITE_API_URL?.replace('/api', '') || 'https://finscreener-production.up.railway.app'

interface IndustryItem {
  industry: string
  stocks: number
  pct_chg: number
  avg_pct?: number
  amount?: number
  net_flow?: number
}

interface IndustriesData {
  trade_date: string
  industries: IndustryItem[]
  data_source: string
}

function fetchIndustries(): Promise<IndustriesData> {
  return fetch(`${API_BASE}/api/market/industries`)
    .then(r => r.json())
    .then(d => d.data)
}

type SortKey = 'pct_chg' | 'net_flow' | 'stocks'

function HeatMap({ industries }: { industries: IndustryItem[] }) {
  // 热力图：每个方块大小按 stocks 数量，颜色按 pct_chg
  const maxPct = Math.max(...industries.map(i => Math.abs(i.pct_chg || 0)), 0.01)
  return (
    <div className="flex flex-wrap gap-1.5 p-4">
      {industries.map(item => {
        const pct = item.pct_chg ?? 0
        const intensity = Math.min(Math.abs(pct) / maxPct, 1)
        const up = pct > 0
        const zero = pct === 0
        // 宽度根据股票数量比例
        const stocks = item.stocks ?? 50
        const maxStocks = Math.max(...industries.map(i => i.stocks ?? 50), 50)
        const w = Math.max(60, Math.round((stocks / maxStocks) * 140))
        const bg = zero
          ? '#e5e7eb'
          : up
          ? `rgba(239,68,68,${0.2 + intensity * 0.75})`
          : `rgba(34,197,94,${0.2 + intensity * 0.75})`
        const textColor = intensity > 0.5 ? 'white' : up ? '#b91c1c' : '#15803d'
        return (
          <div
            key={item.industry}
            style={{ width: w, background: bg, color: textColor }}
            className="rounded-lg p-2 text-center select-none cursor-default transition-transform hover:scale-105"
            title={`${item.industry}: ${pct >= 0 ? '+' : ''}${pct.toFixed(2)}% | ${stocks}只`}
          >
            <div className="text-xs font-semibold truncate">{item.industry}</div>
            <div className="text-xs mt-0.5 font-bold">{pct >= 0 ? '+' : ''}{pct.toFixed(2)}%</div>
          </div>
        )
      })}
    </div>
  )
}

export default function IndustriesPage() {
  const [sortKey, setSortKey] = useState<SortKey>('pct_chg')
  const [view, setView] = useState<'table' | 'bar' | 'heat'>('heat')

  const { data, isLoading, isError, refetch } = useQuery<IndustriesData>({
    queryKey: ['industries'],
    queryFn: fetchIndustries,
    staleTime: 5 * 60 * 1000,
  })

  const sorted = [...(data?.industries ?? [])].sort((a, b) => {
    if (sortKey === 'pct_chg') return (b.pct_chg ?? 0) - (a.pct_chg ?? 0)
    if (sortKey === 'net_flow') return (b.net_flow ?? 0) - (a.net_flow ?? 0)
    return (b.stocks ?? 0) - (a.stocks ?? 0)
  })

  // 为柱状图取前15
  const barData = sorted.slice(0, 15).map(i => ({
    ...i,
    name: i.industry.length > 4 ? i.industry.slice(0, 4) : i.industry,
  }))

  return (
    <div className="space-y-6">
      {/* 页头 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">行业分析</h1>
          <p className="text-gray-500 mt-1 text-sm">
            {data?.trade_date ? `交易日 ${data.trade_date}` : '实时数据'}
            {data?.data_source === 'mock' && (
              <span className="ml-2 text-yellow-600 text-xs">（演示数据）</span>
            )}
          </p>
        </div>
        <button
          onClick={() => refetch()}
          className="flex items-center space-x-1 px-3 py-2 rounded-lg border border-gray-200 hover:bg-gray-50 text-sm text-gray-600"
        >
          <RefreshCw size={14} />
          <span>刷新</span>
        </button>
      </div>

      {/* 视图切换 + 排序 */}
      <div className="flex flex-wrap items-center gap-3">
        <div className="flex space-x-1 bg-gray-100 rounded-xl p-1">
          {([['heat', '热力图'], ['bar', '柱状图'], ['table', '列表']] as [typeof view, string][]).map(([k, l]) => (
            <button
              key={k}
              onClick={() => setView(k)}
              className={cn(
                'px-3 py-1.5 rounded-lg text-sm font-medium transition-all',
                view === k ? 'bg-white shadow text-blue-600' : 'text-gray-500 hover:text-gray-700'
              )}
            >{l}</button>
          ))}
        </div>
        <div className="flex space-x-1 bg-gray-100 rounded-xl p-1">
          {([['pct_chg', '按涨跌'], ['net_flow', '按资金'], ['stocks', '按数量']] as [SortKey, string][]).map(([k, l]) => (
            <button
              key={k}
              onClick={() => setSortKey(k)}
              className={cn(
                'px-3 py-1.5 rounded-lg text-sm font-medium transition-all',
                sortKey === k ? 'bg-white shadow text-blue-600' : 'text-gray-500 hover:text-gray-700'
              )}
            >{l}</button>
          ))}
        </div>
      </div>

      {isLoading && (
        <div className="flex flex-col items-center justify-center py-20 space-y-3">
          <div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
          <span className="text-sm text-gray-400">数据加载中...</span>
        </div>
      )}

      {isError && !isLoading && (
        <div className="flex flex-col items-center justify-center py-20 space-y-3 text-red-500">
          <AlertCircle size={32} />
          <span className="text-sm">数据加载失败，请刷新重试</span>
        </div>
      )}

      {!isLoading && !isError && data && (
        <>
          {/* 热力图视图 */}
          {view === 'heat' && (
            <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
              <div className="px-5 py-3 border-b border-gray-100">
                <span className="text-sm text-gray-500">方块大小=板块股票数量，颜色深浅=涨跌幅度（红涨绿跌）</span>
              </div>
              <HeatMap industries={sorted} />
            </div>
          )}

          {/* 柱状图视图 */}
          {view === 'bar' && (
            <div className="bg-white rounded-xl border border-gray-200 p-6">
              <h2 className="text-base font-semibold text-gray-800 mb-4">行业涨跌幅对比（前15）</h2>
              <ResponsiveContainer width="100%" height={360}>
                <BarChart data={barData} margin={{ left: 0, right: 10 }}>
                  <XAxis dataKey="name" tick={{ fontSize: 11 }} />
                  <YAxis tickFormatter={v => `${v > 0 ? '+' : ''}${v}%`} tick={{ fontSize: 11 }} />
                  <Tooltip
                    formatter={(v: number) => [`${v >= 0 ? '+' : ''}${v.toFixed(2)}%`, '涨跌幅']}
                    labelFormatter={label => `${label}行业`}
                  />
                  <Bar dataKey="pct_chg" radius={[4, 4, 0, 0]}>
                    {barData.map((entry, index) => (
                      <Cell
                        key={index}
                        fill={entry.pct_chg > 0 ? '#ef4444' : entry.pct_chg < 0 ? '#22c55e' : '#9ca3af'}
                      />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}

          {/* 列表视图 */}
          {view === 'table' && (
            <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase">#</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase">行业</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase">涨跌幅</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase">股票数量</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase">资金流向(亿)</th>
                    </tr>
                  </thead>
                  <tbody>
                    {sorted.map((item, idx) => {
                      const up = item.pct_chg > 0
                      const zero = item.pct_chg === 0
                      return (
                        <tr key={item.industry} className="border-b border-gray-100 hover:bg-gray-50">
                          <td className="px-4 py-3 text-sm text-gray-400">{idx + 1}</td>
                          <td className="px-4 py-3 font-medium text-gray-900">{item.industry}</td>
                          <td className="px-4 py-3">
                            <span className={cn(
                              'flex items-center space-x-1 text-sm font-semibold',
                              up ? 'text-red-600' : zero ? 'text-gray-500' : 'text-green-600'
                            )}>
                              {up ? <TrendingUp size={14} /> : zero ? null : <TrendingDown size={14} />}
                              <span>{up ? '+' : ''}{item.pct_chg.toFixed(2)}%</span>
                            </span>
                          </td>
                          <td className="px-4 py-3 text-sm text-gray-600">{item.stocks ?? '-'}</td>
                          <td className="px-4 py-3 text-sm">
                            {item.net_flow != null ? (
                              <span className={item.net_flow > 0 ? 'text-red-500' : 'text-green-500'}>
                                {item.net_flow > 0 ? '+' : ''}{item.net_flow.toFixed(1)}
                              </span>
                            ) : '-'}
                          </td>
                        </tr>
                      )
                    })}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </>
      )}

      {/* 免责声明 */}
      <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
        <p className="text-sm text-yellow-800">
          ⚠️ <strong>重要提示：</strong>本页面所有信息仅供学习参考，不构成任何投资建议。股市有风险，投资需谨慎。
        </p>
      </div>
    </div>
  )
}
