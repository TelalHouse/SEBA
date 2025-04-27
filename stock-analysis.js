// ملف لتكامل لوحة تحكم تحليل الأسهم مع واجهة برمجة التطبيقات
// هذا الملف يحتوي على وظائف لعرض تحليل الأسهم وإنشاء الرسوم البيانية

document.addEventListener('DOMContentLoaded', function() {
    // التحقق من وجود عناصر تحليل الأسهم في الصفحة
    const stockAnalysisContainer = document.getElementById('stockAnalysisContainer');
    const stockSymbolInput = document.getElementById('stockSymbol');
    const analyzeButton = document.getElementById('analyzeButton');
    
    if (stockAnalysisContainer && stockSymbolInput && analyzeButton) {
        // إضافة مستمع حدث لزر التحليل
        analyzeButton.addEventListener('click', function() {
            const symbol = stockSymbolInput.value.trim().toUpperCase();
            if (symbol) {
                analyzeStock(symbol);
            } else {
                showErrorMessage('يرجى إدخال رمز السهم');
            }
        });
        
        // إضافة مستمع حدث للضغط على Enter في حقل الإدخال
        stockSymbolInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                analyzeButton.click();
            }
        });
        
        // التحقق من وجود معلمة symbol في عنوان URL
        const urlParams = new URLSearchParams(window.location.search);
        const symbolParam = urlParams.get('symbol');
        if (symbolParam) {
            stockSymbolInput.value = symbolParam.toUpperCase();
            analyzeButton.click();
        }
    }
    
    // تحليل السهم
    async function analyzeStock(symbol) {
        try {
            // عرض مؤشر التحميل
            showLoadingIndicator();
            
            // الحصول على معلومات السهم
            const stockInfo = await SEBA_API.Stocks.getStockInfo(symbol);
            
            // الحصول على البيانات التاريخية للسهم
            const historicalData = await SEBA_API.Stocks.getHistoricalData(symbol);
            
            // الحصول على المؤشرات الفنية للسهم
            const technicalIndicators = await SEBA_API.Stocks.getTechnicalIndicators(symbol);
            
            // الحصول على تحليل SEPA للسهم
            const sepaAnalysis = await SEBA_API.Analysis.analyzeStock(symbol);
            
            // عرض معلومات السهم
            displayStockInfo(stockInfo);
            
            // إنشاء الرسم البياني للسهم
            createStockChart(historicalData, technicalIndicators);
            
            // عرض تحليل SEPA
            displaySEPAAnalysis(sepaAnalysis);
            
            // إخفاء مؤشر التحميل
            hideLoadingIndicator();
        } catch (error) {
            // إخفاء مؤشر التحميل
            hideLoadingIndicator();
            
            // عرض رسالة الخطأ
            showErrorMessage(`حدث خطأ أثناء تحليل السهم ${symbol}: ${error.message}`);
        }
    }
    
    // عرض معلومات السهم
    function displayStockInfo(stockInfo) {
        const stockInfoContainer = document.getElementById('stockInfoContainer');
        if (!stockInfoContainer) return;
        
        // تنسيق التغير في السعر
        const priceChange = stockInfo.priceChange;
        const priceChangePercent = stockInfo.priceChangePercent;
        const priceChangeClass = priceChange >= 0 ? 'stock-up' : 'stock-down';
        const priceChangeIcon = priceChange >= 0 ? 'fa-caret-up' : 'fa-caret-down';
        
        stockInfoContainer.innerHTML = `
            <div class="stock-info-header">
                <div class="row align-items-center">
                    <div class="col-md-6">
                        <h2>${stockInfo.name} (${stockInfo.symbol})</h2>
                        <p class="text-muted">${stockInfo.exchange} | ${stockInfo.sector}</p>
                    </div>
                    <div class="col-md-6 text-md-end">
                        <h3 class="stock-price">${stockInfo.price.toFixed(2)} ${stockInfo.currency}</h3>
                        <p class="stock-change ${priceChangeClass}">
                            <i class="fas ${priceChangeIcon}"></i>
                            ${Math.abs(priceChange).toFixed(2)} (${Math.abs(priceChangePercent).toFixed(2)}%)
                        </p>
                    </div>
                </div>
            </div>
            <div class="stock-info-details mt-4">
                <div class="row">
                    <div class="col-md-3 col-6 mb-3">
                        <div class="info-item">
                            <span class="info-label">افتتاح</span>
                            <span class="info-value">${stockInfo.open.toFixed(2)}</span>
                        </div>
                    </div>
                    <div class="col-md-3 col-6 mb-3">
                        <div class="info-item">
                            <span class="info-label">أعلى سعر</span>
                            <span class="info-value">${stockInfo.high.toFixed(2)}</span>
                        </div>
                    </div>
                    <div class="col-md-3 col-6 mb-3">
                        <div class="info-item">
                            <span class="info-label">أدنى سعر</span>
                            <span class="info-value">${stockInfo.low.toFixed(2)}</span>
                        </div>
                    </div>
                    <div class="col-md-3 col-6 mb-3">
                        <div class="info-item">
                            <span class="info-label">حجم التداول</span>
                            <span class="info-value">${formatNumber(stockInfo.volume)}</span>
                        </div>
                    </div>
                </div>
                <div class="row mt-2">
                    <div class="col-md-3 col-6 mb-3">
                        <div class="info-item">
                            <span class="info-label">أعلى 52 أسبوع</span>
                            <span class="info-value">${stockInfo.fiftyTwoWeekHigh.toFixed(2)}</span>
                        </div>
                    </div>
                    <div class="col-md-3 col-6 mb-3">
                        <div class="info-item">
                            <span class="info-label">أدنى 52 أسبوع</span>
                            <span class="info-value">${stockInfo.fiftyTwoWeekLow.toFixed(2)}</span>
                        </div>
                    </div>
                    <div class="col-md-3 col-6 mb-3">
                        <div class="info-item">
                            <span class="info-label">القيمة السوقية</span>
                            <span class="info-value">${formatMarketCap(stockInfo.marketCap)}</span>
                        </div>
                    </div>
                    <div class="col-md-3 col-6 mb-3">
                        <div class="info-item">
                            <span class="info-label">نسبة السعر للربح</span>
                            <span class="info-value">${stockInfo.pe ? stockInfo.pe.toFixed(2) : 'غير متوفر'}</span>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }
    
    // إنشاء الرسم البياني للسهم
    function createStockChart(historicalData, technicalIndicators) {
        const chartContainer = document.getElementById('stockChartContainer');
        if (!chartContainer) return;
        
        // تحويل البيانات إلى تنسيق مناسب للرسم البياني
        const dates = historicalData.map(item => new Date(item.date));
        const prices = historicalData.map(item => item.close);
        const volumes = historicalData.map(item => item.volume);
        
        // إنشاء الرسم البياني باستخدام Chart.js
        const ctx = document.getElementById('stockChart').getContext('2d');
        
        // التحقق من وجود رسم بياني سابق وتدميره
        if (window.stockChart) {
            window.stockChart.destroy();
        }
        
        // إنشاء رسم بياني جديد
        window.stockChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: dates,
                datasets: [
                    {
                        label: 'سعر الإغلاق',
                        data: prices,
                        borderColor: '#4CAF50',
                        backgroundColor: 'rgba(76, 175, 80, 0.1)',
                        borderWidth: 2,
                        pointRadius: 0,
                        fill: true,
                        yAxisID: 'y'
                    },
                    {
                        label: 'المتوسط المتحرك 50 يوم',
                        data: technicalIndicators.sma50,
                        borderColor: '#2196F3',
                        borderWidth: 1.5,
                        pointRadius: 0,
                        fill: false,
                        yAxisID: 'y'
                    },
                    {
                        label: 'المتوسط المتحرك 200 يوم',
                        data: technicalIndicators.sma200,
                        borderColor: '#FF5722',
                        borderWidth: 1.5,
                        pointRadius: 0,
                        fill: false,
                        yAxisID: 'y'
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    mode: 'index',
                    intersect: false
                },
                scales: {
                    x: {
                        type: 'time',
                        time: {
                            unit: 'month',
                            displayFormats: {
                                month: 'MMM yyyy'
                            }
                        },
                        title: {
                            display: true,
                            text: 'التاريخ'
                        }
                    },
                    y: {
                        position: 'right',
                        title: {
                            display: true,
                            text: 'السعر'
                        }
                    }
                },
                plugins: {
                    legend: {
                        position: 'top'
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                let label = context.dataset.label || '';
                                if (label) {
                                    label += ': ';
                                }
                                if (context.parsed.y !== null) {
                                    label += context.parsed.y.toFixed(2);
                                }
                                return label;
                            }
                        }
                    }
                }
            }
        });
        
        // إنشاء رسم بياني للمؤشرات الفنية
        createTechnicalIndicatorsChart(technicalIndicators);
    }
    
    // إنشاء رسم بياني للمؤشرات الفنية
    function createTechnicalIndicatorsChart(technicalIndicators) {
        const rsiChartContainer = document.getElementById('rsiChartContainer');
        if (!rsiChartContainer) return;
        
        // إنشاء رسم بياني لمؤشر القوة النسبية RSI
        const rsiCtx = document.getElementById('rsiChart').getContext('2d');
        
        // التحقق من وجود رسم بياني سابق وتدميره
        if (window.rsiChart) {
            window.rsiChart.destroy();
        }
        
        // إنشاء رسم بياني جديد
        window.rsiChart = new Chart(rsiCtx, {
            type: 'line',
            data: {
                labels: technicalIndicators.dates,
                datasets: [
                    {
                        label: 'مؤشر القوة النسبية RSI',
                        data: technicalIndicators.rsi,
                        borderColor: '#9C27B0',
                        backgroundColor: 'rgba(156, 39, 176, 0.1)',
                        borderWidth: 2,
                        pointRadius: 0,
                        fill: true
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        type: 'time',
                        time: {
                            unit: 'month',
                            displayFormats: {
                                month: 'MMM yyyy'
                            }
                        }
                    },
                    y: {
                        min: 0,
                        max: 100,
                        ticks: {
                            stepSize: 10
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });
        
        // إنشاء رسم بياني لمؤشر MACD
        const macdCtx = document.getElementById('macdChart').getContext('2d');
        
        // التحقق من وجود رسم بياني سابق وتدميره
        if (window.macdChart) {
            window.macdChart.destroy();
        }
        
        // إنشاء رسم بياني جديد
        window.macdChart = new Chart(macdCtx, {
            type: 'bar',
            data: {
                labels: technicalIndicators.dates,
                datasets: [
                    {
                        label: 'MACD Histogram',
                        data: technicalIndicators.macdHistogram,
                        backgroundColor: function(context) {
                            const value = context.dataset.data[context.dataIndex];
                            return value >= 0 ? 'rgba(76, 175, 80, 0.5)' : 'rgba(244, 67, 54, 0.5)';
                        },
                        borderColor: function(context) {
                            const value = context.dataset.data[context.dataIndex];
                            return value >= 0 ? 'rgba(76, 175, 80, 1)' : 'rgba(244, 67, 54, 1)';
                        },
                        borderWidth: 1,
                        type: 'bar'
                    },
                    {
                        label: 'MACD Line',
                        data: technicalIndicators.macdLine,
                        borderColor: '#2196F3',
                        borderWidth: 2,
                        pointRadius: 0,
                        fill: false,
                        type: 'line'
                    },
                    {
                        label: 'Signal Line',
                        data: technicalIndicators.macdSignal,
                        borderColor: '#FF9800',
                        borderWidth: 2,
                        pointRadius: 0,
                        fill: false,
                        type: 'line'
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        type: 'time',
                        time: {
                            unit: 'month',
                            displayFormats: {
                                month: 'MMM yyyy'
                            }
                        }
                    }
                }
            }
        });
    }
    
    // عرض تحليل SEPA
    function displaySEPAAnalysis(sepaAnalysis) {
        const sepaAnalysisContainer = document.getElementById('sepaAnalysisContainer');
        if (!sepaAnalysisContainer) return;
        
        // تحديد لون التوصية
        let recommendationClass = 'recommendation-neutral';
        if (sepaAnalysis.recommendation === 'شراء') {
            recommendationClass = 'recommendation-buy';
        } else if (sepaAnalysis.recommendation === 'بيع') {
            recommendationClass 
(Content truncated due to size limit. Use line ranges to read in chunks)