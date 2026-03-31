import { useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import {
  ArrowLeft, ArrowUpRight, ArrowDownRight, TrendingUp, TrendingDown,
  BarChart3, PieChart, DollarSign, RefreshCw, AlertCircle, Bookmark, Share2
} from 'lucide-react'
import { toast } from 'sonner'
import { cn } from '@/utils/cn'
import {
  LineChart, Line, AreaChart, Area, BarChart, Bar,
  XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid
} from 'recharts'

const API_BASE = import.meta.env.VITE_API_URL?.replace('/api', '') || 'https://finscreener-production.up.railway.app'

interface KLineItem {
  date: string
  open: number
  high: number
  low: number
  close: number
  vol: number
  pct_chg: number
}

interface StockBasic {
  ts_code?: string
  name?: string
  industry?: string
  market?: string
  area?: string
  list_date?: string
}

interface StockDetailData {
  basic: StockBasic
  quote: Record<string, any>
  kline: KLineItem[]
}

async function fetchStockDetail(tsCode: string): Promise<StockDetailData> {
  const res = await fetch(`${API_BASE}/api/stocks/${tsCode}`)
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  const json = await res.json()
  return json.data
}

function PriceTag({ val, pre }: { val: number; pre?: number }) {
  const up = pre !== undefined ? val >= pre : val >= 0
  return (
    <span className={cn('font-bold text-3xl', up ? 'text-red-600' : 'text-green-600')}>
      {val.toFixed(2)}
    </span>
  )
}

const StockDetailPage = () => {
  const { code } = useParams<{ code: string }>()
  const [activeTab, setActiveTab] = useState('overview')
  const tsCode = code ?? '000001.SZ'
  const symbol = tsCode.split('.')[0]

  const { data, isLoading, isError, refetch } = useQuery<StockDetailData>({
    queryKey: ['stock-detail', tsCode],
    queryFn: () => fetchStockDetail(tsCode),
    staleTime: 5 * 60 * 1000,
  })

  const basic = data?.basic ?? {}
  const quote = data?.quote ?? {}
  const kline = data?.kline ?? []

  // 近30日行情用于折线图
  const chartData = kline.slice(-30).map(k => ({
    date: k.date.slice(4),
    close: k.close,
    vol: +(k.vol / 10000).toFixed(0),
    pct: k.pct_chg,
  }))

  const pct = quote.pct_chg ?? 0
  const isUp = pct >= 0

  const tabs = [
    { id: 'overview', name: '概览', icon: BarChart3 },
    { id: 'kline', name: 'K线图', icon: TrendingUp },
    { id: 'fundamental', name: '财务分析', icon: PieChart },
    { id: 'capital', name: '资金流向', icon: DollarSign },
  ]

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center py-32 space-y-4">
        <div className="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin" />
        <span className="text-gray-500">正在加载股票数据...</span>
      </div>
    )
  }

  if (isError) {
    return (
      <div className="flex flex-col items-center justify-center py-32 space-y-4 text-red-500">
        <AlertCircle size={48} />
        <span>数据加载失败</span>
        <button onClick={() => refetch()} className="px-4 py-2 bg-blue-600 text-white rounded-lg">
          重试
        </button>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* 返回按钮 */}
      <Link to="/screener" className="inline-flex items-center space-x-2 text-sm text-gray-500 hover:text-gray-700">
        <ArrowLeft size={16} />
        <span>返回筛选列表</span>
      </Link>

      {/* 头部信息卡 */}
      <div className="bg-white rounded-xl p-6 border border-gray-200">
        <div className="flex items-start justify-between flex-wrap gap-4">
          <div className="flex items-center space-x-4">
            <div className="w-14 h-14 bg-gradient-to-br from-blue-500 to-blue-700 rounded-xl flex items-center justify-center text-white font-bold text-xl">
              {symbol.slice(0, 2)}
            </div>
            <div>
              <div className="flex items-center space-x-3 flex-wrap gap-2">
                <h1 className="text-2xl font-bold text-gray-900">
                  {basic.name || tsCode} ({symbol})
                </h1>
                {basic.market && (
                  <span className="px-2 py-0.5 text-xs bg-gray-100 text-gray-600 rounded">{basic.market}</span>
                )}
                {basic.industry && (
                  <span className="px-2 py-0.5 text-xs bg-blue-100 text-blue-600 rounded">{basic.industry}</span>
                )}
              </div>
              <p className="text-sm text-gray-500 mt-1">
                {basic.area && `${basic.area} · `}
                {basic.list_date && `上市日期：${basic.list_date}`}
              </p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <button onClick={() => refetch()} className="p-2 rounded-lg hover:bg-gray-100">
              <RefreshCw size={18} className="text-gray-500" />
            </button>
            <button onClick={() => toast.success('已加入自选股')} className="p-2 rounded-lg hover:bg-gray-100">
              <Bookmark size={18} className="text-gray-500" />
            </button>
            <button onClick={() => { navigator.clipboard.writeText(window.location.href); toast.success('链接已复制') }} className="p-2 rounded-lg hover:bg-gray-100">
              <Share2 size={18} className="text-gray-500" />
            </button>
          </div>
        </div>

        {/* 价格行情 */}
        <div className="mt-6 grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
          <div className="col-span-2">
            <div className="text-sm text-gray-400 mb-1">最新价</div>
            <PriceTag val={quote.close ?? 0} pre={quote.pre_close} />
            <div className={cn('flex items-center mt-1 text-sm font-medium', isUp ? 'text-red-600' : 'text-green-600')}>
              {isUp ? <ArrowUpRight size={14} /> : <ArrowDownRight size={14} />}
              <span>{isUp ? '+' : ''}{(quote.change ?? 0).toFixed(2)}</span>
              <span className="ml-1">({isUp ? '+' : ''}{pct.toFixed(2)}%)</span>
            </div>
          </div>
          {[
            { label: '今开', val: (quote.open ?? 0).toFixed(2) },
            { label: '昨收', val: (quote.pre_close ?? 0).toFixed(2) },
            { label: '最高', val: (quote.high ?? 0).toFixed(2) },
            { label: '最低', val: (quote.low ?? 0).toFixed(2) },
          ].map(item => (
            <div key={item.label}>
              <div className="text-xs text-gray-400">{item.label}</div>
              <div className="text-lg font-semibold text-gray-900 mt-0.5">{item.val}</div>
            </div>
          ))}
          {[
            { label: '成交量(万手)', val: quote.vol ? (quote.vol / 10000).toFixed(1) : '-' },
            { label: '成交额(亿)', val: quote.amount ? (quote.amount / 100000000).toFixed(2) : '-' },
            { label: '市盈率', val: quote.pe ? quote.pe.toFixed(1) : '-' },
            { label: '市净率', val: quote.pb ? quote.pb.toFixed(2) : '-' },
          ].map(item => (
            <div key={item.label}>
              <div className="text-xs text-gray-400">{item.label}</div>
              <div className="text-lg font-semibold text-gray-900 mt-0.5">{item.val}</div>
            </div>
          ))}
        </div>
      </div>

      {/* 标签页 */}
      <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
        <div className="border-b border-gray-200">
          <nav className="flex space-x-0 px-4">
            {tabs.map(tab => {
              const Icon = tab.icon
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={cn(
                    'flex items-center space-x-2 px-5 py-4 text-sm font-medium border-b-2 transition-colors',
                    activeTab === tab.id
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700'
                  )}
                >
                  <Icon size={16} />
                  <span>{tab.name}</span>
                </button>
              )
            })}
          </nav>
        </div>

        <div className="p-6">
          {activeTab === 'overview' && (
            <div className="space-y-6">
              {/* 近30日价格走势 */}
              <div>
                <h3 className="text-base font-semibold text-gray-800 mb-4">近30日收盘价走势</h3>
                {chartData.length > 0 ? (
                  <ResponsiveContainer width="100%" height={240}>
                    <AreaChart data={chartData}>
                      <defs>
                        <linearGradient id="priceGrad" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor={isUp ? '#ef4444' : '#22c55e'} stopOpacity={0.3} />
                          <stop offset="95%" stopColor={isUp ? '#ef4444' : '#22c55e'} stopOpacity={0} />
                        </linearGradient>
                      </defs>
                      <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                      <XAxis dataKey="date" tick={{ fontSize: 11 }} interval={4} />
                      <YAxis domain={['auto', 'auto']} tick={{ fontSize: 11 }} />
                      <Tooltip formatter={(v: number) => [`${v.toFixed(2)}`, '收盘价']} />
                      <Area
                        type="monotone"
                        dataKey="close"
                        stroke={isUp ? '#ef4444' : '#22c55e'}
                        fill="url(#priceGrad)"
                        strokeWidth={2}
                        dot={false}
                      />
                    </AreaChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="flex items-center justify-center h-40 bg-gray-50 rounded-lg text-gray-400">
                    暂无K线数据
                  </div>
                )}
              </div>

              {/* 涨跌幅柱状图 */}
              {chartData.length > 0 && (
                <div>
                  <h3 className="text-base font-semibold text-gray-800 mb-4">每日涨跌幅</h3>
                  <ResponsiveContainer width="100%" height={120}>
                    <BarChart data={chartData}>
                      <XAxis dataKey="date" tick={{ fontSize: 10 }} interval={4} />
                      <YAxis tick={{ fontSize: 10 }} tickFormatter={v => `${v}%`} />
                      <Tooltip formatter={(v: number) => [`${v.toFixed(2)}%`, '涨跌幅']} />
                      <Bar dataKey="pct" radius={[2, 2, 0, 0]}>
                        {chartData.map((entry, idx) => (
                          <rect key={idx} fill={entry.pct >= 0 ? '#ef4444' : '#22c55e'} />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              )}
            </div>
          )}

          {activeTab === 'kline' && (
            <div className="space-y-4">
              <h3 className="text-base font-semibold text-gray-800">日K数据（近60日）</h3>
              {chartData.length > 0 ? (
                <ResponsiveContainer width="100%" height={360}>
                  <LineChart data={kline.slice(-60).map(k => ({
                    date: k.date.slice(4),
                    close: k.close,
                    open: k.open,
                    high: k.high,
                    low: k.low,
                  }))}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                    <XAxis dataKey="date" tick={{ fontSize: 10 }} interval={5} />
                    <YAxis domain={['auto', 'auto']} tick={{ fontSize: 10 }} />
                    <Tooltip />
                    <Line type="monotone" dataKey="high" stroke="#ef4444" dot={false} name="最高" strokeWidth={1} opacity={0.5} />
                    <Line type="monotone" dataKey="close" stroke={isUp ? '#ef4444' : '#22c55e'} dot={false} name="收盘" strokeWidth={2} />
                    <Line type="monotone" dataKey="low" stroke="#22c55e" dot={false} name="最低" strokeWidth={1} opacity={0.5} />
                  </LineChart>
                </ResponsiveContainer>
              ) : (
                <div className="flex items-center justify-center h-40 bg-gray-50 rounded-lg text-gray-400">
                  暂无K线数据
                </div>
              )}
              <p className="text-xs text-gray-400">注：受免费API限制，此处用折线图展示高低收盘价，红色=最高/收盘，绿色=最低</p>
            </div>
          )}

          {activeTab === 'fundamental' && (
            <div className="space-y-4">
              <h3 className="text-base font-semibold text-gray-800">基本面数据</h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {[
                  { label: '市盈率(TTM)', val: quote.pe ? quote.pe.toFixed(2) : '-', tip: 'PE < 15 低估' },
                  { label: '市净率', val: quote.pb ? quote.pb.toFixed(2) : '-', tip: 'PB < 1 可能低估' },
                  { label: '总市值', val: quote.total_mv ? `${(quote.total_mv / 10000).toFixed(0)}亿` : '-', tip: '' },
                  { label: '流通市值', val: quote.circ_mv ? `${(quote.circ_mv / 10000).toFixed(0)}亿` : '-', tip: '' },
                ].map(item => (
                  <div key={item.label} className="bg-gray-50 p-4 rounded-xl">
                    <div className="text-xs text-gray-400">{item.label}</div>
                    <div className="text-xl font-bold text-gray-900 mt-1">{item.val}</div>
                    {item.tip && <div className="text-xs text-gray-400 mt-1">{item.tip}</div>}
                  </div>
                ))}
              </div>
              <div className="p-4 bg-blue-50 border border-blue-200 rounded-xl text-sm text-blue-700">
                💡 财务报表数据（ROE、毛利率、负债率等）需要 Tushare 更高权限接口，当前版本展示基础市值/PE/PB 数据。
              </div>
            </div>
          )}

          {activeTab === 'capital' && (
            <div className="space-y-4">
              <h3 className="text-base font-semibold text-gray-800">成交量走势</h3>
              {chartData.length > 0 ? (
                <ResponsiveContainer width="100%" height={200}>
                  <BarChart data={chartData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                    <XAxis dataKey="date" tick={{ fontSize: 10 }} interval={4} />
                    <YAxis tick={{ fontSize: 10 }} tickFormatter={v => `${v}万`} />
                    <Tooltip formatter={(v: number) => [`${v}万手`, '成交量']} />
                    <Bar dataKey="vol" fill="#3b82f6" radius={[2, 2, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <div className="flex items-center justify-center h-40 bg-gray-50 rounded-lg text-gray-400">
                  暂无成交量数据
                </div>
              )}
              <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-xl text-sm text-yellow-700">
                💡 资金流向（主力/游资/散户分类）需要 Tushare VIP 权限接口，当前展示原始成交量数据。
              </div>
            </div>
          )}
        </div>
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

export default StockDetailPage
