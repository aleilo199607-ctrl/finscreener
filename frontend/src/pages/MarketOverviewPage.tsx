import { useQuery } from '@tanstack/react-query'
import { RefreshCw, TrendingUp, TrendingDown, Minus, AlertCircle } from 'lucide-react'
import { cn } from '@/utils/cn'
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'

const API_BASE = import.meta.env.VITE_API_URL?.replace('/api', '') || 'https://finscreener-production.up.railway.app'

interface IndexItem {
  name: string
  code: string
  close: number
  pct_chg: number
  vol: number
  amount: number
}

interface MarketStats {
  up_count: number
  down_count: number
  flat_count: number
  total: number
  limit_up: number
  limit_down: number
  up_ratio: number
}

interface OverviewData {
  trade_date: string
  indices: IndexItem[]
  market_stats: MarketStats
  data_source: string
}

function fetchOverview(): Promise<OverviewData> {
  return fetch(`${API_BASE}/api/market/overview`)
    .then(r => r.json())
    .then(d => d.data)
}

function IndexCard({ item }: { item: IndexItem }) {
  const up = item.pct_chg > 0
  const zero = item.pct_chg === 0
  return (
    <div className={cn(
      'bg-white rounded-xl p-5 border-l-4 shadow-sm',
      up ? 'border-red-500' : zero ? 'border-gray-300' : 'border-green-500'
    )}>
      <div className="flex items-center justify-between mb-2">
        <span className="text-sm text-gray-500">{item.name}</span>
        <span className={cn(
          'flex items-center space-x-1 text-sm font-semibold',
          up ? 'text-red-600' : zero ? 'text-gray-500' : 'text-green-600'
        )}>
          {up ? <TrendingUp size={14} /> : zero ? <Minus size={14} /> : <TrendingDown size={14} />}
          <span>{up ? '+' : ''}{item.pct_chg.toFixed(2)}%</span>
        </span>
      </div>
      <div className={cn(
        'text-2xl font-bold',
        up ? 'text-red-600' : zero ? 'text-gray-800' : 'text-green-600'
      )}>
        {item.close.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
      </div>
      <div className="mt-2 text-xs text-gray-400">
        成交量 {(item.vol / 100000000).toFixed(2)}亿手 &nbsp;|&nbsp; 成交额 {(item.amount / 100000000).toFixed(0)}亿
      </div>
    </div>
  )
}

// 涨跌家数比例条
function UpDownBar({ stats }: { stats: MarketStats }) {
  const upPct = stats.up_ratio
  const downPct = Math.round((stats.down_count / stats.total) * 100)
  const flatPct = 100 - upPct - downPct
  return (
    <div className="space-y-3">
      <div className="flex justify-between text-sm text-gray-600">
        <span className="text-red-500 font-medium">▲ 上涨 {stats.up_count.toLocaleString()}</span>
        <span className="text-gray-400">→ 平盘 {stats.flat_count.toLocaleString()}</span>
        <span className="text-green-500 font-medium">▼ 下跌 {stats.down_count.toLocaleString()}</span>
      </div>
      <div className="flex h-4 rounded-full overflow-hidden">
        <div className="bg-red-500 transition-all" style={{ width: `${upPct}%` }} />
        <div className="bg-gray-200 transition-all" style={{ width: `${flatPct}%` }} />
        <div className="bg-green-500 transition-all" style={{ width: `${downPct}%` }} />
      </div>
      <div className="flex justify-between text-xs text-gray-400">
        <span>涨停 <strong className="text-red-500">{stats.limit_up}</strong></span>
        <span>共 {stats.total.toLocaleString()} 只</span>
        <span>跌停 <strong className="text-green-500">{stats.limit_down}</strong></span>
      </div>
    </div>
  )
}

// 模拟市场情绪走势图（固定模拟，仅作展示）
const MOOD_DATA = [
  { time: '09:30', mood: 52 }, { time: '10:00', mood: 55 }, { time: '10:30', mood: 51 },
  { time: '11:00', mood: 58 }, { time: '11:30', mood: 62 }, { time: '13:00', mood: 60 },
  { time: '13:30', mood: 57 }, { time: '14:00', mood: 63 }, { time: '14:30', mood: 68 },
  { time: '15:00', mood: 65 },
]

export default function MarketOverviewPage() {
  const { data, isLoading, isError, refetch } = useQuery<OverviewData>({
    queryKey: ['market-overview'],
    queryFn: fetchOverview,
    staleTime: 3 * 60 * 1000,
  })

  return (
    <div className="space-y-6">
      {/* 页头 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">市场概况</h1>
          <p className="text-gray-500 mt-1 text-sm">
            {data?.trade_date ? `交易日 ${data.trade_date}` : '实时行情'}
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
          {/* 主要指数卡片 */}
          <div>
            <h2 className="text-lg font-semibold text-gray-800 mb-3">主要指数</h2>
            <div className="grid grid-cols-2 lg:grid-cols-5 gap-4">
              {data.indices.map(idx => (
                <IndexCard key={idx.code || idx.name} item={idx} />
              ))}
            </div>
          </div>

          {/* 市场宽度 */}
          <div className="bg-white rounded-xl border border-gray-200 p-6">
            <h2 className="text-lg font-semibold text-gray-800 mb-4">市场宽度</h2>
            <UpDownBar stats={data.market_stats} />
          </div>

          {/* 两列：情绪走势 + 统计卡片 */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* 情绪走势图 */}
            <div className="bg-white rounded-xl border border-gray-200 p-6">
              <h2 className="text-lg font-semibold text-gray-800 mb-1">市场情绪走势</h2>
              <p className="text-xs text-gray-400 mb-4">上涨家数占比趋势（%）</p>
              <ResponsiveContainer width="100%" height={200}>
                <AreaChart data={MOOD_DATA}>
                  <defs>
                    <linearGradient id="moodGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
                      <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <XAxis dataKey="time" tick={{ fontSize: 11 }} />
                  <YAxis domain={[40, 75]} tick={{ fontSize: 11 }} />
                  <Tooltip formatter={(v: number) => [`${v}%`, '情绪指数']} />
                  <Area type="monotone" dataKey="mood" stroke="#3b82f6" fill="url(#moodGrad)" strokeWidth={2} />
                </AreaChart>
              </ResponsiveContainer>
            </div>

            {/* 统计卡片 */}
            <div className="grid grid-cols-2 gap-4 content-start">
              {[
                { label: '上涨家数', val: data.market_stats.up_count.toLocaleString(), color: 'text-red-500', bg: 'bg-red-50' },
                { label: '下跌家数', val: data.market_stats.down_count.toLocaleString(), color: 'text-green-500', bg: 'bg-green-50' },
                { label: '涨停家数', val: data.market_stats.limit_up.toString(), color: 'text-red-600', bg: 'bg-red-50' },
                { label: '跌停家数', val: data.market_stats.limit_down.toString(), color: 'text-green-600', bg: 'bg-green-50' },
                { label: '平盘家数', val: data.market_stats.flat_count.toLocaleString(), color: 'text-gray-500', bg: 'bg-gray-50' },
                { label: '上涨比例', val: `${data.market_stats.up_ratio}%`, color: 'text-blue-600', bg: 'bg-blue-50' },
              ].map(item => (
                <div key={item.label} className={cn('rounded-xl p-4', item.bg)}>
                  <div className="text-xs text-gray-500 mb-1">{item.label}</div>
                  <div className={cn('text-2xl font-bold', item.color)}>{item.val}</div>
                </div>
              ))}
            </div>
          </div>
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
