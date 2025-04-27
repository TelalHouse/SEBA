// ملف لتكامل واجهة المستخدم مع واجهة برمجة التطبيقات
// هذا الملف يحتوي على وظائف للاتصال بواجهة برمجة التطبيقات الخاصة بنظام SEBA

// تكوين الاتصال بواجهة برمجة التطبيقات
const API_CONFIG = {
    BASE_URL: 'https://api.seba-analysis.com/v1',
    TIMEOUT: 30000, // 30 ثانية
    HEADERS: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
};

// إنشاء نسخة من Axios مع التكوين الأساسي
const apiClient = axios.create({
    baseURL: API_CONFIG.BASE_URL,
    timeout: API_CONFIG.TIMEOUT,
    headers: API_CONFIG.HEADERS
});

// إضافة معترض للطلبات لإضافة رمز الوصول إذا كان المستخدم مسجل الدخول
apiClient.interceptors.request.use(
    config => {
        const token = localStorage.getItem('auth_token');
        if (token) {
            config.headers['Authorization'] = `Bearer ${token}`;
        }
        return config;
    },
    error => {
        return Promise.reject(error);
    }
);

// إضافة معترض للاستجابات للتعامل مع الأخطاء الشائعة
apiClient.interceptors.response.use(
    response => {
        return response;
    },
    error => {
        if (error.response) {
            // الخطأ من الخادم مع رمز استجابة
            if (error.response.status === 401) {
                // غير مصرح - تسجيل الخروج
                localStorage.removeItem('auth_token');
                localStorage.removeItem('user_info');
                window.location.href = '/login.html?session_expired=true';
            } else if (error.response.status === 403) {
                // ممنوع - عرض رسالة خطأ
                showErrorMessage('ليس لديك صلاحية للوصول إلى هذا المورد');
            } else if (error.response.status === 404) {
                // غير موجود - عرض رسالة خطأ
                showErrorMessage('المورد المطلوب غير موجود');
            } else if (error.response.status === 500) {
                // خطأ في الخادم - عرض رسالة خطأ
                showErrorMessage('حدث خطأ في الخادم. يرجى المحاولة مرة أخرى لاحقاً');
            }
        } else if (error.request) {
            // لم يتم استلام استجابة من الخادم
            showErrorMessage('لا يمكن الاتصال بالخادم. يرجى التحقق من اتصالك بالإنترنت والمحاولة مرة أخرى');
        } else {
            // حدث خطأ أثناء إعداد الطلب
            showErrorMessage('حدث خطأ أثناء إرسال الطلب. يرجى المحاولة مرة أخرى');
        }
        return Promise.reject(error);
    }
);

// عرض رسالة خطأ
function showErrorMessage(message) {
    // التحقق من وجود عنصر لعرض الأخطاء
    const errorContainer = document.getElementById('errorContainer');
    if (errorContainer) {
        errorContainer.innerHTML = `
            <div class="alert alert-danger alert-dismissible fade show" role="alert">
                <i class="fas fa-exclamation-circle me-2"></i>
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            </div>
        `;
    } else {
        // إنشاء عنصر جديد لعرض الأخطاء إذا لم يكن موجوداً
        const newErrorContainer = document.createElement('div');
        newErrorContainer.id = 'errorContainer';
        newErrorContainer.className = 'container mt-3';
        newErrorContainer.innerHTML = `
            <div class="alert alert-danger alert-dismissible fade show" role="alert">
                <i class="fas fa-exclamation-circle me-2"></i>
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            </div>
        `;
        document.body.insertBefore(newErrorContainer, document.body.firstChild);
    }
}

// وظائف المصادقة
const AuthAPI = {
    // تسجيل الدخول
    login: async (email, password) => {
        try {
            const response = await apiClient.post('/auth/login', { email, password });
            // حفظ رمز الوصول ومعلومات المستخدم في التخزين المحلي
            localStorage.setItem('auth_token', response.data.token);
            localStorage.setItem('user_info', JSON.stringify(response.data.user));
            return response.data;
        } catch (error) {
            console.error('خطأ في تسجيل الدخول:', error);
            throw error;
        }
    },

    // تسجيل مستخدم جديد
    register: async (name, email, password) => {
        try {
            const response = await apiClient.post('/auth/register', { name, email, password });
            return response.data;
        } catch (error) {
            console.error('خطأ في تسجيل مستخدم جديد:', error);
            throw error;
        }
    },

    // تسجيل الخروج
    logout: () => {
        localStorage.removeItem('auth_token');
        localStorage.removeItem('user_info');
        window.location.href = '/index.html';
    },

    // التحقق من حالة تسجيل الدخول
    isLoggedIn: () => {
        return !!localStorage.getItem('auth_token');
    },

    // الحصول على معلومات المستخدم
    getUserInfo: () => {
        const userInfo = localStorage.getItem('user_info');
        return userInfo ? JSON.parse(userInfo) : null;
    }
};

// وظائف الأسهم
const StocksAPI = {
    // الحصول على معلومات السهم
    getStockInfo: async (symbol) => {
        try {
            const response = await apiClient.get(`/stocks/${symbol}`);
            return response.data;
        } catch (error) {
            console.error(`خطأ في الحصول على معلومات السهم ${symbol}:`, error);
            throw error;
        }
    },

    // الحصول على البيانات التاريخية للسهم
    getHistoricalData: async (symbol, interval = '1d', range = '1y') => {
        try {
            const response = await apiClient.get(`/stocks/${symbol}/historical`, {
                params: { interval, range }
            });
            return response.data;
        } catch (error) {
            console.error(`خطأ في الحصول على البيانات التاريخية للسهم ${symbol}:`, error);
            throw error;
        }
    },

    // الحصول على البيانات الأساسية للسهم
    getFundamentalData: async (symbol) => {
        try {
            const response = await apiClient.get(`/stocks/${symbol}/fundamental`);
            return response.data;
        } catch (error) {
            console.error(`خطأ في الحصول على البيانات الأساسية للسهم ${symbol}:`, error);
            throw error;
        }
    },

    // الحصول على المؤشرات الفنية للسهم
    getTechnicalIndicators: async (symbol, indicators = ['sma', 'ema', 'rsi', 'macd']) => {
        try {
            const response = await apiClient.get(`/stocks/${symbol}/indicators`, {
                params: { indicators: indicators.join(',') }
            });
            return response.data;
        } catch (error) {
            console.error(`خطأ في الحصول على المؤشرات الفنية للسهم ${symbol}:`, error);
            throw error;
        }
    }
};

// وظائف التحليل
const AnalysisAPI = {
    // تحليل السهم باستخدام منهجية SEPA
    analyzeStock: async (symbol, reportType = 'detailed') => {
        try {
            const response = await apiClient.get(`/analysis/${symbol}`, {
                params: { type: reportType }
            });
            return response.data;
        } catch (error) {
            console.error(`خطأ في تحليل السهم ${symbol}:`, error);
            throw error;
        }
    },

    // فحص الأسهم باستخدام معايير محددة
    screenStocks: async (criteria) => {
        try {
            const response = await apiClient.post('/analysis/screen', criteria);
            return response.data;
        } catch (error) {
            console.error('خطأ في فحص الأسهم:', error);
            throw error;
        }
    },

    // الحصول على ملخص حالة السوق
    getMarketSummary: async () => {
        try {
            const response = await apiClient.get('/analysis/market-summary');
            return response.data;
        } catch (error) {
            console.error('خطأ في الحصول على ملخص حالة السوق:', error);
            throw error;
        }
    }
};

// وظائف التنبيهات
const AlertsAPI = {
    // إنشاء تنبيه جديد
    createAlert: async (alertData) => {
        try {
            const response = await apiClient.post('/alerts', alertData);
            return response.data;
        } catch (error) {
            console.error('خطأ في إنشاء تنبيه جديد:', error);
            throw error;
        }
    },

    // الحصول على تنبيهات المستخدم
    getUserAlerts: async () => {
        try {
            const response = await apiClient.get('/alerts');
            return response.data;
        } catch (error) {
            console.error('خطأ في الحصول على تنبيهات المستخدم:', error);
            throw error;
        }
    },

    // حذف تنبيه
    deleteAlert: async (alertId) => {
        try {
            const response = await apiClient.delete(`/alerts/${alertId}`);
            return response.data;
        } catch (error) {
            console.error(`خطأ في حذف التنبيه ${alertId}:`, error);
            throw error;
        }
    }
};

// وظائف روبوت المحادثة
const ChatbotAPI = {
    // إرسال رسالة إلى روبوت المحادثة
    sendMessage: async (message) => {
        try {
            const response = await apiClient.post('/chatbot/message', { message });
            return response.data;
        } catch (error) {
            console.error('خطأ في إرسال رسالة إلى روبوت المحادثة:', error);
            throw error;
        }
    },

    // مسح سياق المحادثة
    clearContext: async () => {
        try {
            const response = await apiClient.post('/chatbot/clear-context');
            return response.data;
        } catch (error) {
            console.error('خطأ في مسح سياق المحادثة:', error);
            throw error;
        }
    }
};

// تصدير جميع واجهات برمجة التطبيقات
const SEBA_API = {
    Auth: AuthAPI,
    Stocks: StocksAPI,
    Analysis: AnalysisAPI,
    Alerts: AlertsAPI,
    Chatbot: ChatbotAPI
};

// إضافة واجهة برمجة التطبيقات إلى النافذة للوصول إليها من ملفات JavaScript الأخرى
window.SEBA_API = SEBA_API;
