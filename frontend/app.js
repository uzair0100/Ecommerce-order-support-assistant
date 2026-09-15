/**
 * GadgetMart Support Assistant - Frontend Client
 * WebSocket-based chat interface with streaming responses
 */

// Configuration
const WS_URL = 'ws://localhost:8000/ws/chat';
const MAX_CONTENT_LENGTH = 2000;
const RECONNECT_DELAY = 3000;

// State
let ws = null;
let sessionId = null;
let currentTurnId = null;
let isConnected = false;
let isProcessing = false;
let reconnectAttempts = 0;
let currentMessageElement = null;

// DOM Elements
const chatContainer = document.getElementById('chatContainer');
const messageInput = document.getElementById('messageInput');
const sendBtn = document.getElementById('sendBtn');
const resetBtn = document.getElementById('resetBtn');
const charCounter = document.getElementById('charCounter');
const statusIndicator = document.getElementById('statusIndicator');
const statusText = document.getElementById('statusText');
const sampleQuestions = document.getElementById('sampleQuestions');

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    initializeWebSocket();
    setupEventListeners();
    updateCharCounter();
});

// WebSocket Connection Management
function initializeWebSocket() {
    try {
        ws = new WebSocket(WS_URL);
        
        ws.onopen = handleWebSocketOpen;
        ws.onmessage = handleWebSocketMessage;
        ws.onerror = handleWebSocketError;
        ws.onclose = handleWebSocketClose;
    } catch (error) {
        console.error('WebSocket initialization failed:', error);
        updateStatus('disconnected', 'Connection failed');
    }
}

function handleWebSocketOpen() {
    console.log('WebSocket connected');
    isConnected = true;
    reconnectAttempts = 0;
    updateStatus('connected', 'Connected');
    enableInput();
}

function handleWebSocketMessage(event) {
    try {
        const message = JSON.parse(event.data);
        console.log('Received:', message);
        
        switch (message.type) {
            case 'start':
                handleStartEvent(message);
                break;
            case 'chunk':
                handleChunkEvent(message);
                break;
            case 'done':
                handleDoneEvent(message);
                break;
            case 'error':
                handleErrorEvent(message);
                break;
            case 'reset':
                handleResetAck(message);
                break;
            default:
                console.warn('Unknown message type:', message.type);
        }
    } catch (error) {
        console.error('Failed to parse WebSocket message:', error);
    }
}

function handleWebSocketError(error) {
    console.error('WebSocket error:', error);
    updateStatus('disconnected', 'Connection error');
}

function handleWebSocketClose(event) {
    console.log('WebSocket closed:', event.code, event.reason);
    isConnected = false;
    updateStatus('disconnected', 'Disconnected');
    disableInput();
    
    // Attempt reconnection
    if (reconnectAttempts < 5) {
        reconnectAttempts++;
        console.log(`Reconnecting in ${RECONNECT_DELAY}ms (attempt ${reconnectAttempts})`);
        setTimeout(() => {
            updateStatus('connecting', 'Reconnecting...');
            initializeWebSocket();
        }, RECONNECT_DELAY);
    } else {
        updateStatus('disconnected', 'Connection lost. Refresh to retry.');
    }
}

// Message Handlers
function handleStartEvent(message) {
    sessionId = message.session_id;
    currentTurnId = message.turn_id;
    
    // Create typing indicator
    showTypingIndicator();
    
    // Prepare for streaming response
    currentMessageElement = null;
}

function handleChunkEvent(message) {
    const content = message.content || '';
    
    // Remove typing indicator on first chunk
    if (currentMessageElement === null) {
        removeTypingIndicator();
        currentMessageElement = createAssistantMessage('');
    }
    
    // Append chunk to current message
    appendToAssistantMessage(currentMessageElement, content);
}

function handleDoneEvent(message) {
    removeTypingIndicator();
    
    // Finalize message if it exists
    if (currentMessageElement) {
        finalizeMessage(currentMessageElement);
    }
    
    // Reset state
    currentTurnId = null;
    currentMessageElement = null;
    isProcessing = false;
    enableInput();
    
    console.log('Turn completed. Total tokens:', message.total_tokens);
}

function handleErrorEvent(message) {
    removeTypingIndicator();
    
    const errorMsg = message.message || 'An error occurred';
    const errorCode = message.code || 'UNKNOWN';
    
    displayErrorMessage(`Error (${errorCode}): ${errorMsg}`);
    
    // Reset state
    currentTurnId = null;
    currentMessageElement = null;
    isProcessing = false;
    enableInput();
    
    console.error('Server error:', message);
}

function handleResetAck(message) {
    sessionId = message.session_id;
    
    // Clear chat container except welcome message
    const welcomeMsg = chatContainer.querySelector('.welcome-message');
    chatContainer.innerHTML = '';
    if (welcomeMsg) {
        chatContainer.appendChild(welcomeMsg);
    } else {
        createWelcomeMessage();
    }
    
    // Show sample questions again
    sampleQuestions.classList.remove('hidden');
    
    isProcessing = false;
    enableInput();
    
    console.log('Session reset. New session ID:', sessionId);
}

// UI Update Functions
function updateStatus(status, text) {
    statusText.textContent = text;
    statusIndicator.className = 'status-indicator';
    
    if (status === 'connected') {
        statusIndicator.classList.add('connected');
    } else if (status === 'disconnected') {
        statusIndicator.classList.add('disconnected');
    }
}

function updateCharCounter() {
    const length = messageInput.value.length;
    charCounter.textContent = `${length}/${MAX_CONTENT_LENGTH}`;
    
    // Update color based on usage
    charCounter.classList.remove('warning', 'error');
    if (length >= MAX_CONTENT_LENGTH) {
        charCounter.classList.add('error');
    } else if (length >= MAX_CONTENT_LENGTH * 0.9) {
        charCounter.classList.add('warning');
    }
}

function enableInput() {
    messageInput.disabled = false;
    sendBtn.disabled = false;
    resetBtn.disabled = false;
}

function disableInput() {
    // Keep textarea enabled so user can type while waiting
    // Only disable send/reset buttons
    sendBtn.disabled = true;
    resetBtn.disabled = true;
}

// Message Creation Functions
function createWelcomeMessage() {
    const welcomeDiv = document.createElement('div');
    welcomeDiv.className = 'welcome-message';
    welcomeDiv.innerHTML = `
        <h2>👋 Welcome to GadgetMart Support!</h2>
        <p>I'm here to help you with orders, returns, product information, and delivery questions.</p>
        <p class="welcome-note">Ask me anything about your GadgetMart shopping experience.</p>
    `;
    chatContainer.appendChild(welcomeDiv);
}

function createUserMessage(content) {
    // Hide welcome message on first user message
    const welcomeMsg = chatContainer.querySelector('.welcome-message');
    if (welcomeMsg) {
        welcomeMsg.remove();
    }
    
    // Hide sample questions after first message
    sampleQuestions.classList.add('hidden');
    
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message user';
    
    const timestamp = formatTimestamp(new Date());
    
    messageDiv.innerHTML = `
        <div class="message-header">
            <span class="message-role">You</span>
            <span class="message-timestamp">${timestamp}</span>
        </div>
        <div class="message-content">${escapeHtml(content)}</div>
    `;
    
    chatContainer.appendChild(messageDiv);
    scrollToBottom();
    
    return messageDiv;
}

function createAssistantMessage(content) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message assistant';
    
    const timestamp = formatTimestamp(new Date());
    
    messageDiv.innerHTML = `
        <div class="message-header">
            <span class="message-role">Assistant</span>
            <span class="message-timestamp">${timestamp}</span>
        </div>
        <div class="message-content">${escapeHtml(content)}</div>
    `;
    
    chatContainer.appendChild(messageDiv);
    scrollToBottom();
    
    return messageDiv;
}

function appendToAssistantMessage(messageElement, content) {
    const contentDiv = messageElement.querySelector('.message-content');
    contentDiv.textContent += content;
    scrollToBottom();
}

function finalizeMessage(messageElement) {
    // Add copy button
    const actionsDiv = document.createElement('div');
    actionsDiv.className = 'message-actions';
    
    const copyBtn = document.createElement('button');
    copyBtn.className = 'copy-btn';
    copyBtn.textContent = '📋 Copy';
    copyBtn.onclick = () => copyMessageContent(copyBtn, messageElement);
    
    actionsDiv.appendChild(copyBtn);
    messageElement.appendChild(actionsDiv);
}

function showTypingIndicator() {
    // Remove existing typing indicator if any
    removeTypingIndicator();
    
    const typingDiv = document.createElement('div');
    typingDiv.className = 'typing-indicator';
    typingDiv.id = 'typingIndicator';
    
    typingDiv.innerHTML = `
        <span>Assistant is typing</span>
        <div class="typing-dots">
            <span class="typing-dot"></span>
            <span class="typing-dot"></span>
            <span class="typing-dot"></span>
        </div>
    `;
    
    chatContainer.appendChild(typingDiv);
    scrollToBottom();
}

function removeTypingIndicator() {
    const typingIndicator = document.getElementById('typingIndicator');
    if (typingIndicator) {
        typingIndicator.remove();
    }
}

function displayErrorMessage(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.textContent = message;
    
    chatContainer.appendChild(errorDiv);
    scrollToBottom();
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        errorDiv.remove();
    }, 5000);
}

// Event Handlers
function setupEventListeners() {
    // Send button
    sendBtn.addEventListener('click', sendMessage);
    
    // Reset button
    resetBtn.addEventListener('click', resetConversation);
    
    // Input field
    messageInput.addEventListener('input', updateCharCounter);
    messageInput.addEventListener('keydown', (e) => {
        // Send on Enter (without Shift)
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
    
    // Auto-resize textarea
    messageInput.addEventListener('input', () => {
        messageInput.style.height = 'auto';
        messageInput.style.height = messageInput.scrollHeight + 'px';
    });
    
    // Sample question buttons
    document.querySelectorAll('.sample-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const question = btn.getAttribute('data-question');
            messageInput.value = question;
            updateCharCounter();
            sendMessage();
        });
    });
}

function sendMessage() {
    if (!isConnected || isProcessing) {
        console.warn('Cannot send message: not connected or already processing');
        return;
    }
    
    const content = messageInput.value.trim();
    
    // Validation
    if (!content) {
        return;
    }
    
    if (content.length > MAX_CONTENT_LENGTH) {
        displayErrorMessage(`Message too long. Maximum ${MAX_CONTENT_LENGTH} characters.`);
        return;
    }
    
    // Create user message in UI
    createUserMessage(content);
    
    // Send to server
    const message = {
        type: 'message',
        session_id: sessionId,
        content: content
    };
    
    try {
        ws.send(JSON.stringify(message));
        
        // Clear input and update state
        messageInput.value = '';
        messageInput.style.height = 'auto';
        updateCharCounter();
        
        isProcessing = true;
        disableInput();
        
    } catch (error) {
        console.error('Failed to send message:', error);
        displayErrorMessage('Failed to send message. Please try again.');
        isProcessing = false;
        enableInput();
    }
}

function resetConversation() {
    if (!isConnected) {
        console.warn('Cannot reset: not connected');
        return;
    }
    
    const message = {
        type: 'reset',
        session_id: sessionId
    };
    
    try {
        ws.send(JSON.stringify(message));
        isProcessing = true;
        disableInput();
    } catch (error) {
        console.error('Failed to reset conversation:', error);
        displayErrorMessage('Failed to reset conversation. Please try again.');
    }
}

function copyMessageContent(button, messageElement) {
    const contentDiv = messageElement.querySelector('.message-content');
    const text = contentDiv.textContent;
    
    navigator.clipboard.writeText(text).then(() => {
        // Visual feedback
        const originalText = button.textContent;
        button.textContent = '✓ Copied!';
        button.classList.add('copied');
        
        setTimeout(() => {
            button.textContent = originalText;
            button.classList.remove('copied');
        }, 2000);
    }).catch(error => {
        console.error('Failed to copy text:', error);
        displayErrorMessage('Failed to copy text to clipboard');
    });
}

// Utility Functions
function formatTimestamp(date) {
    const hours = date.getHours().toString().padStart(2, '0');
    const minutes = date.getMinutes().toString().padStart(2, '0');
    return `${hours}:${minutes}`;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function scrollToBottom() {
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

// Handle page visibility changes (pause/resume)
document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
        console.log('Page hidden');
    } else {
        console.log('Page visible');
        // Reconnect if disconnected while hidden
        if (!isConnected && reconnectAttempts < 5) {
            initializeWebSocket();
        }
    }
});

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.close();
    }
});
