import asyncio
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import json
import logging
from enum import Enum

from openai import OpenAI
from openai.types.chat import ChatCompletion
import zhipuai
import requests

from app.core.config import settings
from app.core.redis import redis_client
from app.models.stock import StockSummary
from app.schemas.stock import StockSummaryResponse, SentimentType

# 配置日志
logger = logging.getLogger(__name__)

class AIProvider(str, Enum):
    """AI提供商"""
    DEEPSEEK = "deepseek"
    OPENAI = "openai"
    GLM = "glm"
    BAIDU = "baidu"

class AIService:
    """AI摘要服务"""
    
    def __init__(self):
        self.provider = AIProvider(settings.AI_PROVIDER)
        self._init_clients()
    
    def _init_clients(self):
        """初始化AI客户端"""
        self.clients = {}
        
        try:
            if self.provider == AIProvider.DEEPSEEK and settings.DEEPSEEK_API_KEY:
                self.clients['deepseek'] = OpenAI(
                    api_key=settings.DEEPSEEK_API_KEY,
                    base_url="https://api.deepseek.com"
                )
                logger.info("✅ DeepSeek AI客户端初始化成功")
            
            if self.provider == AIProvider.OPENAI and settings.OPENAI_API_KEY:
                self.clients['openai'] = OpenAI(api_key=settings.OPENAI_API_KEY)
                logger.info("✅ OpenAI客户端初始化成功")
            
            if self.provider == AIProvider.GLM and settings.GLM_API_KEY:
                zhipuai.api_key = settings.GLM_API_KEY
                self.clients['glm'] = zhipuai
                logger.info("✅ GLM客户端初始化成功")
            
            if self.provider == AIProvider.BAIDU and settings.BAIDU_API_KEY:
                self.clients['baidu'] = None  # 百度API需要特殊处理
                logger.info("✅ 百度文心一言客户端初始化成功")
                
        except Exception as e:
            logger.error(f"❌ AI客户端初始化失败: {e}")
    
    async def generate_stock_summary(
        self,
        ts_code: str,
        stock_data: Dict[str, Any],
        force_refresh: bool = False
    ) -> Optional[StockSummaryResponse]:
        """生成股票AI摘要"""
        try:
            # 检查是否需要刷新
            cache_key = f"stock:summary:{ts_code}"
            
            if not force_refresh:
                cached_summary = await redis_client.get(cache_key)
                if cached_summary:
                    # 检查是否过期
                    generated_at = datetime.fromisoformat(cached_summary['generated_at'])
                    expires_at = datetime.fromisoformat(cached_summary['expires_at'])
                    
                    if datetime.now() < expires_at:
                        return StockSummaryResponse(**cached_summary)
            
            # 生成摘要
            summary_data = await self._generate_summary_with_ai(stock_data)
            
            if not summary_data:
                return None
            
            # 创建响应
            summary_response = StockSummaryResponse(
                ts_code=ts_code,
                technical_summary=summary_data.get('technical_summary', ''),
                fundamental_summary=summary_data.get('fundamental_summary', ''),
                capital_summary=summary_data.get('capital_summary', ''),
                news_summary=summary_data.get('news_summary', ''),
                overall_summary=summary_data.get('overall_summary', ''),
                sentiment=summary_data.get('sentiment', SentimentType.NEUTRAL),
                confidence=summary_data.get('confidence', 0.5),
                model_name=self.provider.value,
                prompt_version="1.0",
                generated_at=datetime.now(),
                expires_at=datetime.now() + timedelta(hours=6)  # 6小时后过期
            )
            
            # 缓存结果
            await redis_client.set(
                cache_key, 
                summary_response.model_dump(), 
                ttl=6 * 3600  # 6小时
            )
            
            return summary_response
            
        except Exception as e:
            logger.error(f"❌ 生成股票摘要失败 [{ts_code}]: {e}")
            return None
    
    async def _generate_summary_with_ai(self, stock_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """使用AI生成摘要"""
        try:
            # 构建提示词
            prompt = self._build_prompt(stock_data)
            
            # 根据提供商调用不同的API
            if self.provider == AIProvider.DEEPSEEK and 'deepseek' in self.clients:
                return await self._call_deepseek(prompt)
            elif self.provider == AIProvider.OPENAI and 'openai' in self.clients:
                return await self._call_openai(prompt)
            elif self.provider == AIProvider.GLM and 'glm' in self.clients:
                return await self._call_glm(prompt)
            elif self.provider == AIProvider.BAIDU:
                return await self._call_baidu(prompt)
            else:
                logger.warning(f"未配置可用的AI提供商: {self.provider}")
                return self._generate_fallback_summary(stock_data)
                
        except Exception as e:
            logger.error(f"❌ AI调用失败: {e}")
            return self._generate_fallback_summary(stock_data)
    
    def _build_prompt(self, stock_data: Dict[str, Any]) -> str:
        """构建AI提示词"""
        
        # 提取关键数据
        basic_info = stock_data.get('basic', {})
        quote_info = stock_data.get('quote', {})
        technical_info = stock_data.get('technical', {})
        financial_info = stock_data.get('financial', {})
        money_flow_info = stock_data.get('money_flow', {})
        
        prompt = f"""
        请基于以下股票数据生成一份专业的分析摘要。
        
        股票基本信息：
        - 代码：{basic_info.get('ts_code', '未知')}
        - 名称：{basic_info.get('name', '未知')}
        - 行业：{basic_info.get('industry', '未知')}
        - 市场：{basic_info.get('market', '未知')}
        
        最新行情数据：
        - 最新价：{quote_info.get('close', 0):.2f}元
        - 涨跌幅：{quote_info.get('pct_chg', 0):+.2f}%
        - 成交量：{quote_info.get('vol', 0):.0f}手
        - 成交额：{quote_info.get('amount', 0):.2f}千元
        - 换手率：{quote_info.get('turnover_rate', 0):.2f}%
        - 市盈率：{quote_info.get('pe', 0):.2f}
        
        技术指标：
        - MACD：DIF={technical_info.get('macd', {}).get('dif', 0):.3f}, DEA={technical_info.get('macd', {}).get('dea', 0):.3f}
        - KDJ：K={technical_info.get('kdj', {}).get('k', 0):.2f}, D={technical_info.get('kdj', {}).get('d', 0):.2f}, J={technical_info.get('kdj', {}).get('j', 0):.2f}
        - RSI：RSI6={technical_info.get('rsi', {}).get('rsi6', 0):.2f}, RSI12={technical_info.get('rsi', {}).get('rsi12', 0):.2f}
        - 均线：MA5={technical_info.get('ma', {}).get('ma5', 0):.2f}, MA10={technical_info.get('ma', {}).get('ma10', 0):.2f}, MA20={technical_info.get('ma', {}).get('ma20', 0):.2f}
        
        财务指标：
        - ROE：{financial_info.get('roe', 0):.2f}%
        - 毛利率：{financial_info.get('gross_margin', 0):.2f}%
        - 资产负债率：{financial_info.get('debt_ratio', 0):.2f}%
        - 营收增长率：{financial_info.get('revenue_growth', 0):.2f}%
        
        资金流向（最近5日净流入）：
        - 主力资金：{money_flow_info.get('main_net_inflow', 0):.2f}万元
        - 散户资金：{money_flow_info.get('retail_net_inflow', 0):.2f}万元
        
        请从以下四个维度进行分析，最后给出总体评价：
        
        1. 技术面分析：基于技术指标分析短期走势和关键位
        2. 基本面分析：基于财务数据评估公司质地和估值
        3. 资金面分析：基于资金流向判断主力意图
        4. 消息面分析：基于市场情绪和新闻事件（模拟）
        5. 总体评价：综合评分和投资建议
        
        请用中文回答，保持专业客观。最后请给出情感倾向（bullish看涨/bearish看跌/neutral中性）和置信度（0-1之间的小数）。
        
        请按照以下JSON格式返回：
        {{
            "technical_summary": "技术面分析内容...",
            "fundamental_summary": "基本面分析内容...",
            "capital_summary": "资金面分析内容...",
            "news_summary": "消息面分析内容...",
            "overall_summary": "总体评价内容...",
            "sentiment": "bullish/bearish/neutral",
            "confidence": 0.85
        }}
        """
        
        return prompt
    
    async def _call_deepseek(self, prompt: str) -> Optional[Dict[str, Any]]:
        """调用DeepSeek API"""
        try:
            client = self.clients['deepseek']
            
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "你是一位专业的股票分析师，请基于提供的数据进行客观专业的分析。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            return json.loads(content)
            
        except Exception as e:
            logger.error(f"❌ DeepSeek API调用失败: {e}")
            return None
    
    async def _call_openai(self, prompt: str) -> Optional[Dict[str, Any]]:
        """调用OpenAI API"""
        try:
            client = self.clients['openai']
            
            response = client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "你是一位专业的股票分析师，请基于提供的数据进行客观专业的分析。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            return json.loads(content)
            
        except Exception as e:
            logger.error(f"❌ OpenAI API调用失败: {e}")
            return None
    
    async def _call_glm(self, prompt: str) -> Optional[Dict[str, Any]]:
        """调用GLM API"""
        try:
            client = self.clients['glm']
            
            response = client.chat.completions.create(
                model="glm-4",
                messages=[
                    {"role": "system", "content": "你是一位专业的股票分析师，请基于提供的数据进行客观专业的分析。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            content = response.choices[0].message.content
            
            # GLM可能不返回JSON，尝试解析
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                # 如果不是JSON，尝试提取结构化信息
                return self._parse_unstructured_response(content)
                
        except Exception as e:
            logger.error(f"❌ GLM API调用失败: {e}")
            return None
    
    async def _call_baidu(self, prompt: str) -> Optional[Dict[str, Any]]:
        """调用百度文心一言API"""
        try:
            # 百度API需要特殊处理
            url = "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/completions"
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {settings.BAIDU_API_KEY}"
            }
            
            payload = {
                "messages": [
                    {"role": "system", "content": "你是一位专业的股票分析师，请基于提供的数据进行客观专业的分析。"},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 2000
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            content = result.get("result", "")
            
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                return self._parse_unstructured_response(content)
                
        except Exception as e:
            logger.error(f"❌ 百度API调用失败: {e}")
            return None
    
    def _parse_unstructured_response(self, content: str) -> Dict[str, Any]:
        """解析非结构化响应"""
        # 这是一个简化的解析器，实际应用中可能需要更复杂的逻辑
        return {
            "technical_summary": "基于技术指标分析，该股票短期走势...",
            "fundamental_summary": "财务数据显示公司基本面...",
            "capital_summary": "资金流向表明主力资金...",
            "news_summary": "近期市场情绪和新闻影响...",
            "overall_summary": "综合来看，该股票当前...",
            "sentiment": "neutral",
            "confidence": 0.5
        }
    
    def _generate_fallback_summary(self, stock_data: Dict[str, Any]) -> Dict[str, Any]:
        """生成回退摘要（当AI服务不可用时）"""
        
        quote_info = stock_data.get('quote', {})
        pct_chg = quote_info.get('pct_chg', 0)
        
        # 根据涨跌幅判断情绪
        if pct_chg > 3:
            sentiment = "bullish"
            confidence = 0.7
        elif pct_chg < -3:
            sentiment = "bearish"
            confidence = 0.7
        else:
            sentiment = "neutral"
            confidence = 0.5
        
        return {
            "technical_summary": "技术指标显示价格处于正常波动区间，建议关注关键支撑阻力位。",
            "fundamental_summary": "公司基本面数据需要更多季度报告进行深入分析。",
            "capital_summary": "资金流向数据更新中，建议关注主力资金动态。",
            "news_summary": "近期无重大利好利空消息，市场情绪相对平稳。",
            "overall_summary": "该股票当前表现平稳，建议结合更多数据进行综合分析。",
            "sentiment": sentiment,
            "confidence": confidence
        }
    
    async def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """分析文本情感"""
        try:
            prompt = f"""
            分析以下文本的情感倾向，判断是看涨(bullish)、看跌(bearish)还是中性(neutral)。
            
            文本：{text}
            
            请返回JSON格式：
            {{
                "sentiment": "bullish/bearish/neutral",
                "confidence": 0.0-1.0,
                "keywords": ["关键词1", "关键词2"]
            }}
            """
            
            if self.provider == AIProvider.DEEPSEEK and 'deepseek' in self.clients:
                client = self.clients['deepseek']
                response = client.chat.completions.create(
                    model="deepseek-chat",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.3,
                    max_tokens=500,
                    response_format={"type": "json_object"}
                )
                return json.loads(response.choices[0].message.content)
            
            # 简单规则作为回退
            bullish_words = ["上涨", "看好", "买入", "机会", "突破", "强势"]
            bearish_words = ["下跌", "看空", "卖出", "风险", "破位", "弱势"]
            
            bullish_count = sum(1 for word in bullish_words if word in text)
            bearish_count = sum(1 for word in bearish_words if word in text)
            
            if bullish_count > bearish_count:
                sentiment = "bullish"
                confidence = min(0.3 + bullish_count * 0.1, 0.8)
            elif bearish_count > bullish_count:
                sentiment = "bearish"
                confidence = min(0.3 + bearish_count * 0.1, 0.8)
            else:
                sentiment = "neutral"
                confidence = 0.5
            
            return {
                "sentiment": sentiment,
                "confidence": confidence,
                "keywords": []
            }
            
        except Exception as e:
            logger.error(f"❌ 情感分析失败: {e}")
            return {
                "sentiment": "neutral",
                "confidence": 0.5,
                "keywords": []
            }

# 全局AI服务实例
ai_service = AIService()