"""
وحدة تحسين الأداء لمشروع SEBA
توفر هذه الوحدة وظائف لتحسين أداء النظام وتخزين البيانات المؤقت
"""

import os
import logging
import json
import time
import hashlib
from typing import Dict, List, Optional, Union, Any, Callable
from datetime import datetime, date, timedelta
import pandas as pd
import redis
from functools import wraps

# إعداد السجل
logger = logging.getLogger(__name__)

class CacheManager:
    """فئة لإدارة التخزين المؤقت"""
    
    def __init__(self, redis_url: Optional[str] = None):
        """
        تهيئة الفئة
        
        المعلمات:
            redis_url (str, optional): عنوان URL لخادم Redis. إذا لم يتم تحديده، سيتم استخدام التخزين المؤقت في الذاكرة.
        """
        self.use_redis = redis_url is not None
        self.redis_client = None
        self.memory_cache = {}
        
        if self.use_redis:
            try:
                self.redis_client = redis.from_url(redis_url)
                logger.info(f"تم الاتصال بخادم Redis: {redis_url}")
            except Exception as e:
                logger.error(f"خطأ في الاتصال بخادم Redis: {str(e)}")
                self.use_redis = False
        
        logger.info(f"تهيئة مدير التخزين المؤقت (استخدام Redis: {self.use_redis})")
    
    def get(self, key: str) -> Optional[Any]:
        """
        الحصول على قيمة من التخزين المؤقت
        
        المعلمات:
            key (str): المفتاح
            
        العائد:
            Any: القيمة المخزنة، أو None إذا لم يتم العثور على المفتاح
        """
        try:
            if self.use_redis and self.redis_client:
                value = self.redis_client.get(key)
                if value:
                    return json.loads(value)
                return None
            else:
                return self.memory_cache.get(key)
        except Exception as e:
            logger.error(f"خطأ في الحصول على قيمة من التخزين المؤقت: {str(e)}")
            return None
    
    def set(self, key: str, value: Any, expiry: Optional[int] = None) -> bool:
        """
        تخزين قيمة في التخزين المؤقت
        
        المعلمات:
            key (str): المفتاح
            value (Any): القيمة
            expiry (int, optional): مدة الصلاحية بالثواني
            
        العائد:
            bool: True في حالة النجاح، False في حالة الفشل
        """
        try:
            if self.use_redis and self.redis_client:
                serialized_value = json.dumps(value)
                if expiry:
                    self.redis_client.setex(key, expiry, serialized_value)
                else:
                    self.redis_client.set(key, serialized_value)
            else:
                self.memory_cache[key] = value
                if expiry:
                    # تنفيذ آلية انتهاء الصلاحية في الذاكرة غير مدعوم حالياً
                    pass
            return True
        except Exception as e:
            logger.error(f"خطأ في تخزين قيمة في التخزين المؤقت: {str(e)}")
            return False
    
    def delete(self, key: str) -> bool:
        """
        حذف قيمة من التخزين المؤقت
        
        المعلمات:
            key (str): المفتاح
            
        العائد:
            bool: True في حالة النجاح، False في حالة الفشل
        """
        try:
            if self.use_redis and self.redis_client:
                self.redis_client.delete(key)
            else:
                if key in self.memory_cache:
                    del self.memory_cache[key]
            return True
        except Exception as e:
            logger.error(f"خطأ في حذف قيمة من التخزين المؤقت: {str(e)}")
            return False
    
    def clear(self) -> bool:
        """
        مسح جميع القيم من التخزين المؤقت
        
        العائد:
            bool: True في حالة النجاح، False في حالة الفشل
        """
        try:
            if self.use_redis and self.redis_client:
                self.redis_client.flushdb()
            else:
                self.memory_cache.clear()
            return True
        except Exception as e:
            logger.error(f"خطأ في مسح التخزين المؤقت: {str(e)}")
            return False
    
    def get_dataframe(self, key: str) -> Optional[pd.DataFrame]:
        """
        الحصول على DataFrame من التخزين المؤقت
        
        المعلمات:
            key (str): المفتاح
            
        العائد:
            pd.DataFrame: DataFrame المخزن، أو None إذا لم يتم العثور على المفتاح
        """
        try:
            data = self.get(key)
            if data:
                return pd.DataFrame.from_dict(data)
            return None
        except Exception as e:
            logger.error(f"خطأ في الحصول على DataFrame من التخزين المؤقت: {str(e)}")
            return None
    
    def set_dataframe(self, key: str, df: pd.DataFrame, expiry: Optional[int] = None) -> bool:
        """
        تخزين DataFrame في التخزين المؤقت
        
        المعلمات:
            key (str): المفتاح
            df (pd.DataFrame): DataFrame
            expiry (int, optional): مدة الصلاحية بالثواني
            
        العائد:
            bool: True في حالة النجاح، False في حالة الفشل
        """
        try:
            data = df.to_dict(orient="records")
            return self.set(key, data, expiry)
        except Exception as e:
            logger.error(f"خطأ في تخزين DataFrame في التخزين المؤقت: {str(e)}")
            return False


def cache(expiry: int = 3600):
    """
    مزخرف للتخزين المؤقت
    
    المعلمات:
        expiry (int, optional): مدة الصلاحية بالثواني
        
    العائد:
        Callable: الدالة المزخرفة
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # إنشاء مفتاح التخزين المؤقت
            key_parts = [func.__name__]
            key_parts.extend([str(arg) for arg in args])
            key_parts.extend([f"{k}={v}" for k, v in kwargs.items()])
            key = hashlib.md5(":".join(key_parts).encode()).hexdigest()
            
            # الحصول على مدير التخزين المؤقت
            cache_manager = CacheManager()
            
            # محاولة الحصول على القيمة من التخزين المؤقت
            cached_value = cache_manager.get(key)
            if cached_value is not None:
                logger.debug(f"تم الحصول على القيمة من التخزين المؤقت: {key}")
                return cached_value
            
            # تنفيذ الدالة
            result = func(*args, **kwargs)
            
            # تخزين النتيجة في التخزين المؤقت
            cache_manager.set(key, result, expiry)
            logger.debug(f"تم تخزين القيمة في التخزين المؤقت: {key}")
            
            return result
        return wrapper
    return decorator


class PerformanceMonitor:
    """فئة لمراقبة الأداء"""
    
    def __init__(self):
        """تهيئة الفئة"""
        self.metrics = {}
        logger.info("تهيئة مراقب الأداء")
    
    def start_timer(self, name: str) -> None:
        """
        بدء مؤقت
        
        المعلمات:
            name (str): اسم المؤقت
        """
        self.metrics[name] = {
            'start_time': time.time(),
            'end_time': None,
            'duration': None
        }
    
    def stop_timer(self, name: str) -> float:
        """
        إيقاف مؤقت
        
        المعلمات:
            name (str): اسم المؤقت
            
        العائد:
            float: المدة بالثواني
        """
        if name in self.metrics:
            self.metrics[name]['end_time'] = time.time()
            self.metrics[name]['duration'] = self.metrics[name]['end_time'] - self.metrics[name]['start_time']
            return self.metrics[name]['duration']
        return 0.0
    
    def get_duration(self, name: str) -> float:
        """
        الحصول على مدة مؤقت
        
        المعلمات:
            name (str): اسم المؤقت
            
        العائد:
            float: المدة بالثواني
        """
        if name in self.metrics and self.metrics[name]['duration'] is not None:
            return self.metrics[name]['duration']
        return 0.0
    
    def get_all_metrics(self) -> Dict:
        """
        الحصول على جميع المقاييس
        
        العائد:
            Dict: المقاييس
        """
        return self.metrics
    
    def clear_metrics(self) -> None:
        """مسح جميع المقاييس"""
        self.metrics.clear()


def measure_performance(name: str):
    """
    مزخرف لقياس أداء الدالة
    
    المعلمات:
        name (str): اسم المقياس
        
    العائد:
        Callable: الدالة المزخرفة
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # إنشاء مراقب الأداء
            monitor = PerformanceMonitor()
            
            # بدء المؤقت
            monitor.start_timer(name)
            
            # تنفيذ الدالة
            result = func(*args, **kwargs)
            
            # إيقاف المؤقت
            duration = monitor.stop_timer(name)
            logger.debug(f"مدة تنفيذ {name}: {duration:.4f} ثانية")
            
            return result
        return wrapper
    return decorator


class OptimizationManager:
    """فئة لإدارة تحسين الأداء"""
    
    def __init__(self):
        """تهيئة الفئة"""
        self.cache_manager = CacheManager()
        self.performance_monitor = PerformanceMonitor()
        logger.info("تهيئة مدير تحسين الأداء")
    
    def optimize_data_loading(self, data_loader: Callable, key: str, expiry: int = 3600, *args, **kwargs) -> Any:
        """
        تحسين تحميل البيانات باستخدام التخزين المؤقت
        
        المعلمات:
            data_loader (Callable): دالة تحميل البيانات
            key (str): مفتاح التخزين المؤقت
            expiry (int, optional): مدة الصلاحية بالثواني
            *args: المعلمات الإضافية لدالة تحميل البيانات
            **kwargs: المعلمات الإضافية المسماة لدالة تحميل البيانات
            
        العائد:
            Any: البيانات المحملة
        """
        # محاولة الحصول على البيانات من التخزين المؤقت
        cached_data = self.cache_manager.get(key)
        if cached_data is not None:
            logger.debug(f"تم الحصول على البيانات من التخزين المؤقت: {key}")
            return cached_data
        
        # تحميل البيانات
        self.performance_monitor.start_timer(key)
        data = data_loader(*args, **kwargs)
        duration = self.performance_monitor.stop_timer(key)
        logger.debug(f"مدة تحميل البيانات {key}: {duration:.4f} ثانية")
        
        # تخزين البيانات في التخزين المؤقت
        self.cache_manager.set(key, data, expiry)
        logger.debug(f"تم تخزين البيانات في التخزين المؤقت: {key}")
        
        return data
    
    def optimize_dataframe_loading(self, data_loader: Callable, key: str, expiry: int = 3600, *args, **kwargs) -> pd.DataFrame:
        """
        تحسين تحميل DataFrame باستخدام التخزين المؤقت
        
        المعلمات:
            data_loader (Callable): دالة تحميل البيانات
            key (str): مفتاح التخزين المؤقت
            expiry (int, optional): مدة الصلاحية بالثواني
            *args: المعلمات الإضافية لدالة تحميل البيانات
            **kwargs: المعلمات الإضافية المسماة لدالة تحميل البيانات
            
        العائد:
            pd.DataFrame: DataFrame المحمل
        """
        # محاولة الحصول على البيانات من التخزين المؤقت
        cached_df = self.cache_manager.get_dataframe(key)
        if cached_df is not None:
            logger.debug(f"تم الحصول على DataFrame من التخزين المؤقت: {key}")
            return cached_df
        
        # تحميل البيانات
        self.performance_monitor.start_timer(key)
        df = data_loader(*args, **kwargs)
        duration = self.performance_monitor.stop_timer(key)
        logger.debug(f"مدة تحميل DataFrame {key}: {duration:.4f} ثانية")
        
        # تخزين البيانات في التخزين المؤقت
        self.cache_manager.set_dataframe(key, df, expiry)
        logger.debug(f"تم تخزين DataFrame في التخزين المؤقت: {key}")
        
        return df
    
    def get_performance_metrics(self) -> Dict:
        """
        الحصول على مقاييس الأداء
        
        العائد:
            Dict: مقاييس الأداء
        """
        return self.performance_monitor.get_all_metrics()
    
    def clear_cache(self) -> bool:
        """
        مسح التخزين المؤقت
        
        العائد:
            bool: True في حالة النجاح، False في حالة الفشل
        """
        return self.cache_manager.clear()
    
    def clear_performance_metrics(self) -> None:
        """مسح مقاييس الأداء"""
        self.performance_monitor.clear_metrics()
