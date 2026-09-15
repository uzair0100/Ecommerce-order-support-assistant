# GadgetMart Backend - Phase III

## Overview

Phase III implements the conversation manager and prompt orchestration for the GadgetMart assistant.

**Features:**
- Session management with isolated conversation state
- Bounded conversation history with automatic trimming
- Turn-taking guard (prevents concurrent requests per session)
- Structured system prompts using GadgetMart store facts
- Session summaries for context retention
- Ollama integration using `/api/chat` endpoint

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
├── ollama_client.py            # Ollama API client
├── prompt_builder.py           # Prompt construction and history management
├── conversation_manager.py     # Session and conversation orchestration
├── cli_test.py                 # CLI test harness
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

Run all tests:

```bash
pytest tests/
```

Run specific test file:

```bash
pytest tests/test_conversation_manager.py -v
```

Run with coverage:

```bash
pytest tests/ --cov=backend --cov-report=html
```

### Manual CLI Test Harness

```bash
python -m backend.cli_test
```

**CLI Commands:**
- `/reset` - Clear current session history
- `/new` - Start a new session
- `/info` - Show session metadata
- `/exit` - Exit the CLI

**Test Scenarios:**
1. Product inquiry with topic switch
2. Multi-turn context retention
3. Tracking guidance (user supplies status)
4. Return policy questions
5. Off-topic handling
6. Session reset
7. History trimming (send >8 messages)

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
