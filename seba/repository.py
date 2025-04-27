"""
وحدة التخزين والاسترجاع لمشروع SEBA
توفر هذه الوحدة الوظائف اللازمة لتخزين واسترجاع البيانات من قاعدة البيانات
"""

import logging
from typing import List, Dict, Optional, Union, Any
from datetime import datetime, date
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import and_, or_, desc, func

from seba.database.db_manager import DatabaseManager
from seba.database.models import (
    Stock, HistoricalData, FundamentalData, TechnicalIndicator,
    Earnings, SEPAAnalysis, StockList, User, Alert, MarketData,
    ChatSession, ChatMessage
)

# إعداد السجل
logger = logging.getLogger(__name__)

class StockRepository:
    """فئة للتعامل مع تخزين واسترجاع بيانات الأسهم"""
    
    def __init__(self):
        """تهيئة الفئة"""
        self.db_manager = DatabaseManager()
    
    def add_stock(self, stock_data: Dict) -> Optional[Stock]:
        """
        إضافة سهم جديد إلى قاعدة البيانات
        
        المعلمات:
            stock_data (Dict): بيانات السهم
            
        العائد:
            Optional[Stock]: كائن السهم المضاف، أو None في حالة الفشل
        """
        session = self.db_manager.get_session()
        try:
            # التحقق من وجود السهم
            existing_stock = session.query(Stock).filter(Stock.symbol == stock_data['symbol']).first()
            if existing_stock:
                logger.info(f"السهم {stock_data['symbol']} موجود بالفعل، سيتم تحديث البيانات")
                
                # تحديث البيانات الموجودة
                for key, value in stock_data.items():
                    if key != 'symbol' and hasattr(existing_stock, key):
                        setattr(existing_stock, key, value)
                
                existing_stock.updated_at = datetime.utcnow()
                session.commit()
                return existing_stock
            
            # إنشاء سهم جديد
            new_stock = Stock(**stock_data)
            session.add(new_stock)
            session.commit()
            logger.info(f"تمت إضافة السهم {stock_data['symbol']} بنجاح")
            return new_stock
            
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"خطأ في إضافة السهم {stock_data.get('symbol', 'unknown')}: {str(e)}")
            return None
        finally:
            session.close()
    
    def get_stock_by_symbol(self, symbol: str) -> Optional[Stock]:
        """
        الحصول على سهم بواسطة الرمز
        
        المعلمات:
            symbol (str): رمز السهم
            
        العائد:
            Optional[Stock]: كائن السهم، أو None إذا لم يتم العثور عليه
        """
        session = self.db_manager.get_session()
        try:
            stock = session.query(Stock).filter(Stock.symbol == symbol).first()
            return stock
        except SQLAlchemyError as e:
            logger.error(f"خطأ في الحصول على السهم {symbol}: {str(e)}")
            return None
        finally:
            session.close()
    
    def get_stock_by_id(self, stock_id: int) -> Optional[Stock]:
        """
        الحصول على سهم بواسطة المعرف
        
        المعلمات:
            stock_id (int): معرف السهم
            
        العائد:
            Optional[Stock]: كائن السهم، أو None إذا لم يتم العثور عليه
        """
        session = self.db_manager.get_session()
        try:
            stock = session.query(Stock).filter(Stock.id == stock_id).first()
            return stock
        except SQLAlchemyError as e:
            logger.error(f"خطأ في الحصول على السهم بالمعرف {stock_id}: {str(e)}")
            return None
        finally:
            session.close()
    
    def get_all_stocks(self, active_only: bool = True) -> List[Stock]:
        """
        الحصول على جميع الأسهم
        
        المعلمات:
            active_only (bool, optional): استرجاع الأسهم النشطة فقط
            
        العائد:
            List[Stock]: قائمة بكائنات الأسهم
        """
        session = self.db_manager.get_session()
        try:
            query = session.query(Stock)
            if active_only:
                query = query.filter(Stock.is_active == True)
            stocks = query.all()
            return stocks
        except SQLAlchemyError as e:
            logger.error(f"خطأ في الحصول على جميع الأسهم: {str(e)}")
            return []
        finally:
            session.close()
    
    def search_stocks(self, search_term: str) -> List[Stock]:
        """
        البحث عن الأسهم
        
        المعلمات:
            search_term (str): مصطلح البحث
            
        العائد:
            List[Stock]: قائمة بكائنات الأسهم المطابقة
        """
        session = self.db_manager.get_session()
        try:
            # البحث في الرمز والاسم
            search_pattern = f"%{search_term}%"
            stocks = session.query(Stock).filter(
                or_(
                    Stock.symbol.ilike(search_pattern),
                    Stock.name.ilike(search_pattern)
                )
            ).all()
            return stocks
        except SQLAlchemyError as e:
            logger.error(f"خطأ في البحث عن الأسهم بالمصطلح {search_term}: {str(e)}")
            return []
        finally:
            session.close()
    
    def delete_stock(self, symbol: str) -> bool:
        """
        حذف سهم من قاعدة البيانات
        
        المعلمات:
            symbol (str): رمز السهم
            
        العائد:
            bool: True في حالة النجاح، False في حالة الفشل
        """
        session = self.db_manager.get_session()
        try:
            stock = session.query(Stock).filter(Stock.symbol == symbol).first()
            if not stock:
                logger.warning(f"لم يتم العثور على السهم {symbol} للحذف")
                return False
            
            # حذف البيانات المرتبطة
            session.query(HistoricalData).filter(HistoricalData.stock_id == stock.id).delete()
            session.query(FundamentalData).filter(FundamentalData.stock_id == stock.id).delete()
            session.query(TechnicalIndicator).filter(TechnicalIndicator.stock_id == stock.id).delete()
            session.query(Earnings).filter(Earnings.stock_id == stock.id).delete()
            session.query(SEPAAnalysis).filter(SEPAAnalysis.stock_id == stock.id).delete()
            session.query(Alert).filter(Alert.stock_id == stock.id).delete()
            
            # حذف السهم
            session.delete(stock)
            session.commit()
            logger.info(f"تم حذف السهم {symbol} بنجاح")
            return True
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"خطأ في حذف السهم {symbol}: {str(e)}")
            return False
        finally:
            session.close()

class HistoricalDataRepository:
    """فئة للتعامل مع تخزين واسترجاع البيانات التاريخية"""
    
    def __init__(self):
        """تهيئة الفئة"""
        self.db_manager = DatabaseManager()
        self.stock_repo = StockRepository()
    
    def add_historical_data(self, symbol: str, data_df, source: str = "yahoo_finance") -> bool:
        """
        إضافة بيانات تاريخية لسهم معين
        
        المعلمات:
            symbol (str): رمز السهم
            data_df: إطار بيانات pandas يحتوي على البيانات التاريخية
            source (str, optional): مصدر البيانات
            
        العائد:
            bool: True في حالة النجاح، False في حالة الفشل
        """
        session = self.db_manager.get_session()
        try:
            # الحصول على السهم
            stock = self.stock_repo.get_stock_by_symbol(symbol)
            if not stock:
                logger.error(f"لم يتم العثور على السهم {symbol} لإضافة البيانات التاريخية")
                return False
            
            # تحويل إطار البيانات إلى قائمة قواميس
            records = []
            for _, row in data_df.iterrows():
                record = {
                    'stock_id': stock.id,
                    'date': row['date'] if isinstance(row['date'], date) else row['date'].date(),
                    'open': row.get('open'),
                    'high': row.get('high'),
                    'low': row.get('low'),
                    'close': row.get('close'),
                    'adj_close': row.get('adj_close'),
                    'volume': row.get('volume'),
                    'source': source,
                    'created_at': datetime.utcnow()
                }
                records.append(record)
            
            # حذف البيانات الموجودة للتواريخ المتداخلة
            dates = [record['date'] for record in records]
            session.query(HistoricalData).filter(
                and_(
                    HistoricalData.stock_id == stock.id,
                    HistoricalData.date.in_(dates)
                )
            ).delete(synchronize_session=False)
            
            # إضافة البيانات الجديدة
            for record in records:
                session.add(HistoricalData(**record))
            
            session.commit()
            logger.info(f"تمت إضافة {len(records)} سجل من البيانات التاريخية للسهم {symbol}")
            return True
            
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"خطأ في إضافة البيانات التاريخية للسهم {symbol}: {str(e)}")
            return False
        finally:
            session.close()
    
    def get_historical_data(
        self, 
        symbol: str, 
        start_date: Optional[date] = None, 
        end_date: Optional[date] = None,
        limit: Optional[int] = None
    ) -> List[HistoricalData]:
        """
        الحصول على البيانات التاريخية لسهم معين
        
        المعلمات:
            symbol (str): رمز السهم
            start_date (date, optional): تاريخ البداية
            end_date (date, optional): تاريخ النهاية
            limit (int, optional): عدد السجلات المطلوبة
            
        العائد:
            List[HistoricalData]: قائمة بكائنات البيانات التاريخية
        """
        session = self.db_manager.get_session()
        try:
            # الحصول على السهم
            stock = self.stock_repo.get_stock_by_symbol(symbol)
            if not stock:
                logger.error(f"لم يتم العثور على السهم {symbol} للحصول على البيانات التاريخية")
                return []
            
            # بناء الاستعلام
            query = session.query(HistoricalData).filter(HistoricalData.stock_id == stock.id)
            
            if start_date:
                query = query.filter(HistoricalData.date >= start_date)
            
            if end_date:
                query = query.filter(HistoricalData.date <= end_date)
            
            # ترتيب البيانات حسب التاريخ (من الأحدث إلى الأقدم)
            query = query.order_by(desc(HistoricalData.date))
            
            if limit:
                query = query.limit(limit)
            
            historical_data = query.all()
            return historical_data
            
        except SQLAlchemyError as e:
            logger.error(f"خطأ في الحصول على البيانات التاريخية للسهم {symbol}: {str(e)}")
            return []
        finally:
            session.close()

class FundamentalDataRepository:
    """فئة للتعامل مع تخزين واسترجاع البيانات الأساسية"""
    
    def __init__(self):
        """تهيئة الفئة"""
        self.db_manager = DatabaseManager()
        self.stock_repo = StockRepository()
    
    def add_fundamental_data(self, symbol: str, data: Dict, source: str = "yahoo_finance") -> bool:
        """
        إضافة بيانات أساسية لسهم معين
        
        المعلمات:
            symbol (str): رمز السهم
            data (Dict): بيانات أساسية
            source (str, optional): مصدر البيانات
            
        العائد:
            bool: True في حالة النجاح، False في حالة الفشل
        """
        session = self.db_manager.get_session()
        try:
            # الحصول على السهم
            stock = self.stock_repo.get_stock_by_symbol(symbol)
            if not stock:
                logger.error(f"لم يتم العثور على السهم {symbol} لإضافة البيانات الأساسية")
                return False
            
            # إعداد البيانات
            today = datetime.utcnow().date()
            fundamental_data = {
                'stock_id': stock.id,
                'date': today,
                'market_cap': data.get('market_cap'),
                'pe_ratio': data.get('pe_ratio'),
                'eps': data.get('eps'),
                'dividend_yield': data.get('dividend_yield'),
                'beta': data.get('beta'),
                'fifty_two_week_high': data.get('fifty_two_week_high'),
                'fifty_two_week_low': data.get('fifty_two_week_low'),
                'fifty_day_average': data.get('fifty_day_average'),
                'two_hundred_day_average': data.get('two_hundred_day_average'),
                'earnings_growth': data.get('earnings_growth'),
                'revenue_growth': data.get('revenue_growth'),
                'profit_margin': data.get('profit_margin'),
                'return_on_equity': data.get('return_on_equity'),
                'return_on_assets': data.get('return_on_assets'),
                'debt_to_equity': data.get('debt_to_equity'),
                'current_ratio': data.get('current_ratio'),
                'quick_ratio': data.get('quick_ratio'),
                'book_value': data.get('book_value'),
                'price_to_book': data.get('price_to_book'),
                'source': source,
                'raw_data': data,
                'created_at': datetime.utcnow()
            }
            
            # حذف البيانات الموجودة لنفس اليوم
            session.query(FundamentalData).filter(
                and_(
                    FundamentalData.stock_id == stock.id,
                    FundamentalData.date == today
                )
            ).delete(synchronize_session=False)
            
            # إضافة البيانات الجديدة
            session.add(FundamentalData(**fundamental_data))
            
            session.commit()
            logger.info(f"تمت إضافة البيانات الأساسية للسهم {symbol}")
            return True
            
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"خطأ في إضافة البيانات الأساسية للسهم {symbol}: {str(e)}")
            return False
        finally:
            session.close()
    
    def get_latest_fundamental_data(self, symbol: str) -> Optional[FundamentalData]:
        """
        الحصول على أحدث البيانات الأساسية لسهم معين
        
        المعلمات:
            symbol (str): رمز السهم
            
        العائد:
            Optional[FundamentalData]: كائن البيانات الأساسية، أو None إذا لم يتم العثور عليه
        """
        session = self.db_manager.get_session()
        try:
            # الحصول على السهم
            stock = self.stock_repo.get_stock_by_symbol(symbol)
            if not stock:
                logger.error(f"لم يتم العثور على السهم {symbol} للحصول على البيانات الأساسية")
                return None
            
            # الحصول على أحدث البيانات
            fundamental_data = session.query(FundamentalData).filter(
                FundamentalData.stock_id == stock.id
            ).order_by(desc(FundamentalData.date)).first()
            
            return fundamental_data
            
        except SQLAlchemyError as e:
            logger.error(f"خطأ في الحصول على البيانات الأساسية للسهم {symbol}: {str(e)}")
            return None
        finally:
            session.close()

class TechnicalIndicatorRepository:
    """فئة للتعامل مع تخزين واسترجاع المؤشرات الفنية"""
    
    def __init__(self):
        """تهيئة الفئة"""
        self.db_manager = DatabaseManager()
        self.stock_repo = StockRepository()
    
    def add_technical_indicator(
        self, 
        symbol: str, 
        indicator_type: str, 
        date_val: date, 
        value: float, 
        time_period: int = None, 
        parameters: Dict = None, 
        source: str = "alpha_vantage"
    ) -> bool:
        """
        إضافة مؤشر فني لسهم معين
    
(Content truncated due to size limit. Use line ranges to read in chunks)