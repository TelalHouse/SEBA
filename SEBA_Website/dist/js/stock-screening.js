// ملف لتكامل لوحة تحكم فحص الأسهم مع واجهة برمجة التطبيقات
// هذا الملف يحتوي على وظائف لفحص الأسهم وعرض النتائج

document.addEventListener('DOMContentLoaded', function() {
    // التحقق من وجود عناصر فحص الأسهم في الصفحة
    const screeningForm = document.getElementById('screeningForm');
    const screeningResults = document.getElementById('screeningResults');
    
    if (screeningForm && screeningResults) {
        // إضافة مستمع حدث لنموذج الفحص
        screeningForm.addEventListener('submit', function(e) {
            e.preventDefault();
            screenStocks();
        });
        
        // إضافة مستمعات أحداث للأسئلة المقترحة
        const suggestedQueries = document.querySelectorAll('.suggested-query');
        suggestedQueries.forEach(button => {
            button.addEventListener('click', function() {
                // تعبئة النموذج بناءً على الاستعلام المقترح
                fillFormWithSuggestedQuery(this.dataset.query);
                // تقديم النموذج
                screeningForm.dispatchEvent(new Event('submit'));
            });
        });
    }
    
    // فحص الأسهم
    async function screenStocks() {
        try {
            // عرض مؤشر التحميل
            showLoadingIndicator();
            
            // جمع معايير الفحص من النموذج
            const criteria = collectScreeningCriteria();
            
            // إرسال طلب فحص الأسهم
            const results = await SEBA_API.Analysis.screenStocks(criteria);
            
            // عرض نتائج الفحص
            displayScreeningResults(results);
            
            // إخفاء مؤشر التحميل
            hideLoadingIndicator();
        } catch (error) {
            // إخفاء مؤشر التحميل
            hideLoadingIndicator();
            
            // عرض رسالة الخطأ
            showErrorMessage(`حدث خطأ أثناء فحص الأسهم: ${error.message}`);
        }
    }
    
    // جمع معايير الفحص من النموذج
    function collectScreeningCriteria() {
        const criteria = {
            trendTemplate: {
                enabled: document.getElementById('trendTemplate').checked,
                minScore: parseInt(document.querySelector('select[aria-labelledby="minTrendScore"]').value)
            },
            vcpPattern: {
                enabled: document.getElementById('vcpPattern').checked,
                stage3Only: document.getElementById('vcpStage3').checked
            },
            additionalCriteria: {
                highVolume: document.getElementById('highVolume').checked,
                strongEarnings: document.getElementById('strongEarnings').checked
            },
            sector: document.getElementById('sector').value,
            marketCap: document.getElementById('marketCap').value,
            maxResults: parseInt(document.getElementById('maxResults').value)
        };
        
        return criteria;
    }
    
    // تعبئة النموذج بناءً على الاستعلام المقترح
    function fillFormWithSuggestedQuery(query) {
        // إعادة تعيين النموذج أولاً
        screeningForm.reset();
        
        // تعبئة النموذج بناءً على الاستعلام
        switch (query) {
            case 'trend-template':
                document.getElementById('trendTemplate').checked = true;
                document.querySelector('select[aria-labelledby="minTrendScore"]').value = '7';
                document.getElementById('vcpPattern').checked = false;
                document.getElementById('highVolume').checked = true;
                document.getElementById('strongEarnings').checked = true;
                break;
            case 'vcp-breakout':
                document.getElementById('trendTemplate').checked = true;
                document.querySelector('select[aria-labelledby="minTrendScore"]').value = '6';
                document.getElementById('vcpPattern').checked = true;
                document.getElementById('vcpStage3').checked = true;
                document.getElementById('highVolume').checked = true;
                document.getElementById('strongEarnings').checked = true;
                break;
            case 'tech-leaders':
                document.getElementById('trendTemplate').checked = true;
                document.querySelector('select[aria-labelledby="minTrendScore"]').value = '6';
                document.getElementById('vcpPattern').checked = true;
                document.getElementById('highVolume').checked = true;
                document.getElementById('strongEarnings').checked = true;
                document.getElementById('sector').value = 'technology';
                break;
            case 'healthcare-leaders':
                document.getElementById('trendTemplate').checked = true;
                document.querySelector('select[aria-labelledby="minTrendScore"]').value = '6';
                document.getElementById('vcpPattern').checked = true;
                document.getElementById('highVolume').checked = true;
                document.getElementById('strongEarnings').checked = true;
                document.getElementById('sector').value = 'healthcare';
                break;
            case 'small-cap-growth':
                document.getElementById('trendTemplate').checked = true;
                document.querySelector('select[aria-labelledby="minTrendScore"]').value = '6';
                document.getElementById('vcpPattern').checked = true;
                document.getElementById('highVolume').checked = true;
                document.getElementById('strongEarnings').checked = true;
                document.getElementById('marketCap').value = 'small';
                break;
        }
    }
    
    // عرض نتائج الفحص
    function displayScreeningResults(results) {
        if (!results || results.stocks.length === 0) {
            screeningResults.innerHTML = `
                <div class="alert alert-info">
                    <i class="fas fa-info-circle me-2"></i>
                    لم يتم العثور على أسهم تطابق معايير البحث. يرجى تعديل المعايير والمحاولة مرة أخرى.
                </div>
            `;
            return;
        }
        
        // إنشاء HTML لعرض النتائج
        let html = `
            <div class="screening-results-header">
                <h3>نتائج الفحص</h3>
                <p>تم العثور على ${results.stocks.length} سهم يطابق معايير البحث.</p>
            </div>
            
            <div class="table-responsive mt-4">
                <table class="table table-hover">
                    <thead>
                        <tr>
                            <th>الرمز</th>
                            <th>الاسم</th>
                            <th>السعر</th>
                            <th>التغير</th>
                            <th>درجة Trend Template</th>
                            <th>نمط VCP</th>
                            <th>القطاع</th>
                            <th>القيمة السوقية</th>
                            <th>إجراءات</th>
                        </tr>
                    </thead>
                    <tbody>
        `;
        
        // إضافة صفوف لكل سهم
        results.stocks.forEach(stock => {
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
                    <td>${stock.sector}</td>
                    <td>${formatMarketCap(stock.marketCap)}</td>
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
        `;
        
        // إضافة قسم للتصدير والتصفية
        html += `
            <div class="screening-results-actions mt-4">
                <div class="row">
                    <div class="col-md-6">
                        <button class="btn btn-outline-primary" onclick="exportToCSV()">
                            <i class="fas fa-download me-2"></i>
                            تصدير إلى CSV
                        </button>
                    </div>
                    <div class="col-md-6 text-md-end">
                        <button class="btn btn-outline-secondary" onclick="clearResults()">
                            <i class="fas fa-times me-2"></i>
                            مسح النتائج
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        // عرض النتائج
        screeningResults.innerHTML = html;
        
        // إضافة وظيفة التصدير إلى CSV
        window.exportToCSV = function() {
            let csv = 'الرمز,الاسم,السعر,التغير,التغير %,درجة Trend Template,نمط VCP,القطاع,القيمة السوقية\n';
            
            results.stocks.forEach(stock => {
                csv += `${stock.symbol},${stock.name},${stock.price.toFixed(2)},${stock.priceChange.toFixed(2)},${stock.priceChangePercent.toFixed(2)}%,${stock.trendTemplateScore}/8,${stock.vcpDetected ? 'نعم' : 'لا'},${stock.sector},${formatMarketCap(stock.marketCap)}\n`;
            });
            
            const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
            const link = document.createElement('a');
            const url = URL.createObjectURL(blob);
            
            link.setAttribute('href', url);
            link.setAttribute('download', 'seba_screening_results.csv');
            link.style.visibility = 'hidden';
            
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        };
        
        // إضافة وظيفة مسح النتائج
        window.clearResults = function() {
            screeningResults.innerHTML = '';
        };
    }
    
    // عرض مؤشر التحميل
    function showLoadingIndicator() {
        screeningResults.innerHTML = `
            <div class="loading-indicator">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">جاري التحميل...</span>
                </div>
                <p class="mt-2">جاري فحص الأسهم...</p>
            </div>
        `;
    }
    
    // إخفاء مؤشر التحميل
    function hideLoadingIndicator() {
        const loadingIndicator = screeningResults.querySelector('.loading-indicator');
        if (loadingIndicator) {
            loadingIndicator.remove();
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
    
    // عرض رسالة خطأ
    function showErrorMessage(message) {
        screeningResults.innerHTML = `
            <div class="alert alert-danger alert-dismissible fade show" role="alert">
                <i class="fas fa-exclamation-circle me-2"></i>
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            </div>
        `;
    }
});
