import { Link } from 'react-router-dom'
import { Home, Search, BarChart3 } from 'lucide-react'

const NotFoundPage = () => {
  return (
    <div className="min-h-[60vh] flex items-center justify-center px-4">
      <div className="text-center max-w-md">
        <div className="w-20 h-20 mx-auto bg-gradient-to-br from-gray-200 to-gray-300 rounded-2xl flex items-center justify-center mb-6">
          <BarChart3 className="w-10 h-10 text-gray-500" />
        </div>
        
        <h1 className="text-6xl font-bold text-gray-900 mb-4">404</h1>
        <h2 className="text-2xl font-semibold text-gray-800 mb-4">页面未找到</h2>
        
        <p className="text-gray-600 mb-8">
          抱歉，您访问的页面不存在或已被移除。
          可能是股票代码错误，或者页面正在维护中。
        </p>
        
        <div className="space-y-4">
          <Link
            to="/"
            className="inline-flex items-center justify-center space-x-2 w-full px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <Home size={20} />
            <span>返回首页</span>
          </Link>
          
          <Link
            to="/screener"
            className="inline-flex items-center justify-center space-x-2 w-full px-6 py-3 bg-white border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <Search size={20} />
            <span>去股票筛选</span>
          </Link>
        </div>
        
        <div className="mt-8 pt-6 border-t border-gray-200">
          <p className="text-sm text-gray-500 mb-2">热门股票推荐：</p>
          <div className="flex flex-wrap justify-center gap-2">
            {[
              { code: '000001', name: '平安银行' },
              { code: '600519', name: '贵州茅台' },
              { code: '000858', name: '五粮液' },
              { code: '300750', name: '宁德时代' },
            ].map((stock) => (
              <Link
                key={stock.code}
                to={`/stock/${stock.code}`}
                className="inline-block px-3 py-1.5 text-sm bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
              >
                {stock.code} {stock.name}
              </Link>
            ))}
          </div>
        </div>
        
        <div className="mt-8 text-xs text-gray-400">
          <p>如果问题持续存在，请联系技术支持或查看帮助文档。</p>
        </div>
      </div>
    </div>
  )
}

export default NotFoundPage