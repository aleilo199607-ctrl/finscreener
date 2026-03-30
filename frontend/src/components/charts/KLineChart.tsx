import React, { useState } from 'react';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, Brush, Area,
  ReferenceLine, Legend
} from 'recharts';
import { format, subDays, parseISO } from 'date-fns';
import { cn } from '@/utils/cn';
import { Candlestick, KLineData } from '@/types';
import { TrendingUp, TrendingDown, BarChart3, Maximize2, Minimize2 } from 'lucide-react';

interface KLineChartProps {
  data: KLineData[];
  period?: '1d' | '5d' | '1m' | '3m' | '6m' | '1y';
  symbol?: string;
  name?: string;
  showVolume?: boolean;
  showTechnicalIndicators?: boolean;
  className?: string;
  height?: number;
}

export const KLineChart: React.FC<KLineChartProps> = ({
  data,
  period = '1m',
  symbol = '',
  name = '',
  showVolume = true,
  showTechnicalIndicators = false,
  className,
  height = 400,
}) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [showMA, setShowMA] = useState(true);
  const [showVolumeChart, setShowVolumeChart] = useState(showVolume);

  // 生成模拟K线数据（如果传入数据为空）
  const chartData = data.length > 0 ? data : generateMockKLineData(period);

  // 计算技术指标
  const chartDataWithIndicators = chartData.map((item, index) => {
    // MA5
    const ma5 = index >= 4 
      ? chartData.slice(index - 4, index + 1).reduce((sum, d) => sum + d.close, 0) / 5
      : item.close;

    // MA20
    const ma20 = index >= 19
      ? chartData.slice(index - 19, index + 1).reduce((sum, d) => sum + d.close, 0) / 20
      : item.close;

    // RSI（简化版本）
    let rsi = 50;
    if (index >= 14) {
      const gains = chartData.slice(index - 13, index + 1)
        .map(d => Math.max(d.close - d.open, 0))
        .reduce((sum, gain) => sum + gain, 0) / 14;
      const losses = chartData.slice(index - 13, index + 1)
        .map(d => Math.max(d.open - d.close, 0))
        .reduce((sum, loss) => sum + loss, 0) / 14;
      rsi = losses === 0 ? 100 : 100 - (100 / (1 + gains / losses));
    }

    // MACD（简化版本）
    const ema12 = item.close; // 简化计算
    const ema26 = item.close;
    const macd = ema12 - ema26;
    const signal = macd * 0.9;
    const histogram = macd - signal;

    return {
      ...item,
      date: format(parseISO(item.date), 'MM-dd'),
      ma5,
      ma20,
      rsi,
      macd,
      signal,
      histogram,
    };
  });

  // 自定义工具提示
  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      const isUp = data.close >= data.open;
      
      return (
        <div className="bg-white border border-gray-300 rounded-lg shadow-lg p-4">
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <span className="font-semibold text-gray-700">{label}</span>
              <span className={cn(
                "text-sm px-2 py-1 rounded",
                isUp ? "bg-red-100 text-red-700" : "bg-green-100 text-green-700"
              )}>
                {isUp ? '涨' : '跌'}
              </span>
            </div>
            
            <div className="grid grid-cols-2 gap-3">
              <div>
                <div className="text-xs text-gray-500">开盘</div>
                <div className="font-bold">¥{data.open.toFixed(2)}</div>
              </div>
              <div>
                <div className="text-xs text-gray-500">收盘</div>
                <div className={cn(
                  "font-bold",
                  isUp ? "text-red-600" : "text-green-600"
                )}>
                  ¥{data.close.toFixed(2)}
                </div>
              </div>
              <div>
                <div className="text-xs text-gray-500">最高</div>
                <div className="font-semibold text-gray-800">¥{data.high.toFixed(2)}</div>
              </div>
              <div>
                <div className="text-xs text-gray-500">最低</div>
                <div className="font-semibold text-gray-800">¥{data.low.toFixed(2)}</div>
              </div>
            </div>

            <div className="pt-2 border-t border-gray-200">
              <div className="text-xs text-gray-500">成交量</div>
              <div className="font-semibold">
                {(data.volume / 10000).toFixed(1)}万手
              </div>
            </div>

            {showMA && (
              <div className="pt-2 border-t border-gray-200">
                <div className="flex justify-between text-xs">
                  <span className="text-blue-600">MA5: ¥{data.ma5?.toFixed(2) || '--'}</span>
                  <span className="text-purple-600">MA20: ¥{data.ma20?.toFixed(2) || '--'}</span>
                </div>
              </div>
            )}
          </div>
        </div>
      );
    }
    return null;
  };

  // 格式化Y轴
  const formatYAxis = (value: number) => {
    return `¥${value.toFixed(2)}`;
  };

  // 获取最新价格和涨跌幅
  const latestData = chartDataWithIndicators[chartDataWithIndicators.length - 1];
  const prevData = chartDataWithIndicators[chartDataWithIndicators.length - 2];
  const priceChange = latestData ? latestData.close - (prevData?.close || latestData.open) : 0;
  const priceChangePercent = latestData && prevData 
    ? ((latestData.close - prevData.close) / prevData.close * 100)
    : 0;

  return (
    <div className={cn(
      "bg-white rounded-xl shadow-lg border border-gray-200 p-6",
      isExpanded && "fixed inset-4 z-50 bg-white p-6 overflow-auto",
      className
    )}>
      {/* 图表头部 */}
      <div className="flex justify-between items-start mb-6">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-100 to-blue-50 flex items-center justify-center">
              <BarChart3 className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <h3 className="text-xl font-bold text-gray-900">
                {symbol} {name} K线图
              </h3>
              <div className="flex items-center gap-4 mt-1">
                {latestData && (
                  <>
                    <span className="text-2xl font-bold text-gray-900">
                      ¥{latestData.close.toFixed(2)}
                    </span>
                    <div className={cn(
                      "flex items-center gap-1 px-3 py-1 rounded-lg",
                      priceChange >= 0
                        ? "bg-red-50 text-red-700 border border-red-200"
                        : "bg-green-50 text-green-700 border border-green-200"
                    )}>
                      {priceChange >= 0 ? (
                        <TrendingUp className="w-4 h-4" />
                      ) : (
                        <TrendingDown className="w-4 h-4" />
                      )}
                      <span className="font-bold">
                        {priceChange >= 0 ? '+' : ''}{priceChange.toFixed(2)}
                      </span>
                      <span className="font-bold">
                        ({priceChange >= 0 ? '+' : ''}{priceChangePercent.toFixed(2)}%)
                      </span>
                    </div>
                  </>
                )}
              </div>
            </div>
          </div>
          <div className="flex items-center gap-2 text-sm text-gray-600">
            <span>周期: {getPeriodText(period)}</span>
            <span>•</span>
            <span>数据更新: {format(new Date(), 'MM-dd HH:mm')}</span>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => setShowMA(!showMA)}
            className={cn(
              "px-3 py-1.5 text-sm rounded-lg border transition-colors",
              showMA
                ? "bg-blue-600 text-white border-blue-600"
                : "bg-gray-100 text-gray-700 border-gray-300 hover:bg-gray-200"
            )}
          >
            均线
          </button>
          <button
            onClick={() => setShowVolumeChart(!showVolumeChart)}
            className={cn(
              "px-3 py-1.5 text-sm rounded-lg border transition-colors",
              showVolumeChart
                ? "bg-blue-600 text-white border-blue-600"
                : "bg-gray-100 text-gray-700 border-gray-300 hover:bg-gray-200"
            )}
          >
            成交量
          </button>
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="p-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
            title={isExpanded ? "缩小" : "全屏"}
          >
            {isExpanded ? (
              <Minimize2 className="w-4 h-4" />
            ) : (
              <Maximize2 className="w-4 h-4" />
            )}
          </button>
        </div>
      </div>

      {/* K线图 */}
      <div style={{ height: isExpanded ? 'calc(100vh - 200px)' : `${height}px` }}>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart
            data={chartDataWithIndicators}
            margin={{ top: 20, right: 30, left: 20, bottom: 40 }}
          >
            <CartesianGrid 
              strokeDasharray="3 3" 
              stroke="#f0f0f0" 
              vertical={false}
            />
            
            <XAxis
              dataKey="date"
              axisLine={{ stroke: '#e5e7eb' }}
              tickLine={false}
              tick={{ fill: '#6b7280', fontSize: 12 }}
              padding={{ left: 10, right: 10 }}
            />
            
            <YAxis
              domain={['dataMin - 1', 'dataMax + 1']}
              axisLine={{ stroke: '#e5e7eb' }}
              tickLine={false}
              tick={{ fill: '#6b7280', fontSize: 12 }}
              tickFormatter={formatYAxis}
              orientation="right"
            />
            
            <Tooltip content={<CustomTooltip />} />
            <Legend />

            {/* 价格线 */}
            <Line
              type="monotone"
              dataKey="close"
              stroke="#3b82f6"
              strokeWidth={2}
              dot={false}
              name="收盘价"
              activeDot={{ r: 6, fill: '#3b82f6' }}
            />

            {/* MA5线 */}
            {showMA && (
              <Line
                type="monotone"
                dataKey="ma5"
                stroke="#8b5cf6"
                strokeWidth={1.5}
                strokeDasharray="3 3"
                dot={false}
                name="MA5"
              />
            )}

            {/* MA20线 */}
            {showMA && (
              <Line
                type="monotone"
                dataKey="ma20"
                stroke="#10b981"
                strokeWidth={1.5}
                strokeDasharray="3 3"
                dot={false}
                name="MA20"
              />
            )}

            {/* 成交量 */}
            {showVolumeChart && (
              <Area
                type="monotone"
                dataKey="volume"
                stroke="#f59e0b"
                fill="#fbbf24"
                fillOpacity={0.3}
                yAxisId={1}
                name="成交量"
              />
            )}

            {/* 支撑线/压力线参考 */}
            {!isExpanded && (
              <>
                <ReferenceLine
                  y={chartDataWithIndicators.reduce((min, d) => Math.min(min, d.low), Infinity)}
                  stroke="#ef4444"
                  strokeDasharray="3 3"
                  label={{ 
                    value: '支撑', 
                    position: 'insideBottomLeft',
                    fill: '#ef4444',
                    fontSize: 12
                  }}
                />
                <ReferenceLine
                  y={chartDataWithIndicators.reduce((max, d) => Math.max(max, d.high), -Infinity)}
                  stroke="#10b981"
                  strokeDasharray="3 3"
                  label={{ 
                    value: '压力', 
                    position: 'insideTopLeft',
                    fill: '#10b981',
                    fontSize: 12
                  }}
                />
              </>
            )}

            {/* 刷选器 */}
            <Brush
              dataKey="date"
              height={30}
              stroke="#9ca3af"
              fill="#f9fafb"
              travellerWidth={10}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* 技术指标面板 */}
      {showTechnicalIndicators && (
        <div className="mt-6 grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-gray-50 p-4 rounded-lg">
            <div className="text-sm text-gray-600 mb-1">RSI</div>
            <div className="text-lg font-bold text-gray-900">
              {latestData?.rsi ? latestData.rsi.toFixed(1) : '--'}
            </div>
            <div className="text-xs mt-1">
              <span className={cn(
                latestData?.rsi > 70 ? "text-red-600" :
                latestData?.rsi < 30 ? "text-green-600" :
                "text-gray-600"
              )}>
                {latestData?.rsi > 70 ? "超买" :
                 latestData?.rsi < 30 ? "超卖" : "中性"}
              </span>
            </div>
          </div>
          
          <div className="bg-gray-50 p-4 rounded-lg">
            <div className="text-sm text-gray-600 mb-1">MACD</div>
            <div className="text-lg font-bold text-gray-900">
              {latestData?.macd ? latestData.macd.toFixed(3) : '--'}
            </div>
            <div className="text-xs mt-1">
              <span className={cn(
                latestData?.macd > 0 ? "text-red-600" : "text-green-600"
              )}>
                {latestData?.macd > 0 ? "多头" : "空头"}
              </span>
            </div>
          </div>

          <div className="bg-gray-50 p-4 rounded-lg">
            <div className="text-sm text-gray-600 mb-1">乖离率</div>
            <div className="text-lg font-bold text-gray-900">
              {latestData?.ma5 && latestData?.ma20 
                ? ((latestData.close - latestData.ma5) / latestData.ma5 * 100).toFixed(2) + '%'
                : '--'}
            </div>
          </div>

          <div className="bg-gray-50 p-4 rounded-lg">
            <div className="text-sm text-gray-600 mb-1">波动率</div>
            <div className="text-lg font-bold text-gray-900">
              {calculateVolatility(chartDataWithIndicators).toFixed(2)}%
            </div>
          </div>
        </div>
      )}

      {/* 周期选择器 */}
      <div className="flex items-center justify-center gap-2 mt-6">
        {['1d', '5d', '1m', '3m', '6m', '1y'].map(p => (
          <button
            key={p}
            className={cn(
              "px-4 py-2 text-sm rounded-lg transition-colors",
              period === p
                ? "bg-blue-600 text-white"
                : "bg-gray-100 text-gray-700 hover:bg-gray-200"
            )}
          >
            {getPeriodText(p)}
          </button>
        ))}
      </div>

      {/* 图表说明 */}
      <div className="mt-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
        <div className="flex items-start gap-2">
          <div className="mt-0.5">
            <Info className="w-4 h-4 text-blue-600" />
          </div>
          <div className="text-sm text-blue-700">
            <p className="font-medium">图表说明：</p>
            <ul className="mt-1 space-y-1">
              <li>• <span className="text-blue-600 font-medium">蓝色线</span>: 收盘价走势</li>
              <li>• <span className="text-purple-600 font-medium">紫色虚线</span>: 5日均线(MA5)</li>
              <li>• <span className="text-green-600 font-medium">绿色虚线</span>: 20日均线(MA20)</li>
              <li>• <span className="text-yellow-600 font-medium">黄色区域</span>: 成交量</li>
              <li>• <span className="text-red-600">红色</span>表示上涨，<span className="text-green-600">绿色</span>表示下跌</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

// 辅助函数：生成模拟K线数据
function generateMockKLineData(period: string): KLineData[] {
  const data: KLineData[] = [];
  const startDate = new Date();
  let days = 30;
  
  switch (period) {
    case '1d': days = 1; break;
    case '5d': days = 5; break;
    case '1m': days = 30; break;
    case '3m': days = 90; break;
    case '6m': days = 180; break;
    case '1y': days = 365; break;
  }
  
  let basePrice = 100 + Math.random() * 20;
  
  for (let i = days; i >= 0; i--) {
    const date = subDays(startDate, i);
    const open = basePrice;
    const change = (Math.random() - 0.5) * 10;
    const close = open + change;
    const high = Math.max(open, close) + Math.random() * 3;
    const low = Math.min(open, close) - Math.random() * 3;
    const volume = Math.floor(Math.random() * 1000000) + 500000;
    
    data.push({
      date: format(date, 'yyyy-MM-dd'),
      open,
      high,
      low,
      close,
      volume,
      turnover: volume * close,
    });
    
    basePrice = close;
  }
  
  return data;
}

// 辅助函数：获取周期文本
function getPeriodText(period: string): string {
  const map: Record<string, string> = {
    '1d': '日K',
    '5d': '5日',
    '1m': '月K',
    '3m': '季K',
    '6m': '半年',
    '1y': '年K',
  };
  return map[period] || period;
}

// 辅助函数：计算波动率
function calculateVolatility(data: any[]): number {
  if (data.length < 2) return 0;
  
  const returns = [];
  for (let i = 1; i < data.length; i++) {
    const returnRate = (data[i].close - data[i-1].close) / data[i-1].close;
    returns.push(returnRate);
  }
  
  const mean = returns.reduce((sum, r) => sum + r, 0) / returns.length;
  const variance = returns.reduce((sum, r) => sum + Math.pow(r - mean, 2), 0) / returns.length;
  
  return Math.sqrt(variance) * 100 * Math.sqrt(252); // 年化波动率
}

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