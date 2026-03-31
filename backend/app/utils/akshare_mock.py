"""
AkShare 模拟模块
由于AkShare可能版本问题，创建模拟模块确保应用能正常运行
"""

import pandas as pd
import numpy as np
import warnings
from typing import Dict, List, Optional, Any
import json

warnings.filterwarnings('ignore')

class MockAkShare:
    """AkShare模拟类"""
    
    @staticmethod
    def stock_zh_a_spot_em() -> pd.DataFrame:
        """获取A股实时行情数据（模拟）"""
        # 创建一个模拟的A股行情数据
        data = {
            '代码': ['000001.SZ', '000002.SZ', '000858.SZ', '002415.SZ'],
            '名称': ['平安银行', '万科A', '五粮液', '海康威视'],
            '最新价': [10.20, 8.75, 145.60, 32.80],
            '涨跌幅': [1.23, -0.56, 2.34, 0.78],
            '涨跌额': [0.12, -0.05, 3.33, 0.25],
            '成交量(手)': [1234567, 876543, 345678, 2345678],
            '成交额(万元)': [45678.9, 23456.7, 12345.6, 34567.8],
            '振幅': [2.34, 1.56, 3.21, 1.89],
            '最高': [10.35, 8.85, 148.90, 33.10],
            '最低': [10.05, 8.65, 142.50, 32.50],
            '今开': [10.15, 8.80, 145.00, 32.70],
            '昨收': [10.08, 8.80, 142.27, 32.55],
            '量比': [1.23, 0.89, 1.56, 1.12],
            '换手率': [0.56, 0.34, 0.78, 1.23],
            '市盈率(动态)': [8.9, 6.7, 25.6, 18.9],
            '市净率': [0.89, 0.67, 4.56, 3.45],
            '总市值': [1987.65, 1567.89, 5678.23, 3456.78],
            '流通市值': [1456.78, 1234.56, 4567.89, 2345.67]
        }
        return pd.DataFrame(data)
    
    @staticmethod
    def stock_zh_a_hist(symbol: str, period: str = "daily", start_date: str = "", end_date: str = "") -> pd.DataFrame:
        """获取股票历史数据（模拟）"""
        # 模拟一些历史数据
        dates = pd.date_range(start='2026-01-01', end='2026-03-30', freq='D')
        data = {
            '日期': dates,
            '开盘': np.random.uniform(10, 20, len(dates)),
            '收盘': np.random.uniform(10, 20, len(dates)),
            '最高': np.random.uniform(15, 25, len(dates)),
            '最低': np.random.uniform(8, 15, len(dates)),
            '成交量': np.random.randint(100000, 1000000, len(dates)),
            '成交额': np.random.uniform(1000, 5000, len(dates)) * 10000,
            '振幅': np.random.uniform(1, 5, len(dates)),
            '涨跌幅': np.random.uniform(-5, 5, len(dates)),
            '涨跌额': np.random.uniform(-1, 1, len(dates)),
            '换手率': np.random.uniform(0.1, 3, len(dates))
        }
        return pd.DataFrame(data)
    
    @staticmethod
    def stock_zh_index_spot() -> pd.DataFrame:
        """获取指数实时行情（模拟）"""
        data = {
            '代码': ['sh000001', 'sz399001', 'sz399006', 'sh000300'],
            '名称': ['上证指数', '深证成指', '创业板指', '沪深300'],
            '最新价': [3200.56, 11000.78, 2200.45, 3800.23],
            '涨跌幅': [0.56, 0.78, 1.23, 0.67],
            '涨跌额': [18.23, 85.67, 26.78, 25.45],
            '成交量(手)': [123456789, 98765432, 45678912, 234567890],
            '成交额(万元)': [4567890.12, 3456789.23, 2345678.45, 5678901.23],
            '振幅': [1.23, 1.45, 2.12, 1.34],
            '最高': [3210.45, 11050.23, 2220.56, 3810.78],
            '最低': [3180.67, 10950.45, 2180.34, 3780.12],
            '今开': [3190.23, 10980.67, 2190.45, 3790.56],
            '昨收': [3182.33, 10915.11, 2174.67, 3774.78]
        }
        return pd.DataFrame(data)
    
    @staticmethod
    def stock_sector_detail(sector: str = "互联网", indicator: str = "涨跌幅") -> pd.DataFrame:
        """获取板块详情（模拟）"""
        sectors = ['互联网', '金融', '消费', '医药', '科技', '新能源', '制造业', '房地产']
        data = {
            '板块': sectors,
            '涨跌幅': np.random.uniform(-3, 5, len(sectors)),
            '主力净流入(万元)': np.random.uniform(-10000, 50000, len(sectors)) * 100,
            '成交额(万元)': np.random.uniform(10000, 100000, len(sectors)) * 100,
            '换手率': np.random.uniform(0.5, 3, len(sectors)),
            '股票数量': np.random.randint(50, 300, len(sectors))
        }
        return pd.DataFrame(data)
    
    @staticmethod
    def stock_hot_rank_em() -> pd.DataFrame:
        """获取热门股票排名（模拟）"""
        stocks = [
            {'代码': '000001.SZ', '名称': '平安银行', '热度': 95.6, '排名': 1},
            {'代码': '000858.SZ', '名称': '五粮液', '热度': 89.3, '排名': 2},
            {'代码': '002415.SZ', '名称': '海康威视', '热度': 85.7, '排名': 3},
            {'代码': '000002.SZ', '名称': '万科A', '热度': 82.4, '排名': 4},
            {'代码': '601318.SH', '名称': '中国平安', '热度': 78.9, '排名': 5},
            {'代码': '600519.SH', '名称': '贵州茅台', '热度': 76.5, '排名': 6},
            {'代码': '000333.SZ', '名称': '美的集团', '热度': 73.2, '排名': 7},
            {'代码': '000651.SZ', '名称': '格力电器', '热度': 70.8, '排名': 8},
            {'代码': '300750.SZ', '名称': '宁德时代', '热度': 68.4, '排名': 9},
            {'代码': '002594.SZ', '名称': '比亚迪', '热度': 65.9, '排名': 10}
        ]
        return pd.DataFrame(stocks)

# 全局导入函数
def try_import_akshare():
    """尝试导入AkShare，如果失败则返回模拟版本"""
    try:
        import akshare as ak
        print("✅ 成功导入真实AkShare库")
        return ak
    except ImportError as e:
        print(f"⚠️  无法导入AkShare库，使用模拟版本: {e}")
        return MockAkShare()
    except Exception as e:
        print(f"⚠️  AkShare导入错误，使用模拟版本: {e}")
        return MockAkShare()

# 创建全局实例
ak = try_import_akshare()