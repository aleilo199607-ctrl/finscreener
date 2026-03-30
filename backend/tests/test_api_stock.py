"""
股票API测试
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch

from app.schemas.stock import (
    StockQuoteResponse,
    StockDetailResponse,
    StockScreeningRequest,
    StockScreeningResponse,
)


class TestStockAPI:
    """股票API测试类"""

    def test_get_stock_list(self, test_client, mock_tushare):
        """测试获取股票列表"""
        response = test_client.get("/api/stocks")
        
        assert response.status_code == 200
        data = response.json()
        assert "stocks" in data
        assert len(data["stocks"]) > 0
        
        # 验证数据格式
        stock = data["stocks"][0]
        assert "symbol" in stock
        assert "name" in stock
        assert "latest_price" in stock
        assert "change_percent" in stock

    def test_get_stock_detail(self, test_client, mock_tushare, mock_ai_service):
        """测试获取股票详情"""
        response = test_client.get("/api/stocks/000001")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "symbol" in data
        assert data["symbol"] == "000001"
        assert "name" in data
        assert "basic_info" in data
        assert "quote" in data
        assert "financials" in data
        assert "ai_summary" in data
        
        # 验证AI摘要
        assert data["ai_summary"] == "这是一只优秀的股票，具有良好的基本面和成长性。"

    def test_get_stock_kline(self, test_client, mock_tushare):
        """测试获取股票K线数据"""
        response = test_client.get("/api/stocks/000001/kline?period=1m")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "symbol" in data
        assert "period" in data
        assert "kline_data" in data
        
        kline_data = data["kline_data"]
        assert len(kline_data) > 0
        
        # 验证K线数据格式
        kline = kline_data[0]
        assert "date" in kline
        assert "open" in kline
        assert "high" in kline
        assert "low" in kline
        assert "close" in kline
        assert "volume" in kline

    @pytest.mark.parametrize("indicator", ["rsi", "macd", "kdj", "boll"])
    def test_get_technical_indicators(self, test_client, mock_tushare, indicator):
        """测试获取技术指标"""
        response = test_client.get(f"/api/stocks/000001/indicators/{indicator}")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "symbol" in data
        assert "indicator" in data
        assert indicator in data["indicator"]
        assert "data" in data
        
        # 验证数据格式
        indicator_data = data["data"]
        assert len(indicator_data) > 0
        assert "date" in indicator_data[0]
        assert indicator in indicator_data[0]

    def test_get_stock_financials(self, test_client, mock_tushare):
        """测试获取财务数据"""
        response = test_client.get("/api/stocks/000001/financials")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "symbol" in data
        assert "financials" in data
        
        financials = data["financials"]
        assert len(financials) > 0
        
        # 验证财务数据格式
        financial = financials[0]
        assert "period" in financial
        assert "revenue" in financial
        assert "net_income" in financial
        assert "eps" in financial
        assert "roe" in financial

    def test_screen_stocks(self, test_client, mock_tushare):
        """测试筛选股票"""
        screening_request = {
            "conditions": [
                {
                    "id": "pe_ratio",
                    "name": "市盈率",
                    "type": "range",
                    "value": [0, 15]
                },
                {
                    "id": "roe", 
                    "name": "净资产收益率",
                    "type": "range",
                    "value": [10, 30]
                }
            ],
            "sort_by": "pe_ratio",
            "sort_order": "asc",
            "page": 1,
            "page_size": 20
        }
        
        response = test_client.post("/api/stocks/screen", json=screening_request)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "stocks" in data
        assert "total" in data
        assert "page" in data
        assert "page_size" in data
        assert "total_pages" in data
        
        # 验证返回的股票数据
        stocks = data["stocks"]
        assert isinstance(stocks, list)

    def test_get_market_overview(self, test_client, mock_tushare):
        """测试获取市场概览"""
        response = test_client.get("/api/market/overview")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "shanghai" in data
        assert "shenzhen" in data
        assert "chi_next" in data
        assert "total_market_cap" in data
        assert "turnover" in data
        
        # 验证市场数据格式
        shanghai = data["shanghai"]
        assert "index" in shanghai
        assert "change" in shanghai
        assert "change_percent" in shanghai

    def test_get_hot_sectors(self, test_client, mock_tushare):
        """测试获取热门板块"""
        response = test_client.get("/api/market/hot-sectors")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "sectors" in data
        assert isinstance(data["sectors"], list)
        
        if len(data["sectors"]) > 0:
            sector = data["sectors"][0]
            assert "name" in sector
            assert "change_percent" in sector
            assert "top_stocks" in sector

    def test_generate_ai_summary(self, test_client, mock_tushare, mock_ai_service):
        """测试生成AI摘要"""
        response = test_client.post("/api/stocks/000001/summary")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "symbol" in data
        assert data["symbol"] == "000001"
        assert "summary" in data
        assert "generated_at" in data
        assert "provider" in data
        
        # 验证摘要内容
        assert data["summary"] == "这是一只优秀的股票，具有良好的基本面和成长性。"

    def test_search_stocks(self, test_client, mock_tushare):
        """测试搜索股票"""
        response = test_client.get("/api/stocks/search?q=平安")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "stocks" in data
        assert isinstance(data["stocks"], list)
        
        if len(data["stocks"]) > 0:
            stock = data["stocks"][0]
            assert "symbol" in stock
            assert "name" in stock
            assert "平安" in stock["name"]

    def test_get_stock_news(self, test_client):
        """测试获取股票新闻"""
        response = test_client.get("/api/stocks/000001/news")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "symbol" in data
        assert "news" in data
        assert isinstance(data["news"], list)

    def test_get_stock_not_found(self, test_client):
        """测试获取不存在的股票"""
        response = test_client.get("/api/stocks/999999")
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data

    def test_invalid_kline_period(self, test_client):
        """测试无效的K线周期"""
        response = test_client.get("/api/stocks/000001/kline?period=invalid")
        
        assert response.status_code == 422  # FastAPI验证错误

    def test_empty_screening_conditions(self, test_client):
        """测试空的筛选条件"""
        screening_request = {
            "conditions": [],
            "page": 1,
            "page_size": 20
        }
        
        response = test_client.post("/api/stocks/screen", json=screening_request)
        
        assert response.status_code == 200
        data = response.json()
        assert "stocks" in data
        assert len(data["stocks"]) >= 0  # 空条件应该返回所有股票或空列表

    @pytest.mark.asyncio
    async def test_stock_quote_schema(self):
        """测试股票报价schema验证"""
        quote_data = {
            "symbol": "000001",
            "name": "平安银行",
            "latest_price": 10.5,
            "change_amount": 0.2,
            "change_percent": 1.92,
            "open": 10.3,
            "high": 10.8,
            "low": 10.2,
            "volume": 1000000,
            "turnover": 10500000,
            "pe_ratio": 8.5,
            "pb_ratio": 0.9,
            "market_cap": 300000000000,
            "dividend_yield": 3.2,
        }
        
        # 验证schema可以正确创建
        quote = StockQuoteResponse(**quote_data)
        assert quote.symbol == "000001"
        assert quote.name == "平安银行"
        assert quote.latest_price == 10.5
        assert quote.change_percent == 1.92

    @pytest.mark.asyncio
    async def test_stock_screening_schema(self):
        """测试股票筛选schema验证"""
        screening_data = {
            "conditions": [
                {
                    "id": "pe_ratio",
                    "name": "市盈率",
                    "type": "range",
                    "value": [0, 15]
                }
            ],
            "sort_by": "pe_ratio",
            "sort_order": "asc",
            "page": 1,
            "page_size": 20
        }
        
        # 验证schema可以正确创建
        screening = StockScreeningRequest(**screening_data)
        assert len(screening.conditions) == 1
        assert screening.conditions[0].id == "pe_ratio"
        assert screening.conditions[0].value == [0, 15]
        assert screening.page == 1
        assert screening.page_size == 20

    def test_stock_endpoint_cache_headers(self, test_client):
        """测试API缓存头"""
        response = test_client.get("/api/stocks/000001")
        
        assert response.status_code == 200
        # 检查缓存相关头
        assert "Cache-Control" in response.headers
        assert "ETag" in response.headers or "Last-Modified" in response.headers

    def test_api_rate_limiting(self, test_client):
        """测试API限流（如果配置了限流）"""
        # 快速连续调用同一个端点多次
        for _ in range(10):
            response = test_client.get("/api/stocks")
            # 应该都能成功，除非配置了严格的限流
            assert response.status_code in [200, 429]

    @pytest.mark.integration
    def test_stock_data_consistency(self, test_client, mock_tushare):
        """测试股票数据一致性"""
        # 获取股票列表
        list_response = test_client.get("/api/stocks")
        assert list_response.status_code == 200
        stocks = list_response.json()["stocks"]
        
        if len(stocks) > 0:
            first_stock = stocks[0]
            symbol = first_stock["symbol"]
            
            # 获取该股票的详情
            detail_response = test_client.get(f"/api/stocks/{symbol}")
            assert detail_response.status_code == 200
            detail = detail_response.json()
            
            # 验证基本信息一致
            assert detail["symbol"] == first_stock["symbol"]
            assert detail["name"] == first_stock["name"]
            
            # 验证价格数据一致或有合理的差异
            list_price = first_stock["latest_price"]
            detail_price = detail["quote"]["latest_price"]
            
            # 价格应该相同或非常接近
            assert abs(list_price - detail_price) < 0.1

    def test_error_handling(self, test_client):
        """测试错误处理"""
        # 测试无效的股票代码格式
        response = test_client.get("/api/stocks/invalid-code-format")
        assert response.status_code == 422  # 验证错误
        
        # 测试无效的查询参数
        response = test_client.get("/api/stocks/000001/kline?period=1m&invalid_param=test")
        assert response.status_code == 200  # 额外参数应该被忽略
        
        # 测试缺失必需参数
        response = test_client.post("/api/stocks/screen", json={})
        assert response.status_code == 422  # 验证错误

    @pytest.mark.slow
    def test_performance_stock_screening(self, test_client, mock_tushare):
        """测试筛选性能"""
        import time
        
        start_time = time.time()
        
        screening_request = {
            "conditions": [
                {"id": "pe_ratio", "type": "range", "value": [0, 20]},
                {"id": "pb_ratio", "type": "range", "value": [0, 3]},
                {"id": "roe", "type": "range", "value": [10, 50]},
                {"id": "market_cap", "type": "range", "value": [1000000000, 1000000000000]},
            ],
            "page": 1,
            "page_size": 50
        }
        
        response = test_client.post("/api/stocks/screen", json=screening_request)
        end_time = time.time()
        
        assert response.status_code == 200
        execution_time = end_time - start_time
        
        # 筛选应该在合理时间内完成（这里设置为5秒）
        assert execution_time < 5.0, f"筛选耗时 {execution_time:.2f}秒，超过预期"
        
        print(f"筛选性能: {execution_time:.3f}秒")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])