"""
وحدة تحسين الأمان لمشروع SEBA
توفر هذه الوحدة وظائف لتحسين أمان النظام وحماية البيانات
"""

import os
import logging
import hashlib
import secrets
import re
import jwt
from typing import Dict, List, Optional, Union, Any
from datetime import datetime, timedelta
from passlib.context import CryptContext

# إعداد السجل
logger = logging.getLogger(__name__)

# إعداد سياق التشفير
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class SecurityManager:
    """فئة لإدارة الأمان"""
    
    def __init__(self, secret_key: Optional[str] = None):
        """
        تهيئة الفئة
        
        المعلمات:
            secret_key (str, optional): المفتاح السري. إذا لم يتم تحديده، سيتم استخدام المفتاح من متغيرات البيئة.
        """
        self.secret_key = secret_key or os.getenv("JWT_SECRET_KEY", "secret")
        logger.info("تهيئة مدير الأمان")
    
    def hash_password(self, password: str) -> str:
        """
        تشفير كلمة المرور
        
        المعلمات:
            password (str): كلمة المرور
            
        العائد:
            str: كلمة المرور المشفرة
        """
        return pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        التحقق من كلمة المرور
        
        المعلمات:
            plain_password (str): كلمة المرور العادية
            hashed_password (str): كلمة المرور المشفرة
            
        العائد:
            bool: True إذا كانت كلمة المرور صحيحة، False خلاف ذلك
        """
        return pwd_context.verify(plain_password, hashed_password)
    
    def create_access_token(self, data: Dict, expires_delta: Optional[timedelta] = None) -> str:
        """
        إنشاء رمز الوصول
        
        المعلمات:
            data (Dict): البيانات المراد تضمينها في الرمز
            expires_delta (timedelta, optional): مدة صلاحية الرمز
            
        العائد:
            str: رمز الوصول
        """
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm="HS256")
        
        return encoded_jwt
    
    def decode_access_token(self, token: str) -> Dict:
        """
        فك تشفير رمز الوصول
        
        المعلمات:
            token (str): رمز الوصول
            
        العائد:
            Dict: البيانات المضمنة في الرمز
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            return payload
        except jwt.PyJWTError as e:
            logger.error(f"خطأ في فك تشفير رمز الوصول: {str(e)}")
            raise ValueError("رمز الوصول غير صالح")
    
    def generate_random_token(self, length: int = 32) -> str:
        """
        توليد رمز عشوائي
        
        المعلمات:
            length (int, optional): طول الرمز
            
        العائد:
            str: الرمز العشوائي
        """
        return secrets.token_hex(length // 2)
    
    def validate_password_strength(self, password: str) -> bool:
        """
        التحقق من قوة كلمة المرور
        
        المعلمات:
            password (str): كلمة المرور
            
        العائد:
            bool: True إذا كانت كلمة المرور قوية، False خلاف ذلك
        """
        # التحقق من طول كلمة المرور
        if len(password) < 8:
            return False
        
        # التحقق من وجود حرف كبير
        if not re.search(r'[A-Z]', password):
            return False
        
        # التحقق من وجود حرف صغير
        if not re.search(r'[a-z]', password):
            return False
        
        # التحقق من وجود رقم
        if not re.search(r'[0-9]', password):
            return False
        
        # التحقق من وجود حرف خاص
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return False
        
        return True
    
    def sanitize_input(self, input_str: str) -> str:
        """
        تنظيف المدخلات
        
        المعلمات:
            input_str (str): النص المدخل
            
        العائد:
            str: النص المنظف
        """
        # إزالة الأكواد الضارة المحتملة
        sanitized = re.sub(r'<script.*?>.*?</script>', '', input_str, flags=re.DOTALL)
        sanitized = re.sub(r'<.*?javascript:.*?>', '', sanitized)
        sanitized = re.sub(r'<.*?\\s+on\\w+\\s*=.*?>', '', sanitized)
        
        return sanitized
    
    def validate_api_key(self, api_key: str, expected_key: str) -> bool:
        """
        التحقق من مفتاح API
        
        المعلمات:
            api_key (str): مفتاح API المقدم
            expected_key (str): مفتاح API المتوقع
            
        العائد:
            bool: True إذا كان المفتاح صحيحاً، False خلاف ذلك
        """
        return api_key == expected_key
    
    def hash_data(self, data: str) -> str:
        """
        تشفير البيانات باستخدام SHA-256
        
        المعلمات:
            data (str): البيانات المراد تشفيرها
            
        العائد:
            str: البيانات المشفرة
        """
        return hashlib.sha256(data.encode()).hexdigest()


class RateLimiter:
    """فئة للحد من معدل الطلبات"""
    
    def __init__(self, max_requests: int = 100, time_window: int = 60):
        """
        تهيئة الفئة
        
        المعلمات:
            max_requests (int, optional): الحد الأقصى لعدد الطلبات
            time_window (int, optional): النافذة الزمنية بالثواني
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = {}
        logger.info(f"تهيئة محدد معدل الطلبات (الحد الأقصى: {max_requests} طلب في {time_window} ثانية)")
    
    def is_allowed(self, client_id: str) -> bool:
        """
        التحقق مما إذا كان الطلب مسموحاً به
        
        المعلمات:
            client_id (str): معرف العميل
            
        العائد:
            bool: True إذا كان الطلب مسموحاً به، False خلاف ذلك
        """
        current_time = datetime.utcnow()
        
        # إنشاء سجل للعميل إذا لم يكن موجوداً
        if client_id not in self.requests:
            self.requests[client_id] = []
        
        # إزالة الطلبات القديمة
        self.requests[client_id] = [
            req_time for req_time in self.requests[client_id]
            if (current_time - req_time).total_seconds() < self.time_window
        ]
        
        # التحقق من عدد الطلبات
        if len(self.requests[client_id]) >= self.max_requests:
            return False
        
        # إضافة الطلب الحالي
        self.requests[client_id].append(current_time)
        
        return True
    
    def get_remaining_requests(self, client_id: str) -> int:
        """
        الحصول على عدد الطلبات المتبقية
        
        المعلمات:
            client_id (str): معرف العميل
            
        العائد:
            int: عدد الطلبات المتبقية
        """
        if client_id not in self.requests:
            return self.max_requests
        
        current_time = datetime.utcnow()
        
        # إزالة الطلبات القديمة
        self.requests[client_id] = [
            req_time for req_time in self.requests[client_id]
            if (current_time - req_time).total_seconds() < self.time_window
        ]
        
        return max(0, self.max_requests - len(self.requests[client_id]))
    
    def reset(self, client_id: str) -> None:
        """
        إعادة تعيين عداد الطلبات للعميل
        
        المعلمات:
            client_id (str): معرف العميل
        """
        if client_id in self.requests:
            self.requests[client_id] = []


class DataProtection:
    """فئة لحماية البيانات"""
    
    @staticmethod
    def mask_sensitive_data(data: Dict, sensitive_fields: List[str]) -> Dict:
        """
        إخفاء البيانات الحساسة
        
        المعلمات:
            data (Dict): البيانات
            sensitive_fields (List[str]): قائمة الحقول الحساسة
            
        العائد:
            Dict: البيانات مع إخفاء الحقول الحساسة
        """
        masked_data = data.copy()
        
        for field in sensitive_fields:
            if field in masked_data:
                if isinstance(masked_data[field], str):
                    # إخفاء جزء من النص
                    if len(masked_data[field]) > 4:
                        masked_data[field] = masked_data[field][:2] + '*' * (len(masked_data[field]) - 4) + masked_data[field][-2:]
                    else:
                        masked_data[field] = '*' * len(masked_data[field])
                else:
                    # إخفاء القيمة بالكامل
                    masked_data[field] = '********'
        
        return masked_data
    
    @staticmethod
    def validate_data_access(user_id: str, data_owner_id: str, is_admin: bool = False) -> bool:
        """
        التحقق من صلاحية الوصول إلى البيانات
        
        المعلمات:
            user_id (str): معرف المستخدم
            data_owner_id (str): معرف مالك البيانات
            is_admin (bool, optional): ما إذا كان المستخدم مديراً
            
        العائد:
            bool: True إذا كان الوصول مسموحاً به، False خلاف ذلك
        """
        return user_id == data_owner_id or is_admin
    
    @staticmethod
    def log_data_access(user_id: str, data_type: str, data_id: str, action: str) -> None:
        """
        تسجيل الوصول إلى البيانات
        
        المعلمات:
            user_id (str): معرف المستخدم
            data_type (str): نوع البيانات
            data_id (str): معرف البيانات
            action (str): الإجراء المتخذ
        """
        logger.info(f"وصول إلى البيانات: المستخدم {user_id} قام بـ {action} على {data_type} بمعرف {data_id}")
