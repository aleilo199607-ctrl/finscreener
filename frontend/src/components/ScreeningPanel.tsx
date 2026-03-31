import React, { useState, useCallback } from 'react';
import { Search, Filter, X, ChevronDown, ChevronRight, Save, Loader2, RotateCcw } from 'lucide-react';
import { cn } from '@/utils/cn';
import { StockScreeningCondition } from '@/types';

interface ScreeningConditionDef {
  id: string;
  name: string;
  type: 'range' | 'select' | 'boolean';
  min?: number;
  max?: number;
  step?: number;
  unit?: string;
  options?: Array<{ label: string; value: string }>;
  defaultValue: number | [number, number] | string | boolean;
  description?: string;
}

interface ConditionGroup {
  id: string;
  title: string;
  emoji: string;
  conditions: ScreeningConditionDef[];
}

interface ScreeningPanelProps {
  onApplyFilters: (conditions: StockScreeningCondition[]) => void;
  onSavePreset?: (name: string, conditions: StockScreeningCondition[]) => void;
  savedPresets?: Array<{ name: string; conditions: StockScreeningCondition[] }>;
  isLoading?: boolean;
}

// 所有筛选条件定义
const CONDITION_GROUPS: ConditionGroup[] = [
  {
    id: 'price-volume',
    title: '价格与量能',
    emoji: '💰',
    conditions: [
      { id: 'price_range', name: '股价区间', type: 'range', min: 0, max: 500, step: 0.5, unit: '元', defaultValue: [5, 100] },
      { id: 'price_change_pct', name: '涨跌幅', type: 'range', min: -20, max: 20, step: 0.1, unit: '%', defaultValue: [-10, 10] },
      { id: 'volume_ratio', name: '量比', type: 'range', min: 0, max: 10, step: 0.1, unit: 'x', defaultValue: [0.8, 3] },
      { id: 'turnover_rate', name: '换手率', type: 'range', min: 0, max: 30, step: 0.1, unit: '%', defaultValue: [1, 10] },
    ],
  },
  {
    id: 'financial',
    title: '财务指标',
    emoji: '📊',
    conditions: [
      { id: 'pe_ratio', name: '市盈率 (PE)', type: 'range', min: 0, max: 200, step: 1, unit: 'x', defaultValue: [5, 50] },
      { id: 'pb_ratio', name: '市净率 (PB)', type: 'range', min: 0, max: 20, step: 0.1, unit: 'x', defaultValue: [0.5, 5] },
      { id: 'roe', name: '净资产收益率 (ROE)', type: 'range', min: 0, max: 60, step: 0.5, unit: '%', defaultValue: [8, 30] },
    ],
  },
  {
    id: 'market',
    title: '市场属性',
    emoji: '🏷️',
    conditions: [
      {
        id: 'sector', name: '行业板块', type: 'select',
        options: [
          { label: '全部行业', value: '' },
          { label: '电子 / 半导体', value: '电子' },
          { label: '计算机 / 软件', value: '计算机' },
          { label: '医药生物', value: '医药' },
          { label: '银行 / 保险', value: '银行|保险' },
          { label: '新能源 / 光伏', value: '新能源|光伏|电池' },
          { label: '食品饮料', value: '食品饮料' },
          { label: '汽车', value: '汽车' },
          { label: '化工', value: '化工' },
          { label: '房地产', value: '房地产' },
          { label: '机械设备', value: '机械' },
        ],
        defaultValue: '',
      },
      {
        id: 'market_board', name: '上市板块', type: 'select',
        options: [
          { label: '全部', value: '' },
          { label: '主板', value: '主板' },
          { label: '创业板', value: '创业板' },
          { label: '科创板', value: '科创板' },
          { label: '北交所', value: '北交所' },
        ],
        defaultValue: '',
      },
    ],
  },
];

// 把面板条件转成后端需要的格式（由 ScreenerPage 调用）
export function panelConditionsToApi(actives: Record<string, any>) {
  const apiConditions: any[] = [];
  let market = '';
  let industry = '';

  for (const [id, value] of Object.entries(actives)) {
    if (value === null || value === undefined) continue;

    const fieldMap: Record<string, string> = {
      price_range: 'close',
      price_change_pct: 'pct_chg',
      volume_ratio: 'vol',
      turnover_rate: 'turnover_rate',
      pe_ratio: 'pe',
      pb_ratio: 'pb',
      roe: 'roe',
    };

    if (id in fieldMap && Array.isArray(value)) {
      const [lo, hi] = value as [number, number];
      const field = fieldMap[id];
      if (lo > 0) apiConditions.push({ field, operator: 'gte', value: lo });
      const def = CONDITION_GROUPS.flatMap(g => g.conditions).find(c => c.id === id);
      const maxDefault = (def?.defaultValue as [number, number])?.[1] ?? 9999;
      if (hi < (def?.max ?? 9999) || hi !== maxDefault) {
        apiConditions.push({ field, operator: 'lte', value: hi });
      }
    } else if (id === 'sector') {
      industry = value as string;
    } else if (id === 'market_board') {
      market = value as string;
    }
  }

  return { conditions: apiConditions, market, industry };
}

// ─── 双滑块 + 数字输入框组件 ────────────────────────────────────────────────

interface RangeInputProps {
  min: number;
  max: number;
  step: number;
  value: [number, number];
  unit: string;
  onChange: (v: [number, number]) => void;
}

const RangeInput: React.FC<RangeInputProps> = ({ min, max, step, value, unit, onChange }) => {
  const [low, high] = value;

  const clamp = (v: number) => Math.max(min, Math.min(max, v));
  const fmt = (v: number) => step < 1 ? v.toFixed(step < 0.1 ? 2 : 1) : String(v);

  const handleLowInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const v = parseFloat(e.target.value);
    if (!isNaN(v)) onChange([clamp(Math.min(v, high - step)), high]);
  };
  const handleHighInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const v = parseFloat(e.target.value);
    if (!isNaN(v)) onChange([low, clamp(Math.max(v, low + step))]);
  };
  const handleLowSlider = (e: React.ChangeEvent<HTMLInputElement>) => {
    const v = parseFloat(e.target.value);
    onChange([Math.min(v, high - step), high]);
  };
  const handleHighSlider = (e: React.ChangeEvent<HTMLInputElement>) => {
    const v = parseFloat(e.target.value);
    onChange([low, Math.max(v, low + step)]);
  };

  const pctLow = ((low - min) / (max - min)) * 100;
  const pctHigh = ((high - min) / (max - min)) * 100;

  return (
    <div className="space-y-3">
      {/* 数字输入框行 */}
      <div className="flex items-center gap-2">
        <div className="flex-1">
          <label className="block text-[10px] text-gray-400 mb-1">最小值</label>
          <div className="flex items-center border border-gray-300 rounded-lg overflow-hidden focus-within:ring-2 focus-within:ring-blue-400 focus-within:border-blue-400 bg-white">
            <input
              type="number"
              value={fmt(low)}
              step={step}
              min={min}
              max={high - step}
              onChange={handleLowInput}
              className="w-full px-2 py-1.5 text-sm text-center outline-none bg-transparent"
            />
            {unit && <span className="pr-2 text-xs text-gray-400 whitespace-nowrap">{unit}</span>}
          </div>
        </div>
        <div className="text-gray-300 text-sm mt-4">~</div>
        <div className="flex-1">
          <label className="block text-[10px] text-gray-400 mb-1">最大值</label>
          <div className="flex items-center border border-gray-300 rounded-lg overflow-hidden focus-within:ring-2 focus-within:ring-blue-400 focus-within:border-blue-400 bg-white">
            <input
              type="number"
              value={fmt(high)}
              step={step}
              min={low + step}
              max={max}
              onChange={handleHighInput}
              className="w-full px-2 py-1.5 text-sm text-center outline-none bg-transparent"
            />
            {unit && <span className="pr-2 text-xs text-gray-400 whitespace-nowrap">{unit}</span>}
          </div>
        </div>
      </div>

      {/* 双轨滑块 */}
      <div className="relative h-5 flex items-center">
        {/* 背景轨道 */}
        <div className="absolute w-full h-1.5 bg-gray-200 rounded-full" />
        {/* 选中范围高亮 */}
        <div
          className="absolute h-1.5 bg-blue-500 rounded-full"
          style={{ left: `${pctLow}%`, right: `${100 - pctHigh}%` }}
        />
        {/* 低值滑块 */}
        <input
          type="range"
          min={min} max={max} step={step}
          value={low}
          onChange={handleLowSlider}
          className="absolute w-full h-1.5 appearance-none bg-transparent cursor-pointer
            [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:h-4
            [&::-webkit-slider-thumb]:w-4 [&::-webkit-slider-thumb]:rounded-full
            [&::-webkit-slider-thumb]:bg-white [&::-webkit-slider-thumb]:border-2
            [&::-webkit-slider-thumb]:border-blue-500 [&::-webkit-slider-thumb]:shadow-md
            [&::-webkit-slider-thumb]:cursor-grab [&::-webkit-slider-thumb]:active:cursor-grabbing"
        />
        {/* 高值滑块 */}
        <input
          type="range"
          min={min} max={max} step={step}
          value={high}
          onChange={handleHighSlider}
          className="absolute w-full h-1.5 appearance-none bg-transparent cursor-pointer
            [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:h-4
            [&::-webkit-slider-thumb]:w-4 [&::-webkit-slider-thumb]:rounded-full
            [&::-webkit-slider-thumb]:bg-white [&::-webkit-slider-thumb]:border-2
            [&::-webkit-slider-thumb]:border-blue-500 [&::-webkit-slider-thumb]:shadow-md
            [&::-webkit-slider-thumb]:cursor-grab [&::-webkit-slider-thumb]:active:cursor-grabbing"
        />
      </div>
      <div className="flex justify-between text-[10px] text-gray-400">
        <span>{fmt(min)}{unit}</span>
        <span>{fmt(max)}{unit}</span>
      </div>
    </div>
  );
};

// ─── 主组件 ────────────────────────────────────────────────────────────────────

export const ScreeningPanel: React.FC<ScreeningPanelProps> = ({
  onApplyFilters,
  onSavePreset,
  savedPresets = [],
  isLoading = false,
}) => {
  const [expandedGroups, setExpandedGroups] = useState<Record<string, boolean>>({
    'price-volume': true,
    'financial': false,
    'market': true,
  });

  // 每个条件 id -> 当前值（null 表示未启用）
  const [activeValues, setActiveValues] = useState<Record<string, any>>({});
  // 记录哪些条件被"勾选启用"
  const [enabledIds, setEnabledIds] = useState<Set<string>>(new Set());
  const [presetName, setPresetName] = useState('');

  const toggleGroup = (id: string) => setExpandedGroups(p => ({ ...p, [id]: !p[id] }));

  const allDefs = CONDITION_GROUPS.flatMap(g => g.conditions);

  const getDefaultValue = (def: ScreeningConditionDef) => {
    return def.defaultValue;
  };

  const getValue = (def: ScreeningConditionDef) => {
    return activeValues[def.id] ?? def.defaultValue;
  };

  const toggleEnable = (def: ScreeningConditionDef) => {
    setEnabledIds(prev => {
      const next = new Set(prev);
      if (next.has(def.id)) {
        next.delete(def.id);
      } else {
        next.add(def.id);
        // 首次启用时保证有值
        if (!(def.id in activeValues)) {
          setActiveValues(pv => ({ ...pv, [def.id]: def.defaultValue }));
        }
      }
      return next;
    });
  };

  const handleChange = (id: string, value: any) => {
    setActiveValues(pv => ({ ...pv, [id]: value }));
    // 修改时自动启用
    setEnabledIds(prev => {
      const next = new Set(prev);
      next.add(id);
      return next;
    });
  };

  const resetCondition = (id: string) => {
    const def = allDefs.find(d => d.id === id);
    if (def) setActiveValues(pv => ({ ...pv, [id]: def.defaultValue }));
    setEnabledIds(prev => {
      const next = new Set(prev);
      next.delete(id);
      return next;
    });
  };

  // 构建传给父组件的条件列表
  const buildConditions = useCallback((): StockScreeningCondition[] => {
    return Array.from(enabledIds).map(id => {
      const def = allDefs.find(d => d.id === id)!;
      const value = activeValues[id] ?? def.defaultValue;
      return {
        id: def.id,
        name: def.name,
        type: def.type,
        min: def.min,
        max: def.max,
        unit: def.unit,
        options: def.options,
        value,
      } as StockScreeningCondition;
    });
  }, [enabledIds, activeValues, allDefs]);

  const applyFilters = () => {
    onApplyFilters(buildConditions());
  };

  const resetAll = () => {
    setActiveValues({});
    setEnabledIds(new Set());
    onApplyFilters([]);
  };

  const savePreset = () => {
    if (presetName.trim() && onSavePreset) {
      onSavePreset(presetName.trim(), buildConditions());
      setPresetName('');
    }
  };

  const loadPreset = (preset: { name: string; conditions: StockScreeningCondition[] }) => {
    const newValues: Record<string, any> = {};
    const newEnabled = new Set<string>();
    preset.conditions.forEach(c => {
      newValues[c.id] = c.value;
      newEnabled.add(c.id);
    });
    setActiveValues(newValues);
    setEnabledIds(newEnabled);
    onApplyFilters(preset.conditions);
  };

  const enabledCount = enabledIds.size;

  return (
    <div className="bg-white rounded-xl border border-gray-200 overflow-hidden flex flex-col h-full">
      {/* 标题栏 */}
      <div className="px-4 py-3 bg-gradient-to-r from-blue-600 to-blue-500 text-white">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Filter className="w-4 h-4" />
            <span className="font-semibold text-sm">智能筛选器</span>
            {enabledCount > 0 && (
              <span className="text-xs bg-white/20 px-2 py-0.5 rounded-full">
                已启用 {enabledCount} 项
              </span>
            )}
          </div>
          {enabledCount > 0 && (
            <button onClick={resetAll} className="text-xs text-white/80 hover:text-white flex items-center gap-1">
              <RotateCcw className="w-3 h-3" />
              重置
            </button>
          )}
        </div>
        <p className="text-xs text-blue-100 mt-1">勾选条件并输入数值后点击"开始筛选"</p>
      </div>

      {/* 条件组列表 */}
      <div className="flex-1 overflow-y-auto">
        {CONDITION_GROUPS.map(group => (
          <div key={group.id} className="border-b border-gray-100 last:border-b-0">
            {/* 组标题 */}
            <button
              onClick={() => toggleGroup(group.id)}
              className="w-full flex items-center justify-between px-4 py-2.5 bg-gray-50 hover:bg-gray-100 transition-colors"
            >
              <div className="flex items-center gap-2">
                <span>{group.emoji}</span>
                <span className="font-medium text-gray-700 text-sm">{group.title}</span>
                {/* 本组已启用数 */}
                {group.conditions.filter(c => enabledIds.has(c.id)).length > 0 && (
                  <span className="text-[10px] bg-blue-100 text-blue-700 px-1.5 py-0.5 rounded-full">
                    {group.conditions.filter(c => enabledIds.has(c.id)).length}
                  </span>
                )}
              </div>
              {expandedGroups[group.id]
                ? <ChevronDown className="w-4 h-4 text-gray-400" />
                : <ChevronRight className="w-4 h-4 text-gray-400" />}
            </button>

            {/* 条件列表 */}
            {expandedGroups[group.id] && (
              <div className="px-4 py-3 space-y-4 bg-white">
                {group.conditions.map(def => {
                  const enabled = enabledIds.has(def.id);
                  const val = getValue(def);

                  return (
                    <div
                      key={def.id}
                      className={cn(
                        'rounded-lg p-3 border transition-all',
                        enabled
                          ? 'border-blue-300 bg-blue-50/40'
                          : 'border-gray-200 bg-white'
                      )}
                    >
                      {/* 条件头：勾选框 + 名称 + 重置 */}
                      <div className="flex items-center justify-between mb-2">
                        <label className="flex items-center gap-2 cursor-pointer select-none">
                          <input
                            type="checkbox"
                            checked={enabled}
                            onChange={() => toggleEnable(def)}
                            className="w-3.5 h-3.5 rounded border-gray-300 text-blue-600 cursor-pointer"
                          />
                          <span className={cn('text-sm font-medium', enabled ? 'text-blue-700' : 'text-gray-700')}>
                            {def.name}
                          </span>
                        </label>
                        {enabled && (
                          <button
                            onClick={() => resetCondition(def.id)}
                            className="text-xs text-gray-400 hover:text-gray-600 flex items-center gap-0.5"
                          >
                            <RotateCcw className="w-3 h-3" />
                            还原
                          </button>
                        )}
                      </div>

                      {/* 条件输入 */}
                      <div className={cn(!enabled && 'opacity-50 pointer-events-none')}>
                        {def.type === 'range' && (
                          <RangeInput
                            min={def.min!}
                            max={def.max!}
                            step={def.step ?? 1}
                            unit={def.unit ?? ''}
                            value={val as [number, number]}
                            onChange={v => handleChange(def.id, v)}
                          />
                        )}

                        {def.type === 'select' && (
                          <select
                            value={val as string}
                            onChange={e => handleChange(def.id, e.target.value)}
                            className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 bg-white"
                          >
                            {def.options?.map(opt => (
                              <option key={opt.value} value={opt.value}>{opt.label}</option>
                            ))}
                          </select>
                        )}

                        {def.type === 'boolean' && (
                          <label className="flex items-center gap-2 cursor-pointer">
                            <input
                              type="checkbox"
                              checked={val as boolean}
                              onChange={e => handleChange(def.id, e.target.checked)}
                              className="w-4 h-4 rounded text-blue-600"
                            />
                            <span className="text-sm text-gray-600">启用此条件</span>
                          </label>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        ))}
      </div>

      {/* 预设区域 */}
      {savedPresets.length > 0 && (
        <div className="px-4 py-3 border-t border-gray-100 bg-gray-50">
          <p className="text-xs text-gray-500 font-medium mb-2">我的预设</p>
          <div className="flex flex-wrap gap-1.5">
            {savedPresets.map(p => (
              <button
                key={p.name}
                onClick={() => loadPreset(p)}
                className="px-2.5 py-1 text-xs bg-white border border-gray-200 rounded-lg hover:bg-blue-50 hover:border-blue-300 hover:text-blue-700 transition-colors"
              >
                {p.name}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* 底部操作栏 */}
      <div className="px-4 py-3 border-t border-gray-200 bg-white space-y-2">
        {/* 保存预设行 */}
        {onSavePreset && enabledCount > 0 && (
          <div className="flex gap-2">
            <input
              type="text"
              value={presetName}
              onChange={e => setPresetName(e.target.value)}
              placeholder="预设名称..."
              className="flex-1 px-2.5 py-1.5 text-xs border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-400"
              onKeyDown={e => e.key === 'Enter' && savePreset()}
            />
            <button
              onClick={savePreset}
              disabled={!presetName.trim()}
              className="flex items-center gap-1 px-3 py-1.5 text-xs bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-40"
            >
              <Save className="w-3 h-3" />
              保存
            </button>
          </div>
        )}

        {/* 主按钮 */}
        <div className="flex gap-2">
          <button
            onClick={applyFilters}
            disabled={isLoading}
            className="flex-1 flex items-center justify-center gap-2 px-4 py-2.5 bg-blue-600 text-white text-sm font-semibold rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
          >
            {isLoading ? (
              <><Loader2 className="w-4 h-4 animate-spin" />筛选中...</>
            ) : (
              <><Search className="w-4 h-4" />开始筛选{enabledCount > 0 ? `（${enabledCount}）` : ''}</>
            )}
          </button>
          {enabledCount > 0 && (
            <button
              onClick={resetAll}
              className="px-3 py-2.5 border border-gray-300 text-gray-600 text-sm rounded-lg hover:bg-gray-50"
            >
              <X className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>
    </div>
  );
};
