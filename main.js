// ملف لتحسين تجربة المستخدم وتوفير وظائف مشتركة للموقع
// هذا الملف يحتوي على وظائف عامة تستخدم في جميع صفحات الموقع

document.addEventListener('DOMContentLoaded', function() {
    // تهيئة مكونات Bootstrap
    initBootstrapComponents();
    
    // تهيئة الرسوم البيانية في لوحة التحكم
    initDashboardCharts();
    
    // التحقق من حالة تسجيل الدخول وتحديث واجهة المستخدم
    updateAuthUI();
    
    // إضافة مستمعات أحداث للروابط والأزرار
    addEventListeners();
    
    // تهيئة نماذج البحث
    initSearchForms();
    
    // تحميل البيانات الأولية للصفحة
    loadInitialPageData();
});

// تهيئة مكونات Bootstrap
function initBootstrapComponents() {
    // تهيئة التلميحات
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // تهيئة النوافذ المنبثقة
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
}

// تهيئة الرسوم البيانية في لوحة التحكم
function initDashboardCharts() {
    // التحقق من وجود عنصر الرسم البياني للقطاعات
    const sectorsChartElement = document.getElementById('sectorsChart');
    if (sectorsChartElement) {
        const ctx = sectorsChartElement.getContext('2d');
        
        // إنشاء رسم بياني دائري للقطاعات
        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['التكنولوجيا', 'الصحة', 'المالية', 'الطاقة', 'السلع الاستهلاكية', 'الصناعة'],
                datasets: [{
                    data: [35, 20, 15, 10, 12, 8],
                    backgroundColor: [
                        '#4CAF50',
                        '#2196F3',
                        '#9C27B0',
                        '#FF5722',
                        '#FFC107',
                        '#607D8B'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'right',
                        labels: {
                            font: {
                                family: 'Tajawal'
                            }
                        }
                    }
                }
            }
        });
    }
}

// التحقق من حالة تسجيل الدخول وتحديث واجهة المستخدم
function updateAuthUI() {
    // التحقق من وجود رمز الوصول في التخزين المحلي
    const isLoggedIn = localStorage.getItem('auth_token') !== null;
    
    // الحصول على عناصر واجهة المستخدم المتعلقة بالمصادقة
    const authButtons = document.querySelector('.auth-buttons');
    const userDropdown = document.querySelector('.user-dropdown');
    
    if (authButtons && userDropdown) {
        if (isLoggedIn) {
            // إخفاء أزرار تسجيل الدخول وإظهار قائمة المستخدم المنسدلة
            authButtons.style.display = 'none';
            userDropdown.style.display = 'block';
            
            // تحديث اسم المستخدم
            const userInfo = JSON.parse(localStorage.getItem('user_info') || '{}');
            const userNameElement = document.querySelector('.user-name');
            if (userNameElement && userInfo.name) {
                userNameElement.textContent = userInfo.name;
            }
        } else {
            // إظهار أزرار تسجيل الدخول وإخفاء قائمة المستخدم المنسدلة
            authButtons.style.display = 'flex';
            userDropdown.style.display = 'none';
        }
    }
}

// إضافة مستمعات أحداث للروابط والأزرار
function addEventListeners() {
    // مستمع حدث لزر تسجيل الخروج
    const logoutButton = document.getElementById('logoutButton');
    if (logoutButton) {
        logoutButton.addEventListener('click', function(e) {
            e.preventDefault();
            logout();
        });
    }
    
    // مستمع حدث لزر مسح سياق المحادثة
    const clearChatContextButton = document.getElementById('clearChatContextButton');
    if (clearChatContextButton) {
        clearChatContextButton.addEventListener('click', function(e) {
            e.preventDefault();
            if (window.clearChatContext) {
                window.clearChatContext();
            }
        });
    }
    
    // مستمع حدث لزر التبديل بين الوضع الليلي والنهاري
    const darkModeToggle = document.getElementById('darkModeToggle');
    if (darkModeToggle) {
        darkModeToggle.addEventListener('click', function(e) {
            e.preventDefault();
            toggleDarkMode();
        });
        
        // تحديث حالة زر التبديل بناءً على الوضع الحالي
        updateDarkModeToggle();
    }
}

// تسجيل الخروج
function logout() {
    // مسح بيانات المصادقة من التخزين المحلي
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user_info');
    
    // إعادة تحميل الصفحة
    window.location.reload();
}

// التبديل بين الوضع الليلي والنهاري
function toggleDarkMode() {
    // التحقق من الوضع الحالي
    const isDarkMode = localStorage.getItem('dark_mode') === 'true';
    
    // تبديل الوضع
    localStorage.setItem('dark_mode', (!isDarkMode).toString());
    
    // تطبيق الوضع الجديد
    applyDarkMode();
    
    // تحديث حالة زر التبديل
    updateDarkModeToggle();
}

// تطبيق الوضع الليلي أو النهاري
function applyDarkMode() {
    const isDarkMode = localStorage.getItem('dark_mode') === 'true';
    
    // إضافة أو إزالة فئة الوضع الليلي من عنصر html
    document.documentElement.classList.toggle('dark-mode', isDarkMode);
}

// تحديث حالة زر التبديل بين الوضع الليلي والنهاري
function updateDarkModeToggle() {
    const darkModeToggle = document.getElementById('darkModeToggle');
    if (darkModeToggle) {
        const isDarkMode = localStorage.getItem('dark_mode') === 'true';
        
        // تحديث نص الزر وأيقونته
        const icon = darkModeToggle.querySelector('i');
        if (icon) {
            icon.className = isDarkMode ? 'fas fa-sun' : 'fas fa-moon';
        }
        
        const text = darkModeToggle.querySelector('span');
        if (text) {
            text.textContent = isDarkMode ? 'الوضع النهاري' : 'الوضع الليلي';
        }
    }
}

// تهيئة نماذج البحث
function initSearchForms() {
    // نموذج البحث العام
    const searchForm = document.getElementById('searchForm');
    if (searchForm) {
        searchForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const searchInput = document.getElementById('searchInput');
            if (searchInput) {
                const query = searchInput.value.trim();
                if (query) {
                    // التحقق مما إذا كان الاستعلام هو رمز سهم
                    if (/^[A-Z]{1,5}$/.test(query)) {
                        // الانتقال إلى صفحة تحليل السهم
                        window.location.href = `analysis.html?symbol=${query}`;
                    } else {
                        // الانتقال إلى صفحة البحث العامة
                        window.location.href = `search.html?q=${encodeURIComponent(query)}`;
                    }
                }
            }
        });
    }
}

// تحميل البيانات الأولية للصفحة
function loadInitialPageData() {
    // تحميل ملخص السوق في الصفحة الرئيسية
    loadMarketSummary();
    
    // تحميل الأسهم الرائجة في الصفحة الرئيسية
    loadTrendingStocks();
    
    // تطبيق الوضع الليلي أو النهاري
    applyDarkMode();
}

// تحميل ملخص السوق
async function loadMarketSummary() {
    const marketSummaryContainer = document.getElementById('marketSummaryContainer');
    if (!marketSummaryContainer) return;
    
    try {
        // عرض مؤشر التحميل
        marketSummaryContainer.innerHTML = `
            <div class="loading-indicator">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">جاري التحميل...</span>
                </div>
                <p class="mt-2">جاري تحميل ملخص السوق...</p>
            </div>
        `;
        
        // الحصول على ملخص السوق من واجهة برمجة التطبيقات
        const marketSummary = await SEBA_API.Analysis.getMarketSummary();
        
        // عرض ملخص السوق
        marketSummaryContainer.innerHTML = `
            <div class="row">
                <div class="col-md-3 mb-3">
                    <div class="card text-white bg-primary">
                        <div class="card-body">
                            <h5 class="card-title">S&P 500</h5>
                            <p class="card-text fs-4">${marketSummary.sp500.price.toFixed(2)} <span class="${marketSummary.sp500.change >= 0 ? 'stock-up' : 'stock-down'}"><i class="fas ${marketSummary.sp500.change >= 0 ? 'fa-caret-up' : 'fa-caret-down'}"></i> ${Math.abs(marketSummary.sp500.changePercent).toFixed(2)}%</span></p>
                        </div>
                    </div>
                </div>
                <div class="col-md-3 mb-3">
                    <div class="card text-white bg-info">
                        <div class="card-body">
                            <h5 class="card-title">Nasdaq</h5>
                            <p class="card-text fs-4">${marketSummary.nasdaq.price.toFixed(2)} <span class="${marketSummary.nasdaq.change >= 0 ? 'stock-up' : 'stock-down'}"><i class="fas ${marketSummary.nasdaq.change >= 0 ? 'fa-caret-up' : 'fa-caret-down'}"></i> ${Math.abs(marketSummary.nasdaq.changePercent).toFixed(2)}%</span></p>
                        </div>
                    </div>
                </div>
                <div class="col-md-3 mb-3">
                    <div class="card text-white bg-success">
                        <div class="card-body">
                            <h5 class="card-title">Dow Jones</h5>
                            <p class="card-text fs-4">${marketSummary.dowJones.price.toFixed(2)} <span class="${marketSummary.dowJones.change >= 0 ? 'stock-up' : 'stock-down'}"><i class="fas ${marketSummary.dowJones.change >= 0 ? 'fa-caret-up' : 'fa-caret-down'}"></i> ${Math.abs(marketSummary.dowJones.changePercent).toFixed(2)}%</span></p>
                        </div>
                    </div>
                </div>
                <div class="col-md-3 mb-3">
                    <div class="card text-white bg-danger">
                        <div class="card-body">
                            <h5 class="card-title">Russell 2000</h5>
                            <p class="card-text fs-4">${marketSummary.russell2000.price.toFixed(2)} <span class="${marketSummary.russell2000.change >= 0 ? 'stock-up' : 'stock-down'}"><i class="fas ${marketSummary.russell2000.change >= 0 ? 'fa-caret-up' : 'fa-caret-down'}"></i> ${Math.abs(marketSummary.russell2000.changePercent).toFixed(2)}%</span></p>
                        </div>
                    </div>
                </div>
            </div>
            <div class="mt-3">
                <p><strong>تحديث السوق:</strong> ${marketSummary.summary}</p>
            </div>
        `;
    } catch (error) {
        console.error('خطأ في تحميل ملخص السوق:', error);
        
        // عرض رسالة خطأ
        marketSummaryContainer.innerHTML = `
            <div class="alert alert-danger">
                <i class="fas fa-exclamation-circle me-2"></i>
                حدث خطأ أثناء تحميل ملخص السوق. يرجى المحاولة مرة أخرى لاحقاً.
            </div>
        `;
    }
}

// تحميل الأسهم الرائجة
async function loadTrendingStocks() {
    const trendingStocksContainer = document.getElementById('trendingStocksContainer');
    if (!trendingStocksContainer) return;
    
    try {
        // عرض مؤشر التحميل
        trendingStocksContainer.innerHTML = `
            <div class="loading-indicator">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">جاري التحميل...</span>
                </div>
                <p class="mt-2">جاري تحميل الأسهم الرائجة...</p>
            </div>
        `;
        
        // الحصول على الأسهم الرائجة من واجهة برمجة التطبيقات
        const trendingStocks = await SEBA_API.Analysis.screenStocks({
            trendTemplate: {
                enabled: true,
                minScore: 6
            },
            vcpPattern: {
                enabled: true,
                stage3Only: false
            },
            additionalCriteria: {
                highVolume: true,
                strongEarnings: true
            },
            maxResults: 5
        });
        
        // عرض الأسهم الرائجة
        let html = `
            <div class="table-responsive">
                <table class="table table-hover">
                    <thead>
                        <tr>
                            <th>الرمز</th>
                            <th>الاسم</th>
                            <th>السعر</th>
                            <th>التغير</th>
                            <th>درجة Trend Template</th>
                            <th>نمط VCP</th>
                            <th>إجراءات</th>
                        </tr>
                    </thead>
                    <tbody>
        `;
        
        // إضافة صفوف لكل سهم
        trendingStocks.stocks.forEach(stock => {
            // تنسيق التغير في السعر
            const priceChangeClass = stock.priceChange >= 0 ? 'stock-up' : 'stock-down';
            const priceChangeIcon = stock.priceChange >= 0 ? 'fa-caret-up' : 'fa-caret-down';
            
            // تنسيق نمط VCP
            const vcpBadgeClass = stock.vcpDetected ? 'bg-success' : 'bg-secondary';
            const vcpBadgeText = stock.vcpDetected ? 'نعم' : 'لا';
            
            html += `
                <tr>
                    <td>${stock.symbol}</td>
                    <td>${stock.name}</td>
                    <td>${stock.price.toFixed(2)}</td>
                    <td class="${priceChangeClass}">
                        <i class="fas ${priceChangeIcon}"></i>
                        ${Math.abs(stock.priceChange).toFixed(2)} (${Math.abs(stock.priceChangePercent).toFixed(2)}%)
                    </td>
                    <td>${stock.trendTemplateScore}/8</td>
                    <td><span class="badge ${vcpBadgeClass}">${vcpBadgeText}</span></td>
                    <td>
                        <a href="analysis.html?symbol=${stock.symbol}" class="btn btn-sm btn-primary">تحليل</a>
                    </td>
                </tr>
            `;
        });
        
        html += `
                    </tbody>
                </table>
            </div>
            <div class="text-center mt-3">
                <a href="screening.html" class="btn btn-outline-primary">عرض المزيد من الأسهم</a>
            </div>
        `;
        
        // عرض الأسهم الرائجة
        trendingStocksContainer.innerHTML = html;
    } catch (error) {
        console.error('خطأ في تحميل الأسهم الرائجة:', error);
        
        // عرض رسالة خطأ
        trendingStocksContainer.innerHTML = `
            <div class="alert alert-danger">
                <i class="fas fa-exclamation-circle me-2"></i>
                حدث خطأ أثناء تحميل الأسهم الرائجة. يرجى المحاولة مرة أخرى لاحقاً.
            </div>
        `;
    }
}

// تنسيق القيمة السوقية
function formatMarketCap(marketCap) {
    if (marketCap >= 1e12) {
        return (marketCap / 1e12).toFixed(2) + ' تريليون';
    } else if (marketCap >= 1e9) {
        return (marketCap / 1e9).toFixed(2) + ' مليار';
    } else if (marketCap >= 1e6) {
        return (marketCap / 1e6).toFixed(2) + ' مليون';
    } else {
        return marketCap.toFixed(2);
    }
}

// تنسيق الأرقام
function formatNumber(number) {
    return new Intl.NumberFormat().format(number);
}
