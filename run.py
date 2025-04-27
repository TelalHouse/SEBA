#!/usr/bin/env python3
"""
سكريبت تشغيل نظام SEBA (روبوت خبير الأسهم للتحليل)
"""

import os
import sys
import logging
import argparse
from dotenv import load_dotenv
import uvicorn

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
        logging.FileHandler('seba.log')
    ]
)
logger = logging.getLogger(__name__)

def main():
    """
    الدالة الرئيسية لتشغيل نظام SEBA
    """
    parser = argparse.ArgumentParser(description='تشغيل نظام SEBA (روبوت خبير الأسهم للتحليل)')
    parser.add_argument('--host', type=str, default='0.0.0.0', help='المضيف (الافتراضي: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=8000, help='المنفذ (الافتراضي: 8000)')
    parser.add_argument('--reload', action='store_true', help='إعادة التحميل عند تغيير الملفات')
    parser.add_argument('--debug', action='store_true', help='تشغيل في وضع التصحيح')
    args = parser.parse_args()

    # تعيين مستوى السجل
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug('تم تفعيل وضع التصحيح')

    # طباعة معلومات التشغيل
    logger.info(f'بدء تشغيل نظام SEBA على {args.host}:{args.port}')
    logger.info(f'إعادة التحميل: {args.reload}')
    logger.info(f'وضع التصحيح: {args.debug}')

    # تشغيل التطبيق
    try:
        uvicorn.run(
            "seba.api.api:app",
            host=args.host,
            port=args.port,
            reload=args.reload,
            log_level="debug" if args.debug else "info"
        )
    except Exception as e:
        logger.error(f'حدث خطأ أثناء تشغيل التطبيق: {str(e)}')
        sys.exit(1)

if __name__ == '__main__':
    main()
