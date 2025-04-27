"""
وحدة تكامل Alpha Vantage API
توفر هذه الوحدة الوظائف اللازمة للاتصال بواجهة برمجة تطبيقات Alpha Vantage
والحصول على بيانات الأسهم التاريخية والمؤشرات الفنية المتقدمة.
"""

import os
import logging
from datetime import datetime, timedelta
import pandas as pd
import requests
from typing import Dict, List, Optional, Union, Tuple
from dotenv import load_dotenv

# تحميل متغيرات البيئة
load_dotenv()

# إعداد السجل
logger = logging.getLogger(__name__)

class AlphaVantageAPI:
    """فئة للتعامل مع واجهة برمجة تطبيقات Alpha Vantage"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        تهيئة الفئة
        
        المعلمات:
            api_key (str, optional): مفتاح API لـ Alpha Vantage. إذا لم يتم تحديده، سيتم استخدام المفتاح من متغيرات البيئة.
        """
        self.api_key = api_key or os.getenv("ALPHA_VANTAGE_API_KEY")
        if not self.api_key:
            logger.warning("لم يتم تحديد مفتاح API لـ Alpha Vantage. بعض الوظائف قد لا تعمل.")
        
        self.base_url = "https://www.alphavantage.co/query"
        logger.info("تهيئة واجهة Alpha Vantage API")
    
    def get_historical_data(
        self, 
        symbol: str, 
        output_size: str = "compact",
        interval: str = "daily"
    ) -> pd.DataFrame:
        """
        الحصول على البيانات التاريخية لسهم معين
        
        المعلمات:
            symbol (str): رمز السهم
            output_size (str, optional): حجم المخرجات (compact: 100 نقطة بيانات، full: كل البيانات المتاحة)
            interval (str, optional): الفاصل الزمني (daily, weekly, monthly)
            
        العائد:
            pd.DataFrame: إطار بيانات يحتوي على البيانات التاريخية
        """
        try:
            logger.info(f"جلب البيانات التاريخية للسهم {symbol} من Alpha Vantage")
            
            # تحديد الدالة المناسبة بناءً على الفاصل الزمني
            function = {
                "daily": "TIME_SERIES_DAILY_ADJUSTED",
                "weekly": "TIME_SERIES_WEEKLY_ADJUSTED",
                "monthly": "TIME_SERIES_MONTHLY_ADJUSTED"
            }.get(interval.lower(), "TIME_SERIES_DAILY_ADJUSTED")
            
            # إعداد المعلمات
            params = {
                "function": function,
                "symbol": symbol,
                "outputsize": output_size,
                "apikey": self.api_key,
                "datatype": "json"
            }
            
            # إرسال الطلب
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()  # رفع استثناء في حالة فشل الطلب
            data = response.json()
            
            # استخراج البيانات من الاستجابة
            time_series_key = next((key for key in data.keys() if "Time Series" in key), None)
            if not time_series_key:
                logger.error(f"لم يتم العثور على بيانات السلسلة الزمنية للسهم {symbol}")
                return pd.DataFrame()
            
            # تحويل البيانات إلى إطار بيانات
            time_series = data[time_series_key]
            df = pd.DataFrame.from_dict(time_series, orient="index")
            
            # إعادة تسمية الأعمدة
            column_mapping = {
                "1. open": "open",
                "2. high": "high",
                "3. low": "low",
                "4. close": "close",
                "5. adjusted close": "adj_close",
                "6. volume": "volume",
                "7. dividend amount": "dividend",
                "8. split coefficient": "split_coefficient"
            }
            
            # تطبيق إعادة التسمية على الأعمدة الموجودة فقط
            existing_columns = {col: column_mapping.get(col, col) for col in df.columns if col in column_mapping}
            df = df.rename(columns=existing_columns)
            
            # تحويل الفهرس إلى عمود التاريخ
            df = df.reset_index()
            df = df.rename(columns={"index": "date"})
            
            # تحويل الأعمدة الرقمية
            numeric_columns = ["open", "high", "low", "close", "adj_close", "volume", "dividend", "split_coefficient"]
            for col in [c for c in numeric_columns if c in df.columns]:
                df[col] = pd.to_numeric(df[col], errors="coerce")
            
            # تحويل التاريخ إلى تنسيق موحد
            df["date"] = pd.to_datetime(df["date"]).dt.date
            
            # إضافة عمود رمز السهم
            df["symbol"] = symbol
            
            # ترتيب البيانات حسب التاريخ (من الأقدم إلى الأحدث)
            df = df.sort_values("date")
            
            logger.info(f"تم جلب {len(df)} سجل من البيانات التاريخية للسهم {symbol} من Alpha Vantage")
            return df
            
        except Exception as e:
            logger.error(f"خطأ في جلب البيانات التاريخية للسهم {symbol} من Alpha Vantage: {str(e)}")
            return pd.DataFrame()
    
    def get_technical_indicators(self, symbol: str, indicator: str, time_period: int = 14, interval: str = "daily") -> pd.DataFrame:
        """
        الحصول على المؤشرات الفنية لسهم معين
        
        المعلمات:
            symbol (str): رمز السهم
            indicator (str): المؤشر الفني (SMA, EMA, RSI, MACD, BBANDS, STOCH, ADX, CCI, AROON, OBV)
            time_period (int, optional): الفترة الزمنية للمؤشر
            interval (str, optional): الفاصل الزمني (1min, 5min, 15min, 30min, 60min, daily, weekly, monthly)
            
        العائد:
            pd.DataFrame: إطار بيانات يحتوي على المؤشرات الفنية
        """
        try:
            logger.info(f"جلب المؤشر الفني {indicator} للسهم {symbol} من Alpha Vantage")
            
            # إعداد المعلمات
            params = {
                "function": indicator,
                "symbol": symbol,
                "interval": interval,
                "time_period": time_period,
                "series_type": "close",
                "apikey": self.api_key,
                "datatype": "json"
            }
            
            # تعديل المعلمات حسب المؤشر
            if indicator == "MACD":
                params.pop("time_period", None)
                params.update({
                    "fastperiod": "12",
                    "slowperiod": "26",
                    "signalperiod": "9"
                })
            elif indicator == "BBANDS":
                params.update({
                    "nbdevup": "2",
                    "nbdevdn": "2",
                    "matype": "0"
                })
            elif indicator == "STOCH":
                params.pop("time_period", None)
                params.update({
                    "fastkperiod": "5",
                    "slowkperiod": "3",
                    "slowdperiod": "3"
                })
            
            # إرسال الطلب
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()  # رفع استثناء في حالة فشل الطلب
            data = response.json()
            
            # استخراج البيانات من الاستجابة
            technical_key = next((key for key in data.keys() if "Technical Analysis" in key), None)
            if not technical_key:
                logger.error(f"لم يتم العثور على بيانات المؤشر الفني {indicator} للسهم {symbol}")
                return pd.DataFrame()
            
            # تحويل البيانات إلى إطار بيانات
            technical_data = data[technical_key]
            df = pd.DataFrame.from_dict(technical_data, orient="index")
            
            # تحويل الفهرس إلى عمود التاريخ
            df = df.reset_index()
            df = df.rename(columns={"index": "date"})
            
            # تحويل الأعمدة الرقمية
            for col in df.columns:
                if col != "date":
                    df[col] = pd.to_numeric(df[col], errors="coerce")
            
            # تحويل التاريخ إلى تنسيق موحد
            df["date"] = pd.to_datetime(df["date"]).dt.date
            
            # إضافة عمود رمز السهم والمؤشر
            df["symbol"] = symbol
            df["indicator"] = indicator
            
            # ترتيب البيانات حسب التاريخ (من الأقدم إلى الأحدث)
            df = df.sort_values("date")
            
            logger.info(f"تم جلب {len(df)} سجل من بيانات المؤشر الفني {indicator} للسهم {symbol} من Alpha Vantage")
            return df
            
        except Exception as e:
            logger.error(f"خطأ في جلب المؤشر الفني {indicator} للسهم {symbol} من Alpha Vantage: {str(e)}")
            return pd.DataFrame()
    
    def get_company_overview(self, symbol: str) -> Dict:
        """
        الحصول على نظرة عامة على الشركة
        
        المعلمات:
            symbol (str): رمز السهم
            
        العائد:
            Dict: قاموس يحتوي على معلومات الشركة
        """
        try:
            logger.info(f"جلب نظرة عامة على الشركة للسهم {symbol} من Alpha Vantage")
            
            # إعداد المعلمات
            params = {
                "function": "OVERVIEW",
                "symbol": symbol,
                "apikey": self.api_key
            }
            
            # إرسال الطلب
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()  # رفع استثناء في حالة فشل الطلب
            data = response.json()
            
            # التحقق من وجود بيانات
            if not data or "Symbol" not in data:
                logger.error(f"لم يتم العثور على بيانات الشركة للسهم {symbol}")
                return {}
            
            # تحويل القيم الرقمية
            for key, value in data.items():
                if key not in ["Symbol", "AssetType", "Name", "Description", "Exchange", "Currency", "Country", "Sector", "Industry", "Address", "FiscalYearEnd", "LatestQuarter", "DividendDate", "ExDividendDate"]:
                    try:
                        data[key] = float(value) if "." in value else int(value)
                    except (ValueError, TypeError):
                        pass
            
            logger.info(f"تم جلب نظرة عامة على الشركة للسهم {symbol} من Alpha Vantage")
            return data
            
        except Exception as e:
            logger.error(f"خطأ في جلب نظرة عامة على الشركة للسهم {symbol} من Alpha Vantage: {str(e)}")
            return {}
    
    def get_earnings(self, symbol: str) -> Dict:
        """
        الحصول على بيانات الأرباح للشركة
        
        المعلمات:
            symbol (str): رمز السهم
            
        العائد:
            Dict: قاموس يحتوي على بيانات الأرباح
        """
        try:
            logger.info(f"جلب بيانات الأرباح للسهم {symbol} من Alpha Vantage")
            
            # إعداد المعلمات
            params = {
                "function": "EARNINGS",
                "symbol": symbol,
                "apikey": self.api_key
            }
            
            # إرسال الطلب
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()  # رفع استثناء في حالة فشل الطلب
            data = response.json()
            
            # التحقق من وجود بيانات
            if not data or "symbol" not in data:
                logger.error(f"لم يتم العثور على بيانات الأرباح للسهم {symbol}")
                return {}
            
            # تحويل بيانات الأرباح الربعية إلى إطار بيانات
            if "quarterlyEarnings" in data:
                quarterly_earnings = pd.DataFrame(data["quarterlyEarnings"])
                # تحويل الأعمدة الرقمية
                for col in ["reportedEPS", "estimatedEPS", "surprise", "surprisePercentage"]:
                    if col in quarterly_earnings.columns:
                        quarterly_earnings[col] = pd.to_numeric(quarterly_earnings[col], errors="coerce")
                # تحويل التاريخ
                if "fiscalDateEnding" in quarterly_earnings.columns:
                    quarterly_earnings["fiscalDateEnding"] = pd.to_datetime(quarterly_earnings["fiscalDateEnding"]).dt.date
                if "reportedDate" in quarterly_earnings.columns:
                    quarterly_earnings["reportedDate"] = pd.to_datetime(quarterly_earnings["reportedDate"]).dt.date
                # تحويل إطار البيانات إلى قائمة قواميس
                data["quarterlyEarnings"] = quarterly_earnings.to_dict(orient="records")
            
            # تحويل بيانات الأرباح السنوية إلى إطار بيانات
            if "annualEarnings" in data:
                annual_earnings = pd.DataFrame(data["annualEarnings"])
                # تحويل الأعمدة الرقمية
                if "reportedEPS" in annual_earnings.columns:
                    annual_earnings["reportedEPS"] = pd.to_numeric(annual_earnings["reportedEPS"], errors="coerce")
                # تحويل التاريخ
                if "fiscalDateEnding" in annual_earnings.columns:
                    annual_earnings["fiscalDateEnding"] = pd.to_datetime(annual_earnings["fiscalDateEnding"]).dt.date
                # تحويل إطار البيانات إلى قائمة قواميس
                data["annualEarnings"] = annual_earnings.to_dict(orient="records")
            
            logger.info(f"تم جلب بيانات الأرباح للسهم {symbol} من Alpha Vantage")
            return data
            
        except Exception as e:
            logger.error(f"خطأ في جلب بيانات الأرباح للسهم {symbol} من Alpha Vantage: {str(e)}")
            return {}
    
    def search_stocks(self, keywords: str) -> List[Dict]:
        """
        البحث عن الأسهم باستخدام كلمات مفتاحية
        
        المعلمات:
            keywords (str): كلمات مفتاحية للبحث
            
        العائد:
            List[Dict]: قائمة بالأسهم المطابقة
        """
        try:
            logger.info(f"البحث عن الأسهم باستخدام الكلمات المفتاحية: {keywords} من Alpha Vantage")
            
            # إعداد المعلمات
            params = {
                "function": "SYMBOL_SEARCH",
                "keywords": keywords,
                "apikey": self.api_key
            }
            
            # إرسال الطلب
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()  # رفع استثناء في حالة فشل الطلب
            data = response.json()
            
            # استخراج البيانات من الاستجابة
            if "bestMatches" not in data:
                logger.error(f"لم يتم العثور على نتائج بحث للكلمات المفتاحية: {keywords}")
                return []
            
            # تحويل البيانات إلى قائمة قواميس
            results = []
            for match in data["bestMatches"]:
                result = {
                    "symbol": match.get("1. symbol", ""),
                    "name": match.get("2. name", ""),
                    "type": match.get("3. type", ""),
                    "region": match.get("4. region", ""),
                    "market_open": match.get("5. marketOpen", ""),
                    "market_close": match.get("6. marketClose", ""),
                    "timezone": match.get("7. timezone", ""),
                    "currency": match.get("8. currency", ""),
                    "match_score": float(match.get("9. matchScore", 0))
                }
                results.append(result)
            
            logger.info(f"تم العثور على {len(results)} سهم مطابق للكلمات المفتاحية: {keywords} من Alpha Vantage")
            return results
            
        except Exception as e:
            logger.error(f"خطأ في البحث عن الأسهم باستخدام الكلمات المفتاحية {keywords} من Alpha Vantage: {str(e)}")
            return []
    
    def get_sector_performance(self) -> Dict:
        """
        الحصول على أداء القطاعات
        
        العائد:
            Dict: قاموس يحتوي على أداء القطاعات
        """
        try:
            logger.info("جلب أداء القطاعات من Alpha Vantage")
            
            # إعداد المعلمات
            params = {
                "function": "SECTOR",
                "apikey": self.api_key
            }
            
            # إرسال الطلب
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()  # رفع استثناء في حالة فشل الطلب
            data = response.json(
(Content truncated due to size limit. Use line ranges to read in chunks)