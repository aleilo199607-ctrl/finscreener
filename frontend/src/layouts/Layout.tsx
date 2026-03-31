import { Outlet } from 'react-router-dom'
import { useState } from 'react'
import { 
  Menu, X, BarChart3, Filter, Search, Bell, 
  User, Settings, Home, TrendingUp, PieChart
} from 'lucide-react'
import { cn } from '@/utils/cn'

const Layout = () => {
  const [sidebarOpen, setSidebarOpen] = useState(false)

  const navigation = [
    { name: '首页', href: '/', icon: Home },
    { name: '股票筛选', href: '/screener', icon: Filter },
    { name: '热门股票', href: '/market/hot', icon: TrendingUp },
    { name: '市场概况', href: '/market/overview', icon: BarChart3 },
    { name: '行业分析', href: '/industries', icon: PieChart },
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      {/* 导航栏 */}
      <nav className="sticky top-0 z-50 bg-white/80 backdrop-blur-lg border-b border-gray-200">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Logo和品牌 */}
            <div className="flex items-center space-x-4">
              <button
                onClick={() => setSidebarOpen(!sidebarOpen)}
                className="p-2 rounded-lg hover:bg-gray-100 lg:hidden"
              >
                {sidebarOpen ? <X size={20} /> : <Menu size={20} />}
              </button>
              
              <div className="flex items-center space-x-2">
                <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg flex items-center justify-center">
                  <BarChart3 className="w-5 h-5 text-white" />
                </div>
                <div>
                  <h1 className="text-xl font-bold text-gray-900">FinScreener</h1>
                  <p className="text-xs text-gray-500">智能股票筛选工具</p>
                </div>
              </div>
            </div>

            {/* 搜索框 */}
            <div className="hidden md:flex flex-1 max-w-md mx-8">
              <div className="relative w-full">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Search className="h-5 w-5 text-gray-400" />
                </div>
                <input
                  type="text"
                  className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="搜索股票代码或名称..."
                />
              </div>
            </div>

            {/* 右侧按钮 */}
            <div className="flex items-center space-x-4">
              <button className="p-2 rounded-lg hover:bg-gray-100 relative">
                <Bell size={20} className="text-gray-600" />
                <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
              </button>
              <button className="p-2 rounded-lg hover:bg-gray-100">
                <Settings size={20} className="text-gray-600" />
              </button>
              <button className="flex items-center space-x-2 p-2 rounded-lg hover:bg-gray-100">
                <User size={20} className="text-gray-600" />
                <span className="hidden sm:inline text-sm font-medium text-gray-700">登录</span>
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* 侧边栏（移动端） */}
      <div className={cn(
        "fixed inset-y-0 left-0 z-40 w-64 bg-white transform transition-transform duration-200 ease-in-out lg:hidden",
        sidebarOpen ? "translate-x-0" : "-translate-x-full"
      )}>
        <div className="h-full flex flex-col">
          <div className="flex items-center justify-between p-4 border-b">
            <h2 className="text-lg font-semibold text-gray-900">导航</h2>
            <button
              onClick={() => setSidebarOpen(false)}
              className="p-2 rounded-lg hover:bg-gray-100"
            >
              <X size={20} />
            </button>
          </div>
          <nav className="flex-1 p-4 space-y-2">
            {navigation.map((item) => {
              const Icon = item.icon
              return (
                <a
                  key={item.name}
                  href={item.href}
                  className="flex items-center space-x-3 px-3 py-2 rounded-lg hover:bg-gray-100 text-gray-700 hover:text-gray-900"
                >
                  <Icon size={20} />
                  <span>{item.name}</span>
                </a>
              )
            })}
          </nav>
        </div>
      </div>

      {/* 侧边栏（桌面端） */}
      <div className="hidden lg:flex fixed inset-y-16 left-0 z-40 w-64 bg-white border-r border-gray-200">
        <div className="flex flex-col w-full">
          <div className="p-4 border-b">
            <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wider">市场分类</h2>
          </div>
          <nav className="flex-1 p-4 space-y-1">
            {[
              { name: '全部股票', count: 4500 },
              { name: '主板', count: 2200 },
              { name: '创业板', count: 1200 },
              { name: '科创板', count: 800 },
              { name: '北交所', count: 300 },
            ].map((market) => (
              <a
                key={market.name}
                href={`/market/${market.name}`}
                className="flex items-center justify-between px-3 py-2 rounded-lg hover:bg-gray-100 text-gray-700 hover:text-gray-900 group"
              >
                <span>{market.name}</span>
                <span className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded">
                  {market.count}
                </span>
              </a>
            ))}
          </nav>

          <div className="p-4 border-t">
            <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wider">热门行业</h2>
            <div className="mt-2 space-y-1">
              {['电子', '医药生物', '计算机', '新能源', '消费'].map((industry) => (
                <a
                  key={industry}
                  href={`/industry/${industry}`}
                  className="block px-3 py-1.5 text-sm rounded hover:bg-gray-100 text-gray-600 hover:text-gray-900"
                >
                  {industry}
                </a>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* 主要内容 */}
      <main className={cn(
        "pt-6 pb-12",
        "lg:pl-64" // 桌面端添加左边距
      )}>
        <div className="container mx-auto px-4 sm:px-6 lg:px-8">
          {/* 面包屑导航（可选） */}
          <div className="mb-6">
            <nav className="flex" aria-label="Breadcrumb">
              <ol className="inline-flex items-center space-x-1 md:space-x-3">
                <li className="inline-flex items-center">
                  <a href="/" className="inline-flex items-center text-sm font-medium text-gray-500 hover:text-gray-700">
                    <Home className="w-4 h-4 mr-2" />
                    首页
                  </a>
                </li>
                <li>
                  <div className="flex items-center">
                    <span className="mx-2 text-gray-400">/</span>
                    <a href="/screener" className="ml-1 text-sm font-medium text-gray-500 hover:text-gray-700 md:ml-2">
                      股票筛选
                    </a>
                  </div>
                </li>
              </ol>
            </nav>
          </div>

          {/* 页面内容 */}
          <Outlet />
        </div>
      </main>

      {/* 遮罩层（移动端侧边栏打开时） */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-30 bg-black bg-opacity-50 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}
    </div>
  )
}

export default Layout