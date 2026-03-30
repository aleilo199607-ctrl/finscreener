import React, { useState, useEffect } from 'react';
import { Search, Filter, X, ChevronDown, ChevronRight, Save, Loader2 } from 'lucide-react';
import { cn } from '@/utils/cn';
import { StockScreeningCondition } from '@/types';

interface ScreeningConditionGroup {
  id: string;
  title: string;
  icon: React.ReactNode;
  conditions: StockScreeningCondition[];
}

interface ScreeningPanelProps {
  onApplyFilters: (conditions: StockScreeningCondition[]) => void;
  onSavePreset?: (name: string, conditions: StockScreeningCondition[]) => void;
  savedPresets?: Array<{ name: string; conditions: StockScreeningCondition[] }>;
  isLoading?: boolean;
}

export const ScreeningPanel: React.FC<ScreeningPanelProps> = ({
  onApplyFilters,
  onSavePreset,
  savedPresets = [],
  isLoading = false,
}) => {
  const [expandedGroups, setExpandedGroups] = useState<Record<string, boolean>>({
    'price-volume': true,
    'technical': false,
    'financial': false,
    'market': false,
    'custom': false,
  });

  const [activeConditions, setActiveConditions] = useState<StockScreeningCondition[]>([]);
  const [presetName, setPresetName] = useState('');
  const [selectedPreset, setSelectedPreset] = useState<string>('');

  // 初始筛选条件
  const conditionGroups: ScreeningConditionGroup[] = [
    {
      id: 'price-volume',
      title: '价格与量能',
      icon: <Filter className="w-4 h-4" />,
      conditions: [
        { id: 'price_range', name: '价格区间', type: 'range', min: 0, max: 500, unit: '元', value: [5, 100] },
        { id: 'price_change_pct', name: '涨跌幅', type: 'range', min: -20, max: 20, unit: '%', value: [-10, 10] },
        { id: 'volume_ratio', name: '量比', type: 'range', min: 0, max: 10, unit: '', value: [0.8, 2] },
        { id: 'turnover_rate', name: '换手率', type: 'range', min: 0, max: 50, unit: '%', value: [1, 15] },
        { id: 'market_cap', name: '市值', type: 'select', options: [
          { label: '小盘股 (<50亿)', value: 'small' },
          { label: '中盘股 (50-200亿)', value: 'medium' },
          { label: '大盘股 (>200亿)', value: 'large' },
        ], value: 'medium' },
      ],
    },
    {
      id: 'technical',
      title: '技术指标',
      icon: <Search className="w-4 h-4" />,
      conditions: [
        { id: 'rsi', name: 'RSI强弱指标', type: 'range', min: 0, max: 100, unit: '', value: [30, 70] },
        { id: 'macd', name: 'MACD金叉', type: 'select', options: [
          { label: '金叉向上', value: 'golden' },
          { label: '死叉向下', value: 'death' },
          { label: '无要求', value: 'any' },
        ], value: 'any' },
        { id: 'kdj_k', name: 'KDJ-K值', type: 'range', min: 0, max: 100, unit: '', value: [20, 80] },
        { id: 'ma5_20', name: '5日线上穿20日线', type: 'boolean', value: false },
        { id: 'volume_trend', name: '量能趋势', type: 'select', options: [
          { label: '放量', value: 'volume_up' },
          { label: '缩量', value: 'volume_down' },
          { label: '平量', value: 'volume_flat' },
        ], value: 'volume_up' },
      ],
    },
    {
      id: 'financial',
      title: '财务指标',
      icon: <Filter className="w-4 h-4" />,
      conditions: [
        { id: 'pe_ratio', name: '市盈率(PE)', type: 'range', min: 0, max: 100, unit: '', value: [0, 30] },
        { id: 'pb_ratio', name: '市净率(PB)', type: 'range', min: 0, max: 10, unit: '', value: [0.5, 3] },
        { id: 'roe', name: '净资产收益率', type: 'range', min: 0, max: 50, unit: '%', value: [10, 30] },
        { id: 'debt_ratio', name: '资产负债率', type: 'range', min: 0, max: 100, unit: '%', value: [0, 70] },
        { id: 'dividend_yield', name: '股息率', type: 'range', min: 0, max: 10, unit: '%', value: [1, 5] },
      ],
    },
    {
      id: 'market',
      title: '市场表现',
      icon: <Filter className="w-4 h-4" />,
      conditions: [
        { id: 'sector', name: '行业板块', type: 'select', options: [
          { label: '科技', value: 'tech' },
          { label: '消费', value: 'consumer' },
          { label: '医药', value: 'healthcare' },
          { label: '金融', value: 'financial' },
          { label: '工业', value: 'industrial' },
        ], value: 'tech' },
        { id: 'listed_years', name: '上市年限', type: 'range', min: 0, max: 20, unit: '年', value: [3, 10] },
        { id: 'institutional_holding', name: '机构持股比例', type: 'range', min: 0, max: 100, unit: '%', value: [30, 80] },
      ],
    },
  ];

  const toggleGroup = (groupId: string) => {
    setExpandedGroups(prev => ({ ...prev, [groupId]: !prev[groupId] }));
  };

  const handleConditionChange = (groupId: string, conditionId: string, value: any) => {
    const condition = conditionGroups
      .find(g => g.id === groupId)
      ?.conditions.find(c => c.id === conditionId);
    
    if (condition) {
      const updatedCondition = { ...condition, value };
      const existingIndex = activeConditions.findIndex(c => c.id === conditionId);
      
      let updatedConditions;
      if (existingIndex >= 0) {
        updatedConditions = [...activeConditions];
        updatedConditions[existingIndex] = updatedCondition;
      } else {
        updatedConditions = [...activeConditions, updatedCondition];
      }
      
      setActiveConditions(updatedConditions);
    }
  };

  const removeCondition = (conditionId: string) => {
    setActiveConditions(prev => prev.filter(c => c.id !== conditionId));
  };

  const applyFilters = () => {
    onApplyFilters(activeConditions);
  };

  const resetFilters = () => {
    setActiveConditions([]);
    onApplyFilters([]);
  };

  const loadPreset = (presetName: string) => {
    const preset = savedPresets.find(p => p.name === presetName);
    if (preset) {
      setActiveConditions(preset.conditions);
      setSelectedPreset(presetName);
      onApplyFilters(preset.conditions);
    }
  };

  const saveCurrentPreset = () => {
    if (presetName.trim() && onSavePreset) {
      onSavePreset(presetName.trim(), activeConditions);
      setPresetName('');
    }
  };

  const renderConditionInput = (condition: StockScreeningCondition) => {
    switch (condition.type) {
      case 'range':
        const min = condition.min || 0;
        const max = condition.max || 100;
        const [low, high] = condition.value as [number, number];
        
        return (
          <div className="space-y-2">
            <div className="flex justify-between text-sm text-gray-600">
              <span>{low.toFixed(1)}{condition.unit}</span>
              <span>{high.toFixed(1)}{condition.unit}</span>
            </div>
            <div className="relative">
              <div className="absolute inset-0 bg-gradient-to-r from-green-400 via-yellow-400 to-red-400 rounded-full"></div>
              <input
                type="range"
                min={min}
                max={max}
                value={low}
                onChange={(e) => handleConditionChange(
                  conditionGroups.find(g => g.conditions.includes(condition))?.id || '',
                  condition.id,
                  [parseFloat(e.target.value), high]
                )}
                className="absolute top-0 left-0 w-full h-2 appearance-none bg-transparent [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:h-4 [&::-webkit-slider-thumb]:w-4 [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-white [&::-webkit-slider-thumb]:border-2 [&::-webkit-slider-thumb]:border-blue-500 [&::-webkit-slider-thumb]:shadow-lg"
              />
              <input
                type="range"
                min={min}
                max={max}
                value={high}
                onChange={(e) => handleConditionChange(
                  conditionGroups.find(g => g.conditions.includes(condition))?.id || '',
                  condition.id,
                  [low, parseFloat(e.target.value)]
                )}
                className="absolute top-0 left-0 w-full h-2 appearance-none bg-transparent [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:h-4 [&::-webkit-slider-thumb]:w-4 [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-white [&::-webkit-slider-thumb]:border-2 [&::-webkit-slider-thumb]:border-blue-500 [&::-webkit-slider-thumb]:shadow-lg"
              />
            </div>
          </div>
        );

      case 'select':
        return (
          <select
            value={condition.value as string}
            onChange={(e) => handleConditionChange(
              conditionGroups.find(g => g.conditions.includes(condition))?.id || '',
              condition.id,
              e.target.value
            )}
            className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            {condition.options?.map(option => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        );

      case 'boolean':
        return (
          <div className="flex items-center">
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={condition.value as boolean}
                onChange={(e) => handleConditionChange(
                  conditionGroups.find(g => g.conditions.includes(condition))?.id || '',
                  condition.id,
                  e.target.checked
                )}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
            </label>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-lg border border-gray-200 p-6 h-full overflow-y-auto">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-800 flex items-center gap-2">
          <Filter className="w-6 h-6 text-blue-600" />
          智能筛选器
        </h2>
        <p className="text-gray-600 text-sm mt-1">
          设置多维度条件，精准筛选A股股票
        </p>
      </div>

      {/* 筛选条件组 */}
      <div className="space-y-4">
        {conditionGroups.map(group => (
          <div key={group.id} className="border border-gray-200 rounded-lg overflow-hidden">
            <button
              onClick={() => toggleGroup(group.id)}
              className="w-full flex items-center justify-between p-4 bg-gray-50 hover:bg-gray-100 transition-colors"
            >
              <div className="flex items-center gap-3">
                {group.icon}
                <span className="font-semibold text-gray-700">{group.title}</span>
                <span className="text-xs px-2 py-1 bg-blue-100 text-blue-700 rounded-full">
                  {group.conditions.length} 个条件
                </span>
              </div>
              {expandedGroups[group.id] ? (
                <ChevronDown className="w-5 h-5 text-gray-500" />
              ) : (
                <ChevronRight className="w-5 h-5 text-gray-500" />
              )}
            </button>

            {expandedGroups[group.id] && (
              <div className="p-4 space-y-4 bg-white">
                {group.conditions.map(condition => (
                  <div key={condition.id} className="space-y-2">
                    <div className="flex justify-between items-center">
                      <label className="text-sm font-medium text-gray-700">
                        {condition.name}
                      </label>
                      <span className="text-xs text-gray-500">
                        {activeConditions.some(c => c.id === condition.id) ? '✓ 已启用' : ''}
                      </span>
                    </div>
                    {renderConditionInput(condition)}
                  </div>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>

      {/* 已选条件 */}
      {activeConditions.length > 0 && (
        <div className="mt-6">
          <h3 className="text-lg font-semibold text-gray-800 mb-3">已选条件 ({activeConditions.length})</h3>
          <div className="flex flex-wrap gap-2">
            {activeConditions.map(condition => (
              <div
                key={condition.id}
                className="flex items-center gap-2 px-3 py-2 bg-blue-50 border border-blue-200 rounded-lg"
              >
                <span className="text-sm font-medium text-blue-700">
                  {condition.name}: {(() => {
                    if (condition.type === 'range') {
                      const [low, high] = condition.value as [number, number];
                      return `${low.toFixed(1)}-${high.toFixed(1)}${condition.unit || ''}`;
                    } else if (condition.type === 'select') {
                      return condition.options?.find(opt => opt.value === condition.value)?.label || condition.value;
                    } else if (condition.type === 'boolean') {
                      return condition.value ? '是' : '否';
                    }
                    return condition.value;
                  })()}
                </span>
                <button
                  onClick={() => removeCondition(condition.id)}
                  className="text-blue-500 hover:text-blue-700"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 预设管理 */}
      {savedPresets.length > 0 && (
        <div className="mt-6">
          <h3 className="text-lg font-semibold text-gray-800 mb-3">筛选预设</h3>
          <div className="flex flex-wrap gap-2">
            {savedPresets.map(preset => (
              <button
                key={preset.name}
                onClick={() => loadPreset(preset.name)}
                className={cn(
                  "px-3 py-2 text-sm rounded-lg transition-colors",
                  selectedPreset === preset.name
                    ? "bg-blue-600 text-white"
                    : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                )}
              >
                {preset.name}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* 操作按钮 */}
      <div className="mt-8 space-y-4">
        <div className="flex gap-3">
          <button
            onClick={applyFilters}
            disabled={isLoading}
            className="flex-1 flex items-center justify-center gap-2 px-4 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                筛选中...
              </>
            ) : (
              <>
                <Search className="w-4 h-4" />
                应用筛选 ({activeConditions.length})
              </>
            )}
          </button>
          <button
            onClick={resetFilters}
            className="px-4 py-3 border border-gray-300 text-gray-700 font-semibold rounded-lg hover:bg-gray-50 transition-colors"
          >
            重置
          </button>
        </div>

        {onSavePreset && (
          <div className="flex gap-2">
            <input
              type="text"
              value={presetName}
              onChange={(e) => setPresetName(e.target.value)}
              placeholder="输入预设名称"
              className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
            <button
              onClick={saveCurrentPreset}
              disabled={!presetName.trim() || activeConditions.length === 0}
              className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white font-semibold rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Save className="w-4 h-4" />
              保存预设
            </button>
          </div>
        )}
      </div>

      {/* 使用提示 */}
      <div className="mt-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
        <h4 className="font-semibold text-yellow-800 mb-2">使用提示</h4>
        <ul className="text-sm text-yellow-700 space-y-1">
          <li>• 每个条件组可以展开/折叠，便于管理</li>
          <li>• 启用的条件会显示在"已选条件"区域</li>
          <li>• 可以保存常用筛选组合为预设</li>
          <li>• 筛选结果会实时更新</li>
        </ul>
      </div>
    </div>
  );
};