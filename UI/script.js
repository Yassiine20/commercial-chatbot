// ==================== STATE MANAGEMENT ====================
let chatHistory = [];
let currentChatId = null;
let isTyping = false;
let sessionId = localStorage.getItem('chatbot_session_id') || null;

// ==================== DOM ELEMENTS ====================
const elements = {
    // Sidebar
    newChatBtn: document.getElementById('newChatBtn'),
    historyList: document.getElementById('historyList'),
    clearHistoryBtn: document.getElementById('clearHistoryBtn'),

    // Header
    refreshBtn: document.getElementById('refreshBtn'),
    downloadBtn: document.getElementById('downloadBtn'),

    // Chat
    chatContainer: document.getElementById('chatContainer'),
    welcomeScreen: document.getElementById('welcomeScreen'),
    messages: document.getElementById('messages'),
    messageInput: document.getElementById('messageInput'),
    sendBtn: document.getElementById('sendBtn'),
    attachBtn: document.getElementById('attachBtn'),

    // Quick Actions
    quickActionBtns: document.querySelectorAll('.quick-action-btn')
};

// ==================== INITIALIZATION ====================
function init() {
    loadChatHistory();
    attachEventListeners();

    // Load saved theme preference
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'light') {
        // Future: implement light mode
    }
}

// ==================== EVENT LISTENERS ====================
function attachEventListeners() {
    // Send message
    elements.sendBtn.addEventListener('click', handleSendMessage);
    elements.messageInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSendMessage();
        }
    });

    // Quick actions
    elements.quickActionBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const action = btn.getAttribute('data-action');
            handleQuickAction(action);
        });
    });

    // New chat
    elements.newChatBtn.addEventListener('click', startNewChat);

    // Clear history
    elements.clearHistoryBtn.addEventListener('click', clearAllHistory);

    // Refresh
    elements.refreshBtn.addEventListener('click', refreshChat);

    // Download chat
    elements.downloadBtn.addEventListener('click', downloadChat);

    // Attach file (placeholder)
    elements.attachBtn.addEventListener('click', () => {
        alert('File attachment feature coming soon!');
    });
}

// ==================== CHAT FUNCTIONS ====================
function handleSendMessage() {
    const message = elements.messageInput.value.trim();
    if (!message || isTyping) return;

    // Hide welcome screen if visible
    if (!elements.welcomeScreen.classList.contains('hidden')) {
        elements.welcomeScreen.classList.add('hidden');
    }

    // Add user message
    addMessage(message, 'user');
    elements.messageInput.value = '';

    // Save to history
    saveChatMessage(message, 'user');

    // Simulate bot response
    simulateBotResponse(message);
}

function handleQuickAction(action) {
    // Hide welcome screen
    elements.welcomeScreen.classList.add('hidden');

    // Add user message
    addMessage(action, 'user');

    // Save to history
    saveChatMessage(action, 'user');

    // Simulate bot response
    simulateBotResponse(action);
}

function addMessage(text, sender) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}`;

    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = sender === 'user' ? 'U' : 'CB';

    const content = document.createElement('div');
    content.className = 'message-content';
    content.textContent = text;

    messageDiv.appendChild(avatar);
    messageDiv.appendChild(content);

    elements.messages.appendChild(messageDiv);
    scrollToBottom();

    return messageDiv;
}

function showTypingIndicator() {
    const typingDiv = document.createElement('div');
    typingDiv.className = 'message bot';
    typingDiv.id = 'typing-indicator';

    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = 'CB';

    const content = document.createElement('div');
    content.className = 'message-content';

    const indicator = document.createElement('div');
    indicator.className = 'typing-indicator';
    indicator.innerHTML = '<div class="typing-dot"></div><div class="typing-dot"></div><div class="typing-dot"></div>';

    content.appendChild(indicator);
    typingDiv.appendChild(avatar);
    typingDiv.appendChild(content);

    elements.messages.appendChild(typingDiv);
    scrollToBottom();
}

function removeTypingIndicator() {
    const indicator = document.getElementById('typing-indicator');
    if (indicator) {
        indicator.remove();
    }
}

async function simulateBotResponse(userMessage) {
    isTyping = true;
    showTypingIndicator();

    try {
        // Call the Flask API with session ID for conversation context
        const response = await fetch('http://localhost:5000/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            credentials: 'include',
            body: JSON.stringify({ 
                message: userMessage,
                session_id: sessionId 
            })
        });

        const data = await response.json();
        
        // Store session ID for maintaining conversation history
        if (data.session_id) {
            sessionId = data.session_id;
            localStorage.setItem('chatbot_session_id', sessionId);
        }
        
        removeTypingIndicator();
        
        if (data.error) {
            addMessage('Sorry, there was an error processing your request.', 'bot');
        } else {
            // Add bot response
            addMessage(data.response, 'bot');
            saveChatMessage(data.response, 'bot');
            
            // Display products if any
            if (data.products && data.products.length > 0) {
                displayProducts(data.products);
            }
            
            // Log conversation context info
            if (data.metadata && data.metadata.conversation_turns) {
                console.log(`Conversation turns: ${data.metadata.conversation_turns}`);
            }
        }
        
    } catch (error) {
        console.error('Error:', error);
        removeTypingIndicator();
        addMessage('Sorry, I\'m having trouble connecting to the server. Please try again.', 'bot');
    }
    
    isTyping = false;
}

function generateBotResponse(userMessage) {
    const lowerMessage = userMessage.toLowerCase();

    // Simple response logic (you can replace this with API calls)
    if (lowerMessage.includes('new arrivals') || lowerMessage.includes('new arrival')) {
        return "Great! We have some amazing new arrivals this week. We've just added beautiful summer dresses, trendy denim jackets, and elegant evening wear. Would you like to see a specific category?";
    } else if (lowerMessage.includes('sales') || lowerMessage.includes('discount')) {
        return "We're currently running a fantastic sale! Get up to 50% off on selected items including winter coats, boots, and accessories. The sale ends this Sunday. Would you like me to show you the sale items?";
    } else if (lowerMessage.includes('dress')) {
        return "I'd love to help you find the perfect dress! What's the occasion? Are you looking for something casual, formal, or perhaps a cocktail dress? Also, do you have a preferred color or style in mind?";
    } else if (lowerMessage.includes('track') || lowerMessage.includes('order')) {
        return "I can help you track your order! Please provide your order number, and I'll get you the latest shipping information right away.";
    } else if (lowerMessage.includes('size') || lowerMessage.includes('sizing')) {
        return "I can help you with sizing! Our size chart is available for all products. Generally, we offer sizes XS to XXL. Would you like me to guide you through measuring yourself for the perfect fit?";
    } else if (lowerMessage.includes('return') || lowerMessage.includes('exchange')) {
        return "We offer hassle-free returns within 30 days of purchase. Items must be unworn with tags attached. Would you like to initiate a return or exchange?";
    } else if (lowerMessage.includes('hello') || lowerMessage.includes('hi') || lowerMessage.includes('hey')) {
        return "Hello! Welcome to ChicBot, your personal fashion assistant. I'm here to help you find the perfect outfit, track your orders, or answer any questions about our products. How can I assist you today?";
    } else {
        return "Thank you for your message! I'm here to help you with finding products, checking order status, size recommendations, and answering questions about our clothing collection. How can I assist you today?";
    }
}

function scrollToBottom() {
    elements.chatContainer.scrollTop = elements.chatContainer.scrollHeight;
}

function displayProducts(products) {
    const productContainer = document.createElement('div');
    productContainer.className = 'product-list';
    productContainer.style.cssText = 'display: flex; gap: 15px; flex-wrap: wrap; margin: 10px 0; padding: 10px;';
    
    products.forEach(product => {
        const productCard = document.createElement('div');
        productCard.className = 'product-card';
        productCard.style.cssText = 'border: 1px solid #e5e7eb; border-radius: 8px; overflow: hidden; flex: 1; min-width: 200px; max-width: 250px; background: #ffffff; box-shadow: 0 1px 3px rgba(0,0,0,0.1); transition: transform 0.2s;';
        
        // Add hover effect
        productCard.onmouseenter = () => productCard.style.transform = 'translateY(-4px)';
        productCard.onmouseleave = () => productCard.style.transform = 'translateY(0)';
        
        // Get first image if available
        const imageUrl = product.images && product.images.length > 0 ? product.images[0] : '';
        
        productCard.innerHTML = `
            ${imageUrl ? `
                <div style="width: 100%; height: 200px; overflow: hidden; background: #f3f4f6;">
                    <img src="${imageUrl}" 
                         alt="${product.name}" 
                         style="width: 100%; height: 100%; object-fit: cover;"
                         onerror="this.style.display='none'; this.parentElement.innerHTML='<div style=\\'display:flex;align-items:center;justify-content:center;height:100%;color:#9ca3af;\\'>No Image</div>'">
                </div>
            ` : ''}
            <div class="product-info" style="padding: 15px;">
                <h4 style="font-size: 14px; margin: 0 0 8px 0; color: #111827; font-weight: 600;">${product.name}</h4>
                <p style="font-size: 12px; color: #6b7280; margin: 4px 0;">
                    <span style="display: inline-block; width: 12px; height: 12px; border-radius: 50%; background: ${getColorCode(product.color)}; margin-right: 6px; vertical-align: middle;"></span>
                    ${product.color}
                </p>
                <p style="font-size: 18px; font-weight: 700; color: #059669; margin: 12px 0 8px 0;">£${product.price}</p>
                <a href="${product.url}" target="_blank" 
                   style="display: inline-block; font-size: 13px; color: #ffffff; background: #2563eb; padding: 8px 16px; border-radius: 6px; text-decoration: none; font-weight: 500; transition: background 0.2s;"
                   onmouseover="this.style.background='#1d4ed8'"
                   onmouseout="this.style.background='#2563eb'">
                    View Product →
                </a>
            </div>
        `;
        productContainer.appendChild(productCard);
    });
    
    elements.messages.appendChild(productContainer);
    scrollToBottom();
}

// Helper function to get color code approximation
function getColorCode(colorName) {
    const colorMap = {
        'black': '#000000',
        'white': '#ffffff',
        'red': '#ef4444',
        'blue': '#3b82f6',
        'green': '#10b981',
        'yellow': '#fbbf24',
        'pink': '#ec4899',
        'purple': '#a855f7',
        'brown': '#92400e',
        'grey': '#6b7280',
        'gray': '#6b7280',
        'orange': '#f97316',
        'beige': '#d4c5b9',
        'navy': '#1e3a8a'
    };
    
    const lowerColor = colorName.toLowerCase();
    for (const [key, value] of Object.entries(colorMap)) {
        if (lowerColor.includes(key)) {
            return value;
        }
    }
    return '#9ca3af'; // Default gray
}

// ==================== CHAT HISTORY ====================
function saveChatMessage(message, sender) {
    if (!currentChatId) {
        currentChatId = Date.now().toString();
        const chatTitle = message.substring(0, 30) + (message.length > 30 ? '...' : '');
        addChatToHistory(currentChatId, chatTitle);
    }

    const chat = chatHistory.find(c => c.id === currentChatId);
    if (chat) {
        chat.messages.push({ text: message, sender, timestamp: Date.now() });
        localStorage.setItem('chatHistory', JSON.stringify(chatHistory));
    }
}

function loadChatHistory() {
    const saved = localStorage.getItem('chatHistory');
    if (saved) {
        chatHistory = JSON.parse(saved);
        renderChatHistory();
    }
}

function addChatToHistory(id, title) {
    chatHistory.unshift({ id, title, messages: [] });
    localStorage.setItem('chatHistory', JSON.stringify(chatHistory));
    renderChatHistory();
}

function renderChatHistory() {
    elements.historyList.innerHTML = '';

    chatHistory.forEach((chat, index) => {
        const item = document.createElement('div');
        item.className = 'history-item' + (chat.id === currentChatId ? ' active' : '');

        item.innerHTML = `
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M2 3H14M2 8H14M2 13H14" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
            </svg>
            <span>${chat.title}</span>
            <button class="more-btn">⋯</button>
        `;

        item.addEventListener('click', (e) => {
            if (!e.target.classList.contains('more-btn')) {
                loadChat(chat.id);
            }
        });

        elements.historyList.appendChild(item);
    });
}

function loadChat(chatId) {
    const chat = chatHistory.find(c => c.id === chatId);
    if (!chat) return;

    currentChatId = chatId;
    elements.messages.innerHTML = '';
    elements.welcomeScreen.classList.add('hidden');

    chat.messages.forEach(msg => {
        addMessage(msg.text, msg.sender);
    });

    renderChatHistory();
}

async function startNewChat() {
    currentChatId = null;
    elements.messages.innerHTML = '';
    elements.welcomeScreen.classList.remove('hidden');

    // Reset conversation history on backend
    await resetConversationHistory();

    // Remove active state from all history items
    document.querySelectorAll('.history-item').forEach(item => {
        item.classList.remove('active');
    });
}

async function resetConversationHistory() {
    try {
        await fetch('http://localhost:5000/api/reset', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            credentials: 'include',
            body: JSON.stringify({ 
                session_id: sessionId 
            })
        });
        console.log('Conversation history reset on backend');
    } catch (error) {
        console.error('Error resetting conversation:', error);
    }
}

function clearAllHistory() {
    if (confirm('Are you sure you want to clear all chat history? This cannot be undone.')) {
        chatHistory = [];
        localStorage.removeItem('chatHistory');
        resetConversationHistory();
        startNewChat();
        renderChatHistory();
    }
}

// ==================== UTILITY FUNCTIONS ====================
function refreshChat() {
    if (currentChatId) {
        loadChat(currentChatId);
    } else {
        startNewChat();
    }
}

function downloadChat() {
    if (!currentChatId) {
        alert('No active chat to download');
        return;
    }

    const chat = chatHistory.find(c => c.id === currentChatId);
    if (!chat) return;

    let content = `ChicBot Conversation - ${chat.title}\n`;
    content += `Date: ${new Date().toLocaleString()}\n`;
    content += '='.repeat(50) + '\n\n';

    chat.messages.forEach(msg => {
        const sender = msg.sender === 'user' ? 'You' : 'ChicBot';
        content += `${sender}: ${msg.text}\n\n`;
    });

    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `chicbot-chat-${currentChatId}.txt`;
    a.click();
    URL.revokeObjectURL(url);
}

// ==================== INITIALIZE APP ====================
document.addEventListener('DOMContentLoaded', init);
