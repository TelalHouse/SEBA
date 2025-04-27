"""
وحدة تكامل Yahoo Finance API
توفر هذه الوحدة الوظائف اللازمة للاتصال بواجهة برمجة تطبيقات Yahoo Finance
والحصول على بيانات الأسهم التاريخية والحالية.
"""

import os
import logging
from datetime import datetime, timedelta
import pandas as pd
import yfinance as yf
from typing import Dict, List, Optional, Union, Tuple

# إعداد السجل
logger = logging.getLogger(__name__)

class YahooFinanceAPI:
    """فئة للتعامل مع واجهة برمجة تطبيقات Yahoo Finance"""
    
    def __init__(self):
        """تهيئة الفئة"""
        logger.info("تهيئة واجهة Yahoo Finance API")
    
    def get_historical_data(
        self, 
        symbol: str, 
        start_date: Optional[Union[str, datetime]] = None, 
        end_date: Optional[Union[str, datetime]] = None,
        period: Optional[str] = None,
        interval: str = "1d"
    ) -> pd.DataFrame:
        """
        الحصول على البيانات التاريخية لسهم معين
        
        المعلمات:
            symbol (str): رمز السهم
            start_date (str|datetime, optional): تاريخ البداية
            end_date (str|datetime, optional): تاريخ النهاية
            period (str, optional): الفترة (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            interval (str, optional): الفاصل الزمني (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)
            
        العائد:
            pd.DataFrame: إطار بيانات يحتوي على البيانات التاريخية
        """
        try:
            logger.info(f"جلب البيانات التاريخية للسهم {symbol}")
            
            # إذا تم تحديد الفترة، استخدمها بدلاً من تاريخ البداية والنهاية
            if period:
                data = yf.download(symbol, period=period, interval=interval, progress=False)
            else:
                # إذا لم يتم تحديد تاريخ البداية، استخدم تاريخ قبل سنة واحدة
                if start_date is None:
                    start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
                
                # إذا لم يتم تحديد تاريخ النهاية، استخدم التاريخ الحالي
                if end_date is None:
                    end_date = datetime.now().strftime('%Y-%m-%d')
                
                data = yf.download(symbol, start=start_date, end=end_date, interval=interval, progress=False)
            
            # إعادة تسمية الأعمدة إلى أسماء قياسية
            data = data.rename(columns={
                'Open': 'open',
                'High': 'high',
                'Low': 'low',
                'Close': 'close',
                'Adj Close': 'adj_close',
                'Volume': 'volume'
            })
            
            # إضافة عمود رمز السهم
            data['symbol'] = symbol
            
            # إعادة ضبط الفهرس وتحويل التاريخ إلى عمود
            data = data.reset_index()
            data = data.rename(columns={'Date': 'date'})
            
            # التأكد من أن التاريخ بتنسيق موحد
            data['date'] = pd.to_datetime(data['date']).dt.date
            
            logger.info(f"تم جلب {len(data)} سجل من البيانات التاريخية للسهم {symbol}")
            return data
            
        except Exception as e:
            logger.error(f"خطأ في جلب البيانات التاريخية للسهم {symbol}: {str(e)}")
            return pd.DataFrame()
    
    def get_realtime_data(self, symbol: str) -> Dict:
        """
        الحصول على البيانات في الوقت الفعلي لسهم معين
        
        المعلمات:
            symbol (str): رمز السهم
            
        العائد:
            Dict: قاموس يحتوي على البيانات في الوقت الفعلي
        """
        try:
            logger.info(f"جلب البيانات في الوقت الفعلي للسهم {symbol}")
            
            # الحصول على كائن Ticker
            ticker = yf.Ticker(symbol)
            
            # الحصول على معلومات السهم
            info = ticker.info
            
            # استخراج البيانات المهمة
            realtime_data = {
                'symbol': symbol,
                'price': info.get('regularMarketPrice', None),
                'change': info.get('regularMarketChange', None),
                'change_percent': info.get('regularMarketChangePercent', None),
                'volume': info.get('regularMarketVolume', None),
                'market_cap': info.get('marketCap', None),
                'timestamp': datetime.now().isoformat(),
                'previous_close': info.get('previousClose', None),
                'open': info.get('regularMarketOpen', None),
                'day_high': info.get('regularMarketDayHigh', None),
                'day_low': info.get('regularMarketDayLow', None),
            }
            
            logger.info(f"تم جلب البيانات في الوقت الفعلي للسهم {symbol}")
            return realtime_data
            
        except Exception as e:
            logger.error(f"خطأ في جلب البيانات في الوقت الفعلي للسهم {symbol}: {str(e)}")
            return {}
    
    def get_fundamental_data(self, symbol: str) -> Dict:
        """
        الحصول على البيانات الأساسية لسهم معين
        
        المعلمات:
            symbol (str): رمز السهم
            
        العائد:
            Dict: قاموس يحتوي على البيانات الأساسية
        """
        try:
            logger.info(f"جلب البيانات الأساسية للسهم {symbol}")
            
            # الحصول على كائن Ticker
            ticker = yf.Ticker(symbol)
            
            # الحصول على معلومات السهم
            info = ticker.info
            
            # استخراج البيانات الأساسية
            fundamental_data = {
                'symbol': symbol,
                'company_name': info.get('longName', None),
                'sector': info.get('sector', None),
                'industry': info.get('industry', None),
                'market_cap': info.get('marketCap', None),
                'pe_ratio': info.get('trailingPE', None),
                'eps': info.get('trailingEps', None),
                'dividend_yield': info.get('dividendYield', None),
                'beta': info.get('beta', None),
                'fifty_two_week_high': info.get('fiftyTwoWeekHigh', None),
                'fifty_two_week_low': info.get('fiftyTwoWeekLow', None),
                'fifty_day_average': info.get('fiftyDayAverage', None),
                'two_hundred_day_average': info.get('twoHundredDayAverage', None),
                'earnings_growth': info.get('earningsGrowth', None),
                'revenue_growth': info.get('revenueGrowth', None),
                'timestamp': datetime.now().isoformat(),
            }
            
            logger.info(f"تم جلب البيانات الأساسية للسهم {symbol}")
            return fundamental_data
            
        except Exception as e:
            logger.error(f"خطأ في جلب البيانات الأساسية للسهم {symbol}: {str(e)}")
            return {}
    
    def search_stocks(self, query: str) -> List[Dict]:
        """
        البحث عن الأسهم باستخدام استعلام
        
        المعلمات:
            query (str): استعلام البحث
            
        العائد:
            List[Dict]: قائمة بالأسهم المطابقة
        """
        try:
            logger.info(f"البحث عن الأسهم باستخدام الاستعلام: {query}")
            
            # استخدام yfinance للبحث عن الأسهم
            # ملاحظة: yfinance لا يوفر واجهة برمجة تطبيقات للبحث بشكل مباشر
            # لذلك نستخدم طريقة بديلة
            
            # هذه قائمة مبسطة للأغراض التوضيحية
            # في التطبيق الفعلي، يمكن استخدام واجهة برمجة تطبيقات أخرى للبحث
            results = []
            
            # محاولة الحصول على معلومات السهم مباشرة إذا كان الاستعلام رمز سهم
            try:
                ticker = yf.Ticker(query)
                info = ticker.info
                if 'longName' in info:
                    results.append({
                        'symbol': query,
                        'name': info.get('longName', ''),
                        'exchange': info.get('exchange', ''),
                        'type': 'Equity'
                    })
            except:
                pass
            
            logger.info(f"تم العثور على {len(results)} سهم مطابق للاستعلام: {query}")
            return results
            
        except Exception as e:
            logger.error(f"خطأ في البحث عن الأسهم باستخدام الاستعلام {query}: {str(e)}")
            return []
    
    def get_multiple_stocks_data(self, symbols: List[str], period: str = "1d") -> Dict[str, pd.DataFrame]:
        """
        الحصول على بيانات لعدة أسهم في وقت واحد
        
        المعلمات:
            symbols (List[str]): قائمة برموز الأسهم
            period (str, optional): الفترة (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            
        العائد:
            Dict[str, pd.DataFrame]: قاموس يحتوي على إطارات البيانات لكل سهم
        """
        try:
            logger.info(f"جلب بيانات لـ {len(symbols)} سهم")
            
            result = {}
            for symbol in symbols:
                data = self.get_historical_data(symbol, period=period)
                if not data.empty:
                    result[symbol] = data
            
            logger.info(f"تم جلب بيانات لـ {len(result)} سهم من أصل {len(symbols)}")
            return result
            
        except Exception as e:
            logger.error(f"خطأ في جلب بيانات متعددة للأسهم: {str(e)}")
            return {}
