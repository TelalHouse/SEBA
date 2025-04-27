"""
وحدة محرك قواعد SEPA لمشروع SEBA
توفر هذه الوحدة الوظائف اللازمة لتطبيق منهجية SEPA (Specific Entry Point Analysis)
وتوليد توصيات الدخول والخروج بناءً على قواعد مارك مينيرفيني
"""

import logging
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Union, Tuple
from datetime import datetime, date, timedelta

from seba.models.technical_analysis import TechnicalIndicators, PatternRecognition, DataProcessor

# إعداد السجل
logger = logging.getLogger(__name__)

class SEPAEngine:
    """فئة محرك قواعد SEPA"""
    
    def __init__(self):
        """تهيئة الفئة"""
        logger.info("تهيئة محرك قواعد SEPA")
    
    def analyze_stock(self, stock_data: pd.DataFrame, base_index_data: Optional[pd.DataFrame] = None) -> Dict:
        """
        تحليل السهم باستخدام منهجية SEPA
        
        المعلمات:
            stock_data (pd.DataFrame): إطار البيانات الذي يحتوي على بيانات الأسعار للسهم
            base_index_data (pd.DataFrame, optional): إطار البيانات الذي يحتوي على بيانات الأسعار للمؤشر
            
        العائد:
            Dict: قاموس يحتوي على نتائج التحليل
        """
        try:
            logger.info("تحليل السهم باستخدام منهجية SEPA")
            
            # معالجة البيانات وحساب المؤشرات الفنية
            analysis_results = DataProcessor.analyze_stock(stock_data, base_index_data)
            
            # تطبيق قواعد SEPA الإضافية
            sepa_results = self._apply_sepa_rules(analysis_results, stock_data)
            
            # دمج النتائج
            final_results = {**analysis_results, **sepa_results}
            
            return final_results
            
        except Exception as e:
            logger.error(f"خطأ في تحليل السهم باستخدام منهجية SEPA: {str(e)}")
            return {
                'error': str(e),
                'date': datetime.now().date(),
                'recommendation': "Hold",
                'confidence_score': 0.5
            }
    
    def _apply_sepa_rules(self, analysis_results: Dict, stock_data: pd.DataFrame) -> Dict:
        """
        تطبيق قواعد SEPA الإضافية
        
        المعلمات:
            analysis_results (Dict): نتائج التحليل الأولية
            stock_data (pd.DataFrame): إطار البيانات الذي يحتوي على بيانات الأسعار للسهم
            
        العائد:
            Dict: قاموس يحتوي على نتائج تطبيق قواعد SEPA
        """
        try:
            # استخراج البيانات المهمة من نتائج التحليل
            trend_template_score = analysis_results.get('trend_template_score', 0)
            has_vcp_pattern = analysis_results.get('has_vcp_pattern', False)
            vcp_stage = analysis_results.get('vcp_stage', None)
            
            # تطبيق قواعد SEPA
            
            # 1. قاعدة الاتجاه العام (Trend Rule)
            # يجب أن يكون السهم في اتجاه صاعد (Stage 2) وأن يستوفي معظم معايير Trend Template
            trend_rule_passed = trend_template_score >= 5 and (vcp_stage == "Stage 2" if vcp_stage else True)
            
            # 2. قاعدة النمط (Pattern Rule)
            # يفضل وجود نمط انكماش التقلب (VCP)
            pattern_rule_passed = has_vcp_pattern
            
            # 3. قاعدة الحجم (Volume Rule)
            # يجب أن يكون حجم التداول مرتفعاً عند نقطة الدخول
            volume_rule_passed = self._check_volume_rule(stock_data)
            
            # 4. قاعدة القوة النسبية (Relative Strength Rule)
            # يجب أن يكون تصنيف القوة النسبية للسهم مرتفعاً
            rs_rating = analysis_results.get('rs_rating', 0)
            rs_rule_passed = rs_rating >= 70 if rs_rating else False
            
            # 5. قاعدة الأرباح (Earnings Rule)
            # يجب أن يكون نمو الأرباح قوياً (هذه البيانات غير متوفرة في التحليل الفني، تحتاج إلى بيانات أساسية)
            earnings_rule_passed = True  # افتراضي
            
            # حساب درجة الثقة بناءً على القواعد المستوفاة
            rules_passed = sum([
                trend_rule_passed,
                pattern_rule_passed,
                volume_rule_passed,
                rs_rule_passed,
                earnings_rule_passed
            ])
            
            confidence_score = min(0.5 + (rules_passed / 10) + (trend_template_score / 20), 1.0)
            
            # تحديد التوصية النهائية
            recommendation = "Hold"  # افتراضي
            
            if rules_passed >= 4 and trend_template_score >= 5:
                recommendation = "Buy"
            elif rules_passed <= 2 or trend_template_score <= 2:
                recommendation = "Sell"
            
            # إعداد نتائج تطبيق قواعد SEPA
            sepa_results = {
                'sepa_rules': {
                    'trend_rule_passed': trend_rule_passed,
                    'pattern_rule_passed': pattern_rule_passed,
                    'volume_rule_passed': volume_rule_passed,
                    'rs_rule_passed': rs_rule_passed,
                    'earnings_rule_passed': earnings_rule_passed,
                    'rules_passed': rules_passed,
                    'total_rules': 5
                },
                'recommendation': recommendation,
                'confidence_score': confidence_score
            }
            
            # إضافة تفاصيل إضافية
            sepa_results['sepa_analysis'] = self._generate_sepa_analysis(analysis_results, sepa_results)
            
            return sepa_results
            
        except Exception as e:
            logger.error(f"خطأ في تطبيق قواعد SEPA: {str(e)}")
            return {}
    
    def _check_volume_rule(self, stock_data: pd.DataFrame) -> bool:
        """
        التحقق من قاعدة الحجم
        
        المعلمات:
            stock_data (pd.DataFrame): إطار البيانات الذي يحتوي على بيانات الأسعار للسهم
            
        العائد:
            bool: True إذا تم استيفاء القاعدة، False خلاف ذلك
        """
        try:
            # التأكد من وجود بيانات كافية
            if len(stock_data) < 50:
                return False
            
            # حساب متوسط الحجم للـ 50 يوم الماضية
            avg_volume_50 = stock_data['volume'].rolling(window=50).mean()
            
            # الحصول على آخر قيمة
            last_avg_volume = avg_volume_50.iloc[-1]
            last_volume = stock_data['volume'].iloc[-1]
            
            # التحقق من أن الحجم الحالي أعلى من متوسط الـ 50 يوم
            return last_volume > last_avg_volume
            
        except Exception as e:
            logger.error(f"خطأ في التحقق من قاعدة الحجم: {str(e)}")
            return False
    
    def _generate_sepa_analysis(self, analysis_results: Dict, sepa_results: Dict) -> Dict:
        """
        توليد تحليل SEPA مفصل
        
        المعلمات:
            analysis_results (Dict): نتائج التحليل الأولية
            sepa_results (Dict): نتائج تطبيق قواعد SEPA
            
        العائد:
            Dict: قاموس يحتوي على تحليل SEPA مفصل
        """
        try:
            # استخراج البيانات المهمة
            recommendation = sepa_results.get('recommendation', 'Hold')
            confidence_score = sepa_results.get('confidence_score', 0.5)
            rules_passed = sepa_results.get('sepa_rules', {}).get('rules_passed', 0)
            total_rules = sepa_results.get('sepa_rules', {}).get('total_rules', 5)
            
            trend_template_score = analysis_results.get('trend_template_score', 0)
            has_vcp_pattern = analysis_results.get('has_vcp_pattern', False)
            vcp_stage = analysis_results.get('vcp_stage', None)
            
            entry_point = analysis_results.get('entry_point', 0)
            stop_loss = analysis_results.get('stop_loss', 0)
            target_price = analysis_results.get('target_price', 0)
            risk_reward_ratio = analysis_results.get('risk_reward_ratio', 0)
            
            # توليد تحليل SEPA مفصل
            sepa_analysis = {
                'summary': f"استوفى السهم {rules_passed} من أصل {total_rules} من قواعد SEPA، ودرجة الثقة في التوصية هي {confidence_score:.2f}.",
                'trend_analysis': self._generate_trend_analysis(analysis_results),
                'pattern_analysis': self._generate_pattern_analysis(analysis_results),
                'entry_exit_analysis': {
                    'entry_point': entry_point,
                    'stop_loss': stop_loss,
                    'target_price': target_price,
                    'risk_reward_ratio': risk_reward_ratio,
                    'risk_percentage': ((entry_point - stop_loss) / entry_point) * 100 if entry_point > 0 else 0,
                    'reward_percentage': ((target_price - entry_point) / entry_point) * 100 if entry_point > 0 else 0
                },
                'recommendation_details': {
                    'recommendation': recommendation,
                    'confidence_score': confidence_score,
                    'reasoning': self._generate_recommendation_reasoning(analysis_results, sepa_results)
                }
            }
            
            return sepa_analysis
            
        except Exception as e:
            logger.error(f"خطأ في توليد تحليل SEPA مفصل: {str(e)}")
            return {}
    
    def _generate_trend_analysis(self, analysis_results: Dict) -> Dict:
        """
        توليد تحليل الاتجاه
        
        المعلمات:
            analysis_results (Dict): نتائج التحليل
            
        العائد:
            Dict: قاموس يحتوي على تحليل الاتجاه
        """
        try:
            # استخراج البيانات المهمة
            is_price_above_ma150 = analysis_results.get('is_price_above_ma150', False)
            is_price_above_ma200 = analysis_results.get('is_price_above_ma200', False)
            is_ma150_above_ma200 = analysis_results.get('is_ma150_above_ma200', False)
            is_ma50_above_ma150 = analysis_results.get('is_ma50_above_ma150', False)
            is_ma50_above_ma200 = analysis_results.get('is_ma50_above_ma200', False)
            is_rs_rating_above_70 = analysis_results.get('is_rs_rating_above_70', False)
            trend_template_score = analysis_results.get('trend_template_score', 0)
            
            # تحديد حالة الاتجاه
            trend_state = "غير محدد"
            if trend_template_score >= 5:
                trend_state = "اتجاه صاعد قوي"
            elif trend_template_score >= 3:
                trend_state = "اتجاه صاعد ضعيف"
            elif trend_template_score <= 1:
                trend_state = "اتجاه هابط قوي"
            elif trend_template_score <= 3:
                trend_state = "اتجاه هابط ضعيف"
            else:
                trend_state = "اتجاه جانبي"
            
            # توليد تحليل الاتجاه
            trend_analysis = {
                'trend_state': trend_state,
                'trend_template_score': trend_template_score,
                'trend_template_details': {
                    'is_price_above_ma150': is_price_above_ma150,
                    'is_price_above_ma200': is_price_above_ma200,
                    'is_ma150_above_ma200': is_ma150_above_ma200,
                    'is_ma50_above_ma150': is_ma50_above_ma150,
                    'is_ma50_above_ma200': is_ma50_above_ma200,
                    'is_rs_rating_above_70': is_rs_rating_above_70
                },
                'trend_strength': trend_template_score / 6.0,
                'trend_direction': "صاعد" if trend_template_score >= 3 else "هابط" if trend_template_score <= 2 else "جانبي"
            }
            
            return trend_analysis
            
        except Exception as e:
            logger.error(f"خطأ في توليد تحليل الاتجاه: {str(e)}")
            return {}
    
    def _generate_pattern_analysis(self, analysis_results: Dict) -> Dict:
        """
        توليد تحليل النمط
        
        المعلمات:
            analysis_results (Dict): نتائج التحليل
            
        العائد:
            Dict: قاموس يحتوي على تحليل النمط
        """
        try:
            # استخراج البيانات المهمة
            has_vcp_pattern = analysis_results.get('has_vcp_pattern', False)
            vcp_stage = analysis_results.get('vcp_stage', None)
            vcp_contraction_percentage = analysis_results.get('vcp_contraction_percentage', 0)
            vcp_duration = analysis_results.get('vcp_duration', 0)
            vcp_start_date = analysis_results.get('vcp_start_date', None)
            vcp_end_date = analysis_results.get('vcp_end_date', None)
            vcp_price_change = analysis_results.get('vcp_price_change', 0)
            
            # توليد تحليل النمط
            pattern_analysis = {
                'has_vcp_pattern': has_vcp_pattern,
                'pattern_type': "VCP (نمط انكماش التقلب)" if has_vcp_pattern else "لا يوجد نمط محدد",
                'pattern_quality': "عالية" if has_vcp_pattern and vcp_contraction_percentage > 0.7 else "متوسطة" if has_vcp_pattern else "منخفضة",
                'pattern_details': {
                    'vcp_stage': vcp_stage,
                    'vcp_contraction_percentage': vcp_contraction_percentage,
                    'vcp_duration': vcp_duration,
                    'vcp_start_date': vcp_start_date,
                    'vcp_end_date': vcp_end_date,
                    'vcp_price_change': vcp_price_change
                } if has_vcp_pattern else {}
            }
            
            return pattern_analysis
            
        except Exception as e:
            logger.error(f"خطأ في توليد تحليل النمط: {str(e)}")
            return {}
    
    def _generate_recommendation_reasoning(self, analysis_results: Dict, sepa_results: Dict) -> str:
        """
        توليد تفسير التوصية
        
        المعلمات:
            analysis_results (Dict): نتائج التحليل
            sepa_results (Dict): نتائج تطبيق قواعد SEPA
            
        العائد:
            str: تفسير التوصية
        """
        try:
            # استخراج البيانات المهمة
            recommendation = sepa_results.get('recommendation', 'Hold')
            trend_rule_passed = sepa_results.get('sepa_rules', {}).get('trend_rule_passed', False)
            pattern_rule_passed = sepa_results.get('sepa_rules', {}).get('pattern_rule_passed', False)
            volume_rule_passed = sepa_results.get('sepa_rules', {}).get('volume_rule_passed', False)
            rs_rule_passed = sepa_results.get('sepa_rules', {}).get('rs_rule_passed', False)
            
            trend_template_score = analysis_results.get('trend_template_score', 0)
            has_vcp_pattern = analysis_results.get('has_vcp_pattern', False)
            vcp_stage = analysis_results.get('vcp_stage', None)
            
            # توليد تفسير التوصية
            reasoning = ""
            
            if recommendation == "Buy":
                reasoning = "التوصية بالشراء بناءً على: "
                reasons = []
                
                if trend_rule_passed:
                    reasons.append(f"السهم في اتجاه صاعد قوي (درجة Trend Template: {trend_template_score}/6)")
                
                if pattern_rule_passed:
                    reasons.append(f"وجود نمط انكماش التقلب (VCP) في المرحلة {vcp_stage}")
                
                if volume_rule_passed:
                    reasons.append("حجم التداول مرتفع مقارنة بالمتوسط")
                
                if rs_rule_passed:
                    reasons.append("القوة النسبية للسهم مرتفعة مقارنة بالسوق")
                
                reasoning += "، ".join(reasons)
                
            elif recommendation == "Sell":
                reasoning = "التوصية بالبيع بناءً على: "
                reasons = []
                
                if not trend_rule_passed:
                    reasons.append(f"السهم ليس في اتجاه صاعد قوي (درجة Trend Template: {trend_template_score}/6)")
                
                if not pattern_rule_passed:
                    reasons.append("عدم وجود نمط انكماش التقلب (VCP)")
                elif vcp_stage == "Stage 4":
                    reasons.append(f"وجود نمط انكماش التقلب (VCP) في المرحلة {vcp_stage} (مرحلة الاتجاه الهابط)")
(Content truncated due to size limit. Use line ranges to read in chunks)