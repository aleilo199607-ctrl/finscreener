import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { TrendingUp, TrendingDown, DollarSign, RefreshCw, AlertCircle } from 'lucide-react'
import { cn } from '@/utils/cn'

const API_BASE = import.meta.env.VITE_API_URL?.replace('/api', '') || 'https://finscreener-production.up.railway.app'

interface StockItem {
  ts_code: string
  name: string
  industry: string
  market: string
  close: number
  change: number
  pct_chg: number
  vol: number
  amount: number
}

interface HotData {
  trade_date: string
  gainers: StockItem[]
  losers: StockItem[]
  by_amount: StockItem[]
  data_source: string
}

function fetchHotStocks(): Promise<HotData> {
  return fetch(`${API_BASE}/api/market/hot?limit=20`)
    .then(r => r.json())
    .then(d => d.data)
}

function PctBadge({ val }: { val: number }) {
  const up = val > 0
  const zero = val === 0
  return (
    <span className={cn(
      'inline-block px-2 py-0.5 rounded text-sm font-semibold',
      up ? 'bg-red-50 text-red-600' : zero ? 'bg-gray-100 text-gray-500' : 'bg-green-50 text-green-600'
    )}>
      {up ? '+' : ''}{val.toFixed(2)}%
    </span>
  )
}

function StockRow({ stock, rank }: { stock: StockItem; rank: number }) {
  return (
    <tr className="border-b border-gray-100 hover:bg-gray-50 transition-colors">
      <td className="px-4 py-3 text-sm text-gray-400 w-8">{rank}</td>
      <td className="px-4 py-3">
        <Link to={`/stock/${stock.ts_code}`} className="hover:text-blue-600">
          <div className="font-medium text-gray-900">{stock.name}</div>
          <div className="text-xs text-gray-400">{stock.ts_code}</div>
        </Link>
      </td>
      <td className="px-4 py-3 text-sm text-gray-500">{stock.industry}</td>
      <td className="px-4 py-3 text-sm font-medium text-gray-900">{stock.close.toFixed(2)}</td>
      <td className="px-4 py-3"><PctBadge val={stock.pct_chg} /></td>
      <td className="px-4 py-3 text-sm text-gray-500">{(stock.amount / 10000).toFixed(0)}万</td>
    </tr>
  )
}

type TabKey = 'gainers' | 'losers' | 'by_amount'

const TABS: { key: TabKey; label: string; icon: React.ReactNode }[] = [
  { key: 'gainers', label: '涨幅榜', icon: <TrendingUp size={16} /> },
  { key: 'losers', label: '跌幅榜', icon: <TrendingDown size={16} /> },
  { key: 'by_amount', label: '成交额榜', icon: <DollarSign size={16} /> },
]

export default function HotStocksPage() {
  const [tab, setTab] = useState<TabKey>('gainers')

  const { data, isLoading, isError, refetch } = useQuery<HotData>({
    queryKey: ['hot-stocks'],
    queryFn: fetchHotStocks,
    staleTime: 3 * 60 * 1000,
  })

  const list = data?.[tab] ?? []

  return (
    <div className="space-y-6">
      {/* 页头 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">热门股票</h1>
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

      {/* 标签栏 */}
      <div className="flex space-x-1 bg-gray-100 rounded-xl p-1 w-fit">
        {TABS.map(t => (
          <button
            key={t.key}
            onClick={() => setTab(t.key)}
            className={cn(
              'flex items-center space-x-1.5 px-4 py-2 rounded-lg text-sm font-medium transition-all',
              tab === t.key
                ? 'bg-white shadow text-blue-600'
                : 'text-gray-500 hover:text-gray-700'
            )}
          >
            {t.icon}
            <span>{t.label}</span>
          </button>
        ))}
      </div>

      {/* 表格区域 */}
      <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
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

        {!isLoading && !isError && (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase">#</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase">股票</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase">行业</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase">最新价</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase">涨跌幅</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase">成交额</th>
                </tr>
              </thead>
              <tbody>
                {list.map((stock, idx) => (
                  <StockRow key={stock.ts_code} stock={stock} rank={idx + 1} />
                ))}
                {list.length === 0 && (
                  <tr>
                    <td colSpan={6} className="px-4 py-12 text-center text-gray-400 text-sm">
                      暂无数据
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* 免责声明 */}
      <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
        <p className="text-sm text-yellow-800">
          ⚠️ <strong>重要提示：</strong>本页面所有信息仅供学习参考，不构成任何投资建议。股市有风险，投资需谨慎。
        </p>
      </div>
    </div>
  )
}
