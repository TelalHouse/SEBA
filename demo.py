#!/usr/bin/env python3
"""
سكريبت تشغيل تجريبي لنظام SEBA (روبوت خبير الأسهم للتحليل)
"""

import os
import sys
import logging
import argparse
import time
from dotenv import load_dotenv

# إضافة المسار إلى PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# تحميل متغيرات البيئة
load_dotenv()

# إعداد السجل
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('demo.log')
    ]
)
logger = logging.getLogger(__name__)

def run_demo(symbol, report_type="detailed"):
    """
    تشغيل تجربة تحليل سهم
    
    المعلمات:
        symbol (str): رمز السهم
        report_type (str): نوع التقرير (detailed, summary, technical)
    """
    try:
        from seba.data_integration.data_manager import DataIntegrationManager
        from seba.models.technical_analysis import TechnicalIndicators, PatternRecognition
        from seba.models.sepa_engine import SEPAEngine
        from seba.models.ai_integration import AIIntegrationManager
        
        logger.info(f"بدء تحليل السهم {symbol}...")
        
        # إنشاء مدير تكامل البيانات
        data_manager = DataIntegrationManager()
        
        # الحصول على البيانات التاريخية
        logger.info(f"جاري جلب البيانات التاريخية للسهم {symbol}...")
        historical_data = data_manager.get_historical_data(
            symbol=symbol,
            start_date="2020-01-01",
            end_date="2021-01-01",
            interval="1d"
        )
        
        # الحصول على بيانات المؤشر
        logger.info("جاري جلب بيانات المؤشر...")
        index_data = data_manager.get_historical_data(
            symbol="^GSPC",  # S&P 500
            start_date="2020-01-01",
            end_date="2021-01-01",
            interval="1d"
        )
        
        # حساب المؤشرات الفنية
        logger.info("جاري حساب المؤشرات الفنية...")
        historical_data = TechnicalIndicators.calculate_all_indicators(historical_data, index_data)
        
        # التحقق من معايير Trend Template
        logger.info("جاري التحقق من معايير Trend Template...")
        trend_template_score, trend_template_details = PatternRecognition.check_trend_template(historical_data)
        logger.info(f"درجة Trend Template: {trend_template_score}/8")
        
        # اكتشاف نمط VCP
        logger.info("جاري اكتشاف نمط VCP...")
        has_vcp, vcp_details = PatternRecognition.detect_vcp(historical_data)
        logger.info(f"نمط VCP: {'موجود' if has_vcp else 'غير موجود'}")
        
        # تحليل السهم باستخدام محرك SEPA
        logger.info("جاري تحليل السهم باستخدام محرك SEPA...")
        sepa_engine = SEPAEngine()
        analysis_results = sepa_engine.analyze_stock(historical_data, index_data)
        
        # توليد تقرير التحليل
        logger.info("جاري توليد تقرير التحليل...")
        ai_manager = AIIntegrationManager()
        analysis_report = ai_manager.generate_stock_analysis_report(analysis_results, report_type=report_type)
        
        # توليد توصية بلغة طبيعية
        logger.info("جاري توليد توصية بلغة طبيعية...")
        recommendation = ai_manager.generate_natural_language_recommendation(analysis_results)
        
        # عرض النتائج
        print("\n" + "="*80)
        print(f"تحليل سهم {symbol}")
        print("="*80)
        print(f"درجة Trend Template: {trend_template_score}/8")
        print(f"نمط VCP: {'موجود' if has_vcp else 'غير موجود'}")
        print(f"التوصية: {analysis_results['recommendation']}")
        print(f"درجة الثقة: {analysis_results['confidence_score']:.2f}")
        print(f"نقطة الدخول: {analysis_results['entry_point']:.2f}")
        print(f"وقف الخسارة: {analysis_results['stop_loss']:.2f}")
        print(f"السعر المستهدف: {analysis_results['target_price']:.2f}")
        print(f"نسبة المخاطرة/المكافأة: {analysis_results['risk_reward_ratio']:.2f}")
        print("\nتقرير التحليل:")
        print("-"*80)
        print(analysis_report)
        print("\nالتوصية بلغة طبيعية:")
        print("-"*80)
        print(recommendation)
        print("="*80)
        
        logger.info("تم الانتهاء من تحليل السهم بنجاح")
        
    except Exception as e:
        logger.error(f"حدث خطأ أثناء تحليل السهم: {str(e)}")
        raise

def main():
    """
    الدالة الرئيسية
    """
    parser = argparse.ArgumentParser(description='تشغيل تجربة لنظام SEBA (روبوت خبير الأسهم للتحليل)')
    parser.add_argument('--symbol', type=str, default='AAPL', help='رمز السهم (الافتراضي: AAPL)')
    parser.add_argument('--report-type', type=str, default='detailed', choices=['detailed', 'summary', 'technical'], help='نوع التقرير (الافتراضي: detailed)')
    parser.add_argument('--debug', action='store_true', help='تشغيل في وضع التصحيح')
    args = parser.parse_args()
    
    # تعيين مستوى السجل
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug('تم تفعيل وضع التصحيح')
    
    # تشغيل التجربة
    try:
        run_demo(args.symbol, args.report_type)
    except Exception as e:
        logger.error(f'حدث خطأ أثناء تشغيل التجربة: {str(e)}')
        sys.exit(1)

if __name__ == '__main__':
    main()
