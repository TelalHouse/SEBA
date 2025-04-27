"""
وحدة الاتصال بقاعدة البيانات لمشروع SEBA
توفر هذه الوحدة الوظائف اللازمة للاتصال بقاعدة البيانات وإدارة الجلسات
"""

import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv

from seba.database.models import Base

# تحميل متغيرات البيئة
load_dotenv()

# إعداد السجل
logger = logging.getLogger(__name__)

class DatabaseManager:
    """فئة لإدارة الاتصال بقاعدة البيانات"""
    
    _instance = None
    
    def __new__(cls):
        """تنفيذ نمط Singleton للتأكد من وجود نسخة واحدة فقط من مدير قاعدة البيانات"""
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """تهيئة الفئة"""
        if self._initialized:
            return
            
        self._initialized = True
        
        # الحصول على معلومات الاتصال بقاعدة البيانات من متغيرات البيئة
        db_host = os.getenv("DB_HOST", "localhost")
        db_port = os.getenv("DB_PORT", "5432")
        db_name = os.getenv("DB_NAME", "seba_db")
        db_user = os.getenv("DB_USER", "seba_user")
        db_password = os.getenv("DB_PASSWORD", "seba_password")
        
        # تحديد نوع قاعدة البيانات (PostgreSQL أو SQLite)
        db_type = os.getenv("DB_TYPE", "sqlite")
        
        if db_type.lower() == "postgresql":
            # إنشاء رابط الاتصال بقاعدة بيانات PostgreSQL
            db_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
        else:
            # استخدام SQLite كقاعدة بيانات افتراضية
            db_path = os.getenv("DB_PATH", "/home/ubuntu/SEBA_Implementation/seba.db")
            db_url = f"sqlite:///{db_path}"
        
        # إنشاء محرك قاعدة البيانات
        self.engine = create_engine(db_url, echo=False)
        
        # إنشاء صانع الجلسات
        self.session_factory = sessionmaker(bind=self.engine)
        self.Session = scoped_session(self.session_factory)
        
        logger.info(f"تم تهيئة مدير قاعدة البيانات باستخدام {db_type}")
    
    def create_tables(self):
        """إنشاء جداول قاعدة البيانات"""
        try:
            logger.info("إنشاء جداول قاعدة البيانات")
            Base.metadata.create_all(self.engine)
            logger.info("تم إنشاء جداول قاعدة البيانات بنجاح")
            return True
        except Exception as e:
            logger.error(f"خطأ في إنشاء جداول قاعدة البيانات: {str(e)}")
            return False
    
    def drop_tables(self):
        """حذف جداول قاعدة البيانات"""
        try:
            logger.info("حذف جداول قاعدة البيانات")
            Base.metadata.drop_all(self.engine)
            logger.info("تم حذف جداول قاعدة البيانات بنجاح")
            return True
        except Exception as e:
            logger.error(f"خطأ في حذف جداول قاعدة البيانات: {str(e)}")
            return False
    
    def get_session(self):
        """الحصول على جلسة قاعدة البيانات"""
        return self.Session()
    
    def close_session(self, session):
        """إغلاق جلسة قاعدة البيانات"""
        session.close()
    
    def close_all_sessions(self):
        """إغلاق جميع جلسات قاعدة البيانات"""
        self.Session.remove()
    
    def __del__(self):
        """تنظيف الموارد عند حذف الكائن"""
        self.close_all_sessions()
