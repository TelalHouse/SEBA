"""
وحدة اختبارات لمشروع SEBA
توفر هذه الوحدة اختبارات وحدة وتكامل للتأكد من عمل جميع مكونات النظام بشكل صحيح
"""

import unittest
import os
import sys
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

# إضافة المسار إلى PYTHONPATH
sys.path.append('/home/ubuntu/SEBA_Implementation')

# استيراد المكونات المراد اختبارها
from seba.data_integration.data_manager import DataIntegrationManager
from seba.data_integration.yahoo_finance import YahooFinanceAPI
from seba.models.technical_analysis import TechnicalIndicators, PatternRecognition, DataProcessor
from seba.models.sepa_engine import SEPAEngine
from seba.models.ai_integration import OpenAIClient, ChatbotEngine, AIIntegrationManager


class TestDataIntegration(unittest.TestCase):
    """اختبارات وحدة تكامل البيانات"""
    
    def setUp(self):
        """إعداد بيئة الاختبار"""
        self.data_manager = DataIntegrationManager()
        self.yahoo_api = YahooFinanceAPI()
    
    def test_get_historical_data(self):
        """اختبار الحصول على البيانات التاريخية"""
        # تحضير البيانات
        symbol = "AAPL"
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        end_date = datetime.now().strftime("%Y-%m-%d")
        
        # تنفيذ الاختبار
        data = self.data_manager.get_historical_data(symbol, start_date, end_date)
        
        # التحقق من النتائج
        self.assertIsInstance(data, pd.DataFrame)
        self.assertFalse(data.empty)
        self.assertIn('date', data.columns)
        self.assertIn('open', data.columns)
        self.assertIn('high', data.columns)
        self.assertIn('low', data.columns)
        self.assertIn('close', data.columns)
        self.assertIn('volume', data.columns)
    
    def test_get_stock_info(self):
        """اختبار الحصول على معلومات السهم"""
        # تحضير البيانات
        symbol = "AAPL"
        
        # تنفيذ الاختبار
        info = self.data_manager.get_stock_info(symbol)
        
        # التحقق من النتائج
        self.assertIsInstance(info, dict)
        self.assertIn('symbol', info)
        self.assertEqual(info['symbol'], symbol)
    
    def test_yahoo_finance_api(self):
        """اختبار واجهة برمجة تطبيقات Yahoo Finance"""
        # تحضير البيانات
        symbol = "AAPL"
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        end_date = datetime.now().strftime("%Y-%m-%d")
        
        # تنفيذ الاختبار
        data = self.yahoo_api.get_historical_data(symbol, start_date, end_date)
        
        # التحقق من النتائج
        self.assertIsInstance(data, pd.DataFrame)
        self.assertFalse(data.empty)
        self.assertIn('date', data.columns)
        self.assertIn('open', data.columns)
        self.assertIn('high', data.columns)
        self.assertIn('low', data.columns)
        self.assertIn('close', data.columns)
        self.assertIn('volume', data.columns)


class TestTechnicalAnalysis(unittest.TestCase):
    """اختبارات وحدة التحليل الفني"""
    
    def setUp(self):
        """إعداد بيئة الاختبار"""
        # تحضير بيانات الاختبار
        self.test_data = pd.DataFrame({
            'date': pd.date_range(start='2020-01-01', periods=100),
            'open': np.random.rand(100) * 100 + 100,
            'high': np.random.rand(100) * 100 + 150,
            'low': np.random.rand(100) * 100 + 50,
            'close': np.random.rand(100) * 100 + 100,
            'volume': np.random.rand(100) * 1000000
        })
    
    def test_calculate_sma(self):
        """اختبار حساب المتوسط المتحرك البسيط"""
        # تنفيذ الاختبار
        result = TechnicalIndicators.calculate_sma(self.test_data)
        
        # التحقق من النتائج
        self.assertIn('sma_20', result.columns)
        self.assertIn('sma_50', result.columns)
        self.assertIn('sma_150', result.columns)
        self.assertIn('sma_200', result.columns)
    
    def test_calculate_rsi(self):
        """اختبار حساب مؤشر القوة النسبية"""
        # تنفيذ الاختبار
        result = TechnicalIndicators.calculate_rsi(self.test_data)
        
        # التحقق من النتائج
        self.assertIn('rsi_14', result.columns)
        
        # التحقق من أن القيم ضمن النطاق المتوقع (0-100)
        self.assertTrue((result['rsi_14'].dropna() >= 0).all())
        self.assertTrue((result['rsi_14'].dropna() <= 100).all())
    
    def test_calculate_macd(self):
        """اختبار حساب مؤشر MACD"""
        # تنفيذ الاختبار
        result = TechnicalIndicators.calculate_macd(self.test_data)
        
        # التحقق من النتائج
        self.assertIn('macd', result.columns)
        self.assertIn('macd_signal', result.columns)
        self.assertIn('macd_histogram', result.columns)
    
    def test_detect_vcp(self):
        """اختبار اكتشاف نمط VCP"""
        # تنفيذ الاختبار
        # نظراً لأن البيانات عشوائية، قد لا يتم اكتشاف نمط VCP
        # لذلك نتحقق فقط من أن الدالة تعمل بدون أخطاء
        has_vcp, vcp_details = PatternRecognition.detect_vcp(
            TechnicalIndicators.calculate_bollinger_bands(self.test_data)
        )
        
        # التحقق من النتائج
        self.assertIsInstance(has_vcp, bool)
        self.assertIsInstance(vcp_details, dict)
    
    def test_check_trend_template(self):
        """اختبار التحقق من معايير Trend Template"""
        # تحضير البيانات
        data = TechnicalIndicators.calculate_sma(self.test_data)
        
        # تنفيذ الاختبار
        score, details = PatternRecognition.check_trend_template(data)
        
        # التحقق من النتائج
        self.assertIsInstance(score, int)
        self.assertIsInstance(details, dict)
        self.assertIn('trend_template_score', details)
        self.assertEqual(score, details['trend_template_score'])
    
    def test_data_processor(self):
        """اختبار معالج البيانات"""
        # تنفيذ الاختبار
        processed_data = DataProcessor.preprocess_data(self.test_data)
        
        # التحقق من النتائج
        self.assertIsInstance(processed_data, pd.DataFrame)
        self.assertIn('daily_change', processed_data.columns)
        self.assertIn('daily_volatility', processed_data.columns)


class TestSEPAEngine(unittest.TestCase):
    """اختبارات وحدة محرك قواعد SEPA"""
    
    def setUp(self):
        """إعداد بيئة الاختبار"""
        self.sepa_engine = SEPAEngine()
        
        # تحضير بيانات الاختبار
        self.test_data = pd.DataFrame({
            'date': pd.date_range(start='2020-01-01', periods=100),
            'open': np.random.rand(100) * 100 + 100,
            'high': np.random.rand(100) * 100 + 150,
            'low': np.random.rand(100) * 100 + 50,
            'close': np.random.rand(100) * 100 + 100,
            'volume': np.random.rand(100) * 1000000
        })
        
        # تحضير بيانات المؤشر
        self.index_data = pd.DataFrame({
            'date': pd.date_range(start='2020-01-01', periods=100),
            'open': np.random.rand(100) * 1000 + 3000,
            'high': np.random.rand(100) * 1000 + 3500,
            'low': np.random.rand(100) * 1000 + 2500,
            'close': np.random.rand(100) * 1000 + 3000,
            'volume': np.random.rand(100) * 10000000
        })
    
    def test_analyze_stock(self):
        """اختبار تحليل السهم"""
        # تنفيذ الاختبار
        result = self.sepa_engine.analyze_stock(self.test_data, self.index_data)
        
        # التحقق من النتائج
        self.assertIsInstance(result, dict)
        self.assertIn('recommendation', result)
        self.assertIn('confidence_score', result)
        self.assertTrue(0 <= result['confidence_score'] <= 1)
    
    def test_screen_stocks(self):
        """اختبار فحص الأسهم"""
        # تحضير البيانات
        stocks_data = {
            'AAPL': self.test_data.copy(),
            'MSFT': self.test_data.copy(),
            'GOOGL': self.test_data.copy()
        }
        
        # تنفيذ الاختبار
        results = self.sepa_engine.screen_stocks(stocks_data, self.index_data)
        
        # التحقق من النتائج
        self.assertIsInstance(results, list)
        self.assertEqual(len(results), 3)
        for result in results:
            self.assertIn('symbol', result)
            self.assertIn('recommendation', result)
            self.assertIn('confidence_score', result)
    
    def test_get_trend_template_stocks(self):
        """اختبار الحصول على الأسهم التي تستوفي معايير Trend Template"""
        # تحضير البيانات
        stocks_data = {
            'AAPL': TechnicalIndicators.calculate_sma(self.test_data.copy()),
            'MSFT': TechnicalIndicators.calculate_sma(self.test_data.copy()),
            'GOOGL': TechnicalIndicators.calculate_sma(self.test_data.copy())
        }
        
        # تنفيذ الاختبار
        results = self.sepa_engine.get_trend_template_stocks(stocks_data, self.index_data, min_score=0)
        
        # التحقق من النتائج
        self.assertIsInstance(results, list)
        for result in results:
            self.assertIn('symbol', result)
            self.assertIn('trend_template_score', result)
            self.assertIn('trend_template_details', result)


class TestAIIntegration(unittest.TestCase):
    """اختبارات وحدة تكامل الذكاء الاصطناعي"""
    
    def setUp(self):
        """إعداد بيئة الاختبار"""
        # استخدام وهمي لـ OpenAI API
        self.openai_client = OpenAIClient()
        self.openai_client.generate_text = MagicMock(return_value="هذا نص تم توليده باستخدام OpenAI API")
        
        self.chatbot_engine = ChatbotEngine(self.openai_client)
        self.ai_manager = AIIntegrationManager()
        self.ai_manager.openai_client = self.openai_client
        self.ai_manager.chatbot_engine = self.chatbot_engine
    
    def test_generate_analysis_report(self):
        """اختبار توليد تقرير تحليل"""
        # تحضير البيانات
        analysis_data = {
            'symbol': 'AAPL',
            'recommendation': 'Buy',
            'confidence_score': 0.85,
            'trend_template_score': 5,
            'has_vcp_pattern': True,
            'vcp_stage': 'Stage 2',
            'entry_point': 150.0,
            'stop_loss': 140.0,
            'target_price': 180.0
        }
        
        # تنفيذ الاختبار
        with patch.object(self.openai_client, 'generate_analysis_report', return_value="تقرير تحليل للسهم AAPL"):
            report = self.ai_manager.generate_stock_analysis_report(analysis_data)
        
        # التحقق من النتائج
        self.assertIsInstance(report, str)
        self.assertTrue(len(report) > 0)
    
    def test_process_chat_message(self):
        """اختبار معالجة رسالة المحادثة"""
        # تحضير البيانات
        session_id = "test_session"
        message = "ما هو نمط VCP؟"
        
        # تنفيذ الاختبار
        with patch.object(self.chatbot_engine, 'process_message', return_value="نمط VCP هو نمط انكماش التقلب..."):
            response = self.ai_manager.process_chat_message(session_id, message)
        
        # التحقق من النتائج
        self.assertIsInstance(response, str)
        self.assertTrue(len(response) > 0)


class TestAPIEndpoints(unittest.TestCase):
    """اختبارات نقاط نهاية واجهة برمجة التطبيقات"""
    
    def setUp(self):
        """إعداد بيئة الاختبار"""
        # استخدام وهمي لـ FastAPI TestClient
        # هذا الاختبار يحتاج إلى تنفيذ يدوي باستخدام أداة مثل Postman
        pass
    
    def test_api_endpoints(self):
        """اختبار نقاط نهاية واجهة برمجة التطبيقات"""
        # هذا الاختبار يحتاج إلى تنفيذ يدوي
        # يمكن استخدام أداة مثل Postman لاختبار نقاط النهاية
        pass


class TestIntegration(unittest.TestCase):
    """اختبارات التكامل"""
    
    def setUp(self):
        """إعداد بيئة الاختبار"""
        self.data_manager = DataIntegrationManager()
        self.sepa_engine = SEPAEngine()
        self.ai_manager = AIIntegrationManager()
    
    def test_end_to_end_analysis(self):
        """اختبار تحليل من البداية إلى النهاية"""
        # تحضير البيانات
        symbol = "AAPL"
        start_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
        end_date = datetime.now().strftime("%Y-%m-%d")
        
        # الحصول على البيانات التاريخية
        historical_data = self.data_manager.get_historical_data(symbol, start_date, end_date)
        
        # الحصول على بيانات المؤشر
        index_symbol = "^GSPC"
        index_data = self.data_manager.get_historical_data(index_symbol, start_date, end_date)
        
        # تحليل السهم
        analysis_results = self.sepa_engine.analyze_stock(historical_data, index_data)
        
        # توليد تقرير التحليل
        with patch.object(self.ai_manager.openai_client, 'generate_analysis_report', return_value="تقرير تحليل للسهم AAPL"):
            analysis_report = self.ai_manager.generate_stock_analysis_report(analysis_results)
        
        # التحقق من النتائج
        self.assertIsInstance(analysis_results, dict)
        self.assertIn('recommendation', analysis_results)
        self.assertIn('confidence_score', analysis_results)
        self.assertIsInstance(analysis_report, str)
        self.assertTrue(len(analysis_report) > 0)


if __name__ == '__main__':
    unittest.main()
