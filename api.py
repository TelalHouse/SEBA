"""
وحدة واجهة برمجة التطبيقات (API) لمشروع SEBA
توفر هذه الوحدة واجهة RESTful API تتيح للتطبيقات الخارجية الوصول إلى وظائف النظام المختلفة
"""

import os
import logging
import json
from typing import Dict, List, Optional, Union, Any
from datetime import datetime, date, timedelta
from fastapi import FastAPI, HTTPException, Depends, Query, Path, Body, Header, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, Field
import pandas as pd
import numpy as np
import jwt
from jwt.exceptions import InvalidTokenError

from seba.data_integration.data_manager import DataIntegrationManager
from seba.database.db_manager import DatabaseManager
from seba.database.repository import StockRepository, UserRepository, AlertRepository
from seba.models.technical_analysis import DataProcessor
from seba.models.sepa_engine import SEPAEngine
from seba.models.ai_integration import AIIntegrationManager

# إعداد السجل
logger = logging.getLogger(__name__)

# تهيئة تطبيق FastAPI
app = FastAPI(
    title="SEBA API",
    description="واجهة برمجة التطبيقات لنظام SEBA (روبوت خبير الأسهم للتحليل)",
    version="1.0.0"
)

# إضافة CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # يمكن تعديلها للسماح بأصول محددة فقط
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# تهيئة OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# تهيئة المكونات الرئيسية
data_manager = DataIntegrationManager()
db_manager = DatabaseManager()
stock_repository = StockRepository(db_manager)
user_repository = UserRepository(db_manager)
alert_repository = AlertRepository(db_manager)
sepa_engine = SEPAEngine()
ai_manager = AIIntegrationManager()

# تعريف النماذج
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class User(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None

class UserInDB(User):
    hashed_password: str

class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    full_name: Optional[str] = None

class StockData(BaseModel):
    symbol: str
    name: Optional[str] = None
    sector: Optional[str] = None
    industry: Optional[str] = None
    country: Optional[str] = None
    exchange: Optional[str] = None

class HistoricalDataRequest(BaseModel):
    symbol: str
    start_date: str
    end_date: str
    interval: str = "1d"

class AnalysisRequest(BaseModel):
    symbol: str
    report_type: Optional[str] = "detailed"

class ScreenRequest(BaseModel):
    criteria: Dict[str, Any]
    limit: Optional[int] = 20

class AlertRequest(BaseModel):
    symbol: str
    price: float
    condition: str  # "above" or "below"
    message: Optional[str] = None

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

# وظائف المساعدة
def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """
    الحصول على المستخدم الحالي من رمز الوصول
    
    المعلمات:
        token (str): رمز الوصول
        
    العائد:
        User: المستخدم الحالي
    """
    try:
        secret_key = os.getenv("JWT_SECRET_KEY", "secret")
        payload = jwt.decode(token, secret_key, algorithms=["HS256"])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="رمز الوصول غير صالح",
                headers={"WWW-Authenticate": "Bearer"},
            )
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="رمز الوصول غير صالح",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = user_repository.get_user_by_username(token_data.username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="المستخدم غير موجود",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return User(
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        disabled=user.disabled
    )

def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """
    الحصول على المستخدم النشط الحالي
    
    المعلمات:
        current_user (User): المستخدم الحالي
        
    العائد:
        User: المستخدم النشط الحالي
    """
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="المستخدم غير نشط")
    return current_user

# المسارات
@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    الحصول على رمز الوصول
    
    المعلمات:
        form_data (OAuth2PasswordRequestForm): بيانات النموذج
        
    العائد:
        Token: رمز الوصول
    """
    user = user_repository.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="اسم المستخدم أو كلمة المرور غير صحيحة",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # إنشاء رمز الوصول
    secret_key = os.getenv("JWT_SECRET_KEY", "secret")
    access_token_expires = timedelta(minutes=30)
    access_token_data = {
        "sub": user.username,
        "exp": datetime.utcnow() + access_token_expires
    }
    access_token = jwt.encode(access_token_data, secret_key, algorithm="HS256")
    
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/users", response_model=User)
async def create_user(user: UserCreate):
    """
    إنشاء مستخدم جديد
    
    المعلمات:
        user (UserCreate): بيانات المستخدم
        
    العائد:
        User: المستخدم الجديد
    """
    db_user = user_repository.get_user_by_username(user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="اسم المستخدم موجود بالفعل")
    
    created_user = user_repository.create_user(
        username=user.username,
        email=user.email,
        password=user.password,
        full_name=user.full_name
    )
    
    return User(
        username=created_user.username,
        email=created_user.email,
        full_name=created_user.full_name,
        disabled=created_user.disabled
    )

@app.get("/users/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    """
    الحصول على معلومات المستخدم الحالي
    
    المعلمات:
        current_user (User): المستخدم الحالي
        
    العائد:
        User: معلومات المستخدم
    """
    return current_user

@app.get("/stocks/{symbol}")
async def get_stock_info(symbol: str):
    """
    الحصول على معلومات السهم
    
    المعلمات:
        symbol (str): رمز السهم
        
    العائد:
        Dict: معلومات السهم
    """
    try:
        stock_info = data_manager.get_stock_info(symbol)
        if not stock_info:
            raise HTTPException(status_code=404, detail=f"لم يتم العثور على معلومات للسهم {symbol}")
        
        return stock_info
    except Exception as e:
        logger.error(f"خطأ في الحصول على معلومات السهم {symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/stocks/historical")
async def get_historical_data(request: HistoricalDataRequest):
    """
    الحصول على البيانات التاريخية للسهم
    
    المعلمات:
        request (HistoricalDataRequest): طلب البيانات التاريخية
        
    العائد:
        Dict: البيانات التاريخية
    """
    try:
        historical_data = data_manager.get_historical_data(
            symbol=request.symbol,
            start_date=request.start_date,
            end_date=request.end_date,
            interval=request.interval
        )
        
        if historical_data.empty:
            raise HTTPException(status_code=404, detail=f"لم يتم العثور على بيانات تاريخية للسهم {request.symbol}")
        
        # تحويل DataFrame إلى قائمة من القواميس
        result = historical_data.to_dict(orient="records")
        
        return {"symbol": request.symbol, "data": result}
    except Exception as e:
        logger.error(f"خطأ في الحصول على البيانات التاريخية للسهم {request.symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stocks/{symbol}/fundamentals")
async def get_fundamentals(symbol: str):
    """
    الحصول على البيانات الأساسية للسهم
    
    المعلمات:
        symbol (str): رمز السهم
        
    العائد:
        Dict: البيانات الأساسية
    """
    try:
        fundamentals = data_manager.get_fundamentals(symbol)
        if not fundamentals:
            raise HTTPException(status_code=404, detail=f"لم يتم العثور على بيانات أساسية للسهم {symbol}")
        
        return fundamentals
    except Exception as e:
        logger.error(f"خطأ في الحصول على البيانات الأساسية للسهم {symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stocks/{symbol}/indicators")
async def get_technical_indicators(
    symbol: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    indicators: Optional[str] = None
):
    """
    الحصول على المؤشرات الفنية للسهم
    
    المعلمات:
        symbol (str): رمز السهم
        start_date (str, optional): تاريخ البداية
        end_date (str, optional): تاريخ النهاية
        indicators (str, optional): قائمة المؤشرات مفصولة بفواصل
        
    العائد:
        Dict: المؤشرات الفنية
    """
    try:
        # الحصول على البيانات التاريخية
        historical_data = data_manager.get_historical_data(
            symbol=symbol,
            start_date=start_date or (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d"),
            end_date=end_date or datetime.now().strftime("%Y-%m-%d"),
            interval="1d"
        )
        
        if historical_data.empty:
            raise HTTPException(status_code=404, detail=f"لم يتم العثور على بيانات تاريخية للسهم {symbol}")
        
        # تحديد المؤشرات المطلوبة
        indicator_list = indicators.split(",") if indicators else None
        
        # حساب المؤشرات الفنية
        df = DataProcessor.preprocess_data(historical_data)
        
        # الحصول على بيانات المؤشر
        index_symbol = "^GSPC"  # S&P 500
        index_data = data_manager.get_historical_data(
            symbol=index_symbol,
            start_date=start_date or (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d"),
            end_date=end_date or datetime.now().strftime("%Y-%m-%d"),
            interval="1d"
        )
        
        # حساب جميع المؤشرات
        from seba.models.technical_analysis import TechnicalIndicators
        df = TechnicalIndicators.calculate_all_indicators(df, index_data)
        
        # تصفية المؤشرات إذا تم تحديدها
        if indicator_list:
            columns_to_keep = ["date", "open", "high", "low", "close", "volume"]
            for indicator in indicator_list:
                indicator = indicator.strip()
                columns_to_keep.extend([col for col in df.columns if indicator in col])
            df = df[columns_to_keep]
        
        # تحويل DataFrame إلى قائمة من القواميس
        result = df.to_dict(orient="records")
        
        return {"symbol": symbol, "data": result}
    except Exception as e:
        logger.error(f"خطأ في الحصول على المؤشرات الفنية للسهم {symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analysis/{symbol}")
async def analyze_stock(symbol: str, report_type: Optional[str] = "detailed"):
    """
    تحليل السهم
    
    المعلمات:
        symbol (str): رمز السهم
        report_type (str, optional): نوع التقرير
        
    العائد:
        Dict: نتائج التحليل
    """
    try:
        # الحصول على البيانات التاريخية
        historical_data = data_manager.get_historical_data(
            symbol=symbol,
            start_date=(datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d"),
            end_date=datetime.now().strftime("%Y-%m-%d"),
            interval="1d"
        )
        
        if historical_data.empty:
            raise HTTPException(status_code=404, detail=f"لم يتم العثور على بيانات تاريخية للسهم {symbol}")
        
        # الحصول على بيانات المؤشر
        index_symbol = "^GSPC"  # S&P 500
        index_data = data_manager.get_historical_data(
            symbol=index_symbol,
            start_date=(datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d"),
            end_date=datetime.now().strftime("%Y-%m-%d"),
            interval="1d"
        )
        
        # تحليل السهم
        analysis_results = sepa_engine.analyze_stock(historical_data, index_data)
        
        # إضافة رمز السهم إذا لم يكن موجوداً
        if 'symbol' not in analysis_results or analysis_results['symbol'] is None:
            analysis_results['symbol'] = symbol
        
        # توليد تقرير التحليل بلغة طبيعية
        if report_type in ["detailed", "summary", "technical"]:
            analysis_report = ai_manager.generate_stock_analysis_report(analysis_results, report_type)
            analysis_results['analysis_report'] = analysis_report
        
        # توليد توصية بلغة طبيعية
        natural_language_recommendation = ai_manager.generate_natural_language_recommendation(analysis_results)
        analysis_results['natural_language_recommendation'] = natural_language_recommendation
        
        return analysis_results
    except Exception as e:
        logger.error(f"خطأ في تحليل السهم {symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/screen")
async def screen_stocks(request: ScreenRequest, current_user: User = Depends(get_current_active_user)):
    """
    فحص الأسهم باستخدام معايير محددة
    
    المعلمات:
        request (ScreenRequest): طلب الفحص
        current_user (User): المستخدم الحالي
        
    العائد:
        Dict: نتائج الفحص
    """
    try:
        # الحصول على قائمة الأسهم
        symbols = data_manager.get_symbols_list()
        
        # تصفية الأسهم حسب المعايير
        results = []
        
        # الحصول على بيانات المؤشر
        index_symbol = "^GSPC"  # S&P 500
        index_data = data_manager.get_historical_data(
            symbol=index_symbol,
            start_date=(datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d"),
            end_date=datetime.now().strftime("%Y-%m-%d"),
            interval="1d"
        )
        
        # تحضير بيانات الأسهم
        stocks_data = {}
        for symbol in symbols[:min(len(symbols), 100)]:  # تحديد عدد الأسهم للفحص
            try:
                historical_data = data_manager.get_historical_data(
                    symbol=symbol,
                    start_date=(datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d"),
                    end_date=datetime.now().strftime("%Y-%m-%d"),
                    interval="1d"
                )
                
                if not historical_data.empty:
                    stocks_data[symbol] = historical_data
            except Exception as e:
                logger.error(f"خطأ في الحصول على البيانات التاريخية للسهم {symbol}: {str(e)}")
        
        # تطبيق معايير الفحص
        if "trend_template" in request.criteria and request.criteria["trend_template"]:
            min_score = request.criteria.get("trend_template_min_score", 5)
            trend_template_stocks = sepa_engine.get_trend_template_stocks(stocks_data, index_data, min_score)
            results.extend(trend_template_stocks)
        
        if "vcp" in request.criteria and request.criteria["vcp"]:
            vcp_stocks = sepa_engine.get_vcp_stocks(stocks_data)
            results.extend(vcp_stocks)
        
        if "buy_recommendations" in request.criteria:
            buy_recommendations_stocks = sepa_engine.get_buy_recommendations(stocks_data)
            results.extend(buy_recommendations_stocks)

