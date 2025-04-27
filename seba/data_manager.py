"""
وحدة تكامل مصادر البيانات المتعددة
توفر هذه الوحدة واجهة موحدة للتعامل مع مصادر البيانات المختلفة
"""

import logging
from typing import Dict, List, Optional, Union, Any
import pandas as pd
from datetime import datetime, timedelta

from seba.data_integration.yahoo_finance import YahooFinanceAPI
from seba.data_integration.alpha_vantage import AlphaVantageAPI
from seba.data_integration.iex_cloud import IEXCloudAPI

# إعداد السجل
logger = logging.getLogger(__name__)

class DataIntegrationManager:
    """فئة لإدارة تكامل مصادر البيانات المتعددة"""
    
    def __init__(self):
        """تهيئة الفئة"""
        logger.info("تهيئة مدير تكامل البيانات")
        self.yahoo_finance = YahooFinanceAPI()
        self.alpha_vantage = AlphaVantageAPI()
        self.iex_cloud = IEXCloudAPI()
        
        # تعيين مصدر البيانات الافتراضي
        self.default_source = "yahoo_finance"
    
    def get_historical_data(
        self, 
        symbol: str, 
        start_date: Optional[Union[str, datetime]] = None, 
        end_date: Optional[Union[str, datetime]] = None,
        period: Optional[str] = None,
        interval: str = "1d",
        source: Optional[str] = None
    ) -> pd.DataFrame:
        """
        الحصول على البيانات التاريخية لسهم معين من مصدر محدد
        
        المعلمات:
            symbol (str): رمز السهم
            start_date (str|datetime, optional): تاريخ البداية
            end_date (str|datetime, optional): تاريخ النهاية
            period (str, optional): الفترة
            interval (str, optional): الفاصل الزمني
            source (str, optional): مصدر البيانات (yahoo_finance, alpha_vantage, iex_cloud)
            
        العائد:
            pd.DataFrame: إطار بيانات يحتوي على البيانات التاريخية
        """
        # تحديد مصدر البيانات
        source = source or self.default_source
        
        try:
            logger.info(f"جلب البيانات التاريخية للسهم {symbol} من {source}")
            
            if source == "yahoo_finance":
                return self.yahoo_finance.get_historical_data(
                    symbol=symbol,
                    start_date=start_date,
                    end_date=end_date,
                    period=period,
                    interval=interval
                )
            elif source == "alpha_vantage":
                # تحويل المعلمات إلى تنسيق Alpha Vantage
                output_size = "full" if period and period.lower() in ["1y", "2y", "5y", "10y", "max"] else "compact"
                av_interval = "daily"
                if interval:
                    if interval in ["1d", "daily"]:
                        av_interval = "daily"
                    elif interval in ["1wk", "weekly"]:
                        av_interval = "weekly"
                    elif interval in ["1mo", "monthly"]:
                        av_interval = "monthly"
                
                return self.alpha_vantage.get_historical_data(
                    symbol=symbol,
                    output_size=output_size,
                    interval=av_interval
                )
            elif source == "iex_cloud":
                # تحويل المعلمات إلى تنسيق IEX Cloud
                range_period = "1m"  # افتراضي
                if period:
                    if period == "1d":
                        range_period = "1d"
                    elif period == "5d":
                        range_period = "5d"
                    elif period == "1mo" or period == "1m":
                        range_period = "1m"
                    elif period == "3mo" or period == "3m":
                        range_period = "3m"
                    elif period == "6mo" or period == "6m":
                        range_period = "6m"
                    elif period == "1y":
                        range_period = "1y"
                    elif period == "2y":
                        range_period = "2y"
                    elif period == "5y":
                        range_period = "5y"
                    elif period == "max":
                        range_period = "max"
                
                return self.iex_cloud.get_historical_data(
                    symbol=symbol,
                    range_period=range_period
                )
            else:
                logger.error(f"مصدر البيانات غير معروف: {source}")
                return pd.DataFrame()
                
        except Exception as e:
            logger.error(f"خطأ في جلب البيانات التاريخية للسهم {symbol} من {source}: {str(e)}")
            
            # محاولة استخدام مصدر بديل
            if source != "yahoo_finance":
                logger.info(f"محاولة استخدام Yahoo Finance كمصدر بديل للسهم {symbol}")
                return self.yahoo_finance.get_historical_data(
                    symbol=symbol,
                    start_date=start_date,
                    end_date=end_date,
                    period=period,
                    interval=interval
                )
            
            return pd.DataFrame()
    
    def get_realtime_data(self, symbol: str, source: Optional[str] = None) -> Dict:
        """
        الحصول على البيانات في الوقت الفعلي لسهم معين
        
        المعلمات:
            symbol (str): رمز السهم
            source (str, optional): مصدر البيانات (yahoo_finance, iex_cloud)
            
        العائد:
            Dict: قاموس يحتوي على البيانات في الوقت الفعلي
        """
        # تحديد مصدر البيانات
        source = source or self.default_source
        
        try:
            logger.info(f"جلب البيانات في الوقت الفعلي للسهم {symbol} من {source}")
            
            if source == "yahoo_finance":
                return self.yahoo_finance.get_realtime_data(symbol=symbol)
            elif source == "iex_cloud":
                return self.iex_cloud.get_quote(symbol=symbol)
            else:
                logger.error(f"مصدر البيانات غير معروف أو لا يدعم البيانات في الوقت الفعلي: {source}")
                return {}
                
        except Exception as e:
            logger.error(f"خطأ في جلب البيانات في الوقت الفعلي للسهم {symbol} من {source}: {str(e)}")
            
            # محاولة استخدام مصدر بديل
            if source != "yahoo_finance":
                logger.info(f"محاولة استخدام Yahoo Finance كمصدر بديل للسهم {symbol}")
                return self.yahoo_finance.get_realtime_data(symbol=symbol)
            
            return {}
    
    def get_fundamental_data(self, symbol: str, source: Optional[str] = None) -> Dict:
        """
        الحصول على البيانات الأساسية لسهم معين
        
        المعلمات:
            symbol (str): رمز السهم
            source (str, optional): مصدر البيانات (yahoo_finance, alpha_vantage, iex_cloud)
            
        العائد:
            Dict: قاموس يحتوي على البيانات الأساسية
        """
        # تحديد مصدر البيانات
        source = source or self.default_source
        
        try:
            logger.info(f"جلب البيانات الأساسية للسهم {symbol} من {source}")
            
            if source == "yahoo_finance":
                return self.yahoo_finance.get_fundamental_data(symbol=symbol)
            elif source == "alpha_vantage":
                return self.alpha_vantage.get_company_overview(symbol=symbol)
            elif source == "iex_cloud":
                # دمج معلومات الشركة والإحصائيات
                company_info = self.iex_cloud.get_company_info(symbol=symbol)
                stats = self.iex_cloud.get_stats(symbol=symbol)
                return {**company_info, **stats}
            else:
                logger.error(f"مصدر البيانات غير معروف: {source}")
                return {}
                
        except Exception as e:
            logger.error(f"خطأ في جلب البيانات الأساسية للسهم {symbol} من {source}: {str(e)}")
            
            # محاولة استخدام مصدر بديل
            if source != "yahoo_finance":
                logger.info(f"محاولة استخدام Yahoo Finance كمصدر بديل للسهم {symbol}")
                return self.yahoo_finance.get_fundamental_data(symbol=symbol)
            
            return {}
    
    def get_technical_indicators(
        self, 
        symbol: str, 
        indicator: str, 
        time_period: int = 14, 
        source: Optional[str] = None
    ) -> pd.DataFrame:
        """
        الحصول على المؤشرات الفنية لسهم معين
        
        المعلمات:
            symbol (str): رمز السهم
            indicator (str): المؤشر الفني (SMA, EMA, RSI, MACD, BBANDS, STOCH, ADX, CCI, AROON, OBV)
            time_period (int, optional): الفترة الزمنية للمؤشر
            source (str, optional): مصدر البيانات (alpha_vantage)
            
        العائد:
            pd.DataFrame: إطار بيانات يحتوي على المؤشرات الفنية
        """
        # تحديد مصدر البيانات
        source = source or "alpha_vantage"  # Alpha Vantage هو المصدر الأفضل للمؤشرات الفنية
        
        try:
            logger.info(f"جلب المؤشر الفني {indicator} للسهم {symbol} من {source}")
            
            if source == "alpha_vantage":
                return self.alpha_vantage.get_technical_indicators(
                    symbol=symbol,
                    indicator=indicator,
                    time_period=time_period
                )
            else:
                logger.error(f"مصدر البيانات غير معروف أو لا يدعم المؤشرات الفنية: {source}")
                return pd.DataFrame()
                
        except Exception as e:
            logger.error(f"خطأ في جلب المؤشر الفني {indicator} للسهم {symbol} من {source}: {str(e)}")
            return pd.DataFrame()
    
    def search_stocks(self, query: str, source: Optional[str] = None) -> List[Dict]:
        """
        البحث عن الأسهم باستخدام استعلام
        
        المعلمات:
            query (str): استعلام البحث
            source (str, optional): مصدر البيانات (yahoo_finance, alpha_vantage)
            
        العائد:
            List[Dict]: قائمة بالأسهم المطابقة
        """
        # تحديد مصدر البيانات
        source = source or "alpha_vantage"  # Alpha Vantage يوفر واجهة بحث أفضل
        
        try:
            logger.info(f"البحث عن الأسهم باستخدام الاستعلام: {query} من {source}")
            
            if source == "yahoo_finance":
                return self.yahoo_finance.search_stocks(query=query)
            elif source == "alpha_vantage":
                return self.alpha_vantage.search_stocks(keywords=query)
            else:
                logger.error(f"مصدر البيانات غير معروف أو لا يدعم البحث: {source}")
                return []
                
        except Exception as e:
            logger.error(f"خطأ في البحث عن الأسهم باستخدام الاستعلام {query} من {source}: {str(e)}")
            
            # محاولة استخدام مصدر بديل
            if source != "yahoo_finance":
                logger.info(f"محاولة استخدام Yahoo Finance كمصدر بديل للبحث عن {query}")
                return self.yahoo_finance.search_stocks(query=query)
            
            return []
    
    def get_market_data(self, data_type: str, source: Optional[str] = None) -> Any:
        """
        الحصول على بيانات السوق
        
        المعلمات:
            data_type (str): نوع البيانات (sector_performance, gainers, losers, most_active)
            source (str, optional): مصدر البيانات (alpha_vantage, iex_cloud)
            
        العائد:
            Any: بيانات السوق
        """
        # تحديد مصدر البيانات
        source = source or "iex_cloud"  # IEX Cloud يوفر بيانات سوق أكثر تفصيلاً
        
        try:
            logger.info(f"جلب بيانات السوق من نوع {data_type} من {source}")
            
            if data_type == "sector_performance":
                if source == "alpha_vantage":
                    return self.alpha_vantage.get_sector_performance()
                elif source == "iex_cloud":
                    return self.iex_cloud.get_market_sectors()
            elif data_type == "gainers":
                if source == "iex_cloud":
                    return self.iex_cloud.get_market_gainers_losers(list_type="gainers")
            elif data_type == "losers":
                if source == "iex_cloud":
                    return self.iex_cloud.get_market_gainers_losers(list_type="losers")
            elif data_type == "most_active":
                if source == "iex_cloud":
                    return self.iex_cloud.get_market_gainers_losers(list_type="mostactive")
            
            logger.error(f"نوع البيانات غير معروف أو غير مدعوم من المصدر: {data_type} من {source}")
            return None
                
        except Exception as e:
            logger.error(f"خطأ في جلب بيانات السوق من نوع {data_type} من {source}: {str(e)}")
            return None
    
    def get_earnings_data(self, symbol: str, source: Optional[str] = None) -> Dict:
        """
        الحصول على بيانات الأرباح للشركة
        
        المعلمات:
            symbol (str): رمز السهم
            source (str, optional): مصدر البيانات (alpha_vantage, iex_cloud)
            
        العائد:
            Dict: قاموس يحتوي على بيانات الأرباح
        """
        # تحديد مصدر البيانات
        source = source or "alpha_vantage"
        
        try:
            logger.info(f"جلب بيانات الأرباح للسهم {symbol} من {source}")
            
            if source == "alpha_vantage":
                return self.alpha_vantage.get_earnings(symbol=symbol)
            elif source == "iex_cloud":
                return {"earnings": self.iex_cloud.get_earnings(symbol=symbol)}
            else:
                logger.error(f"مصدر البيانات غير معروف أو لا يدعم بيانات الأرباح: {source}")
                return {}
                
        except Exception as e:
            logger.error(f"خطأ في جلب بيانات الأرباح للسهم {symbol} من {source}: {str(e)}")
            
            # محاولة استخدام مصدر بديل
            if source != "alpha_vantage":
                logger.info(f"محاولة استخدام Alpha Vantage كمصدر بديل للسهم {symbol}")
                return self.alpha_vantage.get_earnings(symbol=symbol)
            
            return {}
    
    def get_multiple_stocks_data(
        self, 
        symbols: List[str], 
        period: str = "1d", 
        source: Optional[str] = None
    ) -> Dict[str, pd.DataFrame]:
        """
        الحصول على بيانات لعدة أسهم في وقت واحد
        
        المعلمات:
            symbols (List[str]): قائمة برموز الأسهم
            period (str, optional): الفترة
            source (str, optional): مصدر البيانات (yahoo_finance)
            
        العائد:
            Dict[str, pd.DataFrame]: قاموس يحتوي على إطارات البيانات لكل سهم
        """
        # تحديد مصدر البيانات
        source = source or "yahoo_finance"  # Yahoo Finance يدعم جلب بيانات متعددة بشكل أفضل
        
        try:
            logger.info(f"جلب بيانات لـ {len(symbols)} سهم من {source}")
            
            if source == "yahoo_finance":
                return self.yahoo_finance.get_multiple_stocks_data(symbols=symbols, period=period)
            else:
                logger.error(f"مصدر البيانات غير معروف أو لا يدعم جلب بيانات متعددة: {source}")
                return {}
                
        except Exception as e:
            logger.error(f"خطأ في جلب بيانات متعددة للأسهم من {source}: {str(e)}")
            return {}
