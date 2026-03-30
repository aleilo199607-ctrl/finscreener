import React, { useState, useMemo } from 'react';
import { 
  ChevronUp, ChevronDown, ArrowUpRight, ArrowDownRight, 
  TrendingUp, TrendingDown, Eye, Star, Filter, 
  DollarSign, Percent, PieChart, BarChart3 
} from 'lucide-react';
import { cn } from '@/utils/cn';
import { StockQuote } from '@/types';
import { Link } from 'react-router-dom';

interface StockTableProps {
  stocks: StockQuote[];
  isLoading?: boolean;
  onSort?: (field: string, direction: 'asc' | 'desc') => void;
  onAddToWatchlist?: (stockCode: string) => void;
  onViewDetail?: (stockCode: string) => void;
  className?: string;
}

interface Column {
  key: string;
  title: string;
  align?: 'left' | 'center' | 'right';
  sortable?: boolean;
  icon?: React.ReactNode;
  width?: string;
  render?: (stock: StockQuote) => React.ReactNode;
}

export const StockTable: React.FC<StockTableProps> = ({
  stocks,
  isLoading = false,
  onSort,
  onAddToWatchlist,
  onViewDetail,
  className,
}) => {
  const [sortField, setSortField] = useState<string>('change_percent');
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('desc');

  const columns: Column[] = [
    {
      key: 'symbol',
      title: '代码',
      align: 'left',
      sortable: true,
      icon: <Filter className="w-3 h-3" />,
      width: '80px',
      render: (stock) => (
        <div className="flex flex-col">
          <span className="font-mono font-bold text-gray-900">{stock.symbol}</span>
          <span className="text-xs text-gray-500">{stock.exchange}</span>
        </div>
      ),
    },
    {
      key: 'name',
      title: '名称',
      align: 'left',
      sortable: true,
      width: '140px',
      render: (stock) => (
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-100 to-blue-50 flex items-center justify-center">
            <span className="text-xs font-bold text-blue-600">
              {stock.name.charAt(0)}
            </span>
          </div>
          <span className="font-medium text-gray-900 truncate">{stock.name}</span>
        </div>
      ),
    },
    {
      key: 'latest_price',
      title: '最新价',
      align: 'right',
      sortable: true,
      icon: <DollarSign className="w-3 h-3" />,
      width: '100px',
      render: (stock) => (
        <div className="text-right">
          <span className="text-lg font-bold text-gray-900">
            ¥{stock.latest_price.toFixed(2)}
          </span>
          <div className="flex items-center justify-end gap-1 mt-1">
            <span className={cn(
              "text-xs font-medium",
              stock.change_percent >= 0 ? "text-red-600" : "text-green-600"
            )}>
              {stock.change_percent >= 0 ? '+' : ''}{stock.change_percent.toFixed(2)}%
            </span>
            {stock.change_percent >= 0 ? (
              <ArrowUpRight className="w-3 h-3 text-red-600" />
            ) : (
              <ArrowDownRight className="w-3 h-3 text-green-600" />
            )}
          </div>
        </div>
      ),
    },
    {
      key: 'change_percent',
      title: '涨跌幅',
      align: 'right',
      sortable: true,
      icon: <Percent className="w-3 h-3" />,
      width: '100px',
      render: (stock) => {
        const isPositive = stock.change_percent >= 0;
        return (
          <div className={cn(
            "px-3 py-1.5 rounded-lg text-center",
            isPositive 
              ? "bg-red-50 text-red-700 border border-red-200" 
              : "bg-green-50 text-green-700 border border-green-200"
          )}>
            <div className="flex items-center justify-center gap-1">
              {isPositive ? (
                <TrendingUp className="w-3 h-3" />
              ) : (
                <TrendingDown className="w-3 h-3" />
              )}
              <span className="font-bold">
                {isPositive ? '+' : ''}{stock.change_percent.toFixed(2)}%
              </span>
            </div>
            <div className="text-xs mt-1">
              {stock.change_amount >= 0 ? '+' : ''}{stock.change_amount.toFixed(2)}
            </div>
          </div>
        );
      },
    },
    {
      key: 'volume',
      title: '成交量',
      align: 'right',
      sortable: true,
      icon: <BarChart3 className="w-3 h-3" />,
      width: '100px',
      render: (stock) => (
        <div className="text-right">
          <span className="text-sm font-medium text-gray-900">
            {(stock.volume / 10000).toFixed(1)}万
          </span>
          <div className="mt-1">
            <div className="w-full h-1.5 bg-gray-200 rounded-full overflow-hidden">
              <div 
                className={cn(
                  "h-full",
                  stock.volume_ratio >= 1 ? "bg-green-500" : "bg-yellow-500"
                )}
                style={{ width: `${Math.min(stock.volume_ratio * 20, 100)}%` }}
              />
            </div>
            <span className="text-xs text-gray-500 mt-1 block">
              量比: {stock.volume_ratio.toFixed(2)}
            </span>
          </div>
        </div>
      ),
    },
    {
      key: 'pe_ratio',
      title: 'PE',
      align: 'right',
      sortable: true,
      icon: <PieChart className="w-3 h-3" />,
      width: '80px',
      render: (stock) => (
        <div className="text-right">
          <span className={cn(
            "text-sm font-bold",
            stock.pe_ratio < 15 ? "text-green-700" :
            stock.pe_ratio < 30 ? "text-yellow-700" :
            "text-red-700"
          )}>
            {stock.pe_ratio.toFixed(1)}
          </span>
          <div className="text-xs text-gray-500 mt-1">市盈率</div>
        </div>
      ),
    },
    {
      key: 'pb_ratio',
      title: 'PB',
      align: 'right',
      sortable: true,
      width: '80px',
      render: (stock) => (
        <div className="text-right">
          <span className={cn(
            "text-sm font-bold",
            stock.pb_ratio < 1.5 ? "text-green-700" :
            stock.pb_ratio < 3 ? "text-yellow-700" :
            "text-red-700"
          )}>
            {stock.pb_ratio.toFixed(2)}
          </span>
          <div className="text-xs text-gray-500 mt-1">市净率</div>
        </div>
      ),
    },
    {
      key: 'market_cap',
      title: '市值',
      align: 'right',
      sortable: true,
      width: '120px',
      render: (stock) => {
        const capInBillions = stock.market_cap / 100000000;
        let displayText = '';
        let sizeColor = '';
        
        if (capInBillions < 10) {
          displayText = `${capInBillions.toFixed(1)}亿`;
          sizeColor = 'text-blue-600';
        } else if (capInBillions < 100) {
          displayText = `${capInBillions.toFixed(0)}亿`;
          sizeColor = 'text-purple-600';
        } else {
          displayText = `${(capInBillions / 100).toFixed(1)}千亿`;
          sizeColor = 'text-indigo-600';
        }
        
        return (
          <div className="text-right">
            <span className={`text-sm font-bold ${sizeColor}`}>
              {displayText}
            </span>
            <div className="text-xs text-gray-500 mt-1">
              {stock.market_cap >= 50000000000 ? '大盘股' :
               stock.market_cap >= 10000000000 ? '中盘股' : '小盘股'}
            </div>
          </div>
        );
      },
    },
    {
      key: 'actions',
      title: '操作',
      align: 'center',
      sortable: false,
      width: '120px',
      render: (stock) => (
        <div className="flex items-center justify-center gap-2">
          <Link
            to={`/stock/${stock.symbol}`}
            className="p-2 bg-blue-50 text-blue-600 rounded-lg hover:bg-blue-100 transition-colors"
            title="查看详情"
          >
            <Eye className="w-4 h-4" />
          </Link>
          <button
            onClick={() => onAddToWatchlist?.(stock.symbol)}
            className="p-2 bg-yellow-50 text-yellow-600 rounded-lg hover:bg-yellow-100 transition-colors"
            title="加入自选"
          >
            <Star className="w-4 h-4" />
          </button>
          <button
            onClick={() => onViewDetail?.(stock.symbol)}
            className="p-2 bg-green-50 text-green-600 rounded-lg hover:bg-green-100 transition-colors"
            title="快速分析"
          >
            <TrendingUp className="w-4 h-4" />
          </button>
        </div>
      ),
    },
  ];

  const handleSort = (field: string) => {
    if (!columns.find(col => col.key === field)?.sortable) return;
    
    let newDirection: 'asc' | 'desc' = 'desc';
    if (field === sortField) {
      newDirection = sortDirection === 'desc' ? 'asc' : 'desc';
    }
    
    setSortField(field);
    setSortDirection(newDirection);
    onSort?.(field, newDirection);
  };

  const sortedStocks = useMemo(() => {
    if (!stocks.length) return [];
    
    const sorted = [...stocks].sort((a, b) => {
      let aValue = (a as any)[sortField];
      let bValue = (b as any)[sortField];
      
      // 特殊处理字段
      if (sortField === 'market_cap') {
        aValue = a.market_cap;
        bValue = b.market_cap;
      } else if (sortField === 'volume') {
        aValue = a.volume;
        bValue = b.volume;
      }
      
      if (aValue < bValue) return sortDirection === 'asc' ? -1 : 1;
      if (aValue > bValue) return sortDirection === 'asc' ? 1 : -1;
      return 0;
    });
    
    return sorted;
  }, [stocks, sortField, sortDirection]);

  if (isLoading) {
    return (
      <div className={cn("bg-white rounded-xl shadow-lg border border-gray-200 p-8", className)}>
        <div className="flex flex-col items-center justify-center py-12">
          <div className="w-12 h-12 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin mb-4"></div>
          <p className="text-gray-600">正在加载股票数据...</p>
          <p className="text-sm text-gray-500 mt-2">请稍候</p>
        </div>
      </div>
    );
  }

  if (stocks.length === 0) {
    return (
      <div className={cn("bg-white rounded-xl shadow-lg border border-gray-200 p-8", className)}>
        <div className="flex flex-col items-center justify-center py-12">
          <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mb-4">
            <Filter className="w-8 h-8 text-blue-600" />
          </div>
          <h3 className="text-xl font-semibold text-gray-800 mb-2">暂无股票数据</h3>
          <p className="text-gray-600 text-center max-w-md">
            当前筛选条件没有匹配到任何股票，请尝试放宽筛选条件或重新筛选
          </p>
          <button className="mt-6 px-6 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition-colors">
            重置筛选条件
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className={cn("bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden", className)}>
      {/* 表格头部 */}
      <div className="px-6 py-4 border-b border-gray-200 bg-gray-50">
        <div className="flex justify-between items-center">
          <div>
            <h3 className="text-lg font-semibold text-gray-800">筛选结果</h3>
            <p className="text-sm text-gray-600">
              共找到 <span className="font-bold text-blue-600">{stocks.length}</span> 只股票
            </p>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-sm text-gray-600">排序:</span>
            <div className="flex items-center gap-1 bg-white border border-gray-300 rounded-lg px-3 py-1">
              {columns.find(col => col.key === sortField)?.icon}
              <span className="text-sm font-medium">
                {columns.find(col => col.key === sortField)?.title}
              </span>
              {sortDirection === 'asc' ? (
                <ChevronUp className="w-4 h-4 text-blue-600" />
              ) : (
                <ChevronDown className="w-4 h-4 text-blue-600" />
              )}
            </div>
          </div>
        </div>
      </div>

      {/* 表格内容 */}
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-gray-200 bg-gray-50">
              {columns.map(column => (
                <th
                  key={column.key}
                  style={{ width: column.width }}
                  className={cn(
                    "px-4 py-3 text-left text-sm font-semibold text-gray-700 whitespace-nowrap",
                    column.align === 'center' && 'text-center',
                    column.align === 'right' && 'text-right',
                    column.sortable && 'cursor-pointer hover:bg-gray-100'
                  )}
                  onClick={() => column.sortable && handleSort(column.key)}
                >
                  <div className={cn(
                    "flex items-center gap-1",
                    column.align === 'center' && 'justify-center',
                    column.align === 'right' && 'justify-end'
                  )}>
                    {column.icon}
                    <span>{column.title}</span>
                    {column.sortable && (
                      <div className="flex flex-col ml-1">
                        <ChevronUp className={cn(
                          "w-3 h-3",
                          sortField === column.key && sortDirection === 'asc'
                            ? "text-blue-600"
                            : "text-gray-400"
                        )} />
                        <ChevronDown className={cn(
                          "w-3 h-3 -mt-1",
                          sortField === column.key && sortDirection === 'desc'
                            ? "text-blue-600"
                            : "text-gray-400"
                        )} />
                      </div>
                    )}
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {sortedStocks.map((stock, index) => (
              <tr 
                key={stock.symbol}
                className={cn(
                  "hover:bg-gray-50 transition-colors",
                  index % 2 === 0 ? "bg-white" : "bg-gray-50/50"
                )}
              >
                {columns.map(column => (
                  <td
                    key={`${stock.symbol}-${column.key}`}
                    className={cn(
                      "px-4 py-4 text-sm",
                      column.align === 'center' && 'text-center',
                      column.align === 'right' && 'text-right'
                    )}
                  >
                    {column.render ? column.render(stock) : (
                      <span className="text-gray-900">{(stock as any)[column.key]}</span>
                    )}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* 表格底部 */}
      <div className="px-6 py-4 border-t border-gray-200 bg-gray-50">
        <div className="flex justify-between items-center">
          <div className="text-sm text-gray-600">
            显示 1-{stocks.length} 条，共 {stocks.length} 条
          </div>
          <div className="flex items-center gap-2">
            <button className="px-3 py-1.5 text-sm border border-gray-300 rounded-lg hover:bg-gray-50">
              上一页
            </button>
            <button className="px-3 py-1.5 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700">
              1
            </button>
            <button className="px-3 py-1.5 text-sm border border-gray-300 rounded-lg hover:bg-gray-50">
              下一页
            </button>
          </div>
        </div>
      </div>

      {/* 表格说明 */}
      <div className="px-6 py-4 bg-blue-50 border-t border-blue-200">
        <div className="flex items-start gap-2">
          <div className="mt-0.5">
            <Info className="w-4 h-4 text-blue-600" />
          </div>
          <div className="text-sm text-blue-700">
            <p className="font-medium">表格说明：</p>
            <ul className="mt-1 space-y-1">
              <li>• <span className="text-red-600 font-medium">红色</span>表示上涨，<span className="text-green-600 font-medium">绿色</span>表示下跌（符合A股惯例）</li>
              <li>• PE小于15为低估，15-30为合理，大于30为高估</li>
              <li>• 点击表头可对相应列进行排序</li>
              <li>• 点击操作按钮可查看详情或加入自选</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

// 辅助组件
const Info: React.FC<{ className?: string }> = ({ className }) => (
  <svg 
    className={className}
    xmlns="http://www.w3.org/2000/svg" 
    viewBox="0 0 24 24" 
    fill="none" 
    stroke="currentColor" 
    strokeWidth="2" 
    strokeLinecap="round" 
    strokeLinejoin="round"
  >
    <circle cx="12" cy="12" r="10" />
    <line x1="12" y1="16" x2="12" y2="12" />
    <line x1="12" y1="8" x2="12.01" y2="8" />
  </svg>
);