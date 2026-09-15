# GadgetMart Backend - Phase III & IV

## Overview

Phase III implements conversation management and prompt orchestration.
Phase IV adds FastAPI REST and WebSocket API with streaming responses.

**Phase III Features:**
- Session management with isolated conversation state
- Bounded conversation history with automatic trimming
- Turn-taking guard (prevents concurrent requests per session)
- Structured system prompts using GadgetMart store facts
- Session summaries for context retention
- Ollama integration using `/api/chat` endpoint

**Phase IV Features:**
- FastAPI application with REST and WebSocket endpoints
- `/health` endpoint for monitoring
- `/ws/chat` WebSocket with streaming responses
- JSON protocol: start → chunk → done/error events
- Asynchronous request handling
- Validation and error handling
- Session auto-creation and reset

**Storage:**
- In-memory session storage (sessions lost on restart)
- No persistent database

**Model:**
- Qwen2.5 1.5B Instruct (via Ollama)
- Temperature: 0 (deterministic)
- Context window: 4096 tokens

---

## File Structure

```
backend/
├── __init__.py                 # Package initialization
├── config.py                   # Configuration settings
├── gadgetmart_facts.txt        # Store facts (loaded into system prompt)
├── ollama_client.py            # Ollama API client (streaming + non-streaming)
├── prompt_builder.py           # Prompt construction and history management
├── conversation_manager.py     # Session and conversation orchestration
├── main.py                     # FastAPI application (Phase IV)
├── websocket_handler.py        # WebSocket streaming handler (Phase IV)
├── cli_test.py                 # CLI test harness (Phase III)
├── test_websocket_client.py    # WebSocket manual test client (Phase IV)
├── test_ollama_connection.py   # Ollama connection tester
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

---

## Setup

### 1. Install Dependencies

```bash
pip install -r backend/requirements.txt
```

### 2. Start Ollama

Make sure Ollama is running:

```bash
ollama serve
```

### 3. Verify Model is Available

```bash
ollama list
```

You should see `qwen2.5:1.5b-instruct` in the list.

If not, pull it:

```bash
ollama pull qwen2.5:1.5b-instruct
```

---

## Running Tests

### Automated Tests (pytest)

**Run all tests:**

```bash
pytest tests/ -v
```

**Run Phase III tests only:**

```bash
pytest tests/test_conversation_manager.py tests/test_prompt_builder.py -v
```

**Run Phase IV API tests:**

```bash
pytest tests/test_websocket_api.py -v
```

**Run with live Ollama (slower, requires Ollama running):**

```bash
pytest tests/test_websocket_api.py --run-live -v
```

**Run with coverage:**

```bash
pytest tests/ --cov=backend --cov-report=html
```

### Manual Testing

**Phase III CLI Test Harness:**

```bash
python -m backend.cli_test
```

**Phase IV WebSocket Test Client:**

```bash
# Terminal 1: Start server
python -m backend.main

# Terminal 2: Run test client
python backend/test_websocket_client.py
```

---

## Running the Server (Phase IV)

### Development Mode (with auto-reload):

```bash
python -m backend.main
```

Or using uvicorn directly:

```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

Server will be available at:
- WebSocket: `ws://localhost:8000/ws/chat`
- Health check: `http://localhost:8000/health`
- API docs: `http://localhost:8000/docs` (FastAPI auto-generated)

---

## API Documentation

### REST Endpoints

#### GET /health

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "server_healthy": true,
  "ollama_available": true,
  "model": "qwen2.5:1.5b-instruct",
  "active_sessions": 3
}
```

**Status Codes:**
- `200` - Server is responding
- `503` - Server error (shouldn't happen for health check)

**Notes:**
- `status` is "healthy" if Ollama is available, "degraded" if not
- `server_healthy` is always `true` if the endpoint responds
- `ollama_available` shows whether the model can be reached
- Health check does not hang waiting for Ollama

---

### WebSocket Endpoint

#### WS /ws/chat

Real-time streaming chat endpoint.

**Client → Server Messages:**

**Chat Message:**
```json
{
  "type": "message",
  "session_id": "uuid-or-null",
  "content": "user message text"
}
```

**Reset Session:**
```json
{
  "type": "reset",
  "session_id": "uuid"
}
```

**Server → Client Events:**

**Start Event:**
```json
{
  "type": "start",
  "session_id": "uuid",
  "turn_id": "uuid"
}
```

**Chunk Event (repeated):**
```json
{
  "type": "chunk",
  "session_id": "uuid",
  "turn_id": "uuid",
  "content": "text chunk from Ollama"
}
```

**Done Event:**
```json
{
  "type": "done",
  "session_id": "uuid",
  "turn_id": "uuid",
  "total_tokens": 123
}
```

**Reset Acknowledgment:**
```json
{
  "type": "reset",
  "session_id": "uuid"
}
```

**Error Event:**
```json
{
  "type": "error",
  "session_id": "uuid-or-null",
  "turn_id": "uuid-or-null",
  "error": "error message",
  "code": "ERROR_CODE"
}
```

**Error Codes:**
- `INVALID_JSON` - Malformed JSON
- `MISSING_FIELD` - Required field missing
- `INVALID_MESSAGE_TYPE` - Unknown message type
- `EMPTY_CONTENT` - Content is empty or whitespace-only
- `CONTENT_TOO_LONG` - Content exceeds 2000 characters
- `INVALID_SESSION` - Session not found or invalid UUID
- `SESSION_BUSY` - Another request is in progress for this session
- `MODEL_ERROR` - Ollama error occurred
- `SERVER_ERROR` - Internal server error

**Validation Rules:**
- `content`: Required, non-empty, max 2000 characters
- `session_id`: Optional (auto-created), must be valid UUID if provided
- `type`: Required, must be "message" or "reset"

**Session Behavior:**
- If `session_id` is `null` or omitted, a new session is created
- Session ID is returned in the `start` event
- Sessions are in-memory only (lost on server restart)
- Session timeout: 1 hour of inactivity (not yet enforced)
- Reset clears conversation history but keeps the session ID

**Streaming:**
- Chunks are forwarded from Ollama as received
- Chunks may be sub-word tokens or multiple words
- Frontend should append chunks without assuming word boundaries
- Incomplete streams never enter conversation history

---

## Architecture

### ConversationManager

Central orchestrator that:
- Creates and manages sessions
- Enforces turn-taking per session
- Coordinates prompt building and model calls
- Handles history trimming
- Provides session isolation

### PromptBuilder

Responsible for:
- Loading GadgetMart facts from file
- Building structured message lists for Ollama
- Creating session summaries
- Trimming old conversation turns
- Token count estimation

### OllamaClient

HTTP client that:
- Calls Ollama `/api/chat` endpoint
- Handles timeouts and errors gracefully
- Designed to support streaming (Phase IV)
- Provides health check

### Session State

Each session maintains:
- Unique session ID (UUID)
- Conversation history (list of role/content messages)
- Created and last activity timestamps
- Thread lock for turn-taking
- In-progress flag

---

## Memory Management

**Token Budget:**
- System prompt: ~1200 tokens (GadgetMart facts)
- Conversation history: ~2000 tokens (rolling window)
- Current turn: Always included
- Generation budget: ~800 tokens (for assistant response)
- **Total context: 4096 tokens (num_ctx)**

**Trimming Strategy:**
1. Keep last 8 turns (configurable via MAX_HISTORY_TURNS)
2. When exceeded, remove oldest complete turn pair (user + assistant)
3. Always preserve most recent user message
4. Session summary tracks current product, tracking status, return type

**Session Summary:**
- Compact extraction of key session facts
- Current product being discussed
- User-provided tracking status (if any)
- Return type (change-of-mind vs. faulty)
- Never claims verified order/tracking data

---

## Configuration

Edit `backend/config.py` to adjust:

- `MODEL_NAME` - Ollama model identifier
- `NUM_CTX` - Context window size
- `TEMPERATURE` - Generation temperature
- `MAX_HISTORY_TURNS` - Maximum conversation turns to retain
- `OLLAMA_BASE_URL` - Ollama API endpoint

---

## Testing Phase III

### Test Cases Covered

**Automated (pytest):**
1. ✅ Session creation
2. ✅ Session isolation (multiple sessions)
3. ✅ Session reset
4. ✅ History trimming (exceeding max turns)
5. ✅ Topic switch with context retention
6. ✅ Nonexistent session handling
7. ✅ Session deletion
8. ✅ Session metadata retrieval
9. ✅ Concurrent turn guard
10. ✅ Prompt building with history
11. ✅ Session summary extraction

**Manual (CLI harness):**
1. Product question → topic switch → back to product
2. Tracking guidance with user-supplied status
3. Return policy (change-of-mind vs. faulty)
4. Off-topic request handling
5. Multi-turn conversation >8 turns (verify trimming)
6. Session reset mid-conversation

---

## Known Limitations

1. **In-memory storage** - Sessions lost on restart (documented, accepted for Phase III)
2. **No streaming** - Phase III uses non-streaming responses (Phase IV will add WebSocket streaming)
3. **No persistent sessions** - No database or file persistence
4. **Simple token estimation** - Uses character count heuristic (~4 chars/token)
5. **No rate limiting** - Turn guard prevents concurrent requests per session, but no global rate limit
6. **No session timeout** - Sessions remain in memory indefinitely (timeout enforcement planned for Phase IV)

---

## Next Steps (Phase IV)

Phase IV will add:
- FastAPI application with REST + WebSocket
- `/health` endpoint
- `/ws/chat` WebSocket endpoint with streaming
- JSON protocol with start/chunk/done/error events
- Asynchronous request handling
- Session timeout enforcement
- Proper error responses for malformed requests

---

## Troubleshooting

**"Ollama does not appear to be running"**
- Start Ollama: `ollama serve`
- Check it's listening on port 11434

**"Model not found"**
- Pull the model: `ollama pull qwen2.5:1.5b-instruct`
- Verify: `ollama list`

**Tests fail with timeout**
- Increase timeout in `ollama_client.py` (line 54)
- Check CPU isn't overloaded

**"Another request is in progress"**
- This is the turn-taking guard working correctly
- Wait for current request to complete
- If stuck, restart the CLI/test

**Import errors**
- Run from project root: `python -m backend.cli_test`
- Not from backend directory: `cd backend && python cli_test.py` ❌

---

## Phase III Deliverables ✅

- ✅ Session manager with isolated state
- ✅ Conversation history store with bounded context
- ✅ Prompt builder with GadgetMart facts
- ✅ Ollama integration (/api/chat endpoint)
- ✅ Turn-taking logic (thread-safe)
- ✅ Context faithfulness across turns
- ✅ Memory trimming strategy
- ✅ Session summary for context retention
- ✅ CLI test harness
- ✅ Pytest unit tests
- ✅ No tools/agents/plugins/RAG
- ✅ Documentation

**Phase III Complete!**
