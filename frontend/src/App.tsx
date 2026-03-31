import { Routes, Route } from 'react-router-dom'
import { Toaster } from 'sonner'
import { QueryClientProvider } from '@tanstack/react-query'
import Layout from './layouts/Layout'
import ScreenerPage from './pages/ScreenerPage'
import StockDetailPage from './pages/StockDetailPage'
import HotStocksPage from './pages/HotStocksPage'
import MarketOverviewPage from './pages/MarketOverviewPage'
import IndustriesPage from './pages/IndustriesPage'
import NotFoundPage from './pages/NotFoundPage'
import { queryClient } from './services/api'

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <div className="min-h-screen bg-background">
        <Routes>
          <Route path="/" element={<Layout />}>
            <Route index element={<ScreenerPage />} />
            <Route path="screener" element={<ScreenerPage />} />
            <Route path="stock/:code" element={<StockDetailPage />} />
            <Route path="market/hot" element={<HotStocksPage />} />
            <Route path="market/overview" element={<MarketOverviewPage />} />
            <Route path="industries" element={<IndustriesPage />} />
            <Route path="*" element={<NotFoundPage />} />
          </Route>
        </Routes>
        <Toaster 
          position="bottom-right"
          toastOptions={{
            className: 'font-sans',
            duration: 4000,
          }}
        />
        
        {/* 页脚免责声明 */}
        <footer className="mt-12 border-t py-6 px-4 text-center text-sm text-muted-foreground">
          <div className="container mx-auto">
            <p className="mb-2">
              ⚠️ <strong>免责声明：</strong>本工具所有信息仅供学习参考，不构成任何投资建议。
            </p>
            <p className="text-xs">
              数据来源：Tushare Pro API • 更新时间：实时 • 股市有风险，投资需谨慎
            </p>
          </div>
        </footer>
      </div>
    </QueryClientProvider>
  )
}

export default App