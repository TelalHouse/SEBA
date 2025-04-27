# وثائق واجهة برمجة التطبيقات - نظام SEBA (روبوت خبير الأسهم للتحليل)

## مقدمة

توفر واجهة برمجة التطبيقات (API) لنظام SEBA مجموعة شاملة من نقاط النهاية للوصول إلى وظائف النظام المختلفة، بما في ذلك تحليل الأسهم، وفحص الأسهم، وإدارة التنبيهات، والتفاعل مع روبوت المحادثة.

هذه الوثيقة تشرح بالتفصيل جميع نقاط النهاية المتاحة، والمعلمات المطلوبة، وأمثلة الطلبات والاستجابات.

## معلومات عامة

- **عنوان القاعدة**: `https://api.seba.com/v1`
- **تنسيق البيانات**: JSON
- **المصادقة**: OAuth2 (Bearer Token)

## المصادقة

### الحصول على رمز الوصول

```
POST /token
```

#### المعلمات

| المعلمة | النوع | الوصف |
|---------|------|---------|
| username | string | اسم المستخدم |
| password | string | كلمة المرور |

#### مثال الطلب

```bash
curl -X POST "https://api.seba.com/v1/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user123&password=password123"
```

#### مثال الاستجابة

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### إنشاء مستخدم جديد

```
POST /users
```

#### المعلمات

| المعلمة | النوع | الوصف |
|---------|------|---------|
| username | string | اسم المستخدم |
| email | string | البريد الإلكتروني |
| password | string | كلمة المرور |
| full_name | string | الاسم الكامل (اختياري) |

#### مثال الطلب

```bash
curl -X POST "https://api.seba.com/v1/users" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "user123",
    "email": "user@example.com",
    "password": "password123",
    "full_name": "John Doe"
  }'
```

#### مثال الاستجابة

```json
{
  "username": "user123",
  "email": "user@example.com",
  "full_name": "John Doe",
  "disabled": false
}
```

### الحصول على معلومات المستخدم الحالي

```
GET /users/me
```

#### مثال الطلب

```bash
curl -X GET "https://api.seba.com/v1/users/me" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

#### مثال الاستجابة

```json
{
  "username": "user123",
  "email": "user@example.com",
  "full_name": "John Doe",
  "disabled": false
}
```

## الأسهم

### الحصول على معلومات السهم

```
GET /stocks/{symbol}
```

#### المعلمات

| المعلمة | النوع | الوصف |
|---------|------|---------|
| symbol | string | رمز السهم |

#### مثال الطلب

```bash
curl -X GET "https://api.seba.com/v1/stocks/AAPL" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

#### مثال الاستجابة

```json
{
  "symbol": "AAPL",
  "name": "Apple Inc.",
  "sector": "Technology",
  "industry": "Consumer Electronics",
  "country": "USA",
  "exchange": "NASDAQ",
  "currency": "USD",
  "last_price": 150.25,
  "change": 2.5,
  "change_percent": 1.69,
  "volume": 75000000,
  "market_cap": 2500000000000,
  "pe_ratio": 28.5,
  "dividend_yield": 0.6
}
```

### الحصول على البيانات التاريخية للسهم

```
POST /stocks/historical
```

#### المعلمات

| المعلمة | النوع | الوصف |
|---------|------|---------|
| symbol | string | رمز السهم |
| start_date | string | تاريخ البداية (YYYY-MM-DD) |
| end_date | string | تاريخ النهاية (YYYY-MM-DD) |
| interval | string | الفاصل الزمني (1d, 1wk, 1mo) (اختياري، الافتراضي: 1d) |

#### مثال الطلب

```bash
curl -X POST "https://api.seba.com/v1/stocks/historical" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "AAPL",
    "start_date": "2020-01-01",
    "end_date": "2021-01-01",
    "interval": "1d"
  }'
```

#### مثال الاستجابة

```json
{
  "symbol": "AAPL",
  "data": [
    {
      "date": "2020-01-02",
      "open": 74.06,
      "high": 75.15,
      "low": 73.8,
      "close": 75.09,
      "volume": 135480400,
      "adjusted_close": 73.95
    },
    {
      "date": "2020-01-03",
      "open": 74.29,
      "high": 75.14,
      "low": 74.125,
      "close": 74.36,
      "volume": 146322800,
      "adjusted_close": 73.23
    },
    // ... المزيد من البيانات
  ]
}
```

### الحصول على البيانات الأساسية للسهم

```
GET /stocks/{symbol}/fundamentals
```

#### المعلمات

| المعلمة | النوع | الوصف |
|---------|------|---------|
| symbol | string | رمز السهم |

#### مثال الطلب

```bash
curl -X GET "https://api.seba.com/v1/stocks/AAPL/fundamentals" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

#### مثال الاستجابة

```json
{
  "symbol": "AAPL",
  "name": "Apple Inc.",
  "sector": "Technology",
  "industry": "Consumer Electronics",
  "country": "USA",
  "exchange": "NASDAQ",
  "currency": "USD",
  "market_cap": 2500000000000,
  "pe_ratio": 28.5,
  "forward_pe": 25.2,
  "peg_ratio": 2.1,
  "price_to_sales": 7.5,
  "price_to_book": 35.2,
  "dividend_yield": 0.6,
  "eps": 5.28,
  "eps_growth": 10.5,
  "revenue_growth": 8.2,
  "profit_margin": 21.5,
  "operating_margin": 27.3,
  "roa": 17.5,
  "roe": 85.9,
  "debt_to_equity": 1.5,
  "quick_ratio": 1.2,
  "current_ratio": 1.5,
  "earnings": {
    "quarterly": [
      {
        "date": "2020-12-31",
        "eps": 1.68,
        "revenue": 111439000000,
        "growth": 21.4
      },
      {
        "date": "2020-09-30",
        "eps": 0.73,
        "revenue": 64698000000,
        "growth": 1.0
      },
      // ... المزيد من البيانات
    ],
    "annual": [
      {
        "date": "2020-09-30",
        "eps": 3.28,
        "revenue": 274515000000,
        "growth": 5.5
      },
      {
        "date": "2019-09-30",
        "eps": 2.97,
        "revenue": 260174000000,
        "growth": -2.0
      },
      // ... المزيد من البيانات
    ]
  }
}
```

### الحصول على المؤشرات الفنية للسهم

```
GET /stocks/{symbol}/indicators
```

#### المعلمات

| المعلمة | النوع | الوصف |
|---------|------|---------|
| symbol | string | رمز السهم |
| start_date | string | تاريخ البداية (YYYY-MM-DD) (اختياري) |
| end_date | string | تاريخ النهاية (YYYY-MM-DD) (اختياري) |
| indicators | string | قائمة المؤشرات مفصولة بفواصل (اختياري) |

#### مثال الطلب

```bash
curl -X GET "https://api.seba.com/v1/stocks/AAPL/indicators?start_date=2020-01-01&end_date=2021-01-01&indicators=sma,rsi,macd" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

#### مثال الاستجابة

```json
{
  "symbol": "AAPL",
  "data": [
    {
      "date": "2020-01-02",
      "open": 74.06,
      "high": 75.15,
      "low": 73.8,
      "close": 75.09,
      "volume": 135480400,
      "sma_20": 68.52,
      "sma_50": 64.63,
      "sma_150": 56.21,
      "sma_200": 53.12,
      "rsi_14": 78.2,
      "macd": 4.25,
      "macd_signal": 3.75,
      "macd_histogram": 0.5
    },
    {
      "date": "2020-01-03",
      "open": 74.29,
      "high": 75.14,
      "low": 74.125,
      "close": 74.36,
      "volume": 146322800,
      "sma_20": 68.83,
      "sma_50": 64.82,
      "sma_150": 56.32,
      "sma_200": 53.18,
      "rsi_14": 75.6,
      "macd": 4.15,
      "macd_signal": 3.82,
      "macd_histogram": 0.33
    },
    // ... المزيد من البيانات
  ]
}
```

## التحليل

### تحليل السهم

```
POST /analysis/{symbol}
```

#### المعلمات

| المعلمة | النوع | الوصف |
|---------|------|---------|
| symbol | string | رمز السهم |
| report_type | string | نوع التقرير (detailed, summary, technical) (اختياري، الافتراضي: detailed) |

#### مثال الطلب

```bash
curl -X POST "https://api.seba.com/v1/analysis/AAPL?report_type=detailed" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

#### مثال الاستجابة

```json
{
  "symbol": "AAPL",
  "recommendation": "Buy",
  "confidence_score": 0.85,
  "trend_template_score": 7,
  "trend_template_details": {
    "price_above_sma_150_200": true,
    "sma_150_above_sma_200": true,
    "sma_50_above_sma_150_200": true,
    "sma_200_uptrend": true,
    "price_above_sma_50": true,
    "price_30_percent_above_52w_low": true,
    "price_within_25_percent_52w_high": true,
    "rsi_above_70": false
  },
  "has_vcp_pattern": true,
  "vcp_details": {
    "stage": "Stage 3",
    "contraction_percent": 15.2,
    "volume_decline_percent": 35.8,
    "base_length_days": 42
  },
  "entry_point": 150.75,
  "stop_loss": 140.2,
  "target_price": 180.9,
  "risk_reward_ratio": 3.2,
  "analysis_report": "تحليل مفصل لسهم Apple Inc. (AAPL):\n\nيظهر سهم AAPL قوة فنية ممتازة، حيث يستوفي 7 من 8 معايير Trend Template. السهم يتداول فوق جميع المتوسطات المتحركة الرئيسية (50، 150، 200 يوم)، مما يشير إلى اتجاه صعودي قوي. كما أن المتوسط المتحرك لـ 150 يوم أعلى من المتوسط المتحرك لـ 200 يوم، والمتوسط المتحرك لـ 200 يوم في اتجاه صعودي لأكثر من شهر.\n\nتم اكتشاف نمط انكماش التقلب (VCP) في المرحلة الثالثة، مع انخفاض في التقلب بنسبة 15.2% وانخفاض في حجم التداول بنسبة 35.8% خلال فترة القاعدة التي استمرت 42 يوماً. هذا النمط يشير إلى احتمالية حدوث اختراق صعودي قوي.\n\nنقطة الدخول المقترحة هي 150.75 دولار، وهي تمثل اختراق أعلى مستوى في نمط VCP. مستوى وقف الخسارة المقترح هو 140.2 دولار (7% أسفل نقطة الدخول)، والسعر المستهدف هو 180.9 دولار، مما يعطي نسبة مخاطرة/مكافأة جذابة تبلغ 3.2.\n\nمن الناحية الأساسية، تظهر الشركة نمواً قوياً في الإيرادات والأرباح، مع هوامش ربح ممتازة ومركز مالي قوي. التوصية الحالية هي الشراء بدرجة ثقة 0.85.",
  "natural_language_recommendation": "نوصي بشراء سهم Apple (AAPL) عند سعر 150.75 دولار، مع تحديد مستوى وقف الخسارة عند 140.2 دولار والسعر المستهدف عند 180.9 دولار. يظهر السهم قوة فنية ممتازة، حيث يستوفي 7 من 8 معايير Trend Template، ويشكل نمط انكماش التقلب (VCP) في المرحلة الثالثة. نسبة المخاطرة/المكافأة جذابة عند 3.2، مما يجعل هذه الفرصة مناسبة للمستثمرين الذين يبحثون عن أسهم النمو ذات الزخم القوي."
}
```

### فحص الأسهم

```
POST /screen
```

#### المعلمات

| المعلمة | النوع | الوصف |
|---------|------|---------|
| criteria | object | معايير الفحص |
| limit | integer | الحد الأقصى لعدد النتائج (اختياري، الافتراضي: 20) |

#### مثال الطلب

```bash
curl -X POST "https://api.seba.com/v1/screen" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "criteria": {
      "trend_template": true,
      "trend_template_min_score": 5,
      "vcp": true,
      "buy_recommendations": true,
      "min_confidence": 0.7
    },
    "limit": 10
  }'
```

#### مثال الاستجابة

```json
{
  "results": [
    {
      "symbol": "AAPL",
      "name": "Apple Inc.",
      "sector": "Technology",
      "industry": "Consumer Electronics",
      "trend_template_score": 7,
      "has_vcp_pattern": true,
      "recommendation": "Buy",
      "confidence_score": 0.85,
      "entry_point": 150.75,
      "stop_loss": 140.2,
      "target_price": 180.9
    },
    {
      "symbol": "MSFT",
      "name": "Microsoft Corporation",
      "sector": "Technology",
      "industry": "Software",
      "trend_template_score": 8,
      "has_vcp_pattern": true,
      "recommendation": "Buy",
      "confidence_score": 0.9,
      "entry_point": 280.5,
      "stop_loss": 260.9,
      "target_price": 330.2
    },
    // ... المزيد من النتائج
  ],
  "count": 10
}
```

## التنبيهات

### إنشاء تنبيه جديد

```
POST /alerts
```

#### المعلمات

| المعلمة | النوع | الوصف |
|---------|------|---------|
| symbol | string | رمز السهم |
| price | number | السعر المستهدف |
| condition | string | الشرط (above, below) |
| message | string | رسالة اختيارية |

#### مثال الطلب

```bash
curl -X POST "https://api.seba.com/v1/alerts" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "AAPL",
    "price": 150.0,
    "condition": "above",
    "message": "سعر سهم Apple تجاوز 150 دولار"
  }'
```

#### مثال الاستجابة

```json
{
  "id": 123,
  "user_id": "user123",
  "symbol": "AAPL",
  "price": 150.0,
  "condition": "above",
  "message": "سعر سهم Apple تجاوز 150 دولار",
  "created_at": "2021-01-01T12:00:00Z",
  "triggered": false
}
```

### الحصول على تنبيهات المستخدم

```
GET /alerts
```

#### مثال الطلب

```bash
curl -X GET "https://api.seba.com/v1/alerts" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

#### مثال الاستجابة

```json
[
  {
    "id": 123,
    "user_id": "user123",
    "symbol": "AAPL",
    "price": 150.0,
    "condition": "above",
    "message": "سعر سهم Apple تجاوز 150 دولار",
    "created_at": "2021-01-01T12:00:00Z",
    "triggered": false
  },
  {
    "id": 124,
    "user_id": "user123",
    "symbol": "MSFT",
    "price": 250.0,
    "condition": "below",
    "message": "سعر سهم Microsoft انخفض تحت 250 دولار",
    "created_at": "2021-01-02T12:00:00Z",
    "triggered": true
  },
  // ... المزيد من التنبيهات
]
```

### حذف تنبيه

```
DELETE /alerts/{alert_id}
```

#### المعلمات

| المعلمة | النوع | الوصف |
|---------|------|---------|
| alert_id | integer | معرف التنبيه |

#### مثال الطلب

```bash
curl -X DELETE "https://api.seba.com/v1/alerts/123" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

#### مثال الاستجابة

```json
{
  "message": "تم حذف التنبيه 123 بنجاح"
}
```

## المحادثة

### إرسال رسالة إلى روبوت المحادثة

```
POST /chat
```

#### المعلمات

| المعلمة | النوع | الوصف |
|---------|------|---------|
| message | string | رسالة المستخدم |
| session_id | string | معرف جلسة المحادثة (اختياري) |

#### مثال الطلب

```bash
curl -X POST "https://api.seba.com/v1/chat" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "message": "ما هو نمط VCP؟",
    "session_id": "user123_20210101120000"
  }'
```

#### مثال الاستجابة

```json
{
  "session_id": "user123_20210101120000",
  "message": "ما هو نمط VCP؟",
  "response": "نمط VCP (Volatility Contraction Pattern) أو نمط انكماش التقلب هو نمط سعري طوره مارك مينيرفيني، ويتميز بانخفاض تدريجي في التقلب مع تشكيل قاعدة سعرية. يتكون النمط من ثلاث مراحل: الارتفاع الأولي (ارتفاع قوي في السعر مع حجم تداول مرتفع)، التصحيح (تصحيح سعري مع انخفاض في حجم التداول)، والانكماش (تضييق نطاق التداول مع انخفاض في التقلب وحجم التداول). بعد اكتمال النمط، يحدث اختراق لأعلى مع زيادة في حجم التداول، مما يشير إلى بداية موجة صعودية جديدة. يعتبر هذا النمط إشارة قوية للدخول في صفقة شراء.",
  "timestamp": "2021-01-01T12:05:00Z"
}
```

### مسح سياق المحادثة

```
POST /chat/clear
```

#### المعلمات

| المعلمة | النوع | الوصف |
|---------|------|---------|
| session_id | string | معرف جلسة المحادثة |

#### مثال الطلب

```bash
curl -X POST "https://api.seba.com/v1/chat/clear?session_id=user123_20210101120000" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

#### مثال الاستجابة

```json
{
  "message": "تم مسح سياق المحادثة للجلسة user123_20210101120000 بنجاح"
}
```

## السوق

### الحصول على ملخص حالة السوق

```
GET /market/summary
```

#### مثال الطلب

```bash
curl -X GET "https://api.seba.com/v1/market/summary" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

#### مثال الاستجابة

```json
{
  "market_data": {
    "^GSPC": {
      "name": "S&P 500",
      "last_price": 4500.25,
      "change": 35.75,
      "change_percent": 0.8,
      "volume": 2500000000,
      "date": "2021-01-01"
    },
    "^DJI": {
      "name": "Dow Jones Industrial Average",
      "last_price": 35750.5,
      "change": 250.25,
      "change_percent": 0.7,
      "volume": 350000000,
      "date": "2021-01-01"
    },
    "^IXIC": {
      "name": "NASDAQ Composite",
      "last_price": 15000.75,
      "change": 150.5,
      "change_percent": 1.0,
      "volume": 3000000000,
      "date": "2021-01-01"
    },
    "^RUT": {
      "name": "Russell 2000",
      "last_price": 2250.25,
      "change": 25.5,
      "change_percent": 1.1,
      "volume": 1500000000,
      "date": "2021-01-01"
    }
  },
  "top_stocks": [
    {
      "symbol": "AAPL",
      "name": "Apple Inc.",
      "last_price": 150.25,
      "change_percent": 2.5
    },
    {
      "symbol": "MSFT",
      "name": "Microsoft Corporation",
      "last_price": 280.5,
      "change_percent": 1.8
    },
    {
      "symbol": "GOOGL",
      "name": "Alphabet Inc.",
      "last_price": 2800.75,
      "change_percent": 1.5
    },
    {
      "symbol": "AMZN",
      "name": "Amazon.com, Inc.",
      "last_price": 3500.25,
      "change_percent": 1.2
    },
    {
      "symbol": "TSLA",
      "name": "Tesla, Inc.",
      "last_price": 950.5,
      "change_percent": 3.2
    }
  ],
  "market_summary": "أغلقت المؤشرات الرئيسية على ارتفاع اليوم، حيث ارتفع مؤشر S&P 500 بنسبة 0.8%، وارتفع مؤشر داو جونز الصناعي بنسبة 0.7%، وارتفع مؤشر ناسداك المركب بنسبة 1.0%، وارتفع مؤشر راسل 2000 بنسبة 1.1%. قاد قطاع التكنولوجيا الارتفاع، حيث سجلت أسهم Apple وMicrosoft وAlphabet وAmazon وTesla مكاسب قوية. كان حجم التداول أعلى من المتوسط، مما يشير إلى مشاركة قوية من المستثمرين. تشير البيانات الاقتصادية الإيجابية وتقارير الأرباح القوية إلى استمرار النمو الاقتصادي، مما يدعم الاتجاه الصعودي في سوق الأسهم.",
  "timestamp": "2021-01-01T16:00:00Z"
}
```

## المحتوى التعليمي

### الحصول على محتوى تعليمي

```
GET /educational/{topic}
```

#### المعلمات

| المعلمة | النوع | الوصف |
|---------|------|---------|
| topic | string | الموضوع |

#### مثال الطلب

```bash
curl -X GET "https://api.seba.com/v1/educational/vcp" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

#### مثال الاستجابة

```json
{
  "topic": "vcp",
  "content": "# نمط انكماش التقلب (VCP)\n\n## مقدمة\n\nنمط انكماش التقلب (Volatility Contraction Pattern) أو VCP هو نمط سعري طوره مارك مينيرفيني، وهو أحد أهم الأنماط في منهجية SEPA (Specific Entry Point Analysis). يعتبر هذا النمط إشارة قوية لبداية موجة صعودية جديدة عند اختراقه.\n\n## مراحل النمط\n\n### المرحلة الأولى: الارتفاع الأولي\n\nتبدأ المرحلة الأولى بارتفاع قوي في سعر السهم، عادة بنسبة 50% أو أكثر، مصحوباً بحجم تداول مرتفع. هذا الارتفاع يعكس اهتماماً مؤسسياً بالسهم ويشير إلى قوة أساسية في الشركة.\n\n### المرحلة الثانية: التصحيح\n\nبعد الارتفاع الأولي، يدخل السهم في مرحلة تصحيح سعري. خلال هذه المرحلة، ينخفض السعر بنسبة 20-40% من أعلى مستوى سابق. المهم في هذه المرحلة هو أن حجم التداول ينخفض مع انخفاض السعر، مما يشير إلى أن البيع ليس مدفوعاً بضغط مؤسسي قوي.\n\n### المرحلة الثالثة: الانكماش\n\nفي المرحلة الثالثة، يبدأ نطاق تداول السهم في التضييق، مع انخفاض في التقلب وحجم التداول. يشكل السهم قاعدة سعرية، حيث يتحرك السعر ضمن نطاق ضيق نسبياً. هذه المرحلة يمكن أن تستمر لعدة أسابيع أو أشهر، وكلما طالت فترة القاعدة، كلما كان الاختراق المحتمل أقوى.\n\n## الاختراق\n\nبعد اكتمال المراحل الثلاث، يحدث اختراق لأعلى مستوى في نمط VCP، مصحوباً بزيادة كبيرة في حجم التداول (عادة 50% أو أكثر فوق المتوسط). هذا الاختراق يشير إلى بداية موجة صعودية جديدة، ويعتبر إشارة دخول قوية.\n\n## كيفية تحديد نمط VCP\n\n1. **البحث عن ارتفاع أولي قوي**: ارتفاع بنسبة 50% أو أكثر مع حجم تداول مرتفع.\n2. **تحديد التصحيح**: انخفاض بنسبة 20-40% من أعلى مستوى سابق مع انخفاض في حجم التداول.\n3. **مراقبة الانكماش**: تضييق نطاق التداول مع انخفاض في التقلب وحجم التداول.\n4. **تحديد نقطة الاختراق**: أعلى مستوى في نمط VCP.\n\n## استراتيجية التداول\n\n1. **الدخول**: الشراء عند اختراق أعلى مستوى في نمط VCP مع زيادة في حجم التداول.\n2. **وقف الخسارة**: وضع وقف الخسارة عند 7-8% أسفل سعر الدخول.\n3. **الهدف**: تحديد هدف ربح واقعي بناءً على نسبة المخاطرة/المكافأة (عادة 3:1 أو أكثر).\n\n## أمثلة ناجحة\n\nبعض الأمثلة الناجحة لنمط VCP تشمل:\n\n1. **Apple (AAPL) في عام 2004**: شكل السهم نمط VCP قبل ارتفاعه من 1.50 دولار إلى 28 دولار.\n2. **Netflix (NFLX) في عام 2009**: شكل السهم نمط VCP قبل ارتفاعه من 7 دولارات إلى 300 دولار.\n3. **Amazon (AMZN) في عام 2009**: شكل السهم نمط VCP قبل ارتفاعه من 70 دولار إلى 1000 دولار.\n\n## الخلاصة\n\nnمط VCP هو أداة قوية لتحديد نقاط دخول محددة للأسهم ذات النمو العالي والزخم القوي. من خلال فهم مراحل النمط وكيفية تحديده، يمكن للمتداولين تحديد فرص تداول ذات نسبة مخاطرة/مكافأة جذابة.",
  "timestamp": "2021-01-01T12:00:00Z"
}
```

## رموز الحالة

| الرمز | الوصف |
|------|---------|
| 200 | نجاح |
| 201 | تم الإنشاء بنجاح |
| 400 | طلب غير صالح |
| 401 | غير مصرح |
| 403 | ممنوع |
| 404 | غير موجود |
| 500 | خطأ في الخادم |

## حدود معدل الطلبات

يتم تطبيق حدود معدل الطلبات التالية:

- المستخدمون العاديون: 100 طلب في الدقيقة
- المستخدمون المميزون: 1000 طلب في الدقيقة

عند تجاوز حد معدل الطلبات، سيتم إرجاع رمز الحالة 429 (Too Many Requests) مع رأس `Retry-After` الذي يحدد عدد الثواني قبل إمكانية إرسال طلبات جديدة.

## إخلاء المسؤولية

جميع البيانات والتحليلات والتوصيات المقدمة من واجهة برمجة التطبيقات هي للأغراض المعلوماتية فقط ولا تشكل نصيحة مالية. الاستثمار في سوق الأسهم ينطوي على مخاطر، وقد تخسر جزءاً من أو كل استثمارك. يجب عليك دائماً إجراء البحث الخاص بك واستشارة مستشار مالي مرخص قبل اتخاذ قرارات استثمارية.
