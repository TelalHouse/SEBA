// ملف لتكامل روبوت المحادثة مع واجهة برمجة التطبيقات
// هذا الملف يحتوي على وظائف للتفاعل مع روبوت المحادثة وعرض المحادثة

document.addEventListener('DOMContentLoaded', function() {
    // التحقق من وجود عناصر روبوت المحادثة في الصفحة
    const chatMessages = document.getElementById('chatMessages');
    const chatForm = document.getElementById('chatForm');
    const chatInput = document.getElementById('chatInput');
    
    if (chatMessages && chatForm && chatInput) {
        // إضافة رسالة ترحيبية
        addBotMessage('مرحباً بك في روبوت محادثة SEBA! كيف يمكنني مساعدتك اليوم؟ يمكنك سؤالي عن منهجية SEPA، أو نمط VCP، أو معايير Trend Template، أو أي استفسارات أخرى حول تحليل الأسهم والتداول.');
        
        // إضافة مستمع حدث لنموذج المحادثة
        chatForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const message = chatInput.value.trim();
            if (message) {
                // إضافة رسالة المستخدم إلى المحادثة
                addUserMessage(message);
                
                // مسح حقل الإدخال
                chatInput.value = '';
                
                // إرسال الرسالة إلى روبوت المحادثة
                sendMessageToChatbot(message);
            }
        });
        
        // إضافة مستمعات أحداث للأسئلة المقترحة
        const suggestedQuestions = document.querySelectorAll('.suggested-question');
        suggestedQuestions.forEach(button => {
            button.addEventListener('click', function() {
                chatInput.value = this.textContent;
                chatForm.dispatchEvent(new Event('submit'));
            });
        });
    }
    
    // إرسال رسالة إلى روبوت المحادثة
    async function sendMessageToChatbot(message) {
        try {
            // عرض مؤشر الكتابة
            showTypingIndicator();
            
            // إرسال الرسالة إلى روبوت المحادثة
            const response = await SEBA_API.Chatbot.sendMessage(message);
            
            // إخفاء مؤشر الكتابة
            hideTypingIndicator();
            
            // إضافة رد روبوت المحادثة إلى المحادثة
            addBotMessage(response.message);
            
            // إضافة أسئلة متابعة مقترحة إذا كانت موجودة
            if (response.suggestedFollowUp && response.suggestedFollowUp.length > 0) {
                addSuggestedFollowUp(response.suggestedFollowUp);
            }
        } catch (error) {
            // إخفاء مؤشر الكتابة
            hideTypingIndicator();
            
            // إضافة رسالة خطأ
            addBotMessage('عذراً، حدث خطأ أثناء معالجة رسالتك. يرجى المحاولة مرة أخرى.');
            
            console.error('خطأ في إرسال رسالة إلى روبوت المحادثة:', error);
        }
    }
    
    // إضافة رسالة المستخدم إلى المحادثة
    function addUserMessage(message) {
        const messageElement = document.createElement('div');
        messageElement.className = 'chat-message user-message';
        messageElement.innerHTML = `
            <div class="message-content">
                <p>${formatMessage(message)}</p>
                <span class="message-time">${formatTime(new Date())}</span>
            </div>
        `;
        
        chatMessages.appendChild(messageElement);
        
        // التمرير إلى أسفل المحادثة
        scrollToBottom();
    }
    
    // إضافة رسالة روبوت المحادثة إلى المحادثة
    function addBotMessage(message) {
        const messageElement = document.createElement('div');
        messageElement.className = 'chat-message bot-message';
        messageElement.innerHTML = `
            <div class="message-avatar">
                <i class="fas fa-robot"></i>
            </div>
            <div class="message-content">
                <p>${formatMessage(message)}</p>
                <span class="message-time">${formatTime(new Date())}</span>
            </div>
        `;
        
        chatMessages.appendChild(messageElement);
        
        // التمرير إلى أسفل المحادثة
        scrollToBottom();
    }
    
    // إضافة أسئلة متابعة مقترحة
    function addSuggestedFollowUp(suggestions) {
        const suggestionsElement = document.createElement('div');
        suggestionsElement.className = 'suggested-follow-up';
        
        let html = '<div class="suggested-follow-up-label">أسئلة متابعة مقترحة:</div>';
        html += '<div class="suggested-follow-up-buttons">';
        
        suggestions.forEach(suggestion => {
            html += `<button class="btn btn-sm btn-outline-primary suggested-follow-up-button">${suggestion}</button>`;
        });
        
        html += '</div>';
        
        suggestionsElement.innerHTML = html;
        chatMessages.appendChild(suggestionsElement);
        
        // إضافة مستمعات أحداث للأزرار
        const buttons = suggestionsElement.querySelectorAll('.suggested-follow-up-button');
        buttons.forEach(button => {
            button.addEventListener('click', function() {
                chatInput.value = this.textContent;
                chatForm.dispatchEvent(new Event('submit'));
            });
        });
        
        // التمرير إلى أسفل المحادثة
        scrollToBottom();
    }
    
    // عرض مؤشر الكتابة
    function showTypingIndicator() {
        const typingIndicator = document.createElement('div');
        typingIndicator.className = 'chat-message bot-message typing-indicator-container';
        typingIndicator.id = 'typingIndicator';
        typingIndicator.innerHTML = `
            <div class="message-avatar">
                <i class="fas fa-robot"></i>
            </div>
            <div class="message-content typing-indicator">
                <span></span>
                <span></span>
                <span></span>
            </div>
        `;
        
        chatMessages.appendChild(typingIndicator);
        
        // التمرير إلى أسفل المحادثة
        scrollToBottom();
    }
    
    // إخفاء مؤشر الكتابة
    function hideTypingIndicator() {
        const typingIndicator = document.getElementById('typingIndicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }
    
    // تنسيق الرسالة (تحويل الروابط إلى روابط قابلة للنقر، إلخ)
    function formatMessage(message) {
        // تحويل الروابط إلى روابط قابلة للنقر
        message = message.replace(
            /(https?:\/\/[^\s]+)/g,
            '<a href="$1" target="_blank" rel="noopener noreferrer">$1</a>'
        );
        
        // تحويل رموز الأسهم إلى روابط
        message = message.replace(
            /\b([A-Z]{1,5})\b/g,
            '<a href="analysis.html?symbol=$1" class="stock-symbol">$1</a>'
        );
        
        // تحويل السطور الجديدة إلى عناصر <br>
        message = message.replace(/\n/g, '<br>');
        
        return message;
    }
    
    // تنسيق الوقت
    function formatTime(date) {
        const hours = date.getHours().toString().padStart(2, '0');
        const minutes = date.getMinutes().toString().padStart(2, '0');
        return `${hours}:${minutes}`;
    }
    
    // التمرير إلى أسفل المحادثة
    function scrollToBottom() {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    // مسح سياق المحادثة
    window.clearChatContext = async function() {
        try {
            await SEBA_API.Chatbot.clearContext();
            
            // مسح المحادثة
            chatMessages.innerHTML = '';
            
            // إضافة رسالة ترحيبية جديدة
            addBotMessage('تم مسح سياق المحادثة. كيف يمكنني مساعدتك اليوم؟');
        } catch (error) {
            console.error('خطأ في مسح سياق المحادثة:', error);
            addBotMessage('عذراً، حدث خطأ أثناء مسح سياق المحادثة. يرجى المحاولة مرة أخرى.');
        }
    };
});
