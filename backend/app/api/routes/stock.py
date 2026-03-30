from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.stock import (
    StockResponse, StockDailyResponse, StockFinancialResponse,
    StockMoneyFlowResponse, StockSummaryResponse, StockSummaryRequest,
    ScreeningCondition, ScreeningRequest, ScreeningResult,
    MarketIndicatorResponse, ApiResponse
)
from app.services.stock_service import stock_service
from app.services.ai_service import ai_service

router = APIRouter(prefix="/stocks", tags=["股票"])

@router.get("/", response_model=ApiResponse[List[StockResponse]])
async def get_stocks(
    market: Optional[str] = Query(None, description="市场类型: SH/SZ/BJ"),
    industry: Optional[str] = Query(None, description="行业"),
    limit: int = Query(100, ge=1, le=1000, description="限制数量"),
    session: AsyncSession = Depends(get_db)
):
    """获取股票列表"""
    try:
        stocks = await stock_service.get_stock_list(session, market, industry, limit)
        return ApiResponse.success_response(data=stocks, message="获取股票列表成功")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取股票列表失败: {str(e)}"
        )

@router.get("/{ts_code}", response_model=ApiResponse[StockDailyResponse])
async def get_stock_detail(
    ts_code: str,
    session: AsyncSession = Depends(get_db)
):
    """获取股票详情"""
    try:
        stock_detail = await stock_service.get_stock_detail(session, ts_code)
        if not stock_detail:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"未找到股票: {ts_code}"
            )
        return ApiResponse.success_response(data=stock_detail, message="获取股票详情成功")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取股票详情失败: {str(e)}"
        )

@router.get("/{ts_code}/kline", response_model=ApiResponse[List[dict]])
async def get_stock_kline(
    ts_code: str,
    period: str = Query("D", regex="^(D|W|M)$", description="周期: D日/W周/M月"),
    limit: int = Query(100, ge=1, le=1000, description="数据条数"),
    session: AsyncSession = Depends(get_db)
):
    """获取股票K线数据"""
    try:
        kline_data = await stock_service.get_stock_kline(session, ts_code, period, limit)
        return ApiResponse.success_response(data=kline_data, message="获取K线数据成功")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取K线数据失败: {str(e)}"
        )

@router.get("/{ts_code}/technical", response_model=ApiResponse[dict])
async def get_technical_indicators(
    ts_code: str,
    period: str = Query("D", regex="^(D|W|M)$", description="周期"),
    limit: int = Query(100, ge=1, le=500, description="数据条数")
):
    """获取技术指标"""
    try:
        indicators = await stock_service.get_technical_indicators(ts_code, period, limit)
        return ApiResponse.success_response(data=indicators, message="获取技术指标成功")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取技术指标失败: {str(e)}"
        )

@router.get("/{ts_code}/financial", response_model=ApiResponse[StockFinancialResponse])
async def get_financial_indicators(
    ts_code: str,
    session: AsyncSession = Depends(get_db)
):
    """获取财务指标（简化版）"""
    try:
        # 这里可以调用财务数据服务
        # 暂时返回模拟数据
        financial_data = {
            "ts_code": ts_code,
            "report_date": datetime.now().strftime("%Y%m%d"),
            "roe": 12.5,
            "roa": 8.2,
            "gross_margin": 35.6,
            "net_margin": 15.3,
            "eps": 1.25,
            "bvps": 10.2,
            "revenue_growth": 18.7,
            "profit_growth": 22.1,
            "debt_ratio": 45.3,
            "current_ratio": 2.1,
            "quick_ratio": 1.5
        }
        return ApiResponse.success_response(
            data=StockFinancialResponse(**financial_data), 
            message="获取财务指标成功"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取财务指标失败: {str(e)}"
        )

@router.get("/{ts_code}/moneyflow", response_model=ApiResponse[List[StockMoneyFlowResponse]])
async def get_money_flow(
    ts_code: str,
    days: int = Query(5, ge=1, le=30, description="天数"),
    session: AsyncSession = Depends(get_db)
):
    """获取资金流向"""
    try:
        money_flow = await stock_service.get_money_flow(session, ts_code, days)
        return ApiResponse.success_response(data=money_flow, message="获取资金流向成功")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取资金流向失败: {str(e)}"
        )

@router.post("/{ts_code}/summary", response_model=ApiResponse[StockSummaryResponse])
async def get_stock_summary(
    ts_code: str,
    request: StockSummaryRequest,
    session: AsyncSession = Depends(get_db)
):
    """获取股票AI摘要"""
    try:
        # 获取股票数据
        stock_detail = await stock_service.get_stock_detail(session, ts_code)
        if not stock_detail:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"未找到股票: {ts_code}"
            )
        
        # 获取技术指标
        technical_indicators = await stock_service.get_technical_indicators(ts_code)
        
        # 获取资金流向
        money_flow = await stock_service.get_money_flow(session, ts_code, 5)
        
        # 组装数据
        stock_data = {
            "basic": {
                "ts_code": ts_code,
                "name": "",  # 这里需要从数据库获取
                "industry": "",
                "market": ""
            },
            "quote": stock_detail.model_dump(),
            "technical": technical_indicators,
            "financial": {},  # 这里可以添加财务数据
            "money_flow": {
                "main_net_inflow": sum([flow.net_mf_amount or 0 for flow in money_flow]) / 10000 if money_flow else 0,
                "retail_net_inflow": 0  # 简化的计算
            }
        }
        
        # 生成AI摘要
        summary = await ai_service.generate_stock_summary(
            ts_code, 
            stock_data, 
            force_refresh=request.refresh
        )
        
        if not summary:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="AI摘要生成服务暂不可用"
            )
        
        return ApiResponse.success_response(data=summary, message="获取AI摘要成功")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取AI摘要失败: {str(e)}"
        )

@router.post("/screening", response_model=ApiResponse[ScreeningResult])
async def screen_stocks(
    request: ScreeningRequest,
    session: AsyncSession = Depends(get_db)
):
    """筛选股票"""
    try:
        result = await stock_service.screen_stocks(
            session,
            request.conditions,
            request.page,
            request.page_size,
            request.market.value
        )
        return ApiResponse.success_response(data=result, message="筛选成功")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"筛选失败: {str(e)}"
        )

@router.get("/screening/templates", response_model=ApiResponse[List[ScreeningCondition]])
async def get_screening_templates():
    """获取筛选条件模板"""
    try:
        templates = [
            ScreeningCondition(
                id="template_1",
                type="price",
                field="pct_chg",
                operator="gte",
                value=5.0,
                label="涨幅大于5%",
                unit="%"
            ),
            ScreeningCondition(
                id="template_2",
                type="technical",
                field="turnover_rate",
                operator="gte",
                value=5.0,
                label="换手率大于5%",
                unit="%"
            ),
            ScreeningCondition(
                id="template_3",
                type="financial",
                field="roe",
                operator="gte",
                value=15.0,
                label="ROE大于15%",
                unit="%"
            ),
            ScreeningCondition(
                id="template_4",
                type="price",
                field="pe",
                operator="between",
                value=[10, 30],
                label="市盈率10-30倍",
                unit="倍"
            ),
            ScreeningCondition(
                id="template_5",
                type="volume",
                field="vol",
                operator="gte",
                value=1000000,
                label="成交量大于100万手",
                unit="手"
            )
        ]
        return ApiResponse.success_response(data=templates, message="获取模板成功")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取模板失败: {str(e)}"
        )

@router.get("/market/overview", response_model=ApiResponse[dict])
async def get_market_overview(
    session: AsyncSession = Depends(get_db)
):
    """获取市场概况"""
    try:
        overview = await stock_service.get_market_overview(session)
        return ApiResponse.success_response(data=overview, message="获取市场概况成功")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取市场概况失败: {str(e)}"
        )

@router.get("/market/hot", response_model=ApiResponse[List[StockDailyResponse]])
async def get_hot_stocks(
    limit: int = Query(10, ge=1, le=50, description="数量"),
    session: AsyncSession = Depends(get_db)
):
    """获取热门股票"""
    try:
        # 这里可以使用换手率或成交量排序
        from sqlalchemy import desc
        
        query = """
        SELECT sd.* FROM stock_daily sd
        JOIN (
            SELECT ts_code, MAX(trade_date) as max_date
            FROM stock_daily
            GROUP BY ts_code
        ) latest ON sd.ts_code = latest.ts_code AND sd.trade_date = latest.max_date
        ORDER BY sd.turnover_rate DESC NULLS LAST
        LIMIT :limit
        """
        
        # 执行原生SQL查询（简化示例）
        result = await session.execute(query, {"limit": limit})
        # 这里需要将结果转换为StockDailyResponse
        
        # 暂时返回空列表
        return ApiResponse.success_response(data=[], message="获取热门股票成功")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取热门股票失败: {str(e)}"
        )

@router.post("/sync", response_model=ApiResponse[str])
async def sync_stock_data(
    ts_codes: Optional[List[str]] = None,
    session: AsyncSession = Depends(get_db)
):
    """同步股票数据（管理员接口）"""
    try:
        # 在实际应用中，这里应该有权限检查
        await stock_service.sync_stock_data(session, ts_codes)
        return ApiResponse.success_response(
            data="数据同步任务已启动",
            message="数据同步开始"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"数据同步失败: {str(e)}"
        )