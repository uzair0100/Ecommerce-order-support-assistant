# Phase III Testing Summary

## Test Results

### Automated Tests (pytest)

**Status:** ✅ All 19 tests passing

```
================================= 19 passed in 0.18s =================================
```

**Test Coverage:**
1. ✅ Session creation
2. ✅ Session isolation (multiple sessions don't interfere)
3. ✅ Session reset (clears history)
4. ✅ History trimming (removes old turns when exceeding limit)
5. ✅ Topic switch with context retention
6. ✅ Nonexistent session handling
7. ✅ Session deletion
8. ✅ Session metadata retrieval
9. ✅ Concurrent turn guard (blocks overlapping requests)
10. ✅ System prompt loading
11. ✅ Message building (basic)
12. ✅ Message building with history
13. ✅ Message building with session summary
14. ✅ Trim detection logic
15. ✅ History trimming algorithm
16. ✅ Session summary - product extraction
17. ✅ Session summary - tracking status extraction
18. ✅ Session summary - return type detection
19. ✅ Token count estimation

### Ollama Connection Test

**Status:** ✅ Working

```
✅ Ollama is running
✅ Simple chat response received
✅ GadgetMart system prompt response received (£79.99 for headphones)
```

---

## Fixes Applied

### Fix 1: History Trimming Off-By-One Error

**Issue:** Test expected max 3 turns but got 4

**Cause:** Trimming happened after adding the new message, not before

**Fix:** Trim BEFORE adding new turn if at capacity
```python
# Check if adding this turn would exceed limit
current_turn_count = sum(1 for m in session.history if m["role"] == "user")

if current_turn_count >= self.max_history_turns:
    session.history = self.prompt_builder.trim_history(
        session.history,
        self.max_history_turns - 1  # Leave room for new turn
    )
```

### Fix 2: Session Summary - Faulty Item Detection

**Issue:** "damaged" keyword didn't trigger "faulty item return" summary

**Cause:** Logic checked for "return" first, then nested check for faulty keywords

**Fix:** Check for faulty keywords first, separate from general return detection
```python
# Check for faulty/damaged keywords first
has_faulty = any(
    "faulty" in msg["content"].lower() or 
    "damaged" in msg["content"].lower() or 
    "broken" in msg["content"].lower() or
    "defective" in msg["content"].lower()
    for msg in history[-4:]
)

if has_faulty:
    summary_parts.append("discussing faulty item return")
elif has_return:
    summary_parts.append("discussing change-of-mind return")
```

### Fix 3: Ollama Response Parsing

**Issue:** CLI might hang if Ollama returns response in unexpected format

**Fix:** Added fallback for response field parsing
```python
message_content = data.get("message", {}).get("content", "")

# Fallback: check for 'response' field (some Ollama versions)
if not message_content:
    message_content = data.get("response", "")
```

Also increased timeout: `timeout=(10, 180)` to allow for slow first-generation

---

## Manual Testing Guide

### CLI Test Harness

**Start CLI:**
```powershell
cd "C:\Users\uzair\OneDrive\Desktop\NLP Assignment"
$env:PYTHONPATH = "C:\Users\uzair\OneDrive\Desktop\NLP Assignment"
python -m backend.cli_test
```

### Recommended Test Scenarios

**1. Product Inquiry + Topic Switch**
```
You: Tell me about the headphones
[Check: mentions £79.99, 40-hour battery, ANC]

You: What about shipping?
[Check: mentions £4.99 under £50, free over £50]

You: Is it returnable?
[Check: resolves "it" to headphones, mentions 14-day window]
```

**2. Tracking Guidance**
```
You: Where is my order?
[Check: doesn't claim to look it up, asks for tracking status]

You: My tracking says In Transit
[Check: explains what "In Transit" means]
```

**3. Return Policy - Change of Mind vs Faulty**
```
You: Can I return the keyboard?
[Check: asks if faulty or change-of-mind]

You: I just don't like it
[Check: mentions 14 days, unopened packaging, customer pays postage]

You: Actually it's broken
[Check: mentions 30 days, no seal requirement, GadgetMart pays postage]
```

**4. Off-Topic Handling**
```
You: Can you help with my homework?
[Check: refuses politely, redirects to GadgetMart topics]

You: Do you sell smartphones?
[Check: says no, lists 5 actual products]
```

**5. Session Reset**
```
You: Tell me about the webcam
You: /reset
You: What product was I asking about?
[Check: doesn't remember webcam]
```

**6. History Trimming**
```
Send 10+ messages
Check that oldest messages are trimmed
Latest context should still be preserved
```

---

## Known Limitations (Expected)

1. **In-memory storage** - Sessions lost on restart (documented)
2. **No streaming** - Responses appear all at once (Phase IV will add streaming)
3. **CLI only** - No web interface yet (Phase V)
4. **Simple token estimation** - Uses 4 chars/token heuristic
5. **First response slow** - Model needs to load into memory (10-20s first time)

---

## Performance Observations

- **Automated tests:** ~0.18 seconds for 19 tests
- **Ollama health check:** Instant
- **Simple chat request:** ~2-3 seconds
- **GadgetMart prompt (first call):** ~10-20 seconds (model loading)
- **Subsequent calls:** ~2-4 seconds
- **Memory:** Sessions stored in RAM, minimal footprint

---

## Phase III Completion Checklist

- [x] All automated tests passing (19/19)
- [x] Ollama connection verified
- [x] History trimming working correctly
- [x] Session isolation verified
- [x] Session reset working
- [x] Topic switching with context retention
- [x] Session summaries extracting key facts
- [x] Turn-taking guard prevents concurrent requests
- [x] No tools/RAG/cloud APIs
- [x] Fixed GadgetMart facts loaded from file
- [x] Ollama /api/chat endpoint used
- [x] Temperature=0 (deterministic)
- [x] num_ctx=4096 explicitly set
- [x] CLI test harness functional
- [x] Documentation complete

---

## Ready for Phase IV

Phase III provides a solid foundation for Phase IV:
- Session management with isolated state ✅
- Conversation history with bounded context ✅
- Prompt orchestration with GadgetMart facts ✅
- Ollama integration (non-streaming) ✅
- Turn-taking logic ✅
- Memory management ✅

**Next:** Add FastAPI + WebSocket streaming API
