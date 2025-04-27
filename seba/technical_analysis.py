"""
وحدة معالجة البيانات وحساب المؤشرات الفنية لمشروع SEBA
توفر هذه الوحدة الوظائف اللازمة لمعالجة البيانات وحساب المؤشرات الفنية المختلفة
"""

import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Union, Tuple
from datetime import datetime, date, timedelta

# إعداد السجل
logger = logging.getLogger(__name__)

class TechnicalIndicators:
    """فئة لحساب المؤشرات الفنية المختلفة"""
    
    @staticmethod
    def calculate_sma(data: pd.DataFrame, column: str = 'close', periods: List[int] = [20, 50, 150, 200]) -> pd.DataFrame:
        """
        حساب المتوسط المتحرك البسيط (SMA)
        
        المعلمات:
            data (pd.DataFrame): إطار البيانات الذي يحتوي على بيانات الأسعار
            column (str): اسم العمود الذي يحتوي على الأسعار
            periods (List[int]): قائمة بالفترات الزمنية للمتوسط المتحرك
            
        العائد:
            pd.DataFrame: إطار البيانات مع إضافة أعمدة المتوسط المتحرك
        """
        try:
            df = data.copy()
            
            for period in periods:
                df[f'sma_{period}'] = df[column].rolling(window=period).mean()
            
            return df
        except Exception as e:
            logger.error(f"خطأ في حساب المتوسط المتحرك البسيط: {str(e)}")
            return data
    
    @staticmethod
    def calculate_ema(data: pd.DataFrame, column: str = 'close', periods: List[int] = [12, 26, 50, 200]) -> pd.DataFrame:
        """
        حساب المتوسط المتحرك الأسي (EMA)
        
        المعلمات:
            data (pd.DataFrame): إطار البيانات الذي يحتوي على بيانات الأسعار
            column (str): اسم العمود الذي يحتوي على الأسعار
            periods (List[int]): قائمة بالفترات الزمنية للمتوسط المتحرك
            
        العائد:
            pd.DataFrame: إطار البيانات مع إضافة أعمدة المتوسط المتحرك
        """
        try:
            df = data.copy()
            
            for period in periods:
                df[f'ema_{period}'] = df[column].ewm(span=period, adjust=False).mean()
            
            return df
        except Exception as e:
            logger.error(f"خطأ في حساب المتوسط المتحرك الأسي: {str(e)}")
            return data
    
    @staticmethod
    def calculate_rsi(data: pd.DataFrame, column: str = 'close', period: int = 14) -> pd.DataFrame:
        """
        حساب مؤشر القوة النسبية (RSI)
        
        المعلمات:
            data (pd.DataFrame): إطار البيانات الذي يحتوي على بيانات الأسعار
            column (str): اسم العمود الذي يحتوي على الأسعار
            period (int): الفترة الزمنية للمؤشر
            
        العائد:
            pd.DataFrame: إطار البيانات مع إضافة عمود مؤشر القوة النسبية
        """
        try:
            df = data.copy()
            
            # حساب التغير في الأسعار
            delta = df[column].diff()
            
            # فصل التغيرات الإيجابية والسلبية
            gain = delta.where(delta > 0, 0)
            loss = -delta.where(delta < 0, 0)
            
            # حساب المتوسط المتحرك للمكاسب والخسائر
            avg_gain = gain.rolling(window=period).mean()
            avg_loss = loss.rolling(window=period).mean()
            
            # حساب القوة النسبية
            rs = avg_gain / avg_loss
            
            # حساب مؤشر القوة النسبية
            df[f'rsi_{period}'] = 100 - (100 / (1 + rs))
            
            return df
        except Exception as e:
            logger.error(f"خطأ في حساب مؤشر القوة النسبية: {str(e)}")
            return data
    
    @staticmethod
    def calculate_macd(data: pd.DataFrame, column: str = 'close', fast_period: int = 12, slow_period: int = 26, signal_period: int = 9) -> pd.DataFrame:
        """
        حساب مؤشر تقارب وتباعد المتوسطات المتحركة (MACD)
        
        المعلمات:
            data (pd.DataFrame): إطار البيانات الذي يحتوي على بيانات الأسعار
            column (str): اسم العمود الذي يحتوي على الأسعار
            fast_period (int): الفترة الزمنية للمتوسط المتحرك السريع
            slow_period (int): الفترة الزمنية للمتوسط المتحرك البطيء
            signal_period (int): الفترة الزمنية لخط الإشارة
            
        العائد:
            pd.DataFrame: إطار البيانات مع إضافة أعمدة MACD
        """
        try:
            df = data.copy()
            
            # حساب المتوسطات المتحركة الأسية
            ema_fast = df[column].ewm(span=fast_period, adjust=False).mean()
            ema_slow = df[column].ewm(span=slow_period, adjust=False).mean()
            
            # حساب MACD
            df['macd'] = ema_fast - ema_slow
            
            # حساب خط الإشارة
            df['macd_signal'] = df['macd'].ewm(span=signal_period, adjust=False).mean()
            
            # حساب الهستوجرام
            df['macd_histogram'] = df['macd'] - df['macd_signal']
            
            return df
        except Exception as e:
            logger.error(f"خطأ في حساب مؤشر MACD: {str(e)}")
            return data
    
    @staticmethod
    def calculate_bollinger_bands(data: pd.DataFrame, column: str = 'close', period: int = 20, std_dev: float = 2.0) -> pd.DataFrame:
        """
        حساب نطاقات بولينجر (Bollinger Bands)
        
        المعلمات:
            data (pd.DataFrame): إطار البيانات الذي يحتوي على بيانات الأسعار
            column (str): اسم العمود الذي يحتوي على الأسعار
            period (int): الفترة الزمنية للمتوسط المتحرك
            std_dev (float): عدد الانحرافات المعيارية
            
        العائد:
            pd.DataFrame: إطار البيانات مع إضافة أعمدة نطاقات بولينجر
        """
        try:
            df = data.copy()
            
            # حساب المتوسط المتحرك
            df[f'bb_middle_{period}'] = df[column].rolling(window=period).mean()
            
            # حساب الانحراف المعياري
            rolling_std = df[column].rolling(window=period).std()
            
            # حساب النطاق العلوي والسفلي
            df[f'bb_upper_{period}'] = df[f'bb_middle_{period}'] + (rolling_std * std_dev)
            df[f'bb_lower_{period}'] = df[f'bb_middle_{period}'] - (rolling_std * std_dev)
            
            # حساب عرض النطاق
            df[f'bb_width_{period}'] = (df[f'bb_upper_{period}'] - df[f'bb_lower_{period}']) / df[f'bb_middle_{period}']
            
            return df
        except Exception as e:
            logger.error(f"خطأ في حساب نطاقات بولينجر: {str(e)}")
            return data
    
    @staticmethod
    def calculate_atr(data: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """
        حساب المدى الحقيقي المتوسط (ATR)
        
        المعلمات:
            data (pd.DataFrame): إطار البيانات الذي يحتوي على بيانات الأسعار
            period (int): الفترة الزمنية للمؤشر
            
        العائد:
            pd.DataFrame: إطار البيانات مع إضافة عمود ATR
        """
        try:
            df = data.copy()
            
            # حساب المدى الحقيقي
            df['tr'] = np.maximum(
                np.maximum(
                    df['high'] - df['low'],
                    np.abs(df['high'] - df['close'].shift(1))
                ),
                np.abs(df['low'] - df['close'].shift(1))
            )
            
            # حساب المدى الحقيقي المتوسط
            df[f'atr_{period}'] = df['tr'].rolling(window=period).mean()
            
            # حذف العمود المؤقت
            df = df.drop('tr', axis=1)
            
            return df
        except Exception as e:
            logger.error(f"خطأ في حساب المدى الحقيقي المتوسط: {str(e)}")
            return data
    
    @staticmethod
    def calculate_adx(data: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """
        حساب مؤشر الاتجاه المتوسط (ADX)
        
        المعلمات:
            data (pd.DataFrame): إطار البيانات الذي يحتوي على بيانات الأسعار
            period (int): الفترة الزمنية للمؤشر
            
        العائد:
            pd.DataFrame: إطار البيانات مع إضافة أعمدة ADX
        """
        try:
            df = data.copy()
            
            # حساب +DM و -DM
            df['up_move'] = df['high'].diff()
            df['down_move'] = df['low'].shift(1) - df['low']
            
            df['plus_dm'] = np.where(
                (df['up_move'] > df['down_move']) & (df['up_move'] > 0),
                df['up_move'],
                0
            )
            
            df['minus_dm'] = np.where(
                (df['down_move'] > df['up_move']) & (df['down_move'] > 0),
                df['down_move'],
                0
            )
            
            # حساب ATR
            df = TechnicalIndicators.calculate_atr(df, period)
            
            # حساب +DI و -DI
            df[f'plus_di_{period}'] = 100 * (df['plus_dm'].ewm(alpha=1/period, adjust=False).mean() / df[f'atr_{period}'])
            df[f'minus_di_{period}'] = 100 * (df['minus_dm'].ewm(alpha=1/period, adjust=False).mean() / df[f'atr_{period}'])
            
            # حساب DX
            df[f'dx_{period}'] = 100 * np.abs(
                (df[f'plus_di_{period}'] - df[f'minus_di_{period}']) /
                (df[f'plus_di_{period}'] + df[f'minus_di_{period}'])
            )
            
            # حساب ADX
            df[f'adx_{period}'] = df[f'dx_{period}'].ewm(alpha=1/period, adjust=False).mean()
            
            # حذف الأعمدة المؤقتة
            df = df.drop(['up_move', 'down_move', 'plus_dm', 'minus_dm'], axis=1)
            
            return df
        except Exception as e:
            logger.error(f"خطأ في حساب مؤشر ADX: {str(e)}")
            return data
    
    @staticmethod
    def calculate_stochastic(data: pd.DataFrame, k_period: int = 14, d_period: int = 3) -> pd.DataFrame:
        """
        حساب مؤشر الاستوكاستك (Stochastic)
        
        المعلمات:
            data (pd.DataFrame): إطار البيانات الذي يحتوي على بيانات الأسعار
            k_period (int): الفترة الزمنية لخط %K
            d_period (int): الفترة الزمنية لخط %D
            
        العائد:
            pd.DataFrame: إطار البيانات مع إضافة أعمدة الاستوكاستك
        """
        try:
            df = data.copy()
            
            # حساب أعلى سعر وأدنى سعر خلال الفترة
            low_min = df['low'].rolling(window=k_period).min()
            high_max = df['high'].rolling(window=k_period).max()
            
            # حساب %K
            df[f'stoch_k_{k_period}'] = 100 * ((df['close'] - low_min) / (high_max - low_min))
            
            # حساب %D
            df[f'stoch_d_{k_period}_{d_period}'] = df[f'stoch_k_{k_period}'].rolling(window=d_period).mean()
            
            return df
        except Exception as e:
            logger.error(f"خطأ في حساب مؤشر الاستوكاستك: {str(e)}")
            return data
    
    @staticmethod
    def calculate_obv(data: pd.DataFrame) -> pd.DataFrame:
        """
        حساب مؤشر توازن الحجم (OBV)
        
        المعلمات:
            data (pd.DataFrame): إطار البيانات الذي يحتوي على بيانات الأسعار
            
        العائد:
            pd.DataFrame: إطار البيانات مع إضافة عمود OBV
        """
        try:
            df = data.copy()
            
            # حساب تغير السعر
            df['price_change'] = df['close'].diff()
            
            # حساب OBV
            df['obv'] = np.where(
                df['price_change'] > 0,
                df['volume'],
                np.where(
                    df['price_change'] < 0,
                    -df['volume'],
                    0
                )
            )
            
            # تراكم OBV
            df['obv'] = df['obv'].cumsum()
            
            # حذف العمود المؤقت
            df = df.drop('price_change', axis=1)
            
            return df
        except Exception as e:
            logger.error(f"خطأ في حساب مؤشر OBV: {str(e)}")
            return data
    
    @staticmethod
    def calculate_rs_rating(data: pd.DataFrame, base_index_data: pd.DataFrame, period: int = 252) -> pd.DataFrame:
        """
        حساب تصنيف القوة النسبية (RS Rating) مقارنة بمؤشر السوق
        
        المعلمات:
            data (pd.DataFrame): إطار البيانات الذي يحتوي على بيانات الأسعار للسهم
            base_index_data (pd.DataFrame): إطار البيانات الذي يحتوي على بيانات الأسعار للمؤشر
            period (int): الفترة الزمنية للمقارنة (عدد أيام التداول في السنة)
            
        العائد:
            pd.DataFrame: إطار البيانات مع إضافة عمود RS Rating
        """
        try:
            df = data.copy()
            
            # التأكد من أن التواريخ متطابقة
            df = df.sort_values('date')
            base_index_data = base_index_data.sort_values('date')
            
            # حساب العائد للسهم والمؤشر
            df['return'] = df['close'].pct_change(periods=period)
            base_index_data['return'] = base_index_data['close'].pct_change(periods=period)
            
            # دمج البيانات
            merged_data = pd.merge(
                df[['date', 'return']],
                base_index_data[['date', 'return']],
                on='date',
                how='inner',
                suffixes=('_stock', '_index')
            )
            
            # حساب القوة النسبية
            merged_data['rs'] = merged_data['return_stock'] / merged_data['return_index']
            
            # حساب تصنيف القوة النسبية (0-100)
            # تحويل القوة النسبية إلى تصنيف من 0 إلى 100 باستخدام التوزيع الطبيعي
            merged_data['rs_rating'] = merged_data['rs'].rank(pct=True) * 100
            
            # دمج التصنيف مع البيانات الأصلية
            df = pd.merge(
                df,
                merged_data[['date', 'rs_rating']],
                on='date',
                how='left'
            )
            
            # حذف العمود المؤقت
            df = df.drop('return', axis=1)
            
            return df
        except Exception as e:
            logger.error(f"خطأ في حساب تصنيف القوة النسبية: {str(e)}")
            return data
    
    @staticmethod
    def calculate_all_indicators(data: pd.DataFrame, base_index_data: Optional[pd.DataFrame] = None) -> pd.DataFrame:
        """
        حساب جميع المؤشرات الفنية
        
        المعلمات:
            data (pd.DataFrame): إطار البيانات الذي يحتوي على بيانات الأسعار
            base_index_data (pd.DataFrame, optional): إطار البيانات الذي يحتوي على بيانات الأسعار للمؤشر
            
        العائد:
            pd.DataFrame: إطار البيانات مع إضافة جميع المؤشرات الفنية
        """
        try:
            df = data.copy()
            
            # حساب المتوسطات المتحركة البسيطة
            df = TechnicalIndicators.calculate_sma(df)
            
            # حساب المتوسطات المتحركة الأسية
            df = TechnicalIndicators.calculate_ema(df)
            
            # حساب مؤشر القوة النسبية
            df = TechnicalIndicators.calculate_rsi(df)
            
            # حساب مؤشر MACD
            df = TechnicalIndicators.calculate_macd(df)
            
            # حساب نطاقات بولينجر
            df = TechnicalIndicators.calculate_bollinger_bands(df)
            
            # حساب المدى الحقيقي المتوسط
            df = TechnicalIndicators.calculate_atr(df)
            
            # حساب مؤشر ADX
            df = TechnicalIndicators.calculate_adx(df)
            
            # حساب مؤشر الاستوكاستك
            df = TechnicalIndicators.calculate_stochastic(df)
            
            # حساب مؤشر OBV
            df = TechnicalIndicators.calculate_obv(df)
            
            # حساب تصنيف القوة النسبية إذا كانت بيانات المؤشر متوفرة
            if base_index_data is not None:
                df = TechnicalIndicators.calculate_rs_rating(df, base_index_data)
            
            return df
        except Exception as e:
            logger.error(f"خطأ في حساب جميع المؤشرات الفنية: {str(e)}")
            return data


class PatternRecognition:
    """فئة للتعرف على أنماط الأسعار"""
    
    @staticmethod
    def detect_vcp(data: pd.DataFrame, min_contraction: float = 0.5, max_contraction: float = 0.9, min_duration: int = 5, max_duratio
(Content truncated due to size limit. Use line ranges to read in chunks)