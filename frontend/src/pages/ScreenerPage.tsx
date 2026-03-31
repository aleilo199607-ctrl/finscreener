import { useState } from 'react'
import { Filter, X, Save, Upload, Download } from 'lucide-react'
import { toast } from 'sonner'
import ScreeningPanel from '@/components/ScreeningPanel'
import StockTable from '@/components/StockTable'

const ScreenerPage = () => {
  const [conditions, setConditions] = useState<any[]>([])
  const [showPanel, setShowPanel] = useState(true)
  const [isLoading, setIsLoading] = useState(false)

  const handleAddCondition = (condition: any) => {
    setConditions([...conditions, { ...condition, id: Date.now().toString() }])
    toast.success('条件已添加')
  }

  const handleRemoveCondition = (id: string) => {
    setConditions(conditions.filter(c => c.id !== id))
    toast.info('条件已移除')
  }

  const handleClearConditions = () => {
    setConditions([])
    toast.info('所有条件已清除')
  }

  const handleSaveConditions = () => {
    if (conditions.length === 0) {
      toast.error('请先添加筛选条件')
      return
    }
    
    const name = prompt('请输入筛选条件名称：')
    if (name) {
      // 这里应该调用API保存条件
      toast.success(`"${name}" 已保存`)
    }
  }

  const handleLoadConditions = () => {
    toast.info('加载条件功能开发中...')
  }

  const handleScreening = () => {
    if (conditions.length === 0) {
      toast.error('请先添加筛选条件')
      return
    }
    
    setIsLoading(true)
    // 模拟筛选过程
    setTimeout(() => {
      setIsLoading(false)
      toast.success(`筛选完成，找到 152 只符合条件的股票`)
    }, 1000)
  }

  return (
    <div className="space-y-6">
      {/* 页面标题 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">智能股票筛选器</h1>
          <p className="text-gray-600 mt-2">通过多维度条件筛选A股市场，发现投资机会</p>
        </div>
        <div className="flex items-center space-x-4">
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
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-xl p-4 border border-gray-200">
          <div className="text-sm text-gray-500">符合条件的股票</div>
          <div className="text-2xl font-bold text-gray-900 mt-1">152</div>
          <div className="text-xs text-green-600 mt-1">较昨日 +12</div>
        </div>
        <div className="bg-white rounded-xl p-4 border border-gray-200">
          <div className="text-sm text-gray-500">平均涨幅</div>
          <div className="text-2xl font-bold text-green-600 mt-1">+3.2%</div>
          <div className="text-xs text-gray-500 mt-1">跑赢大盘 1.5%</div>
        </div>
        <div className="bg-white rounded-xl p-4 border border-gray-200">
          <div className="text-sm text-gray-500">平均市盈率</div>
          <div className="text-2xl font-bold text-gray-900 mt-1">28.5</div>
          <div className="text-xs text-gray-500 mt-1">行业平均 32.1</div>
        </div>
        <div className="bg-white rounded-xl p-4 border border-gray-200">
          <div className="text-sm text-gray-500">筛选条件数</div>
          <div className="text-2xl font-bold text-gray-900 mt-1">{conditions.length}</div>
          <div className="text-xs text-gray-500 mt-1">
            {conditions.length > 0 ? '已应用' : '未设置'}
          </div>
        </div>
      </div>

      <div className="flex flex-col lg:flex-row gap-6">
        {/* 筛选面板 */}
        {showPanel && (
          <div className="lg:w-1/4">
            <ScreeningPanel
              onApplyFilters={handleScreening}
              isLoading={isLoading}
            />
          </div>
        )}

        {/* 主要内容 */}
        <div className={showPanel ? "lg:w-3/4" : "w-full"}>
          {/* 条件标签 */}
          {conditions.length > 0 && (
            <div className="mb-6">
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-lg font-medium text-gray-900">已应用的筛选条件</h3>
                <div className="flex items-center space-x-2">
                  <button
                    onClick={handleSaveConditions}
                    className="flex items-center space-x-1 px-3 py-1.5 text-sm bg-blue-50 text-blue-600 rounded-lg hover:bg-blue-100"
                  >
                    <Save size={14} />
                    <span>保存条件</span>
                  </button>
                  <button
                    onClick={handleLoadConditions}
                    className="flex items-center space-x-1 px-3 py-1.5 text-sm bg-gray-50 text-gray-600 rounded-lg hover:bg-gray-100"
                  >
                    <Upload size={14} />
                    <span>加载条件</span>
                  </button>
                  <button
                    onClick={handleClearConditions}
                    className="flex items-center space-x-1 px-3 py-1.5 text-sm bg-red-50 text-red-600 rounded-lg hover:bg-red-100"
                  >
                    <X size={14} />
                    <span>清空条件</span>
                  </button>
                </div>
              </div>
              <div className="flex flex-wrap gap-2">
                {conditions.map((condition) => (
                  <div
                    key={condition.id}
                    className="flex items-center space-x-2 bg-gray-50 px-3 py-2 rounded-lg"
                  >
                    <span className="text-sm text-gray-700">
                      {condition.label}: {condition.value}
                      {condition.unit ? condition.unit : ''}
                    </span>
                    <button
                      onClick={() => handleRemoveCondition(condition.id)}
                      className="text-gray-400 hover:text-gray-600"
                    >
                      <X size={14} />
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* 股票表格 */}
          <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
            <div className="p-6 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-xl font-semibold text-gray-900">筛选结果</h2>
                  <p className="text-gray-600 text-sm mt-1">
                    实时更新，点击表头可排序
                  </p>
                </div>
                <button
                  onClick={handleScreening}
                  disabled={conditions.length === 0 || isLoading}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isLoading ? '筛选中...' : '开始筛选'}
                </button>
              </div>
            </div>
            
            <StockTable stocks={[]} />
          </div>

          {/* 导出功能 */}
          <div className="mt-6 flex justify-end">
            <button className="flex items-center space-x-2 px-4 py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50">
              <Download size={18} />
              <span>导出筛选结果</span>
            </button>
          </div>

          {/* 免责声明 */}
          <div className="mt-8 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
            <p className="text-sm text-yellow-800">
              ⚠️ <strong>重要提示：</strong>本筛选器所有信息仅供学习参考，不构成任何投资建议。
              股市有风险，投资需谨慎。数据来源：Tushare Pro API，更新时间：实时。
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default ScreenerPage