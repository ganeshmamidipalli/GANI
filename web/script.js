// GANI Chatbot JavaScript
class GaniChat {
    constructor() {
        this.apiUrl = 'http://localhost:8000';
        this.messageInput = document.getElementById('messageInput');
        this.sendButton = document.getElementById('sendButton');
        this.chatMessages = document.getElementById('chatMessages');
        this.typingIndicator = document.getElementById('typingIndicator');
        
        this.setupEventListeners();
        this.loadChatHistory();
    }
    
    setupEventListeners() {
        this.sendButton.addEventListener('click', () => this.sendMessage());
        this.messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.sendMessage();
            }
        });
        
        // Focus input on load
        this.messageInput.focus();
    }
    
    async sendMessage() {
        const message = this.messageInput.value.trim();
        if (!message) return;
        
        // Add user message to chat
        this.addMessage(message, 'user');
        
        // Clear input and disable send button
        this.messageInput.value = '';
        this.setInputState(false);
        
        // Show typing indicator
        this.showTypingIndicator();
        
        try {
            // Send to API
            const response = await this.callChatAPI(message);
            
            // Hide typing indicator
            this.hideTypingIndicator();
            
            // Add bot response
            this.addBotMessage(response);
            
        } catch (error) {
            console.error('Error sending message:', error);
            this.hideTypingIndicator();
            this.addErrorMessage('Sorry, I encountered an error. Please try again.');
        }
        
        // Re-enable input
        this.setInputState(true);
        this.messageInput.focus();
    }
    
    async callChatAPI(question) {
        const response = await fetch(`${this.apiUrl}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ question })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    }
    
    addMessage(text, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}`;
        
        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.textContent = sender === 'user' ? 'U' : 'G';
        
        const content = document.createElement('div');
        content.className = 'message-content';
        content.textContent = text;
        
        messageDiv.appendChild(avatar);
        messageDiv.appendChild(content);
        
        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
        
        // Store in local storage
        this.saveMessage(text, sender);
    }
    
    addBotMessage(response) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message bot';
        
        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.textContent = 'G';
        
        const content = document.createElement('div');
        content.className = 'message-content';
        
        // Add the main answer (prefer short answer, fallback to expanded)
        const answerText = response.answer_short || response.answer_expanded;
        content.innerHTML = this.formatAnswer(answerText);
        
        // Add intent and confidence badges
        const badgesDiv = document.createElement('div');
        badgesDiv.className = 'response-badges';
        
        if (response.intent) {
            const intentBadge = document.createElement('div');
            intentBadge.className = 'intent-badge';
            intentBadge.textContent = `Intent: ${response.intent.toUpperCase()}`;
            badgesDiv.appendChild(intentBadge);
        }
        
        if (response.confidence !== undefined) {
            const confidenceBadge = document.createElement('div');
            confidenceBadge.className = 'confidence-badge';
            confidenceBadge.textContent = `Confidence: ${(response.confidence * 100).toFixed(0)}%`;
            badgesDiv.appendChild(confidenceBadge);
        }
        
        content.appendChild(badgesDiv);
        
        // Add citations if available
        if (response.citations && response.citations.length > 0) {
            const citationsDiv = document.createElement('div');
            citationsDiv.className = 'citations';
            citationsDiv.innerHTML = '<strong>Sources:</strong>';
            
            response.citations.forEach(citation => {
                const citationDiv = document.createElement('div');
                citationDiv.className = 'citation';
                citationDiv.innerHTML = `
                    <a href="${citation.url}" target="_blank" rel="noopener noreferrer">
                        ${citation.url}
                    </a>
                    ${citation.section ? ` - ${citation.section}` : ''}
                `;
                citationsDiv.appendChild(citationDiv);
            });
            
            content.appendChild(citationsDiv);
        }
        
        messageDiv.appendChild(avatar);
        messageDiv.appendChild(content);
        
        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
        
        // Store in local storage
        this.saveMessage(response.answer_expanded || response.answer_short, 'bot');
    }
    
    formatAnswer(text) {
        // Convert [1], [2], etc. citations to clickable links
        return text.replace(/\[(\d+)\]/g, '<span class="citation-link">[$1]</span>');
    }
    
    addErrorMessage(text) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.textContent = text;
        
        this.chatMessages.appendChild(errorDiv);
        this.scrollToBottom();
    }
    
    showTypingIndicator() {
        this.typingIndicator.classList.add('show');
        this.scrollToBottom();
    }
    
    hideTypingIndicator() {
        this.typingIndicator.classList.remove('show');
    }
    
    setInputState(enabled) {
        this.messageInput.disabled = !enabled;
        this.sendButton.disabled = !enabled;
        
        if (enabled) {
            this.sendButton.classList.remove('loading');
        } else {
            this.sendButton.classList.add('loading');
        }
    }
    
    scrollToBottom() {
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }
    
    // Local storage for chat history
    saveMessage(text, sender) {
        const messages = this.getChatHistory();
        messages.push({
            text,
            sender,
            timestamp: new Date().toISOString()
        });
        
        // Keep only last 50 messages
        if (messages.length > 50) {
            messages.splice(0, messages.length - 50);
        }
        
        localStorage.setItem('gani_chat_history', JSON.stringify(messages));
    }
    
    getChatHistory() {
        try {
            const history = localStorage.getItem('gani_chat_history');
            return history ? JSON.parse(history) : [];
        } catch (error) {
            console.error('Error loading chat history:', error);
            return [];
        }
    }
    
    loadChatHistory() {
        const messages = this.getChatHistory();
        
        // Clear existing messages (except welcome message)
        const existingMessages = this.chatMessages.querySelectorAll('.message');
        if (existingMessages.length > 1) {
            for (let i = 1; i < existingMessages.length; i++) {
                existingMessages[i].remove();
            }
        }
        
        // Load messages from history
        messages.forEach(msg => {
            if (msg.sender === 'user') {
                this.addMessage(msg.text, 'user');
            } else {
                // For bot messages, we need to reconstruct the response structure
                const mockResponse = {
                    answer_short: msg.text,
                    answer_expanded: msg.text,
                    citations: [],
                    confidence: 0.8
                };
                this.addBotMessage(mockResponse);
            }
        });
    }
    
    clearChatHistory() {
        localStorage.removeItem('gani_chat_history');
        location.reload();
    }
}

// Initialize chat when page loads
document.addEventListener('DOMContentLoaded', () => {
    window.ganiChat = new GaniChat();
});

// Global functions for HTML onclick handlers
function sendMessage() {
    if (window.ganiChat) {
        window.ganiChat.sendMessage();
    }
}

function handleKeyPress(event) {
    if (event.key === 'Enter') {
        sendMessage();
    }
}

// Add some utility functions
function testAPI() {
    fetch('http://localhost:8000/health')
        .then(response => response.json())
        .then(data => {
            console.log('API Health Check:', data);
            alert('API is healthy! Check console for details.');
        })
        .catch(error => {
            console.error('API Health Check Failed:', error);
            alert('API health check failed. Check console for details.');
        });
}

// Add keyboard shortcuts
document.addEventListener('keydown', (e) => {
    // Ctrl/Cmd + K to focus input
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        document.getElementById('messageInput').focus();
    }
    
    // Ctrl/Cmd + L to clear chat
    if ((e.ctrlKey || e.metaKey) && e.key === 'l') {
        e.preventDefault();
        if (confirm('Clear chat history?')) {
            window.ganiChat.clearChatHistory();
        }
    }
});
