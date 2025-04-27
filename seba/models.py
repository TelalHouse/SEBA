"""
نماذج قاعدة البيانات لمشروع SEBA
يحتوي هذا الملف على تعريفات نماذج قاعدة البيانات باستخدام SQLAlchemy
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Table, Text, JSON, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import datetime

Base = declarative_base()

# جدول العلاقة بين الأسهم والقوائم
stock_list_association = Table(
    'stock_list_association',
    Base.metadata,
    Column('stock_id', Integer, ForeignKey('stocks.id')),
    Column('list_id', Integer, ForeignKey('stock_lists.id'))
)

class Stock(Base):
    """نموذج السهم"""
    __tablename__ = 'stocks'
    
    id = Column(Integer, primary_key=True)
    symbol = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    exchange = Column(String(50))
    sector = Column(String(100))
    industry = Column(String(100))
    country = Column(String(50))
    currency = Column(String(10))
    description = Column(Text)
    website = Column(String(255))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # العلاقات
    historical_data = relationship("HistoricalData", back_populates="stock")
    fundamental_data = relationship("FundamentalData", back_populates="stock")
    technical_indicators = relationship("TechnicalIndicator", back_populates="stock")
    earnings = relationship("Earnings", back_populates="stock")
    sepa_analyses = relationship("SEPAAnalysis", back_populates="stock")
    lists = relationship("StockList", secondary=stock_list_association, back_populates="stocks")
    
    def __repr__(self):
        return f"<Stock(symbol='{self.symbol}', name='{self.name}')>"

class HistoricalData(Base):
    """نموذج البيانات التاريخية"""
    __tablename__ = 'historical_data'
    
    id = Column(Integer, primary_key=True)
    stock_id = Column(Integer, ForeignKey('stocks.id'), nullable=False)
    date = Column(Date, nullable=False)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    adj_close = Column(Float)
    volume = Column(Float)
    source = Column(String(50))  # مصدر البيانات (yahoo_finance, alpha_vantage, iex_cloud)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # العلاقات
    stock = relationship("Stock", back_populates="historical_data")
    
    __table_args__ = (
        # إنشاء فهرس مركب للسهم والتاريخ
        {'sqlite_autoincrement': True},
    )
    
    def __repr__(self):
        return f"<HistoricalData(stock='{self.stock.symbol}', date='{self.date}', close='{self.close}')>"

class FundamentalData(Base):
    """نموذج البيانات الأساسية"""
    __tablename__ = 'fundamental_data'
    
    id = Column(Integer, primary_key=True)
    stock_id = Column(Integer, ForeignKey('stocks.id'), nullable=False)
    date = Column(Date, nullable=False)
    market_cap = Column(Float)
    pe_ratio = Column(Float)
    eps = Column(Float)
    dividend_yield = Column(Float)
    beta = Column(Float)
    fifty_two_week_high = Column(Float)
    fifty_two_week_low = Column(Float)
    fifty_day_average = Column(Float)
    two_hundred_day_average = Column(Float)
    earnings_growth = Column(Float)
    revenue_growth = Column(Float)
    profit_margin = Column(Float)
    return_on_equity = Column(Float)
    return_on_assets = Column(Float)
    debt_to_equity = Column(Float)
    current_ratio = Column(Float)
    quick_ratio = Column(Float)
    book_value = Column(Float)
    price_to_book = Column(Float)
    source = Column(String(50))  # مصدر البيانات
    raw_data = Column(JSON)  # البيانات الخام
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # العلاقات
    stock = relationship("Stock", back_populates="fundamental_data")
    
    def __repr__(self):
        return f"<FundamentalData(stock='{self.stock.symbol}', date='{self.date}')>"

class TechnicalIndicator(Base):
    """نموذج المؤشرات الفنية"""
    __tablename__ = 'technical_indicators'
    
    id = Column(Integer, primary_key=True)
    stock_id = Column(Integer, ForeignKey('stocks.id'), nullable=False)
    date = Column(Date, nullable=False)
    indicator_type = Column(String(50), nullable=False)  # نوع المؤشر (SMA, EMA, RSI, MACD, BBANDS, STOCH, ADX, CCI, AROON, OBV)
    time_period = Column(Integer)  # الفترة الزمنية للمؤشر
    value = Column(Float)  # قيمة المؤشر
    parameters = Column(JSON)  # معلمات المؤشر
    source = Column(String(50))  # مصدر البيانات
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # العلاقات
    stock = relationship("Stock", back_populates="technical_indicators")
    
    def __repr__(self):
        return f"<TechnicalIndicator(stock='{self.stock.symbol}', date='{self.date}', indicator_type='{self.indicator_type}')>"

class Earnings(Base):
    """نموذج بيانات الأرباح"""
    __tablename__ = 'earnings'
    
    id = Column(Integer, primary_key=True)
    stock_id = Column(Integer, ForeignKey('stocks.id'), nullable=False)
    fiscal_date_ending = Column(Date, nullable=False)
    reported_date = Column(Date)
    reported_eps = Column(Float)
    estimated_eps = Column(Float)
    surprise = Column(Float)
    surprise_percentage = Column(Float)
    is_quarterly = Column(Boolean, default=True)  # ربعي أو سنوي
    source = Column(String(50))  # مصدر البيانات
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # العلاقات
    stock = relationship("Stock", back_populates="earnings")
    
    def __repr__(self):
        return f"<Earnings(stock='{self.stock.symbol}', fiscal_date_ending='{self.fiscal_date_ending}', reported_eps='{self.reported_eps}')>"

class SEPAAnalysis(Base):
    """نموذج تحليل SEPA"""
    __tablename__ = 'sepa_analyses'
    
    id = Column(Integer, primary_key=True)
    stock_id = Column(Integer, ForeignKey('stocks.id'), nullable=False)
    date = Column(Date, nullable=False)
    
    # معايير Trend Template
    is_price_above_ma150 = Column(Boolean)
    is_price_above_ma200 = Column(Boolean)
    is_ma150_above_ma200 = Column(Boolean)
    is_ma50_above_ma150 = Column(Boolean)
    is_ma50_above_ma200 = Column(Boolean)
    is_rs_rating_above_70 = Column(Boolean)
    trend_template_score = Column(Integer)  # عدد المعايير المستوفاة (0-6)
    
    # معايير VCP (Volatility Contraction Pattern)
    has_vcp_pattern = Column(Boolean)
    vcp_stage = Column(String(50))  # مرحلة النمط (Stage 1, Stage 2, Stage 3, Stage 4)
    vcp_contraction_percentage = Column(Float)  # نسبة انكماش التقلب
    
    # نقاط الدخول والخروج
    entry_point = Column(Float)
    stop_loss = Column(Float)
    target_price = Column(Float)
    risk_reward_ratio = Column(Float)
    
    # التوصية
    recommendation = Column(String(50))  # التوصية (Buy, Sell, Hold)
    confidence_score = Column(Float)  # درجة الثقة (0-1)
    
    # تفاصيل إضافية
    analysis_details = Column(JSON)  # تفاصيل التحليل
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # العلاقات
    stock = relationship("Stock", back_populates="sepa_analyses")
    
    def __repr__(self):
        return f"<SEPAAnalysis(stock='{self.stock.symbol}', date='{self.date}', recommendation='{self.recommendation}')>"

class StockList(Base):
    """نموذج قائمة الأسهم"""
    __tablename__ = 'stock_lists'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    is_system = Column(Boolean, default=False)  # قائمة نظام أو قائمة مستخدم
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # العلاقات
    stocks = relationship("Stock", secondary=stock_list_association, back_populates="lists")
    
    def __repr__(self):
        return f"<StockList(name='{self.name}', stocks_count='{len(self.stocks)}')>"

class User(Base):
    """نموذج المستخدم"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(50))
    last_name = Column(String(50))
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # العلاقات
    alerts = relationship("Alert", back_populates="user")
    
    def __repr__(self):
        return f"<User(username='{self.username}', email='{self.email}')>"

class Alert(Base):
    """نموذج التنبيه"""
    __tablename__ = 'alerts'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    stock_id = Column(Integer, ForeignKey('stocks.id'), nullable=False)
    alert_type = Column(String(50), nullable=False)  # نوع التنبيه (price, technical, pattern)
    condition = Column(String(255), nullable=False)  # شرط التنبيه
    value = Column(Float)  # القيمة المستهدفة
    is_active = Column(Boolean, default=True)
    is_triggered = Column(Boolean, default=False)
    triggered_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # العلاقات
    user = relationship("User", back_populates="alerts")
    stock = relationship("Stock")
    
    def __repr__(self):
        return f"<Alert(user='{self.user.username}', stock='{self.stock.symbol}', alert_type='{self.alert_type}')>"

class MarketData(Base):
    """نموذج بيانات السوق"""
    __tablename__ = 'market_data'
    
    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)
    data_type = Column(String(50), nullable=False)  # نوع البيانات (sector_performance, market_indices)
    data = Column(JSON, nullable=False)  # البيانات
    source = Column(String(50))  # مصدر البيانات
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    def __repr__(self):
        return f"<MarketData(date='{self.date}', data_type='{self.data_type}')>"

class ChatSession(Base):
    """نموذج جلسة المحادثة"""
    __tablename__ = 'chat_sessions'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    session_id = Column(String(100), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # العلاقات
    user = relationship("User")
    messages = relationship("ChatMessage", back_populates="session")
    
    def __repr__(self):
        return f"<ChatSession(session_id='{self.session_id}')>"

class ChatMessage(Base):
    """نموذج رسالة المحادثة"""
    __tablename__ = 'chat_messages'
    
    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey('chat_sessions.id'), nullable=False)
    is_user = Column(Boolean, default=True)  # رسالة من المستخدم أو من النظام
    message = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # العلاقات
    session = relationship("ChatSession", back_populates="messages")
    
    def __repr__(self):
        return f"<ChatMessage(is_user='{self.is_user}', message='{self.message[:20]}...')>"
