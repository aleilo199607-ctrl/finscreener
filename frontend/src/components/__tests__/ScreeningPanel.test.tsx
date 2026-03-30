import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { ScreeningPanel } from '../ScreeningPanel';
import { StockScreeningCondition } from '@/types';

describe('ScreeningPanel', () => {
  const mockOnApplyFilters = vi.fn();
  const mockOnSavePreset = vi.fn();
  
  const mockPresets = [
    { name: '价值投资', conditions: [{ id: 'pe_ratio', name: '市盈率', type: 'range', value: [0, 15] }] },
    { name: '成长股', conditions: [{ id: 'roe', name: '净资产收益率', type: 'range', value: [15, 50] }] },
  ];

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('渲染筛选面板组件', () => {
    render(
      <ScreeningPanel
        onApplyFilters={mockOnApplyFilters}
        onSavePreset={mockOnSavePreset}
        savedPresets={mockPresets}
      />
    );

    // 检查标题
    expect(screen.getByText('智能筛选器')).toBeInTheDocument();
    expect(screen.getByText('设置多维度条件，精准筛选A股股票')).toBeInTheDocument();

    // 检查条件组
    expect(screen.getByText('价格与量能')).toBeInTheDocument();
    expect(screen.getByText('技术指标')).toBeInTheDocument();
    expect(screen.getByText('财务指标')).toBeInTheDocument();
    expect(screen.getByText('市场表现')).toBeInTheDocument();

    // 检查预设
    expect(screen.getByText('价值投资')).toBeInTheDocument();
    expect(screen.getByText('成长股')).toBeInTheDocument();

    // 检查操作按钮
    expect(screen.getByText('应用筛选 (0)')).toBeInTheDocument();
    expect(screen.getByText('重置')).toBeInTheDocument();
  });

  it('展开和折叠条件组', () => {
    render(<ScreeningPanel onApplyFilters={mockOnApplyFilters} />);

    // 默认展开价格与量能组
    expect(screen.getByText('价格区间')).toBeInTheDocument();

    // 点击技术指标组展开
    const technicalGroup = screen.getByText('技术指标');
    fireEvent.click(technicalGroup);
    
    // 应该显示技术指标条件
    expect(screen.getByText('RSI强弱指标')).toBeInTheDocument();

    // 再次点击应该折叠
    fireEvent.click(technicalGroup);
    expect(screen.queryByText('RSI强弱指标')).not.toBeInTheDocument();
  });

  it('选择筛选条件', () => {
    render(<ScreeningPanel onApplyFilters={mockOnApplyFilters} />);

    // 展开财务指标组
    fireEvent.click(screen.getByText('财务指标'));

    // 选择市盈率范围
    const peInputs = screen.getAllByRole('slider');
    expect(peInputs.length).toBeGreaterThan(0);

    // 修改市盈率范围
    fireEvent.change(peInputs[0], { target: { value: '10' } });
    fireEvent.change(peInputs[1], { target: { value: '25' } });

    // 检查已选条件显示
    expect(screen.getByText('市盈率(PE): 10.0-25.0')).toBeInTheDocument();
  });

  it('应用筛选条件', async () => {
    render(<ScreeningPanel onApplyFilters={mockOnApplyFilters} />);

    // 展开财务指标组并选择条件
    fireEvent.click(screen.getByText('财务指标'));
    const peInputs = screen.getAllByRole('slider');
    fireEvent.change(peInputs[0], { target: { value: '10' } });
    fireEvent.change(peInputs[1], { target: { value: '25' } });

    // 点击应用筛选按钮
    const applyButton = screen.getByText('应用筛选 (1)');
    fireEvent.click(applyButton);

    // 验证回调被调用
    await waitFor(() => {
      expect(mockOnApplyFilters).toHaveBeenCalledTimes(1);
      const conditions = mockOnApplyFilters.mock.calls[0][0];
      expect(conditions).toHaveLength(1);
      expect(conditions[0].id).toBe('pe_ratio');
      expect(conditions[0].value).toEqual([10, 25]);
    });
  });

  it('重置筛选条件', () => {
    render(<ScreeningPanel onApplyFilters={mockOnApplyFilters} />);

    // 选择一些条件
    fireEvent.click(screen.getByText('财务指标'));
    const peInputs = screen.getAllByRole('slider');
    fireEvent.change(peInputs[0], { target: { value: '10' } });
    fireEvent.change(peInputs[1], { target: { value: '25' } });

    // 检查条件已选择
    expect(screen.getByText('市盈率(PE): 10.0-25.0')).toBeInTheDocument();

    // 点击重置按钮
    const resetButton = screen.getByText('重置');
    fireEvent.click(resetButton);

    // 检查条件被清除
    expect(screen.queryByText('市盈率(PE): 10.0-25.0')).not.toBeInTheDocument();
    expect(mockOnApplyFilters).toHaveBeenCalledWith([]);
  });

  it('加载预设', async () => {
    render(
      <ScreeningPanel
        onApplyFilters={mockOnApplyFilters}
        onSavePreset={mockOnSavePreset}
        savedPresets={mockPresets}
      />
    );

    // 点击价值投资预设
    const valuePresetButton = screen.getByText('价值投资');
    fireEvent.click(valuePresetButton);

    // 验证回调被调用并传递预设条件
    await waitFor(() => {
      expect(mockOnApplyFilters).toHaveBeenCalledTimes(1);
      const conditions = mockOnApplyFilters.mock.calls[0][0];
      expect(conditions).toHaveLength(1);
      expect(conditions[0].id).toBe('pe_ratio');
      expect(conditions[0].value).toEqual([0, 15]);
    });
  });

  it('保存预设', async () => {
    render(
      <ScreeningPanel
        onApplyFilters={mockOnApplyFilters}
        onSavePreset={mockOnSavePreset}
        savedPresets={mockPresets}
      />
    );

    // 选择条件
    fireEvent.click(screen.getByText('财务指标'));
    const peInputs = screen.getAllByRole('slider');
    fireEvent.change(peInputs[0], { target: { value: '8' } });
    fireEvent.change(peInputs[1], { target: { value: '20' } });

    // 输入预设名称
    const presetInput = screen.getByPlaceholderText('输入预设名称');
    fireEvent.change(presetInput, { target: { value: '低PE策略' } });

    // 点击保存按钮
    const saveButton = screen.getByText('保存预设');
    fireEvent.click(saveButton);

    // 验证回调被调用
    await waitFor(() => {
      expect(mockOnSavePreset).toHaveBeenCalledTimes(1);
      expect(mockOnSavePreset).toHaveBeenCalledWith('低PE策略', [
        expect.objectContaining({
          id: 'pe_ratio',
          value: [8, 20],
        }),
      ]);
    });
  });

  it('显示加载状态', () => {
    render(
      <ScreeningPanel
        onApplyFilters={mockOnApplyFilters}
        isLoading={true}
      />
    );

    // 检查加载状态
    expect(screen.getByText('筛选中...')).toBeInTheDocument();
    expect(screen.getByText('筛选中...').closest('button')).toBeDisabled();
  });

  it('处理布尔类型条件', () => {
    render(<ScreeningPanel onApplyFilters={mockOnApplyFilters} />);

    // 展开技术指标组
    fireEvent.click(screen.getByText('技术指标'));

    // 找到5日线上穿20日线的切换开关
    const toggle = screen.getByRole('checkbox', { name: '' });
    expect(toggle).not.toBeChecked();

    // 切换开关
    fireEvent.click(toggle);
    expect(toggle).toBeChecked();

    // 检查条件已选择
    expect(screen.getByText('5日线上穿20日线: 是')).toBeInTheDocument();
  });

  it('处理选择类型条件', () => {
    render(<ScreeningPanel onApplyFilters={mockOnApplyFilters} />);

    // 展开技术指标组
    fireEvent.click(screen.getByText('技术指标'));

    // 找到MACD选择框
    const select = screen.getByRole('combobox');
    expect(select).toHaveValue('any');

    // 改变选择
    fireEvent.change(select, { target: { value: 'golden' } });

    // 检查条件已选择
    expect(screen.getByText('MACD金叉: 金叉向上')).toBeInTheDocument();
  });

  it('移除已选条件', () => {
    render(<ScreeningPanel onApplyFilters={mockOnApplyFilters} />);

    // 选择条件
    fireEvent.click(screen.getByText('财务指标'));
    const peInputs = screen.getAllByRole('slider');
    fireEvent.change(peInputs[0], { target: { value: '10' } });
    fireEvent.change(peInputs[1], { target: { value: '25' } });

    // 检查条件显示
    const conditionChip = screen.getByText('市盈率(PE): 10.0-25.0');
    expect(conditionChip).toBeInTheDocument();

    // 点击移除按钮
    const removeButton = conditionChip.parentElement!.querySelector('button');
    fireEvent.click(removeButton!);

    // 检查条件被移除
    expect(screen.queryByText('市盈率(PE): 10.0-25.0')).not.toBeInTheDocument();
  });

  it('空预设时不显示预设区域', () => {
    render(
      <ScreeningPanel
        onApplyFilters={mockOnApplyFilters}
        savedPresets={[]}
      />
    );

    // 不应该显示预设标题
    expect(screen.queryByText('筛选预设')).not.toBeInTheDocument();
  });

  it('空条件时禁用保存预设按钮', () => {
    render(
      <ScreeningPanel
        onApplyFilters={mockOnApplyFilters}
        onSavePreset={mockOnSavePreset}
      />
    );

    // 保存按钮应该被禁用
    const saveButton = screen.getByText('保存预设');
    expect(saveButton).toBeDisabled();

    // 输入预设名称
    const presetInput = screen.getByPlaceholderText('输入预设名称');
    fireEvent.change(presetInput, { target: { value: '测试预设' } });

    // 仍然应该被禁用，因为没有条件
    expect(saveButton).toBeDisabled();
  });
});