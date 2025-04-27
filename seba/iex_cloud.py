"""
وحدة تكامل IEX Cloud API
توفر هذه الوحدة الوظائف اللازمة للاتصال بواجهة برمجة تطبيقات IEX Cloud
والحصول على بيانات الأسهم المتقدمة وبيانات السوق.
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

class IEXCloudAPI:
    """فئة للتعامل مع واجهة برمجة تطبيقات IEX Cloud"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        تهيئة الفئة
        
        المعلمات:
            api_key (str, optional): مفتاح API لـ IEX Cloud. إذا لم يتم تحديده، سيتم استخدام المفتاح من متغيرات البيئة.
        """
        self.api_key = api_key or os.getenv("IEX_CLOUD_API_KEY")
        if not self.api_key:
            logger.warning("لم يتم تحديد مفتاح API لـ IEX Cloud. بعض الوظائف قد لا تعمل.")
        
        self.base_url = "https://cloud.iexapis.com/stable"
        logger.info("تهيئة واجهة IEX Cloud API")
    
    def get_historical_data(
        self, 
        symbol: str, 
        range_period: str = "1m",
        chart_interval: int = 1
    ) -> pd.DataFrame:
        """
        الحصول على البيانات التاريخية لسهم معين
        
        المعلمات:
            symbol (str): رمز السهم
            range_period (str, optional): الفترة (max, 5y, 2y, 1y, ytd, 6m, 3m, 1m, 5d, date, dynamic)
            chart_interval (int, optional): الفاصل الزمني بالدقائق (للبيانات داخل اليوم)
            
        العائد:
            pd.DataFrame: إطار بيانات يحتوي على البيانات التاريخية
        """
        try:
            logger.info(f"جلب البيانات التاريخية للسهم {symbol} من IEX Cloud")
            
            # إعداد المسار
            endpoint = f"/stock/{symbol}/chart/{range_period}"
            
            # إضافة معلمات الاستعلام
            params = {
                "token": self.api_key,
                "chartInterval": chart_interval
            }
            
            # إرسال الطلب
            url = f"{self.base_url}{endpoint}"
            response = requests.get(url, params=params)
            response.raise_for_status()  # رفع استثناء في حالة فشل الطلب
            data = response.json()
            
            # التحقق من وجود بيانات
            if not data:
                logger.error(f"لم يتم العثور على بيانات تاريخية للسهم {symbol}")
                return pd.DataFrame()
            
            # تحويل البيانات إلى إطار بيانات
            df = pd.DataFrame(data)
            
            # إعادة تسمية الأعمدة
            column_mapping = {
                "date": "date",
                "open": "open",
                "high": "high",
                "low": "low",
                "close": "close",
                "volume": "volume",
                "uOpen": "unadjusted_open",
                "uHigh": "unadjusted_high",
                "uLow": "unadjusted_low",
                "uClose": "unadjusted_close",
                "uVolume": "unadjusted_volume",
                "change": "change",
                "changePercent": "change_percent",
                "changeOverTime": "change_over_time",
                "symbol": "symbol",
                "id": "id",
                "key": "key",
                "subkey": "subkey",
                "updated": "updated",
                "marketChangeOverTime": "market_change_over_time"
            }
            
            # تطبيق إعادة التسمية على الأعمدة الموجودة فقط
            existing_columns = {col: column_mapping.get(col, col) for col in df.columns if col in column_mapping}
            df = df.rename(columns=existing_columns)
            
            # تحويل التاريخ إلى تنسيق موحد
            if "date" in df.columns:
                df["date"] = pd.to_datetime(df["date"]).dt.date
            
            # إضافة عمود رمز السهم إذا لم يكن موجوداً
            if "symbol" not in df.columns:
                df["symbol"] = symbol
            
            logger.info(f"تم جلب {len(df)} سجل من البيانات التاريخية للسهم {symbol} من IEX Cloud")
            return df
            
        except Exception as e:
            logger.error(f"خطأ في جلب البيانات التاريخية للسهم {symbol} من IEX Cloud: {str(e)}")
            return pd.DataFrame()
    
    def get_quote(self, symbol: str) -> Dict:
        """
        الحصول على اقتباس السهم في الوقت الفعلي
        
        المعلمات:
            symbol (str): رمز السهم
            
        العائد:
            Dict: قاموس يحتوي على بيانات الاقتباس
        """
        try:
            logger.info(f"جلب اقتباس السهم {symbol} من IEX Cloud")
            
            # إعداد المسار
            endpoint = f"/stock/{symbol}/quote"
            
            # إضافة معلمات الاستعلام
            params = {
                "token": self.api_key
            }
            
            # إرسال الطلب
            url = f"{self.base_url}{endpoint}"
            response = requests.get(url, params=params)
            response.raise_for_status()  # رفع استثناء في حالة فشل الطلب
            data = response.json()
            
            # التحقق من وجود بيانات
            if not data:
                logger.error(f"لم يتم العثور على اقتباس للسهم {symbol}")
                return {}
            
            # إضافة طابع زمني
            data["timestamp"] = datetime.now().isoformat()
            
            logger.info(f"تم جلب اقتباس السهم {symbol} من IEX Cloud")
            return data
            
        except Exception as e:
            logger.error(f"خطأ في جلب اقتباس السهم {symbol} من IEX Cloud: {str(e)}")
            return {}
    
    def get_company_info(self, symbol: str) -> Dict:
        """
        الحصول على معلومات الشركة
        
        المعلمات:
            symbol (str): رمز السهم
            
        العائد:
            Dict: قاموس يحتوي على معلومات الشركة
        """
        try:
            logger.info(f"جلب معلومات الشركة للسهم {symbol} من IEX Cloud")
            
            # إعداد المسار
            endpoint = f"/stock/{symbol}/company"
            
            # إضافة معلمات الاستعلام
            params = {
                "token": self.api_key
            }
            
            # إرسال الطلب
            url = f"{self.base_url}{endpoint}"
            response = requests.get(url, params=params)
            response.raise_for_status()  # رفع استثناء في حالة فشل الطلب
            data = response.json()
            
            # التحقق من وجود بيانات
            if not data:
                logger.error(f"لم يتم العثور على معلومات الشركة للسهم {symbol}")
                return {}
            
            logger.info(f"تم جلب معلومات الشركة للسهم {symbol} من IEX Cloud")
            return data
            
        except Exception as e:
            logger.error(f"خطأ في جلب معلومات الشركة للسهم {symbol} من IEX Cloud: {str(e)}")
            return {}
    
    def get_financials(self, symbol: str, period: str = "quarter", last: int = 4) -> List[Dict]:
        """
        الحصول على البيانات المالية للشركة
        
        المعلمات:
            symbol (str): رمز السهم
            period (str, optional): الفترة (quarter, annual)
            last (int, optional): عدد الفترات المطلوبة
            
        العائد:
            List[Dict]: قائمة بالبيانات المالية
        """
        try:
            logger.info(f"جلب البيانات المالية للسهم {symbol} من IEX Cloud")
            
            # إعداد المسار
            endpoint = f"/stock/{symbol}/financials"
            
            # إضافة معلمات الاستعلام
            params = {
                "token": self.api_key,
                "period": period,
                "last": last
            }
            
            # إرسال الطلب
            url = f"{self.base_url}{endpoint}"
            response = requests.get(url, params=params)
            response.raise_for_status()  # رفع استثناء في حالة فشل الطلب
            data = response.json()
            
            # التحقق من وجود بيانات
            if not data or "financials" not in data:
                logger.error(f"لم يتم العثور على بيانات مالية للسهم {symbol}")
                return []
            
            logger.info(f"تم جلب {len(data['financials'])} فترة من البيانات المالية للسهم {symbol} من IEX Cloud")
            return data["financials"]
            
        except Exception as e:
            logger.error(f"خطأ في جلب البيانات المالية للسهم {symbol} من IEX Cloud: {str(e)}")
            return []
    
    def get_earnings(self, symbol: str, last: int = 4) -> List[Dict]:
        """
        الحصول على بيانات الأرباح للشركة
        
        المعلمات:
            symbol (str): رمز السهم
            last (int, optional): عدد الفترات المطلوبة
            
        العائد:
            List[Dict]: قائمة ببيانات الأرباح
        """
        try:
            logger.info(f"جلب بيانات الأرباح للسهم {symbol} من IEX Cloud")
            
            # إعداد المسار
            endpoint = f"/stock/{symbol}/earnings"
            
            # إضافة معلمات الاستعلام
            params = {
                "token": self.api_key,
                "last": last
            }
            
            # إرسال الطلب
            url = f"{self.base_url}{endpoint}"
            response = requests.get(url, params=params)
            response.raise_for_status()  # رفع استثناء في حالة فشل الطلب
            data = response.json()
            
            # التحقق من وجود بيانات
            if not data or "earnings" not in data:
                logger.error(f"لم يتم العثور على بيانات أرباح للسهم {symbol}")
                return []
            
            logger.info(f"تم جلب {len(data['earnings'])} فترة من بيانات الأرباح للسهم {symbol} من IEX Cloud")
            return data["earnings"]
            
        except Exception as e:
            logger.error(f"خطأ في جلب بيانات الأرباح للسهم {symbol} من IEX Cloud: {str(e)}")
            return []
    
    def get_stats(self, symbol: str) -> Dict:
        """
        الحصول على إحصائيات السهم
        
        المعلمات:
            symbol (str): رمز السهم
            
        العائد:
            Dict: قاموس يحتوي على إحصائيات السهم
        """
        try:
            logger.info(f"جلب إحصائيات السهم {symbol} من IEX Cloud")
            
            # إعداد المسار
            endpoint = f"/stock/{symbol}/stats"
            
            # إضافة معلمات الاستعلام
            params = {
                "token": self.api_key
            }
            
            # إرسال الطلب
            url = f"{self.base_url}{endpoint}"
            response = requests.get(url, params=params)
            response.raise_for_status()  # رفع استثناء في حالة فشل الطلب
            data = response.json()
            
            # التحقق من وجود بيانات
            if not data:
                logger.error(f"لم يتم العثور على إحصائيات للسهم {symbol}")
                return {}
            
            logger.info(f"تم جلب إحصائيات السهم {symbol} من IEX Cloud")
            return data
            
        except Exception as e:
            logger.error(f"خطأ في جلب إحصائيات السهم {symbol} من IEX Cloud: {str(e)}")
            return {}
    
    def get_news(self, symbol: str, last: int = 10) -> List[Dict]:
        """
        الحصول على أخبار السهم
        
        المعلمات:
            symbol (str): رمز السهم
            last (int, optional): عدد الأخبار المطلوبة
            
        العائد:
            List[Dict]: قائمة بالأخبار
        """
        try:
            logger.info(f"جلب أخبار السهم {symbol} من IEX Cloud")
            
            # إعداد المسار
            endpoint = f"/stock/{symbol}/news/last/{last}"
            
            # إضافة معلمات الاستعلام
            params = {
                "token": self.api_key
            }
            
            # إرسال الطلب
            url = f"{self.base_url}{endpoint}"
            response = requests.get(url, params=params)
            response.raise_for_status()  # رفع استثناء في حالة فشل الطلب
            data = response.json()
            
            # التحقق من وجود بيانات
            if not data:
                logger.error(f"لم يتم العثور على أخبار للسهم {symbol}")
                return []
            
            logger.info(f"تم جلب {len(data)} خبر للسهم {symbol} من IEX Cloud")
            return data
            
        except Exception as e:
            logger.error(f"خطأ في جلب أخبار السهم {symbol} من IEX Cloud: {str(e)}")
            return []
    
    def get_peers(self, symbol: str) -> List[str]:
        """
        الحصول على الأسهم المماثلة
        
        المعلمات:
            symbol (str): رمز السهم
            
        العائد:
            List[str]: قائمة برموز الأسهم المماثلة
        """
        try:
            logger.info(f"جلب الأسهم المماثلة للسهم {symbol} من IEX Cloud")
            
            # إعداد المسار
            endpoint = f"/stock/{symbol}/peers"
            
            # إضافة معلمات الاستعلام
            params = {
                "token": self.api_key
            }
            
            # إرسال الطلب
            url = f"{self.base_url}{endpoint}"
            response = requests.get(url, params=params)
            response.raise_for_status()  # رفع استثناء في حالة فشل الطلب
            data = response.json()
            
            # التحقق من وجود بيانات
            if not data:
                logger.error(f"لم يتم العثور على أسهم مماثلة للسهم {symbol}")
                return []
            
            logger.info(f"تم جلب {len(data)} سهم مماثل للسهم {symbol} من IEX Cloud")
            return data
            
        except Exception as e:
            logger.error(f"خطأ في جلب الأسهم المماثلة للسهم {symbol} من IEX Cloud: {str(e)}")
            return []
    
    def get_market_gainers_losers(self, list_type: str = "gainers", limit: int = 10) -> List[Dict]:
        """
        الحصول على قائمة الأسهم الرابحة أو الخاسرة
        
        المعلمات:
            list_type (str, optional): نوع القائمة (gainers, losers, mostactive, iexvolume, iexpercent)
            limit (int, optional): عدد الأسهم المطلوبة
            
        العائد:
            List[Dict]: قائمة بالأسهم
        """
        try:
            logger.info(f"جلب قائمة {list_type} من IEX Cloud")
            
            # إعداد المسار
            endpoint = f"/stock/market/list/{list_type}"
            
            # إضافة معلمات الاستعلام
            params = {
                "token": self.api_key,
                "listLimit": limit
            }
            
            # إرسال الطلب
            url = f"{self.base_url}{endpoint}"
            response = requests.get(url, params=params)
            response.raise_for_status()  # رفع استثناء في حالة فشل الطلب
            data = response.json()
            
            # التحقق من وجود بيانات
            if not data:
                logger.error(f"لم يتم العثور على بيانات لقائمة {list_type}")
                return []
            
            logger.info(f"تم جلب {len(data)} سهم من قائمة {list_type} من IEX Cloud")
            return data
            
        except Exception as e:
            logger.error(f"خطأ في جلب قائمة {list_type} من IEX Cloud: {str(e)}")
            return []
    
    def get_market_sectors(self) -> List[Dict]:
        """
        الحصول على أداء القطاعات
        
        العائد:
            List[Dict]: قائمة بأداء القطاعات
        """
        try:
            logger.info("جلب أداء القطاعات من IEX Cloud")
            
            # إعداد المسار
            endpoint = "/stock/market/sector-performance"
            
            # إضافة معلمات الاستعلام
            params = {
                "token": self.api_key
            }
            
            # إرسال الطلب
            url = f"{self.base_url}{endpoint}"
            response = requests.get(url, params=params)
            response.raise_for_status()  # رفع استثناء في حالة فشل الطلب
            data = response.json()
            
            # التحقق من وجود بيانات
            if not data:
                lo
(Content truncated due to size limit. Use line ranges to read in chunks)