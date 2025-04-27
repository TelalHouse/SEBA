#!/usr/bin/env python3
"""
سكريبت نشر نظام SEBA (روبوت خبير الأسهم للتحليل)
"""

import os
import sys
import logging
import argparse
import subprocess
import shutil
import time

# إعداد السجل
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('deploy.log')
    ]
)
logger = logging.getLogger(__name__)

def check_dependencies():
    """
    التحقق من وجود التبعيات المطلوبة
    
    العائد:
        bool: True إذا كانت جميع التبعيات موجودة، False خلاف ذلك
    """
    logger.info("التحقق من وجود التبعيات المطلوبة...")
    
    dependencies = ["python3", "pip3", "uvicorn", "nginx"]
    missing = []
    
    for dep in dependencies:
        try:
            subprocess.run(["which", dep], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            logger.info(f"✓ {dep} موجود")
        except subprocess.CalledProcessError:
            logger.error(f"✗ {dep} غير موجود")
            missing.append(dep)
    
    if missing:
        logger.error(f"التبعيات المفقودة: {', '.join(missing)}")
        return False
    
    return True

def setup_environment(env_file):
    """
    إعداد ملف البيئة
    
    المعلمات:
        env_file (str): مسار ملف البيئة
        
    العائد:
        bool: True في حالة النجاح، False في حالة الفشل
    """
    logger.info(f"إعداد ملف البيئة {env_file}...")
    
    if os.path.exists(env_file):
        logger.info(f"ملف البيئة {env_file} موجود بالفعل")
        return True
    
    try:
        # إنشاء ملف البيئة من النموذج
        env_example = f"{os.path.splitext(env_file)[0]}.example"
        if os.path.exists(env_example):
            shutil.copy(env_example, env_file)
            logger.info(f"تم إنشاء ملف البيئة {env_file} من النموذج {env_example}")
            
            # تعديل ملف البيئة
            logger.info("يرجى تعديل ملف البيئة بالقيم المناسبة")
            return True
        else:
            logger.error(f"نموذج ملف البيئة {env_example} غير موجود")
            return False
    except Exception as e:
        logger.error(f"حدث خطأ أثناء إعداد ملف البيئة: {str(e)}")
        return False

def install_requirements(requirements_file):
    """
    تثبيت المتطلبات
    
    المعلمات:
        requirements_file (str): مسار ملف المتطلبات
        
    العائد:
        bool: True في حالة النجاح، False في حالة الفشل
    """
    logger.info(f"تثبيت المتطلبات من {requirements_file}...")
    
    try:
        subprocess.run(["pip3", "install", "-r", requirements_file], check=True)
        logger.info("تم تثبيت المتطلبات بنجاح")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"حدث خطأ أثناء تثبيت المتطلبات: {str(e)}")
        return False

def setup_database():
    """
    إعداد قاعدة البيانات
    
    العائد:
        bool: True في حالة النجاح، False في حالة الفشل
    """
    logger.info("إعداد قاعدة البيانات...")
    
    try:
        # تنفيذ سكريبت إعداد قاعدة البيانات
        subprocess.run(["python3", "-c", "from seba.database.db_manager import DatabaseManager; DatabaseManager().setup_database()"], check=True)
        logger.info("تم إعداد قاعدة البيانات بنجاح")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"حدث خطأ أثناء إعداد قاعدة البيانات: {str(e)}")
        return False

def setup_nginx(port):
    """
    إعداد Nginx
    
    المعلمات:
        port (int): المنفذ الذي يعمل عليه التطبيق
        
    العائد:
        bool: True في حالة النجاح، False في حالة الفشل
    """
    logger.info(f"إعداد Nginx للعمل مع التطبيق على المنفذ {port}...")
    
    nginx_conf = f"""server {{
    listen 80;
    server_name _;

    location / {{
        proxy_pass http://localhost:{port};
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }}
}}
"""
    
    try:
        # كتابة ملف تكوين Nginx
        with open("/tmp/seba_nginx.conf", "w") as f:
            f.write(nginx_conf)
        
        # نسخ ملف التكوين إلى المكان المناسب
        subprocess.run(["sudo", "cp", "/tmp/seba_nginx.conf", "/etc/nginx/sites-available/seba"], check=True)
        
        # إنشاء رابط رمزي في sites-enabled
        subprocess.run(["sudo", "ln", "-sf", "/etc/nginx/sites-available/seba", "/etc/nginx/sites-enabled/"], check=True)
        
        # التحقق من صحة التكوين
        subprocess.run(["sudo", "nginx", "-t"], check=True)
        
        # إعادة تشغيل Nginx
        subprocess.run(["sudo", "systemctl", "restart", "nginx"], check=True)
        
        logger.info("تم إعداد Nginx بنجاح")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"حدث خطأ أثناء إعداد Nginx: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"حدث خطأ أثناء إعداد Nginx: {str(e)}")
        return False

def setup_systemd(app_dir, port):
    """
    إعداد خدمة Systemd
    
    المعلمات:
        app_dir (str): مسار دليل التطبيق
        port (int): المنفذ الذي يعمل عليه التطبيق
        
    العائد:
        bool: True في حالة النجاح، False في حالة الفشل
    """
    logger.info("إعداد خدمة Systemd...")
    
    service_file = f"""[Unit]
Description=SEBA (روبوت خبير الأسهم للتحليل)
After=network.target

[Service]
User={os.getenv('USER')}
WorkingDirectory={app_dir}
ExecStart={sys.executable} {os.path.join(app_dir, 'run.py')} --host 0.0.0.0 --port {port}
Restart=always
RestartSec=5
Environment="PATH={os.environ['PATH']}"

[Install]
WantedBy=multi-user.target
"""
    
    try:
        # كتابة ملف خدمة Systemd
        with open("/tmp/seba.service", "w") as f:
            f.write(service_file)
        
        # نسخ ملف الخدمة إلى المكان المناسب
        subprocess.run(["sudo", "cp", "/tmp/seba.service", "/etc/systemd/system/"], check=True)
        
        # إعادة تحميل تكوينات Systemd
        subprocess.run(["sudo", "systemctl", "daemon-reload"], check=True)
        
        # تمكين الخدمة
        subprocess.run(["sudo", "systemctl", "enable", "seba"], check=True)
        
        # بدء الخدمة
        subprocess.run(["sudo", "systemctl", "start", "seba"], check=True)
        
        # التحقق من حالة الخدمة
        subprocess.run(["sudo", "systemctl", "status", "seba"], check=True)
        
        logger.info("تم إعداد خدمة Systemd بنجاح")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"حدث خطأ أثناء إعداد خدمة Systemd: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"حدث خطأ أثناء إعداد خدمة Systemd: {str(e)}")
        return False

def deploy_static_files(static_dir, target_dir):
    """
    نشر الملفات الثابتة
    
    المعلمات:
        static_dir (str): مسار دليل الملفات الثابتة
        target_dir (str): مسار دليل الهدف
        
    العائد:
        bool: True في حالة النجاح، False في حالة الفشل
    """
    logger.info(f"نشر الملفات الثابتة من {static_dir} إلى {target_dir}...")
    
    try:
        # إنشاء دليل الهدف إذا لم يكن موجوداً
        os.makedirs(target_dir, exist_ok=True)
        
        # نسخ الملفات الثابتة
        for item in os.listdir(static_dir):
            s = os.path.join(static_dir, item)
            d = os.path.join(target_dir, item)
            if os.path.isdir(s):
                shutil.copytree(s, d, dirs_exist_ok=True)
            else:
                shutil.copy2(s, d)
        
        logger.info("تم نشر الملفات الثابتة بنجاح")
        return True
    except Exception as e:
        logger.error(f"حدث خطأ أثناء نشر الملفات الثابتة: {str(e)}")
        return False

def run_tests():
    """
    تشغيل الاختبارات
    
    العائد:
        bool: True في حالة النجاح، False في حالة الفشل
    """
    logger.info("تشغيل الاختبارات...")
    
    try:
        subprocess.run(["python3", "-m", "unittest", "discover", "tests"], check=True)
        logger.info("تم اجتياز جميع الاختبارات بنجاح")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"فشلت بعض الاختبارات: {str(e)}")
        return False

def deploy_application(args):
    """
    نشر التطبيق
    
    المعلمات:
        args (Namespace): معلمات سطر الأوامر
        
    العائد:
        bool: True في حالة النجاح، False في حالة الفشل
    """
    logger.info("بدء عملية نشر التطبيق...")
    
    # التحقق من وجود التبعيات
    if not check_dependencies():
        if not args.skip_dependencies:
            logger.error("فشل التحقق من وجود التبعيات")
            return False
        else:
            logger.warning("تم تخطي التحقق من وجود التبعيات")
    
    # إعداد ملف البيئة
    if not setup_environment(args.env_file):
        if not args.skip_env:
            logger.error("فشل إعداد ملف البيئة")
            return False
        else:
            logger.warning("تم تخطي إعداد ملف البيئة")
    
    # تثبيت المتطلبات
    if not install_requirements(args.requirements):
        if not args.skip_requirements:
            logger.error("فشل تثبيت المتطلبات")
            return False
        else:
            logger.warning("تم تخطي تثبيت المتطلبات")
    
    # تشغيل الاختبارات
    if not args.skip_tests:
        if not run_tests():
            logger.error("فشلت الاختبارات")
            return False
    else:
        logger.warning("تم تخطي تشغيل الاختبارات")
    
    # إعداد قاعدة البيانات
    if not args.skip_database:
        if not setup_database():
            logger.error("فشل إعداد قاعدة البيانات")
            return False
    else:
        logger.warning("تم تخطي إعداد قاعدة البيانات")
    
    # نشر الملفات الثابتة
    if not args.skip_static:
        if not deploy_static_files(args.static_dir, args.static_target):
            logger.error("فشل نشر الملفات الثابتة")
            return False
    else:
        logger.warning("تم تخطي نشر الملفات الثابتة")
    
    # إعداد Nginx
    if not args.skip_nginx:
        if not setup_nginx(args.port):
            logger.error("فشل إعداد Nginx")
            return False
    else:
        logger.warning("تم تخطي إعداد Nginx")
    
    # إعداد خدمة Systemd
    if not args.skip_systemd:
        if not setup_systemd(args.app_dir, args.port):
            logger.error("فشل إعداد خدمة Systemd")
            return False
    else:
        logger.warning("تم تخطي إعداد خدمة Systemd")
    
    logger.info("تم نشر التطبيق بنجاح!")
    logger.info(f"يمكن الوصول إلى التطبيق على http://localhost:{args.port}")
    
    return True

def main():
    """
    الدالة الرئيسية
    """
    parser = argparse.ArgumentParser(description='نشر نظام SEBA (روبوت خبير الأسهم للتحليل)')
    parser.add_argument('--app-dir', type=str, default=os.path.dirname(os.path.abspath(__file__)), help='مسار دليل التطبيق')
    parser.add_argument('--port', type=int, default=8000, help='المنفذ الذي يعمل عليه التطبيق')
    parser.add_argument('--env-file', type=str, default='.env', help='مسار ملف البيئة')
    parser.add_argument('--requirements', type=str, default='requirements.txt', help='مسار ملف المتطلبات')
    parser.add_argument('--static-dir', type=str, default='static', help='مسار دليل الملفات الثابتة')
    parser.add_argument('--static-target', type=str, default='/var/www/seba/static', help='مسار دليل الهدف للملفات الثابتة')
    parser.add_argument('--skip-dependencies', action='store_true', help='تخطي التحقق من وجود التبعيات')
    parser.add_argument('--skip-env', action='store_true', help='تخطي إعداد ملف البيئة')
    parser.add_argument('--skip-requirements', action='store_true', help='تخطي تثبيت المتطلبات')
    parser.add_argument('--skip-tests', action='store_true', help='تخطي تشغيل الاختبارات')
    parser.add_argument('--skip-database', action='store_true', help='تخطي إعداد قاعدة البيانات')
    parser.add_argument('--skip-static', action='store_true', help='تخطي نشر الملفات الثابتة')
    parser.add_argument('--skip-nginx', action='store_true', help='تخطي إعداد Nginx')
    parser.add_argument('--skip-systemd', action='store_true', help='تخطي إعداد خدمة Systemd')
    parser.add_argument('--debug', action='store_true', help='تشغيل في وضع التصحيح')
    args = parser.parse_args()
    
    # تعيين مستوى السجل
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug('تم تفعيل وضع التصحيح')
    
    # نشر التطبيق
    if deploy_application(args):
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == '__main__':
    main()
