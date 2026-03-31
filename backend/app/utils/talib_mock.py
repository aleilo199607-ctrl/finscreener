"""
TA-LIB 模拟模块
由于TA-LIB需要C扩展，在Railway部署中可能导致问题
这个模块提供基本的TA-LIB功能模拟，用于开发和测试
"""

import numpy as np

# 简单移动平均线
def MA(data, timeperiod=30):
    """移动平均线"""
    if len(data) < timeperiod:
        return np.full(len(data), np.nan)
    
    result = np.zeros(len(data))
    for i in range(len(data)):
        if i < timeperiod - 1:
            result[i] = np.nan
        else:
            result[i] = np.mean(data[i - timeperiod + 1:i + 1])
    return result

# 指数移动平均线
def EMA(data, timeperiod=30):
    """指数移动平均线"""
    if len(data) < timeperiod:
        return np.full(len(data), np.nan)
    
    result = np.zeros(len(data))
    alpha = 2 / (timeperiod + 1)
    
    # 第一天的EMA是当天的值
    result[0] = data[0]
    
    for i in range(1, len(data)):
        result[i] = alpha * data[i] + (1 - alpha) * result[i - 1]
    
    # 前timeperiod-1个值为NaN
    result[:timeperiod - 1] = np.nan
    return result

# RSI指标
def RSI(data, timeperiod=14):
    """相对强弱指数"""
    if len(data) < timeperiod + 1:
        return np.full(len(data), np.nan)
    
    deltas = np.diff(data)
    seed = deltas[:timeperiod]
    up = seed[seed >= 0].sum() / timeperiod
    down = -seed[seed < 0].sum() / timeperiod
    rs = up / down if down != 0 else 0
    rsi = 100 - 100 / (1 + rs)
    
    result = np.zeros(len(data))
    result[:timeperiod] = np.nan
    result[timeperiod] = rsi
    
    for i in range(timeperiod + 1, len(data)):
        delta = deltas[i - 1]
        
        if delta > 0:
            upval = delta
            downval = 0
        else:
            upval = 0
            downval = -delta
        
        up = (up * (timeperiod - 1) + upval) / timeperiod
        down = (down * (timeperiod - 1) + downval) / timeperiod
        
        rs = up / down if down != 0 else 0
        rsi = 100 - 100 / (1 + rs)
        result[i] = rsi
    
    return result

# MACD指标
def MACD(data, fastperiod=12, slowperiod=26, signalperiod=9):
    """MACD指标"""
    ema_fast = EMA(data, fastperiod)
    ema_slow = EMA(data, slowperiod)
    macd_line = ema_fast - ema_slow
    signal_line = EMA(macd_line[~np.isnan(macd_line)], signalperiod)
    hist = macd_line - signal_line
    
    # 确保返回的数组长度一致
    full_signal = np.full(len(data), np.nan)
    full_hist = np.full(len(data), np.nan)
    
    valid_indices = ~np.isnan(signal_line)
    if valid_indices.any():
        start_idx = len(data) - len(signal_line[valid_indices])
        full_signal[start_idx:] = signal_line[valid_indices]
        full_hist[start_idx:] = hist[valid_indices]
    
    return macd_line, full_signal, full_hist

# 布林带
def BBANDS(data, timeperiod=20, nbdevup=2, nbdevdn=2):
    """布林带"""
    if len(data) < timeperiod:
        upper = np.full(len(data), np.nan)
        middle = np.full(len(data), np.nan)
        lower = np.full(len(data), np.nan)
        return upper, middle, lower
    
    middle = MA(data, timeperiod)
    std = np.zeros(len(data))
    
    for i in range(len(data)):
        if i < timeperiod - 1:
            std[i] = np.nan
        else:
            std[i] = np.std(data[i - timeperiod + 1:i + 1])
    
    upper = middle + (std * nbdevup)
    lower = middle - (std * nbdevdn)
    
    return upper, middle, lower

# 随机指标
def STOCH(high, low, close, fastk_period=14, slowk_period=3, slowd_period=3):
    """随机指标"""
    length = len(close)
    slowk = np.full(length, np.nan)
    slowd = np.full(length, np.nan)
    
    for i in range(fastk_period - 1, length):
        high_range = high[i - fastk_period + 1:i + 1]
        low_range = low[i - fastk_period + 1:i + 1]
        current_close = close[i]
        
        highest_high = np.max(high_range)
        lowest_low = np.min(low_range)
        
        if highest_high != lowest_low:
            fastk = 100 * (current_close - lowest_low) / (highest_high - lowest_low)
        else:
            fastk = 50
        
        if i >= fastk_period + slowk_period - 2:
            fastk_values = slowk[i - slowk_period + 1:i + 1]
            slowk[i] = np.mean(fastk_values[~np.isnan(fastk_values)])
            
            if i >= fastk_period + slowk_period + slowd_period - 3:
                slowk_values = slowk[i - slowd_period + 1:i + 1]
                slowd[i] = np.mean(slowk_values[~np.isnan(slowk_values)])
    
    return slowk, slowd

# 提供一个全局可用的talib模块接口
class MockTALib:
    """TA-LIB模拟类"""
    
    @staticmethod
    def MA(data, timeperiod=30):
        return MA(data, timeperiod)
    
    @staticmethod
    def EMA(data, timeperiod=30):
        return EMA(data, timeperiod)
    
    @staticmethod
    def RSI(data, timeperiod=14):
        return RSI(data, timeperiod)
    
    @staticmethod
    def MACD(data, fastperiod=12, slowperiod=26, signalperiod=9):
        return MACD(data, fastperiod, slowperiod, signalperiod)
    
    @staticmethod
    def BBANDS(data, timeperiod=20, nbdevup=2, nbdevdn=2):
        return BBANDS(data, timeperiod, nbdevup, nbdevdn)
    
    @staticmethod
    def STOCH(high, low, close, fastk_period=14, slowk_period=3, slowd_period=3):
        return STOCH(high, low, close, fastk_period, slowk_period, slowd_period)