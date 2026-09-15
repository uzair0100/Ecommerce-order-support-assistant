# Phase IV Quick Start Guide

## Prerequisites

1. **Ollama installed and running**
2. **Python 3.11+**
3. **Dependencies installed**

---

## Installation

### 1. Install Dependencies

```powershell
cd "C:\Users\uzair\OneDrive\Desktop\NLP Assignment"
pip install -r backend/requirements.txt
```

This installs:
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `httpx` - Async HTTP client
- `websockets` - WebSocket library
- `requests` - Sync HTTP (Phase III compatibility)
- `pytest` - Testing framework

### 2. Verify Ollama is Running

```powershell
# Check if Ollama process is running
Get-Process -Name "ollama" -ErrorAction SilentlyContinue

# Or test connection
& "$env:LOCALAPPDATA\Programs\Ollama\ollama.exe" list
```

Should see `qwen2.5:1.5b-instruct` in the list.

---

## Running the Server

### Option 1: Using Python Module (Recommended)

```powershell
cd "C:\Users\uzair\OneDrive\Desktop\NLP Assignment"
python -m backend.main
```

### Option 2: Using Uvicorn Directly

```powershell
cd "C:\Users\uzair\OneDrive\Desktop\NLP Assignment"
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

**Server will start on:**
- http://localhost:8000
- WebSocket: ws://localhost:8000/ws/chat
- Health: http://localhost:8000/health
- API Docs: http://localhost:8000/docs

**You should see:**
```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     GadgetMart Assistant API starting...
INFO:     Model: qwen2.5:1.5b-instruct
INFO:     WebSocket endpoint: /ws/chat
INFO:     Health check endpoint: /health
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

---

## Testing

### 1. Test Health Endpoint (Quick Check)

Open browser or use curl:

```powershell
# Browser:
http://localhost:8000/health

# Or PowerShell:
Invoke-RestMethod -Uri "http://localhost:8000/health"
```

**Expected response:**
```json
{
  "status": "healthy",
  "server_healthy": true,
  "ollama_available": true,
  "model": "qwen2.5:1.5b-instruct",
  "active_sessions": 0
}
```

### 2. Test WebSocket with Test Client

**Open a NEW terminal** (keep server running in first terminal):

```powershell
cd "C:\Users\uzair\OneDrive\Desktop\NLP Assignment"
python backend/test_websocket_client.py
```

**This will:**
1. Connect to WebSocket
2. Send a product question
3. Stream the response
4. Send a follow-up question
5. Reset the session
6. Test validation

**Expected output:**
```
======================================================================
GadgetMart WebSocket Test Client
======================================================================

Connecting to ws://localhost:8000/ws/chat...
✅ Connected!

Test 1: Product question (streaming)
----------------------------------------------------------------------
...
[START] session_id: ae553ae2..., turn_id: 7c9e6679...
Assistant: The Wireless Bluetooth Headphones Pro are priced at £79.99...
[DONE] Tokens: 42
...
```

### 3. Run Automated Tests

```powershell
cd "C:\Users\uzair\OneDrive\Desktop\NLP Assignment"

# Run all Phase IV tests
pytest tests/test_websocket_api.py -v

# Run with live Ollama (slower but more thorough)
pytest tests/test_websocket_api.py --run-live -v
```

**Expected:** 11+ tests passing

---

## Troubleshooting

### Problem: "Connection refused"

**Cause:** Server not running

**Fix:**
```powershell
# Start server in separate terminal
python -m backend.main
```

### Problem: "Ollama not available" in health check

**Cause:** Ollama not running or not on port 11434

**Fix:**
```powershell
# Check if Ollama is running
Get-Process -Name "ollama"

# Check port
Test-NetConnection -ComputerName localhost -Port 11434
```

### Problem: "ModuleNotFoundError: No module named 'backend'"

**Cause:** Running from wrong directory or PYTHONPATH not set

**Fix:**
```powershell
# Make sure you're in project root
cd "C:\Users\uzair\OneDrive\Desktop\NLP Assignment"

# Or set PYTHONPATH
$env:PYTHONPATH = "C:\Users\uzair\OneDrive\Desktop\NLP Assignment"
python -m backend.main
```

### Problem: WebSocket test hangs at "Assistant:"

**Cause:** Model is loading (first request) or CPU is slow

**Solution:** Wait 10-30 seconds for first response. Subsequent responses will be faster.

### Problem: Import errors for httpx, fastapi, etc.

**Cause:** Dependencies not installed

**Fix:**
```powershell
pip install -r backend/requirements.txt
```

---

## Development Workflow

**Terminal 1 (Server):**
```powershell
cd "C:\Users\uzair\OneDrive\Desktop\NLP Assignment"
python -m backend.main
```

Leave this running. It auto-reloads when code changes.

**Terminal 2 (Testing):**
```powershell
# Quick WebSocket test
python backend/test_websocket_client.py

# Or run pytest
pytest tests/test_websocket_api.py -v

# Or test health
Invoke-RestMethod -Uri "http://localhost:8000/health"
```

---

## Next Steps

After verifying Phase IV works:

1. **Manual Testing Checklist:**
   - [ ] Health endpoint returns proper JSON
   - [ ] WebSocket client connects
   - [ ] Streaming responses appear gradually
   - [ ] Follow-up questions use context
   - [ ] Reset clears history
   - [ ] Validation errors are caught
   - [ ] Multiple sessions don't interfere

2. **Ready for Phase V:**
   - Build web frontend (HTML/CSS/JS)
   - Connect to WebSocket endpoint
   - Display streaming responses
   - Add session controls

3. **Document Phase IV:**
   - Update README
   - Update assignment checklist
   - Log prompts used
   - Note any issues encountered

---

## API Documentation

**Full API docs:**
- Auto-generated: http://localhost:8000/docs
- Manual: `docs/PHASE4_API.md`

**WebSocket Protocol:**
- See `docs/PHASE4_API.md` for complete protocol spec
- See `backend/test_websocket_client.py` for example usage

---

## Stopping the Server

Press `Ctrl+C` in the terminal running the server.

**Note:** All sessions will be lost (in-memory storage only).
