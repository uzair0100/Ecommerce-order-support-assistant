# GadgetMart Support Assistant - Frontend

Professional black & cyan themed web interface for the GadgetMart conversational AI assistant.

## Features

### 🎨 Design
- **Professional Theme**: Black (#0a0e14) and cyan (#00d9ff) color scheme
- **Responsive Layout**: Works on desktop, tablet, and mobile (breakpoints at 768px and 480px)
- **High Contrast**: Easy-to-read text with strong visual hierarchy
- **Subtle Background**: Gradient accent without distractions

### 💬 Chat Interface
- **WebSocket Streaming**: Real-time message streaming from backend
- **Typing Indicator**: Animated dots while assistant generates response
- **Message Timestamps**: HH:MM format for each message
- **Copy Button**: Copy assistant messages to clipboard with visual feedback
- **Auto-scroll**: Chat automatically scrolls to latest message

### ⚡ User Experience
- **Sample Questions**: Quick-start buttons with common queries
- **Character Counter**: Live count with color indicators (0-1800: gray, 1800-2000: orange, 2000: red)
- **Input Validation**: 2000 character limit enforced
- **Auto-resize Textarea**: Expands as you type (max 150px height)
- **Keyboard Shortcuts**: 
  - `Enter`: Send message
  - `Shift + Enter`: New line
- **Session Reset**: Clear conversation and start fresh
- **Connection Status**: Visual indicator (green: connected, red: disconnected, pulsing: connecting)

### 🔧 Technical Features
- **Auto-reconnect**: 5 attempts with 3-second delay on connection loss
- **State Management**: Session ID, turn tracking, processing state
- **Error Handling**: User-friendly error messages with auto-dismiss
- **XSS Protection**: HTML escaping on all user/assistant content

## Quick Start

### Prerequisites
1. **Backend server must be running**:
   ```powershell
   python -m backend.main
   ```
   Server should be available at `http://localhost:8000`

2. **Ollama must be running** with `qwen2.5:1.5b-instruct` model

### Running the Frontend

**Option 1: Python HTTP Server (Recommended)**
```powershell
# From the project root
cd frontend
python -m http.server 8080
```

Then open: `http://localhost:8080`

**Option 2: Direct File Opening**
⚠️ **Not recommended** - WebSocket connections may be blocked by CORS when using `file://` protocol.

If you must use this method:
1. Open `frontend/index.html` directly in your browser
2. You may need to disable CORS restrictions (not recommended for security)

## Testing Guide

### 1. Basic Functionality Test
1. Open the frontend in Chrome
2. Verify status bar shows "Connected" (green indicator)
3. Try a sample question: Click "📦 How do I track my order?"
4. Verify:
   - ✅ User message appears immediately
   - ✅ Typing indicator shows "Assistant is typing..."
   - ✅ Response streams in gradually (chunks appear as they arrive)
   - ✅ Copy button appears after response completes
   - ✅ Timestamp shows current time (HH:MM)

### 2. Input Validation Test
1. Type a long message (1900+ characters)
2. Verify character counter changes color:
   - Orange at 1800-1999 chars
   - Red at 2000 chars
3. Try to exceed 2000 chars - should be prevented by `maxlength` attribute

### 3. Streaming Test
1. Ask: "Tell me about all your products in detail"
2. Verify response appears gradually (not all at once)
3. Chat should auto-scroll as response grows

### 4. Reset Test
1. Have a conversation (2-3 messages)
2. Click "🔄 Reset" button
3. Verify:
   - ✅ Chat clears (welcome message returns)
   - ✅ Sample questions reappear
   - ✅ New session ID generated
   - ✅ Input is re-enabled

### 5. Copy Functionality Test
1. Get an assistant response
2. Click "📋 Copy" button
3. Verify:
   - ✅ Button text changes to "✓ Copied!"
   - ✅ Text is in clipboard (paste to verify)
   - ✅ Button reverts after 2 seconds

### 6. Mobile Responsive Test
**Using Chrome DevTools:**
1. Press `F12` to open DevTools
2. Click device toolbar icon (or `Ctrl+Shift+M`)
3. Test these viewports:
   - **Desktop**: 1920x1080 (full layout)
   - **Tablet**: 768x1024 (adjusted grid for sample questions)
   - **Mobile**: 375x667 (single column, stacked controls)
4. Verify:
   - ✅ Text remains readable
   - ✅ Buttons are touch-friendly (not too small)
   - ✅ No horizontal scrolling
   - ✅ Chat takes appropriate height

### 7. Edge Browser Test
1. Open frontend in Microsoft Edge
2. Repeat Basic Functionality Test
3. Verify everything works identically to Chrome

### 8. Error Handling Test
1. Stop the backend server (`Ctrl+C`)
2. Try to send a message
3. Verify:
   - ✅ Status changes to "Disconnected" (red)
   - ✅ Input is disabled
   - ✅ "Reconnecting..." status appears
4. Restart backend server
5. Verify frontend reconnects automatically

## File Structure

```
frontend/
├── index.html      # Main HTML structure
├── style.css       # Black/cyan theme + responsive styles
├── app.js          # WebSocket client + UI logic
└── README.md       # This file
```

## Configuration

### WebSocket URL
Default: `ws://localhost:8000/ws/chat`

To change, edit `app.js`:
```javascript
const WS_URL = 'ws://your-server:port/ws/chat';
```

### Character Limit
Default: 2000 characters

To change, edit both files:
- `app.js`: Update `MAX_CONTENT_LENGTH`
- `index.html`: Update `maxlength` attribute on textarea

### Reconnection Settings
Default: 5 attempts with 3-second delay

To change, edit `app.js`:
```javascript
const RECONNECT_DELAY = 3000;  // milliseconds
// In handleWebSocketClose: if (reconnectAttempts < 5)
```

## Troubleshooting

### "Disconnected" Status on Load
**Cause**: Backend not running or wrong URL  
**Fix**: 
1. Verify backend is running: `python -m backend.main`
2. Check console for errors (`F12` → Console tab)
3. Verify WebSocket URL is correct

### Messages Not Appearing
**Cause**: JavaScript error or WebSocket protocol mismatch  
**Fix**:
1. Open browser console (`F12`)
2. Look for red error messages
3. Verify backend API protocol matches frontend expectations

### CORS Errors
**Cause**: Backend not allowing frontend origin  
**Fix**: Backend `main.py` should include your frontend origin in CORS `allow_origins` list:
```python
allow_origins=[
    "http://localhost:8080",
    "http://127.0.0.1:8080",
]
```

### Copy Button Not Working
**Cause**: Browser security restrictions on clipboard API  
**Fix**: Must serve over HTTP (not file://). Use Python http.server as shown above.

### Sample Questions Not Hiding
**Cause**: JavaScript not executing  
**Fix**: 
1. Check browser console for errors
2. Verify `app.js` is loaded (check Network tab in DevTools)

## Browser Compatibility

**Fully Tested:**
- ✅ Chrome 100+ (Windows)
- ✅ Edge 100+ (Windows)

**Should Work (ES6+ required):**
- Firefox 90+
- Safari 14+
- Opera 85+

**Required Browser Features:**
- WebSocket API
- ES6+ JavaScript (arrow functions, const/let, async/await)
- Clipboard API (for copy button)
- CSS Grid & Flexbox

## Performance Notes

- **Memory Usage**: ~15-20MB for frontend alone
- **Network**: WebSocket messages are small (<1KB each typically)
- **CPU**: Minimal (UI updates on message receive only)
- **Streaming**: Chunks render immediately (no buffering delay)

## Accessibility

**Implemented:**
- Semantic HTML5 elements
- High contrast text (WCAG AA compliant for normal text)
- Keyboard navigation support
- Screen reader friendly structure

**Not Implemented (out of scope for Assignment 1):**
- ARIA labels for dynamic content
- Screen reader announcements for new messages
- Keyboard-only navigation optimization
- Focus management

## Next Steps (Phase VI)

Potential UX/persona polish enhancements:
- Custom avatar images for user/assistant
- Message reactions (thumbs up/down)
- Conversation export (JSON/PDF)
- Dark/light theme toggle
- Markdown rendering in assistant responses
- Message edit/delete functionality
- Multi-language support

## Credits

**Assignment**: NLP Assignment 1 - E-Commerce Order Support Chatbot  
**Model**: Qwen2.5 1.5B Instruct (local via Ollama)  
**Framework**: Vanilla HTML/CSS/JavaScript (no dependencies)  
**Theme**: Professional black & cyan GadgetMart branding  
