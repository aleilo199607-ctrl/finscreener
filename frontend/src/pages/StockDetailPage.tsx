import { useState } from 'react'
import { useParams } from 'react-router-dom'
import { 
  ArrowUpRight, ArrowDownRight, TrendingUp, TrendingDown,
  BarChart3, PieChart, DollarSign, MessageSquare, Download,
  Bookmark, Share2, RefreshCw, AlertCircle
} from 'lucide-react'
import { toast } from 'sonner'
import { cn, formatCurrency, formatPercentage, getChangeColor } from '@/utils/cn'

const StockDetailPage = () => {
  const { code } = useParams<{ code: string }>()
  const [activeTab, setActiveTab] = useState('overview')
  const [isLoading, setIsLoading] = useState(false)

  // 模拟股票数据
  const stockData = {
    ts_code: code || '000001.SZ',
    symbol: code?.split('.')[0] || '000001',
    name: '平安银行',
    area: '广东',
    industry: '银行',
    market: '深圳主板',
    list_date: '19910403',
    
    quote: {
      open: 10.25,
      high: 10.45,
      low: 10.15,
      close: 10.35,
      pre_close: 10.20,
      change: 0.15,
      pct_chg: 1.47,
      vol: 1254300,
      amount: 1295000,
      turnover_rate: 0.65,
      pe: 8.5,
      pb: 0.85,
      total_mv: 200000000,
      circ_mv: 150000000
    },
    
    financial: {
      roe: 12.5,
      gross_margin: 35.6,
      net_margin: 15.3,
      debt_ratio: 45.3,
      revenue_growth: 8.7,
      profit_growth: 12.1,
      eps: 1.25,
      bvps: 10.2
    },
    
    technical: {
      macd: { dif: 0.15, dea: 0.12, histogram: 0.03 },
      kdj: { k: 65.2, d: 58.7, j: 78.1 },
      rsi: { rsi6: 62.5, rsi12: 58.3, rsi24: 52.1 },
      ma: { ma5: 10.25, ma10: 10.18, ma20: 10.05, ma60: 9.85 }
    },
    
    summary: {
      technical_summary: '技术指标显示股价处于上升通道，MACD金叉，KDJ指标偏强，短期有望继续上涨。',
      fundamental_summary: '公司基本面稳健，ROE持续提升，盈利能力较强，估值相对合理。',
      capital_summary: '主力资金连续5日净流入，机构持仓增加，市场关注度提升。',
      news_summary: '近期无重大利空消息，行业政策环境良好，公司经营正常。',
      overall_summary: '综合来看，该股票具备较好的投资价值，建议关注回调机会。',
      sentiment: 'bullish' as const,
      confidence: 0.78
    }
  }

  const handleRefresh = () => {
    setIsLoading(true)
    toast.info('正在刷新数据...')
    setTimeout(() => {
      setIsLoading(false)
      toast.success('数据已刷新')
    }, 1000)
  }

  const handleBookmark = () => {
    toast.success('已添加到自选股')
  }

  const handleShare = () => {
    navigator.clipboard.writeText(window.location.href)
    toast.success('链接已复制到剪贴板')
  }

  const tabs = [
    { id: 'overview', name: '概览', icon: BarChart3 },
    { id: 'technical', name: '技术分析', icon: TrendingUp },
    { id: 'fundamental', name: '财务分析', icon: PieChart },
    { id: 'capital', name: '资金流向', icon: DollarSign },
    { id: 'news', name: '新闻消息', icon: MessageSquare },
  ]

  return (
    <div className="space-y-6">
      {/* 股票头部信息 */}
      <div className="bg-white rounded-xl p-6 border border-gray-200">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center space-x-4">
              <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl flex items-center justify-center">
                <span className="text-2xl font-bold text-white">
                  {stockData.symbol.substring(0, 2)}
                </span>
              </div>
              <div>
                <div className="flex items-center space-x-3">
                  <h1 className="text-3xl font-bold text-gray-900">
                    {stockData.name} ({stockData.symbol})
                  </h1>
                  <span className="px-2 py-1 text-xs font-medium bg-gray-100 text-gray-600 rounded">
                    {stockData.market}
                  </span>
                  <span className="px-2 py-1 text-xs font-medium bg-blue-100 text-blue-600 rounded">
                    {stockData.industry}
                  </span>
                </div>
                <p className="text-gray-600 mt-1">{stockData.area} • 上市时间: {stockData.list_date}</p>
              </div>
            </div>
          </div>

          <div className="flex items-center space-x-3">
            <button
              onClick={handleRefresh}
              disabled={isLoading}
              className={cn(
                "p-2 rounded-lg hover:bg-gray-100",
                isLoading && "animate-spin"
              )}
            >
              <RefreshCw size={20} className="text-gray-600" />
            </button>
            <button
              onClick={handleBookmark}
              className="p-2 rounded-lg hover:bg-gray-100"
            >
              <Bookmark size={20} className="text-gray-600" />
            </button>
            <button
              onClick={handleShare}
              className="p-2 rounded-lg hover:bg-gray-100"
            >
              <Share2 size={20} className="text-gray-600" />
            </button>
            <button className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
              <Download size={18} />
              <span>导出报告</span>
            </button>
          </div>
        </div>

        {/* 价格信息 */}
        <div className="mt-8 grid grid-cols-2 md:grid-cols-4 gap-6">
          <div>
            <div className="text-sm text-gray-500">当前价格</div>
            <div className="text-3xl font-bold text-gray-900 mt-1">
              {stockData.quote.close.toFixed(2)}
            </div>
            <div className={cn(
              "flex items-center mt-1",
              getChangeColor(stockData.quote.pct_chg)
            )}>
              {stockData.quote.pct_chg > 0 ? (
                <ArrowUpRight size={16} className="mr-1" />
              ) : (
                <ArrowDownRight size={16} className="mr-1" />
              )}
              <span className="font-medium">
                {formatPercentage(stockData.quote.pct_chg)}
              </span>
              <span className="ml-2 text-sm">
                {stockData.quote.change.toFixed(2)}
              </span>
            </div>
          </div>

          <div>
            <div className="text-sm text-gray-500">今日区间</div>
            <div className="text-xl font-bold text-gray-900 mt-1">
              {stockData.quote.low.toFixed(2)} - {stockData.quote.high.toFixed(2)}
            </div>
            <div className="text-sm text-gray-500 mt-1">
              昨收: {stockData.quote.pre_close.toFixed(2)}
            </div>
          </div>

          <div>
            <div className="text-sm text-gray-500">成交量</div>
            <div className="text-xl font-bold text-gray-900 mt-1">
              {formatCurrency(stockData.quote.vol)}
            </div>
            <div className="text-sm text-gray-500 mt-1">
              成交额: {formatCurrency(stockData.quote.amount)}
            </div>
          </div>

          <div>
            <div className="text-sm text-gray-500">换手率</div>
            <div className="text-xl font-bold text-gray-900 mt-1">
              {stockData.quote.turnover_rate.toFixed(2)}%
            </div>
            <div className="text-sm text-gray-500 mt-1">
              市盈率: {stockData.quote.pe.toFixed(1)}
            </div>
          </div>
        </div>
      </div>

      {/* AI摘要卡片 */}
      <div className={cn(
        "rounded-xl p-6 border",
        stockData.summary.sentiment === 'bullish' 
          ? "bg-green-50 border-green-200" 
          : stockData.summary.sentiment === 'bearish'
          ? "bg-red-50 border-red-200"
          : "bg-blue-50 border-blue-200"
      )}>
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-3">
            <div className={cn(
              "w-10 h-10 rounded-full flex items-center justify-center",
              stockData.summary.sentiment === 'bullish' 
                ? "bg-green-100" 
                : stockData.summary.sentiment === 'bearish'
                ? "bg-red-100"
                : "bg-blue-100"
            )}>
              {stockData.summary.sentiment === 'bullish' ? (
                <TrendingUp className="w-5 h-5 text-green-600" />
              ) : stockData.summary.sentiment === 'bearish' ? (
                <TrendingDown className="w-5 h-5 text-red-600" />
              ) : (
                <BarChart3 className="w-5 h-5 text-blue-600" />
              )}
            </div>
            <div>
              <h3 className="font-semibold text-gray-900">AI智能分析</h3>
              <p className="text-sm text-gray-600">
                {stockData.summary.sentiment === 'bullish' ? '看涨' : 
                 stockData.summary.sentiment === 'bearish' ? '看跌' : '中性'}
                · 置信度: {(stockData.summary.confidence * 100).toFixed(0)}%
              </p>
            </div>
          </div>
          <div className="text-xs text-gray-500">更新时间: 刚刚</div>
        </div>
        <p className="text-gray-700">{stockData.summary.overall_summary}</p>
        <div className="mt-4 text-sm text-gray-600">
          <p>💡 <strong>提示：</strong>本分析由AI生成，仅供参考，不构成投资建议。</p>
        </div>
      </div>

      {/* 标签页导航 */}
      <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
        <div className="border-b border-gray-200">
          <nav className="flex space-x-1 px-6" aria-label="Tabs">
            {tabs.map((tab) => {
              const Icon = tab.icon
              const isActive = activeTab === tab.id
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={cn(
                    "flex items-center space-x-2 px-4 py-3 text-sm font-medium border-b-2 transition-colors",
                    isActive
                      ? "border-blue-500 text-blue-600"
                      : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
                  )}
                >
                  <Icon size={18} />
                  <span>{tab.name}</span>
                </button>
              )
            })}
          </nav>
        </div>

        {/* 标签页内容 */}
        <div className="p-6">
          {activeTab === 'overview' && (
            <div className="space-y-6">
              <div>
                <h4 className="text-lg font-semibold text-gray-900 mb-4">技术指标</h4>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <div className="text-sm text-gray-500">MACD</div>
                    <div className="text-xl font-bold text-gray-900 mt-1">
                      DIF: {stockData.technical.macd.dif.toFixed(3)}
                    </div>
                    <div className={cn(
                      "text-sm mt-1",
                      stockData.technical.macd.histogram > 0 ? "text-green-600" : "text-red-600"
                    )}>
                      柱状图: {stockData.technical.macd.histogram.toFixed(3)}
                    </div>
                  </div>
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <div className="text-sm text-gray-500">KDJ</div>
                    <div className="text-xl font-bold text-gray-900 mt-1">
                      K: {stockData.technical.kdj.k.toFixed(1)}
                    </div>
                    <div className="text-sm text-gray-600 mt-1">
                      J: {stockData.technical.kdj.j.toFixed(1)}
                    </div>
                  </div>
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <div className="text-sm text-gray-500">RSI</div>
                    <div className="text-xl font-bold text-gray-900 mt-1">
                      RSI6: {stockData.technical.rsi.rsi6.toFixed(1)}
                    </div>
                    <div className="text-sm text-gray-600 mt-1">
                      RSI12: {stockData.technical.rsi.rsi12.toFixed(1)}
                    </div>
                  </div>
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <div className="text-sm text-gray-500">均线系统</div>
                    <div className="text-xl font-bold text-gray-900 mt-1">
                      MA5: {stockData.technical.ma.ma5.toFixed(2)}
                    </div>
                    <div className="text-sm text-gray-600 mt-1">
                      现价/MA5: {(stockData.quote.close / stockData.technical.ma.ma5 * 100 - 100).toFixed(2)}%
                    </div>
                  </div>
                </div>
              </div>

              <div>
                <h4 className="text-lg font-semibold text-gray-900 mb-4">财务指标</h4>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <div className="text-sm text-gray-500">ROE</div>
                    <div className="text-xl font-bold text-gray-900 mt-1">
                      {stockData.financial.roe.toFixed(2)}%
                    </div>
                    <div className="text-sm text-green-600 mt-1">行业领先</div>
                  </div>
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <div className="text-sm text-gray-500">毛利率</div>
                    <div className="text-xl font-bold text-gray-900 mt-1">
                      {stockData.financial.gross_margin.toFixed(2)}%
                    </div>
                    <div className="text-sm text-gray-600 mt-1">较稳定</div>
                  </div>
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <div className="text-sm text-gray-500">资产负债率</div>
                    <div className="text-xl font-bold text-gray-900 mt-1">
                      {stockData.financial.debt_ratio.toFixed(2)}%
                    </div>
                    <div className="text-sm text-gray-600 mt-1">合理水平</div>
                  </div>
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <div className="text-sm text-gray-500">营收增长</div>
                    <div className="text-xl font-bold text-gray-900 mt-1">
                      {stockData.financial.revenue_growth.toFixed(2)}%
                    </div>
                    <div className="text-sm text-green-600 mt-1">正增长</div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'technical' && (
            <div className="space-y-6">
              <div className="text-center py-12 bg-gray-50 rounded-lg">
                <BarChart3 className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                <h4 className="text-lg font-semibold text-gray-900">K线图组件</h4>
                <p className="text-gray-600 mt-2">集成Recharts库实现交互式K线图</p>
                <p className="text-sm text-gray-500 mt-1">支持日K、周K、月K，技术指标叠加</p>
              </div>
              
              <div>
                <h4 className="text-lg font-semibold text-gray-900 mb-4">技术分析详情</h4>
                <p className="text-gray-700">{stockData.summary.technical_summary}</p>
              </div>
            </div>
          )}

          {activeTab === 'fundamental' && (
            <div className="space-y-6">
              <div className="text-center py-12 bg-gray-50 rounded-lg">
                <PieChart className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                <h4 className="text-lg font-semibold text-gray-900">财务图表组件</h4>
                <p className="text-gray-600 mt-2">财务指标对比分析和趋势图表</p>
                <p className="text-sm text-gray-500 mt-1">盈利能力、成长能力、偿债能力等多维度分析</p>
              </div>
              
              <div>
                <h4 className="text-lg font-semibold text-gray-900 mb-4">基本面分析详情</h4>
                <p className="text-gray-700">{stockData.summary.fundamental_summary}</p>
              </div>
            </div>
          )}

          {activeTab === 'capital' && (
            <div className="space-y-6">
              <div className="text-center py-12 bg-gray-50 rounded-lg">
                <DollarSign className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                <h4 className="text-lg font-semibold text-gray-900">资金流向图</h4>
                <p className="text-gray-600 mt-2">主力资金、散户资金、机构资金流向分析</p>
                <p className="text-sm text-gray-500 mt-1">实时监控资金动向，识别主力意图</p>
              </div>
              
              <div>
                <h4 className="text-lg font-semibold text-gray-900 mb-4">资金面分析详情</h4>
                <p className="text-gray-700">{stockData.summary.capital_summary}</p>
              </div>
            </div>
          )}

          {activeTab === 'news' && (
            <div className="space-y-6">
              <div className="text-center py-12 bg-gray-50 rounded-lg">
                <MessageSquare className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                <h4 className="text-lg font-semibold text-gray-900">新闻消息聚合</h4>
                <p className="text-gray-600 mt-2">整合财经新闻、公告、研报等信息源</p>
                <p className="text-sm text-gray-500 mt-1">AI摘要生成，情感分析，影响评估</p>
              </div>
              
              <div>
                <h4 className="text-lg font-semibold text-gray-900 mb-4">消息面分析详情</h4>
                <p className="text-gray-700">{stockData.summary.news_summary}</p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* 免责声明 */}
      <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
        <div className="flex items-start space-x-3">
          <AlertCircle className="w-5 h-5 text-yellow-600 flex-shrink-0 mt-0.5" />
          <div>
            <p className="text-sm text-yellow-800">
              <strong>重要声明：</strong>本页面所有信息仅供学习参考，不构成任何投资建议。
              股市有风险，投资需谨慎。数据来源：Tushare Pro API，AI分析由第三方模型生成。
              投资者应独立判断，风险自担。
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default StockDetailPage