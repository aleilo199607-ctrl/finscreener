import React from 'react';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, Legend, Area
} from 'recharts';
import { cn } from '@/utils/cn';
import { BarChart3, TrendingUp, TrendingDown } from 'lucide-react';

interface TechnicalIndicatorChartProps {
  data: Array<{
    date: string;
    rsi?: number;
    macd?: number;
    signal?: number;
    histogram?: number;
    k?: number;
    d?: number;
    j?: number;
    volume?: number;
  }>;
  indicators?: ('rsi' | 'macd' | 'kdj' | 'volume')[];
  height?: number;
  className?: string;
}

export const TechnicalIndicatorChart: React.FC<TechnicalIndicatorChartProps> = ({
  data,
  indicators = ['rsi', 'macd'],
  height = 300,
  className,
}) => {
  // 格式化数据
  const chartData = data.map(item => ({
    ...item,
    date: item.date.substring(5), // 显示MM-dd格式
  }));

  // 自定义工具提示
  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white border border-gray-300 rounded-lg shadow-lg p-3">
          <div className="text-sm font-semibold text-gray-700 mb-2">{label}</div>
          <div className="space-y-1">
            {payload.map((entry: any, index: number) => (
              <div key={index} className="flex items-center justify-between gap-4">
                <div className="flex items-center gap-2">
                  <div 
                    className="w-3 h-3 rounded-full"
                    style={{ backgroundColor: entry.color }}
                  />
                  <span className="text-xs text-gray-600">{entry.name}</span>
                </div>
                <span className="text-sm font-bold text-gray-900">
                  {typeof entry.value === 'number' 
                    ? entry.value.toFixed(entry.dataKey === 'volume' ? 0 : 2)
                    : entry.value}
                </span>
              </div>
            ))}
          </div>
        </div>
      );
    }
    return null;
  };

  const renderChart = (indicator: string) => {
    switch (indicator) {
      case 'rsi':
        return (
          <div className="h-full">
            <div className="flex items-center gap-2 mb-3">
              <div className="w-8 h-8 rounded-full bg-orange-100 flex items-center justify-center">
                <TrendingUp className="w-4 h-4 text-orange-600" />
              </div>
              <div>
                <h4 className="font-semibold text-gray-800">RSI相对强弱指标</h4>
                <p className="text-xs text-gray-600">14日周期，超买超卖信号</p>
              </div>
            </div>
            <ResponsiveContainer width="100%" height="85%">
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis 
                  dataKey="date" 
                  tick={{ fontSize: 12 }}
                  axisLine={{ stroke: '#e5e7eb' }}
                  tickLine={false}
                />
                <YAxis 
                  domain={[0, 100]}
                  tick={{ fontSize: 12 }}
                  axisLine={{ stroke: '#e5e7eb' }}
                  tickLine={false}
                  label={{ 
                    value: 'RSI', 
                    angle: -90, 
                    position: 'insideLeft',
                    offset: 10,
                    style: { fill: '#6b7280' }
                  }}
                />
                <Tooltip content={<CustomTooltip />} />
                <Line
                  type="monotone"
                  dataKey="rsi"
                  stroke="#f59e0b"
                  strokeWidth={2}
                  dot={false}
                  name="RSI"
                />
                <Line
                  type="monotone"
                  dataKey={() => 70}
                  stroke="#ef4444"
                  strokeWidth={1}
                  strokeDasharray="3 3"
                  dot={false}
                  name="超买线"
                />
                <Line
                  type="monotone"
                  dataKey={() => 30}
                  stroke="#10b981"
                  strokeWidth={1}
                  strokeDasharray="3 3"
                  dot={false}
                  name="超卖线"
                />
              </LineChart>
            </ResponsiveContainer>
            <div className="mt-2 text-xs text-gray-600 flex justify-between">
              <span className={cn(
                "px-2 py-1 rounded",
                chartData[chartData.length - 1]?.rsi > 70 
                  ? "bg-red-100 text-red-700" 
                  : chartData[chartData.length - 1]?.rsi < 30
                  ? "bg-green-100 text-green-700"
                  : "bg-gray-100 text-gray-700"
              )}>
                {chartData[chartData.length - 1]?.rsi > 70 ? '超买' :
                 chartData[chartData.length - 1]?.rsi < 30 ? '超卖' : '中性'}
              </span>
              <span>当前: {chartData[chartData.length - 1]?.rsi?.toFixed(1) || '--'}</span>
            </div>
          </div>
        );

      case 'macd':
        return (
          <div className="h-full">
            <div className="flex items-center gap-2 mb-3">
              <div className="w-8 h-8 rounded-full bg-purple-100 flex items-center justify-center">
                <BarChart3 className="w-4 h-4 text-purple-600" />
              </div>
              <div>
                <h4 className="font-semibold text-gray-800">MACD指标</h4>
                <p className="text-xs text-gray-600">趋势动能指标，金叉死叉信号</p>
              </div>
            </div>
            <ResponsiveContainer width="100%" height="85%">
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis 
                  dataKey="date" 
                  tick={{ fontSize: 12 }}
                  axisLine={{ stroke: '#e5e7eb' }}
                  tickLine={false}
                />
                <YAxis 
                  tick={{ fontSize: 12 }}
                  axisLine={{ stroke: '#e5e7eb' }}
                  tickLine={false}
                  label={{ 
                    value: 'MACD', 
                    angle: -90, 
                    position: 'insideLeft',
                    offset: 10,
                    style: { fill: '#6b7280' }
                  }}
                />
                <Tooltip content={<CustomTooltip />} />
                <Line
                  type="monotone"
                  dataKey="macd"
                  stroke="#8b5cf6"
                  strokeWidth={2}
                  dot={false}
                  name="MACD"
                />
                <Line
                  type="monotone"
                  dataKey="signal"
                  stroke="#f59e0b"
                  strokeWidth={1.5}
                  strokeDasharray="3 3"
                  dot={false}
                  name="信号线"
                />
                <Area
                  type="monotone"
                  dataKey="histogram"
                  stroke="#10b981"
                  fill="#10b981"
                  fillOpacity={0.3}
                  name="柱状图"
                />
              </LineChart>
            </ResponsiveContainer>
            <div className="mt-2 text-xs text-gray-600 flex justify-between">
              <span className={cn(
                "px-2 py-1 rounded",
                (chartData[chartData.length - 1]?.macd || 0) > 0
                  ? "bg-red-100 text-red-700"
                  : "bg-green-100 text-green-700"
              )}>
                {(chartData[chartData.length - 1]?.macd || 0) > 0 ? '多头' : '空头'}
              </span>
              <span>当前: {chartData[chartData.length - 1]?.macd?.toFixed(3) || '--'}</span>
            </div>
          </div>
        );

      case 'kdj':
        return (
          <div className="h-full">
            <div className="flex items-center gap-2 mb-3">
              <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center">
                <TrendingDown className="w-4 h-4 text-blue-600" />
              </div>
              <div>
                <h4 className="font-semibold text-gray-800">KDJ随机指标</h4>
                <p className="text-xs text-gray-600">超买超卖，趋势转折信号</p>
              </div>
            </div>
            <ResponsiveContainer width="100%" height="85%">
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis 
                  dataKey="date" 
                  tick={{ fontSize: 12 }}
                  axisLine={{ stroke: '#e5e7eb' }}
                  tickLine={false}
                />
                <YAxis 
                  domain={[0, 100]}
                  tick={{ fontSize: 12 }}
                  axisLine={{ stroke: '#e5e7eb' }}
                  tickLine={false}
                  label={{ 
                    value: 'KDJ', 
                    angle: -90, 
                    position: 'insideLeft',
                    offset: 10,
                    style: { fill: '#6b7280' }
                  }}
                />
                <Tooltip content={<CustomTooltip />} />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="k"
                  stroke="#3b82f6"
                  strokeWidth={2}
                  dot={false}
                  name="K线"
                />
                <Line
                  type="monotone"
                  dataKey="d"
                  stroke="#8b5cf6"
                  strokeWidth={1.5}
                  strokeDasharray="3 3"
                  dot={false}
                  name="D线"
                />
                <Line
                  type="monotone"
                  dataKey="j"
                  stroke="#10b981"
                  strokeWidth={1.5}
                  dot={false}
                  name="J线"
                />
                <Line
                  type="monotone"
                  dataKey={() => 80}
                  stroke="#ef4444"
                  strokeWidth={1}
                  strokeDasharray="3 3"
                  dot={false}
                  name="超买线"
                />
                <Line
                  type="monotone"
                  dataKey={() => 20}
                  stroke="#10b981"
                  strokeWidth={1}
                  strokeDasharray="3 3"
                  dot={false}
                  name="超卖线"
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        );

      case 'volume':
        return (
          <div className="h-full">
            <div className="flex items-center gap-2 mb-3">
              <div className="w-8 h-8 rounded-full bg-green-100 flex items-center justify-center">
                <BarChart3 className="w-4 h-4 text-green-600" />
              </div>
              <div>
                <h4 className="font-semibold text-gray-800">成交量分析</h4>
                <p className="text-xs text-gray-600">量价关系，资金流向</p>
              </div>
            </div>
            <ResponsiveContainer width="100%" height="85%">
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis 
                  dataKey="date" 
                  tick={{ fontSize: 12 }}
                  axisLine={{ stroke: '#e5e7eb' }}
                  tickLine={false}
                />
                <YAxis 
                  tick={{ fontSize: 12 }}
                  axisLine={{ stroke: '#e5e7eb' }}
                  tickLine={false}
                  label={{ 
                    value: '成交量(万手)', 
                    angle: -90, 
                    position: 'insideLeft',
                    offset: 10,
                    style: { fill: '#6b7280' }
                  }}
                  tickFormatter={(value) => (value / 10000).toFixed(0)}
                />
                <Tooltip 
                  content={<CustomTooltip />}
                  formatter={(value: number) => [(value / 10000).toFixed(1) + '万手', '成交量']}
                />
                <Area
                  type="monotone"
                  dataKey="volume"
                  stroke="#10b981"
                  fill="#10b981"
                  fillOpacity={0.3}
                  name="成交量"
                />
              </LineChart>
            </ResponsiveContainer>
            <div className="mt-2 text-xs text-gray-600">
              <span>日均: {(chartData.reduce((sum, d) => sum + (d.volume || 0), 0) / chartData.length / 10000).toFixed(1)}万手</span>
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className={cn("bg-white rounded-xl shadow-lg border border-gray-200 p-6", className)}>
      <div className="flex justify-between items-center mb-6">
        <h3 className="text-xl font-bold text-gray-900 flex items-center gap-2">
          <BarChart3 className="w-6 h-6 text-blue-600" />
          技术指标分析
        </h3>
        <div className="flex items-center gap-2">
          {['rsi', 'macd', 'kdj', 'volume'].map(indicator => (
            <button
              key={indicator}
              className={cn(
                "px-3 py-1.5 text-sm rounded-lg transition-colors",
                indicators.includes(indicator as any)
                  ? "bg-blue-600 text-white"
                  : "bg-gray-100 text-gray-700 hover:bg-gray-200"
              )}
            >
              {indicator.toUpperCase()}
            </button>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6" style={{ height: `${height}px` }}>
        {indicators.map(indicator => (
          <div key={indicator} className="bg-gray-50 rounded-lg p-4 border border-gray-200">
            {renderChart(indicator)}
          </div>
        ))}
      </div>

      {/* 指标说明 */}
      <div className="mt-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
        <div className="text-sm text-blue-700">
          <p className="font-medium mb-2">技术指标说明：</p>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div>
              <p className="font-semibold">RSI (相对强弱指标)</p>
              <ul className="text-xs mt-1 space-y-1">
                <li>• &gt;70: 超买，可能回调</li>
                <li>• &lt;30: 超卖，可能反弹</li>
                <li>• 30-70: 中性区间</li>
              </ul>
            </div>
            <div>
              <p className="font-semibold">MACD (指数平滑异同平均线)</p>
              <ul className="text-xs mt-1 space-y-1">
                <li>• DIF上穿DEA: 金叉买入信号</li>
                <li>• DIF下穿DEA: 死叉卖出信号</li>
                <li>• 柱状图: 动能强弱</li>
              </ul>
            </div>
            <div>
              <p className="font-semibold">KDJ (随机指标)</p>
              <ul className="text-xs mt-1 space-y-1">
                <li>• K、D、J三线关系</li>
                <li>• &gt;80: 超买区域</li>
                <li>• &lt;20: 超卖区域</li>
              </ul>
            </div>
            <div>
              <p className="font-semibold">成交量</p>
              <ul className="text-xs mt-1 space-y-1">
                <li>• 放量上涨: 强势</li>
                <li>• 缩量上涨: 谨慎</li>
                <li>• 量价背离: 预警</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};