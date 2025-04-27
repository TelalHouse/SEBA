"""
وحدة تكامل الذكاء الاصطناعي مع OpenAI API لمشروع SEBA
توفر هذه الوحدة الوظائف اللازمة للتفاعل مع نماذج GPT-4 لتوليد تحليلات وتوصيات بلغة طبيعية
"""

import os
import logging
import json
import time
from typing import Dict, List, Optional, Union, Any
from datetime import datetime, date, timedelta
import openai
from dotenv import load_dotenv

# إعداد السجل
logger = logging.getLogger(__name__)

# تحميل متغيرات البيئة
load_dotenv()

class OpenAIClient:
    """فئة للتفاعل مع OpenAI API"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        تهيئة الفئة
        
        المعلمات:
            api_key (str, optional): مفتاح API لـ OpenAI. إذا لم يتم تحديده، سيتم استخدام المفتاح من متغيرات البيئة.
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            logger.warning("لم يتم تحديد مفتاح API لـ OpenAI. لن تعمل وظائف الذكاء الاصطناعي.")
        else:
            openai.api_key = self.api_key
        
        self.model = os.getenv("OPENAI_MODEL", "gpt-4")
        logger.info(f"تهيئة عميل OpenAI باستخدام النموذج {self.model}")
    
    def generate_text(self, prompt: str, max_tokens: int = 1000, temperature: float = 0.7) -> str:
        """
        توليد نص باستخدام OpenAI API
        
        المعلمات:
            prompt (str): النص المحفز
            max_tokens (int, optional): الحد الأقصى لعدد الرموز في الاستجابة
            temperature (float, optional): درجة الحرارة (0.0 - 1.0)
            
        العائد:
            str: النص المولد
        """
        try:
            if not self.api_key:
                logger.error("لم يتم تحديد مفتاح API لـ OpenAI")
                return "خطأ: لم يتم تحديد مفتاح API لـ OpenAI"
            
            logger.info(f"توليد نص باستخدام OpenAI API (max_tokens={max_tokens}, temperature={temperature})")
            
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "أنت مساعد مالي خبير في تحليل الأسهم وتوصيات التداول باستخدام منهجية SEPA (Specific Entry Point Analysis) لمارك مينيرفيني."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            generated_text = response.choices[0].message.content.strip()
            
            return generated_text
            
        except Exception as e:
            logger.error(f"خطأ في توليد النص باستخدام OpenAI API: {str(e)}")
            return f"خطأ: {str(e)}"
    
    def generate_analysis_report(self, analysis_data: Dict, report_type: str = "detailed") -> str:
        """
        توليد تقرير تحليل للسهم
        
        المعلمات:
            analysis_data (Dict): بيانات تحليل السهم
            report_type (str, optional): نوع التقرير (detailed, summary, technical)
            
        العائد:
            str: تقرير التحليل
        """
        try:
            logger.info(f"توليد تقرير تحليل للسهم {analysis_data.get('symbol')} (نوع التقرير: {report_type})")
            
            # إعداد النص المحفز
            prompt = self._prepare_analysis_prompt(analysis_data, report_type)
            
            # توليد التقرير
            max_tokens = 2000 if report_type == "detailed" else 1000
            report = self.generate_text(prompt, max_tokens=max_tokens, temperature=0.5)
            
            return report
            
        except Exception as e:
            logger.error(f"خطأ في توليد تقرير تحليل للسهم: {str(e)}")
            return f"خطأ: {str(e)}"
    
    def _prepare_analysis_prompt(self, analysis_data: Dict, report_type: str) -> str:
        """
        إعداد النص المحفز لتوليد تقرير التحليل
        
        المعلمات:
            analysis_data (Dict): بيانات تحليل السهم
            report_type (str): نوع التقرير
            
        العائد:
            str: النص المحفز
        """
        # استخراج البيانات المهمة
        symbol = analysis_data.get('symbol', 'غير معروف')
        recommendation = analysis_data.get('recommendation', 'Hold')
        confidence_score = analysis_data.get('confidence_score', 0.5)
        trend_template_score = analysis_data.get('trend_template_score', 0)
        has_vcp_pattern = analysis_data.get('has_vcp_pattern', False)
        vcp_stage = analysis_data.get('vcp_stage', None)
        entry_point = analysis_data.get('entry_point', 0)
        stop_loss = analysis_data.get('stop_loss', 0)
        target_price = analysis_data.get('target_price', 0)
        
        # إعداد النص المحفز حسب نوع التقرير
        if report_type == "detailed":
            prompt = f"""
            أنت مستشار مالي خبير في تحليل الأسهم باستخدام منهجية SEPA (Specific Entry Point Analysis) لمارك مينيرفيني.
            
            قم بإعداد تقرير تحليل مفصل للسهم {symbol} بناءً على البيانات التالية:
            
            - التوصية: {recommendation}
            - درجة الثقة: {confidence_score:.2f}
            - درجة Trend Template: {trend_template_score}/6
            - وجود نمط VCP: {'نعم' if has_vcp_pattern else 'لا'}
            {f'- مرحلة VCP: {vcp_stage}' if has_vcp_pattern else ''}
            - نقطة الدخول: {entry_point:.2f}
            - مستوى وقف الخسارة: {stop_loss:.2f}
            - الهدف السعري: {target_price:.2f}
            
            يجب أن يتضمن التقرير:
            1. ملخص تنفيذي للتوصية والأساس المنطقي لها
            2. تحليل الاتجاه العام للسهم
            3. تحليل نمط السعر (خاصة نمط VCP إذا كان موجوداً)
            4. استراتيجية الدخول والخروج مع تحديد نقاط الدخول ومستويات وقف الخسارة والأهداف السعرية
            5. تحليل المخاطر والعوائد المحتملة
            6. نصائح إضافية للمستثمر
            
            البيانات الكاملة للتحليل:
            {json.dumps(analysis_data, ensure_ascii=False, indent=2)}
            """
        elif report_type == "summary":
            prompt = f"""
            أنت مستشار مالي خبير في تحليل الأسهم باستخدام منهجية SEPA (Specific Entry Point Analysis) لمارك مينيرفيني.
            
            قم بإعداد ملخص موجز للتحليل الفني للسهم {symbol} بناءً على البيانات التالية:
            
            - التوصية: {recommendation}
            - درجة الثقة: {confidence_score:.2f}
            - درجة Trend Template: {trend_template_score}/6
            - وجود نمط VCP: {'نعم' if has_vcp_pattern else 'لا'}
            - نقطة الدخول: {entry_point:.2f}
            - مستوى وقف الخسارة: {stop_loss:.2f}
            - الهدف السعري: {target_price:.2f}
            
            يجب أن يكون الملخص موجزاً (لا يزيد عن 200 كلمة) ويركز على التوصية الرئيسية والأساس المنطقي لها.
            """
        elif report_type == "technical":
            prompt = f"""
            أنت مستشار مالي خبير في تحليل الأسهم باستخدام منهجية SEPA (Specific Entry Point Analysis) لمارك مينيرفيني.
            
            قم بإعداد تقرير تحليل فني للسهم {symbol} بناءً على البيانات التالية:
            
            - التوصية: {recommendation}
            - درجة الثقة: {confidence_score:.2f}
            - درجة Trend Template: {trend_template_score}/6
            - وجود نمط VCP: {'نعم' if has_vcp_pattern else 'لا'}
            {f'- مرحلة VCP: {vcp_stage}' if has_vcp_pattern else ''}
            - نقطة الدخول: {entry_point:.2f}
            - مستوى وقف الخسارة: {stop_loss:.2f}
            - الهدف السعري: {target_price:.2f}
            
            يجب أن يركز التقرير على الجوانب الفنية للتحليل، مثل المتوسطات المتحركة ومؤشر القوة النسبية ونمط VCP وغيرها من المؤشرات الفنية.
            
            البيانات الفنية:
            {json.dumps(analysis_data.get('analysis_details', {}), ensure_ascii=False, indent=2)}
            """
        else:
            prompt = f"""
            أنت مستشار مالي خبير في تحليل الأسهم باستخدام منهجية SEPA (Specific Entry Point Analysis) لمارك مينيرفيني.
            
            قم بإعداد تقرير تحليل موجز للسهم {symbol} بناءً على البيانات التالية:
            
            - التوصية: {recommendation}
            - درجة الثقة: {confidence_score:.2f}
            - درجة Trend Template: {trend_template_score}/6
            - وجود نمط VCP: {'نعم' if has_vcp_pattern else 'لا'}
            - نقطة الدخول: {entry_point:.2f}
            - مستوى وقف الخسارة: {stop_loss:.2f}
            - الهدف السعري: {target_price:.2f}
            """
        
        return prompt
    
    def generate_market_summary(self, market_data: Dict, stocks_analysis: List[Dict]) -> str:
        """
        توليد ملخص لحالة السوق
        
        المعلمات:
            market_data (Dict): بيانات السوق
            stocks_analysis (List[Dict]): قائمة بتحليلات الأسهم
            
        العائد:
            str: ملخص حالة السوق
        """
        try:
            logger.info("توليد ملخص لحالة السوق")
            
            # إعداد النص المحفز
            prompt = f"""
            أنت مستشار مالي خبير في تحليل الأسواق المالية.
            
            قم بإعداد ملخص لحالة السوق بناءً على البيانات التالية:
            
            بيانات السوق:
            {json.dumps(market_data, ensure_ascii=False, indent=2)}
            
            تحليلات الأسهم الرئيسية:
            {json.dumps([{
                'symbol': stock.get('symbol'),
                'recommendation': stock.get('recommendation'),
                'confidence_score': stock.get('confidence_score'),
                'trend_template_score': stock.get('trend_template_score')
            } for stock in stocks_analysis[:10]], ensure_ascii=False, indent=2)}
            
            يجب أن يتضمن الملخص:
            1. نظرة عامة على حالة السوق
            2. تحليل أداء القطاعات الرئيسية
            3. الاتجاه العام للسوق
            4. الأسهم الموصى بها للمتابعة
            5. المخاطر المحتملة
            """
            
            # توليد الملخص
            summary = self.generate_text(prompt, max_tokens=1500, temperature=0.5)
            
            return summary
            
        except Exception as e:
            logger.error(f"خطأ في توليد ملخص لحالة السوق: {str(e)}")
            return f"خطأ: {str(e)}"
    
    def generate_comparison_report(self, stocks_analysis: List[Dict]) -> str:
        """
        توليد تقرير مقارنة بين الأسهم
        
        المعلمات:
            stocks_analysis (List[Dict]): قائمة بتحليلات الأسهم
            
        العائد:
            str: تقرير المقارنة
        """
        try:
            logger.info(f"توليد تقرير مقارنة بين {len(stocks_analysis)} سهم")
            
            # إعداد النص المحفز
            prompt = f"""
            أنت مستشار مالي خبير في تحليل الأسهم باستخدام منهجية SEPA (Specific Entry Point Analysis) لمارك مينيرفيني.
            
            قم بإعداد تقرير مقارنة بين الأسهم التالية:
            
            {json.dumps([{
                'symbol': stock.get('symbol'),
                'recommendation': stock.get('recommendation'),
                'confidence_score': stock.get('confidence_score'),
                'trend_template_score': stock.get('trend_template_score'),
                'has_vcp_pattern': stock.get('has_vcp_pattern', False),
                'entry_point': stock.get('entry_point'),
                'stop_loss': stock.get('stop_loss'),
                'target_price': stock.get('target_price'),
                'risk_reward_ratio': stock.get('risk_reward_ratio')
            } for stock in stocks_analysis], ensure_ascii=False, indent=2)}
            
            يجب أن يتضمن التقرير:
            1. مقارنة بين الأسهم من حيث القوة الفنية
            2. ترتيب الأسهم حسب جاذبية الاستثمار
            3. تحليل المخاطر والعوائد المحتملة لكل سهم
            4. توصيات للمستثمرين بناءً على أهداف الاستثمار المختلفة
            """
            
            # توليد التقرير
            report = self.generate_text(prompt, max_tokens=2000, temperature=0.5)
            
            return report
            
        except Exception as e:
            logger.error(f"خطأ في توليد تقرير مقارنة بين الأسهم: {str(e)}")
            return f"خطأ: {str(e)}"


class ChatbotEngine:
    """فئة محرك روبوت المحادثة"""
    
    def __init__(self, openai_client: Optional[OpenAIClient] = None):
        """
        تهيئة الفئة
        
        المعلمات:
            openai_client (OpenAIClient, optional): عميل OpenAI
        """
        self.openai_client = openai_client or OpenAIClient()
        self.context = {}  # سياق المحادثة
        logger.info("تهيئة محرك روبوت المحادثة")
    
    def process_message(self, session_id: str, message: str, user_data: Optional[Dict] = None, stock_data: Optional[Dict] = None) -> str:
        """
        معالجة رسالة المستخدم
        
        المعلمات:
            session_id (str): معرف جلسة المحادثة
            message (str): رسالة المستخدم
            user_data (Dict, optional): بيانات المستخدم
            stock_data (Dict, optional): بيانات الأسهم
            
        العائد:
            str: رد روبوت المحادثة
        """
        try:
            logger.info(f"معالجة رسالة المستخدم في الجلسة {session_id}")
            
            # إنشاء أو تحديث سياق المحادثة
            if session_id not in self.context:
                self.context[session_id] = {
                    'messages': [],
                    'last_update': datetime.now()
                }
            
            # إضافة رسالة المستخدم إلى السياق
            self.context[session_id]['messages'].append({
                'role': 'user',
                'content': message,
                'timestamp': datetime.now()
            })
            
            # تحديث وقت آخر تحديث
            self.context[session_id]['last_update'] = datetime.now()
            
            # إعداد النص المحفز
            prompt = self._prepare_chat_prompt(session_id, message, user_data, stock_data)
            
            # توليد الرد
            response = self.openai_client.generate_text(prompt, max_tokens=1000, temperature=0.7)
            
            # إضافة رد الروبوت إلى السياق
            self.context[session_id]['messages'].append({
                'role': 'assistant',
                'content': response,
                'timestamp': datetime.now()
            })
            
            return response
            
        except Exception as e:
            logger.error(f"خطأ في معالجة رسالة المستخدم: {str(e)}")
            return f"عذراً، حدث خطأ أثناء معالجة رسالتك. الرجاء المحاولة مرة أخرى."
    
    def _prepare_chat_prompt(self, session_id: str, message: str, user_data: Optional[Dict], stock_data: Optional[Dict]) -> str:
        """
        إعداد النص المحفز لروبوت المحادثة
        
        المعلمات:
            session_id (str): معرف جلسة المحادثة
            message (str): رسالة المستخدم
            user_data (Dict, optional): بيانات المستخدم
            stock_data (Dict, optional): بيانات الأسهم
            
        العائد:
            str: النص المحفز
        """
        # الحصول على سجل المحادثة
        chat_history = self.context[session_id]['messages'][-5:]  # آخر 5 رسائل
        
        # إعداد سجل المحادثة كنص
        history_text = "\n".join([
            f"{'المستخدم' if msg['role'] == 'user' else 'المساعد'}: {msg['content']}"
            for msg in chat_history[:-1]  # استبعاد الرسالة الحالية
        ])
        
        # إعداد النص المحفز
        prompt = f"""
        أنت مساعد مالي خبير في تحليل الأسهم وتوصيات التداول باستخدام منهجية SEPA (Specific Entry Point Analysis) لمارك مينيرفيني.
        
        سجل المحادثة السابق:
        {history_text}
        
        رسالة المستخدم الحالية:
        {message}
        
        """
        
        # إضافة بيانات المستخدم إذا كانت متوفرة
        if user_data:
            prompt += f"""
            بيانات المستخدم:
            {json.dumps(user_data, ensure_ascii=False, indent=2)}
            """
        
        # إضافة بيانات الأسهم إذا كانت متوفرة
        if stock_data:
            prompt += f"""
            بيانات الأسهم:
            {json.dumps(stock_data, ensure_ascii=False, indent=2)}
            """
        
        # إضافة تعليمات إضا
(Content truncated due to size limit. Use line ranges to read in chunks)