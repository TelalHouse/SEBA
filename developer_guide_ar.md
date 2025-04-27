# دليل المطور - نظام SEBA (روبوت خبير الأسهم للتحليل)

## مقدمة

هذا الدليل مخصص للمطورين الذين يعملون على تطوير وصيانة وتوسيع نظام SEBA (روبوت خبير الأسهم للتحليل). يوفر هذا الدليل نظرة عامة على هيكل النظام، والمكونات الرئيسية، وإرشادات التطوير، وأفضل الممارسات.

## هيكل المشروع

يتبع مشروع SEBA هيكل تطبيق Python قياسي مع تنظيم الشيفرة في وحدات وحزم منطقية:

```
SEBA_Implementation/
├── seba/                      # الحزمة الرئيسية
│   ├── __init__.py            # ملف تهيئة الحزمة
│   ├── data_integration/      # وحدات تكامل البيانات
│   │   ├── __init__.py
│   │   ├── data_manager.py    # مدير تكامل البيانات
│   │   ├── yahoo_finance.py   # واجهة Yahoo Finance API
│   │   ├── alpha_vantage.py   # واجهة Alpha Vantage API
│   │   └── iex_cloud.py       # واجهة IEX Cloud API
│   ├── database/              # وحدات قاعدة البيانات
│   │   ├── __init__.py
│   │   ├── models.py          # نماذج قاعدة البيانات
│   │   ├── db_manager.py      # مدير قاعدة البيانات
│   │   └── repository.py      # مستودعات البيانات
│   ├── models/                # وحدات النماذج والخوارزميات
│   │   ├── __init__.py
│   │   ├── technical_analysis.py  # التحليل الفني
│   │   ├── sepa_engine.py     # محرك قواعد SEPA
│   │   └── ai_integration.py  # تكامل الذكاء الاصطناعي
│   ├── api/                   # وحدات واجهة برمجة التطبيقات
│   │   ├── __init__.py
│   │   └── api.py             # تعريف واجهة برمجة التطبيقات
│   └── utils/                 # وحدات المساعدة
│       ├── __init__.py
│       ├── optimization.py    # تحسين الأداء
│       └── security.py        # تحسين الأمان
├── tests/                     # اختبارات الوحدة والتكامل
│   ├── __init__.py
│   └── test_seba.py           # اختبارات شاملة
├── docs/                      # الوثائق
│   ├── user_guide_ar.md       # دليل المستخدم (عربي)
│   ├── developer_guide_ar.md  # دليل المطور (عربي)
│   └── api_docs.md            # وثائق واجهة برمجة التطبيقات
├── setup.py                   # ملف إعداد المشروع
├── requirements.txt           # متطلبات المشروع
└── .env.example               # نموذج ملف البيئة
```

## المكونات الرئيسية

### 1. تكامل البيانات

وحدات تكامل البيانات مسؤولة عن جمع البيانات من مصادر مختلفة مثل Yahoo Finance وAlpha Vantage وIEX Cloud.

#### DataIntegrationManager

`DataIntegrationManager` هو الواجهة الرئيسية لتكامل البيانات، ويوفر طبقة تجريد فوق مصادر البيانات المختلفة.

```python
from seba.data_integration.data_manager import DataIntegrationManager

# إنشاء مدير تكامل البيانات
data_manager = DataIntegrationManager()

# الحصول على البيانات التاريخية
historical_data = data_manager.get_historical_data(
    symbol="AAPL",
    start_date="2020-01-01",
    end_date="2021-01-01",
    interval="1d"
)

# الحصول على معلومات السهم
stock_info = data_manager.get_stock_info("AAPL")

# الحصول على البيانات الأساسية
fundamentals = data_manager.get_fundamentals("AAPL")
```

### 2. قاعدة البيانات

وحدات قاعدة البيانات مسؤولة عن تخزين واسترجاع البيانات من قاعدة البيانات.

#### DatabaseManager

`DatabaseManager` هو المسؤول عن إدارة الاتصال بقاعدة البيانات وجلسات العمل.

```python
from seba.database.db_manager import DatabaseManager

# إنشاء مدير قاعدة البيانات
db_manager = DatabaseManager()

# الحصول على جلسة عمل
session = db_manager.get_session()

# استخدام الجلسة
# ...

# إغلاق الجلسة
session.close()
```

#### Repository

الفئات المشتقة من `Repository` توفر واجهات لتخزين واسترجاع أنواع محددة من البيانات.

```python
from seba.database.repository import StockRepository
from seba.database.db_manager import DatabaseManager

# إنشاء مدير قاعدة البيانات
db_manager = DatabaseManager()

# إنشاء مستودع الأسهم
stock_repository = StockRepository(db_manager)

# الحصول على سهم
stock = stock_repository.get_stock_by_symbol("AAPL")

# إضافة سهم جديد
new_stock = stock_repository.add_stock(
    symbol="MSFT",
    name="Microsoft Corporation",
    sector="Technology",
    industry="Software",
    country="USA",
    exchange="NASDAQ"
)
```

### 3. النماذج والخوارزميات

وحدات النماذج والخوارزميات مسؤولة عن تحليل البيانات وتطبيق منهجية SEPA.

#### TechnicalIndicators

`TechnicalIndicators` توفر وظائف لحساب المؤشرات الفنية المختلفة.

```python
from seba.models.technical_analysis import TechnicalIndicators
import pandas as pd

# إنشاء DataFrame للبيانات التاريخية
data = pd.DataFrame({
    # ...
})

# حساب المتوسطات المتحركة
data = TechnicalIndicators.calculate_sma(data)

# حساب مؤشر القوة النسبية
data = TechnicalIndicators.calculate_rsi(data)

# حساب MACD
data = TechnicalIndicators.calculate_macd(data)

# حساب نطاقات بولينجر
data = TechnicalIndicators.calculate_bollinger_bands(data)
```

#### PatternRecognition

`PatternRecognition` توفر وظائف للتعرف على أنماط الأسعار مثل نمط VCP.

```python
from seba.models.technical_analysis import PatternRecognition
import pandas as pd

# إنشاء DataFrame للبيانات التاريخية
data = pd.DataFrame({
    # ...
})

# اكتشاف نمط VCP
has_vcp, vcp_details = PatternRecognition.detect_vcp(data)

# التحقق من معايير Trend Template
score, details = PatternRecognition.check_trend_template(data)
```

#### SEPAEngine

`SEPAEngine` هو المحرك الرئيسي لتطبيق منهجية SEPA وتوليد التوصيات.

```python
from seba.models.sepa_engine import SEPAEngine
import pandas as pd

# إنشاء محرك SEPA
sepa_engine = SEPAEngine()

# تحليل سهم
analysis_results = sepa_engine.analyze_stock(historical_data, index_data)

# فحص الأسهم
results = sepa_engine.screen_stocks(stocks_data, index_data)

# الحصول على الأسهم التي تستوفي معايير Trend Template
trend_template_stocks = sepa_engine.get_trend_template_stocks(stocks_data, index_data, min_score=5)

# الحصول على الأسهم التي تشكل نمط VCP
vcp_stocks = sepa_engine.get_vcp_stocks(stocks_data)

# الحصول على توصيات الشراء
buy_recommendations = sepa_engine.get_buy_recommendations(stocks_data, index_data, min_confidence=0.7)
```

### 4. تكامل الذكاء الاصطناعي

وحدات تكامل الذكاء الاصطناعي مسؤولة عن التفاعل مع OpenAI API وتوليد تقارير التحليل والتوصيات بلغة طبيعية.

#### AIIntegrationManager

`AIIntegrationManager` هو الواجهة الرئيسية لتكامل الذكاء الاصطناعي، ويوفر وظائف لتوليد تقارير التحليل والتوصيات ومعالجة رسائل المحادثة.

```python
from seba.models.ai_integration import AIIntegrationManager

# إنشاء مدير تكامل الذكاء الاصطناعي
ai_manager = AIIntegrationManager()

# توليد تقرير تحليل
analysis_report = ai_manager.generate_stock_analysis_report(analysis_results, report_type="detailed")

# توليد توصية بلغة طبيعية
recommendation = ai_manager.generate_natural_language_recommendation(analysis_results)

# معالجة رسالة محادثة
response = ai_manager.process_chat_message(session_id, message, user_data)

# توليد ملخص السوق
market_summary = ai_manager.generate_market_summary(market_data, top_stocks)

# توليد محتوى تعليمي
educational_content = ai_manager.generate_educational_content(topic)
```

### 5. واجهة برمجة التطبيقات

وحدة واجهة برمجة التطبيقات مسؤولة عن توفير واجهة RESTful API للتفاعل مع النظام.

#### API

`api.py` يحتوي على تعريف واجهة برمجة التطبيقات باستخدام FastAPI.

```python
from fastapi import FastAPI, Depends
from seba.api.api import app

# تشغيل التطبيق
import uvicorn
uvicorn.run(app, host="0.0.0.0", port=8000)
```

### 6. الأدوات المساعدة

وحدات الأدوات المساعدة توفر وظائف مساعدة مثل تحسين الأداء وتحسين الأمان.

#### OptimizationManager

`OptimizationManager` يوفر وظائف لتحسين أداء النظام باستخدام التخزين المؤقت ومراقبة الأداء.

```python
from seba.utils.optimization import OptimizationManager

# إنشاء مدير تحسين الأداء
optimization_manager = OptimizationManager()

# تحسين تحميل البيانات
data = optimization_manager.optimize_data_loading(
    data_loader=data_manager.get_historical_data,
    key="historical_data_AAPL_1d",
    expiry=3600,
    symbol="AAPL",
    start_date="2020-01-01",
    end_date="2021-01-01",
    interval="1d"
)

# الحصول على مقاييس الأداء
metrics = optimization_manager.get_performance_metrics()
```

#### SecurityManager

`SecurityManager` يوفر وظائف لتحسين أمان النظام وحماية البيانات.

```python
from seba.utils.security import SecurityManager

# إنشاء مدير الأمان
security_manager = SecurityManager()

# تشفير كلمة المرور
hashed_password = security_manager.hash_password("password123")

# التحقق من كلمة المرور
is_valid = security_manager.verify_password("password123", hashed_password)

# إنشاء رمز الوصول
access_token = security_manager.create_access_token(
    data={"sub": "user123"},
    expires_delta=timedelta(minutes=30)
)

# فك تشفير رمز الوصول
payload = security_manager.decode_access_token(access_token)
```

## إرشادات التطوير

### إعداد بيئة التطوير

1. استنساخ المستودع:
   ```bash
   git clone https://github.com/your-username/seba.git
   cd seba
   ```

2. إنشاء بيئة افتراضية:
   ```bash
   python -m venv venv
   source venv/bin/activate  # على Linux/Mac
   venv\Scripts\activate     # على Windows
   ```

3. تثبيت المتطلبات:
   ```bash
   pip install -r requirements.txt
   ```

4. إعداد ملف البيئة:
   ```bash
   cp .env.example .env
   # تعديل .env بالقيم المناسبة
   ```

### تشغيل الاختبارات

لتشغيل اختبارات الوحدة:

```bash
python -m unittest discover tests
```

### تشغيل واجهة برمجة التطبيقات

لتشغيل واجهة برمجة التطبيقات محلياً:

```bash
cd SEBA_Implementation
python -m seba.api.api
```

ستكون واجهة برمجة التطبيقات متاحة على `http://localhost:8000`.

### إضافة مصدر بيانات جديد

لإضافة مصدر بيانات جديد:

1. إنشاء ملف جديد في مجلد `data_integration` (مثل `new_source.py`).
2. تنفيذ الفئة التي توفر واجهة لمصدر البيانات الجديد.
3. تحديث `data_manager.py` لدمج مصدر البيانات الجديد.

مثال:

```python
# new_source.py
class NewSourceAPI:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("NEW_SOURCE_API_KEY")
        
    def get_historical_data(self, symbol, start_date, end_date, interval="1d"):
        # تنفيذ الوظيفة
        pass
        
    def get_stock_info(self, symbol):
        # تنفيذ الوظيفة
        pass
        
    def get_fundamentals(self, symbol):
        # تنفيذ الوظيفة
        pass
```

```python
# data_manager.py
from seba.data_integration.new_source import NewSourceAPI

class DataIntegrationManager:
    def __init__(self):
        # ...
        self.new_source_api = NewSourceAPI()
        
    def get_historical_data(self, symbol, start_date, end_date, interval="1d", source="yahoo"):
        if source == "new_source":
            return self.new_source_api.get_historical_data(symbol, start_date, end_date, interval)
        # ...
```

### إضافة مؤشر فني جديد

لإضافة مؤشر فني جديد:

1. إضافة وظيفة جديدة في فئة `TechnicalIndicators` في `technical_analysis.py`.
2. تحديث وظيفة `calculate_all_indicators` لتضمين المؤشر الجديد.

مثال:

```python
@staticmethod
def calculate_new_indicator(df, period=14):
    """
    حساب المؤشر الفني الجديد
    
    المعلمات:
        df (pd.DataFrame): DataFrame للبيانات التاريخية
        period (int, optional): الفترة الزمنية
        
    العائد:
        pd.DataFrame: DataFrame مع المؤشر الفني الجديد
    """
    df = df.copy()
    # حساب المؤشر
    df['new_indicator'] = # ...
    return df

@staticmethod
def calculate_all_indicators(df, index_data=None):
    """
    حساب جميع المؤشرات الفنية
    
    المعلمات:
        df (pd.DataFrame): DataFrame للبيانات التاريخية
        index_data (pd.DataFrame, optional): DataFrame لبيانات المؤشر
        
    العائد:
        pd.DataFrame: DataFrame مع جميع المؤشرات الفنية
    """
    df = TechnicalIndicators.calculate_sma(df)
    df = TechnicalIndicators.calculate_rsi(df)
    df = TechnicalIndicators.calculate_macd(df)
    df = TechnicalIndicators.calculate_bollinger_bands(df)
    df = TechnicalIndicators.calculate_new_indicator(df)  # إضافة المؤشر الجديد
    # ...
    return df
```

### إضافة معيار جديد لمنهجية SEPA

لإضافة معيار جديد لمنهجية SEPA:

1. تحديث وظيفة `check_trend_template` في فئة `PatternRecognition` لتضمين المعيار الجديد.
2. تحديث وظيفة `analyze_stock` في فئة `SEPAEngine` لتضمين المعيار الجديد في التحليل.

مثال:

```python
@staticmethod
def check_trend_template(df):
    """
    التحقق من معايير Trend Template
    
    المعلمات:
        df (pd.DataFrame): DataFrame للبيانات التاريخية
        
    العائد:
        tuple: (درجة Trend Template، تفاصيل)
    """
    # ...
    
    # إضافة معيار جديد
    if # شرط المعيار الجديد:
        score += 1
        details['new_criterion'] = True
    else:
        details['new_criterion'] = False
        
    # ...
    
    return score, details
```

### إضافة نقطة نهاية جديدة لواجهة برمجة التطبيقات

لإضافة نقطة نهاية جديدة لواجهة برمجة التطبيقات:

1. إضافة مسار جديد في `api.py`.

مثال:

```python
@app.get("/new-endpoint/{param}")
async def new_endpoint(param: str, query_param: Optional[str] = None):
    """
    نقطة نهاية جديدة
    
    المعلمات:
        param (str): معلمة المسار
        query_param (str, optional): معلمة الاستعلام
        
    العائد:
        Dict: النتيجة
    """
    try:
        # تنفيذ المنطق
        result = # ...
        
        return result
    except Exception as e:
        logger.error(f"خطأ في نقطة النهاية الجديدة: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
```

## أفضل الممارسات

### التعليقات والتوثيق

- استخدم docstrings لتوثيق الفئات والوظائف.
- اتبع معيار [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html) للتعليقات.
- وثق المعلمات والقيم المرجعة والاستثناءات.

### التعامل مع الأخطاء

- استخدم بلوكات try-except للتعامل مع الأخطاء المتوقعة.
- سجل الأخطاء باستخدام وحدة logging.
- أعد الاستثناءات المناسبة مع رسائل خطأ واضحة.

### الاختبارات

- اكتب اختبارات وحدة لكل وظيفة جديدة.
- استخدم unittest أو pytest لكتابة الاختبارات.
- استخدم mock objects لمحاكاة السلوك الخارجي.

### الأمان

- لا تخزن المفاتيح السرية وكلمات المرور في الشيفرة.
- استخدم متغيرات البيئة أو ملفات التكوين الآمنة.
- تحقق من صحة جميع المدخلات.
- استخدم HTTPS لجميع طلبات API.

### الأداء

- استخدم التخزين المؤقت لتقليل عدد طلبات API.
- استخدم مزخرف `@cache` لتخزين نتائج الوظائف المتكررة.
- استخدم `PerformanceMonitor` لقياس أداء الوظائف.

## استكشاف الأخطاء وإصلاحها

### مشاكل تكامل البيانات

إذا واجهت مشاكل في الحصول على البيانات من مصادر البيانات:

1. تحقق من صحة مفاتيح API.
2. تحقق من حدود معدل الطلبات لمصدر البيانات.
3. تحقق من تنسيق المعلمات (مثل تنسيق التاريخ).
4. تحقق من سجلات الأخطاء للحصول على رسائل خطأ محددة.

### مشاكل قاعدة البيانات

إذا واجهت مشاكل في الاتصال بقاعدة البيانات:

1. تحقق من صحة سلسلة الاتصال.
2. تحقق من وجود قاعدة البيانات وجداولها.
3. تحقق من صلاحيات المستخدم.
4. تحقق من سجلات الأخطاء للحصول على رسائل خطأ محددة.

### مشاكل واجهة برمجة التطبيقات

إذا واجهت مشاكل في واجهة برمجة التطبيقات:

1. تحقق من سجلات الخادم للحصول على رسائل خطأ محددة.
2. تحقق من صحة المعلمات المرسلة.
3. استخدم أداة مثل Postman لاختبار نقاط النهاية.
4. تحقق من رموز الحالة HTTP ورسائل الخطأ.

## الموارد

### المراجع

- [منهجية SEPA لمارك مينيرفيني](https://www.minervini.com/blog/index.php/category/sepa/)
- [وثائق FastAPI](https://fastapi.tiangolo.com/)
- [وثائق SQLAlchemy](https://docs.sqlalchemy.org/)
- [وثائق pandas](https://pandas.pydata.org/docs/)
- [وثائق OpenAI API](https://beta.openai.com/docs/)

### الأدوات

- [Visual Studio Code](https://code.visualstudio.com/) - محرر الشيفرة
- [Postman](https://www.postman.com/) - اختبار واجهة برمجة التطبيقات
- [DBeaver](https://dbeaver.io/) - إدارة قاعدة البيانات
- [Git](https://git-scm.com/) - نظام إدارة الإصدارات

## الخاتمة

هذا الدليل يوفر نظرة عامة على هيكل نظام SEBA والمكونات الرئيسية وإرشادات التطوير وأفضل الممارسات. يرجى الرجوع إلى وثائق واجهة برمجة التطبيقات للحصول على معلومات مفصلة حول نقاط النهاية المتاحة.

إذا كان لديك أي أسئلة أو اقتراحات، يرجى التواصل مع فريق التطوير.
