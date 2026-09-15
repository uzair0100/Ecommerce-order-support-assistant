# Assignment 1: Final Audit & Verification Checklist

**Deadline:** Tonight 11:59 PM  
**Auditor:** Senior Developer Review  
**Date:** September 15, 2026

---

## PART 1: CORE REQUIREMENTS VERIFICATION

### 1.1 Domain & Business Case ✅ VERIFIED

| Requirement | Evidence | Status |
|------------|----------|--------|
| Approved e-commerce domain | docs/store-facts.md (GadgetMart UK electronics) | ✅ PASS |
| 5 products defined | store-facts.md lines 1-45 (headphones, stand, keyboard, webcam, power bank) | ✅ PASS |
| UK shipping/return policies | store-facts.md lines 47-90 | ✅ PASS |
| Use case description | README.md "Use Case Description" section | ✅ PASS |
| 3+ example dialogues | README.md (4 dialogues provided) | ✅ PASS |
| Conversation flow with stages | README.md with ASCII diagram | ✅ PASS |
| Topic switching documented | README.md "Topic Switching Behavior" section | ✅ PASS |
| Off-topic handling strategy | README.md "Off-Topic Detection" section | ✅ PASS |

**Finding:** All Phase I deliverables present and documented.

---

### 1.2 Model Selection (0.5B-4B, Q4, CPU-only) ✅ VERIFIED

| Requirement | Evidence | Status |
|------------|----------|--------|
| Model in 0.5B-4B range | Qwen2.5:1.5b-instruct (1.5B parameters) | ✅ PASS |
| Q4 quantization | docs/model-benchmark.md confirms Q4_K_M | ✅ PASS |
| Local CPU inference | Ollama, no cloud API | ✅ PASS |
| Benchmarks on own hardware | scripts/benchmark_results.json (Intel i7-8650U, 8GB RAM) | ✅ PASS |
| TTFT measured | P01-P12 results: 2.3-20.2s TTFT | ✅ PASS |
| Tokens/sec measured | 7.71-12.10 tokens/sec for Qwen | ✅ PASS |
| Model selection rationale | docs/model-selection.md + benchmark.md | ✅ PASS |

**Finding:** Model selection properly benchmarked with real hardware results. Qwen2.5 1.5B selected over Phi3 due to 2x speed advantage.

---

### 1.3 NO Prohibited Features ⚠️ NEEDS VERIFICATION

| Prohibited Item | Check | Status |
|----------------|-------|--------|
| No cloud model API | grep codebase for openai/anthropic/cohere | ⬜ TODO |
| No tools/function calling | Inspect ollama_client.py | ⬜ TODO |
| No RAG/retrieval | Check for vector stores/embeddings | ⬜ TODO |
| No agents/plugins | Verify pure conversation flow | ⬜ TODO |
| No live order lookup | System prompt explicitly forbids | ⬜ TODO |
| No inventory API calls | No external HTTP clients except Ollama | ⬜ TODO |

**Action Required:** Verify no prohibited features in codebase.

---

### 1.4 Session Memory & Conversation Manager ⚠️ NEEDS TESTING

| Requirement | Evidence | Status |
|------------|----------|--------|
| Per-session dialogue history | backend/conversation_manager.py | ✅ EXISTS |
| Context window management | Summarization + bounded history | ✅ EXISTS |
| Turn-taking logic | threading.Lock per session | ✅ EXISTS |
| System prompt integration | prompt_builder.py | ✅ EXISTS |
| Session isolation | UUID-based sessions | ✅ EXISTS |
| Reset functionality | reset_session() method | ✅ EXISTS |
| **Manual test: context retention** | - | ⬜ TODO |
| **Manual test: topic switching** | - | ⬜ TODO |
| **Manual test: session isolation** | - | ⬜ TODO |

**Action Required:** Run manual conversation tests to verify memory works.

---

### 1.5 FastAPI Backend with Streaming ⚠️ NEEDS TESTING

| Requirement | Evidence | Status |
|------------|----------|--------|
| REST health endpoint | backend/main.py `/health` | ✅ EXISTS |
| WebSocket `/ws/chat` | backend/main.py `/ws/chat` | ✅ EXISTS |
| JSON request/response | websocket_handler.py | ✅ EXISTS |
| Asynchronous handling | FastAPI async def | ✅ EXISTS |
| Token streaming (word-by-word) | ollama_client.py chat_stream() | ✅ EXISTS |
| **Manual test: streaming visible** | - | ⬜ TODO |
| **Manual test: concurrent sessions** | - | ⬜ TODO |
| **Manual test: malformed JSON** | - | ⬜ TODO |
| **Manual test: Ollama unavailable** | - | ⬜ TODO |

**Action Required:** Run backend API tests including edge cases.

---

### 1.6 Web UI ⚠️ NEEDS TESTING

| Requirement | Evidence | Status |
|------------|----------|--------|
| Real-time messaging | frontend/app.js WebSocket client | ✅ EXISTS |
| Visible streaming chunks | handleChunkEvent() appends incrementally | ✅ EXISTS |
| Conversation history display | Chat container with message bubbles | ✅ EXISTS |
| Reset/new session control | Reset button → `{type: "reset"}` message | ✅ EXISTS |
| Clean, usable UI | Professional black/cyan theme | ✅ EXISTS |
| **Manual test: streaming animation** | - | ⬜ TODO |
| **Manual test: reset clears chat** | - | ⬜ TODO |
| **Manual test: mobile responsive** | - | ⬜ TODO |

**Action Required:** Visual inspection and interaction testing.

---

### 1.7 Error Handling & Robustness ⚠️ NEEDS TESTING

| Scenario | Expected Behavior | Status |
|----------|------------------|--------|
| Empty message | Validation error, no send | ⬜ TODO |
| 2001-char message | Blocked by maxlength | ⬜ TODO |
| Malformed JSON | Error response, no crash | ⬜ TODO |
| Ollama not running | Health check fails, graceful error | ⬜ TODO |
| WebSocket disconnect mid-stream | Frontend reconnects | ⬜ TODO |
| Concurrent sessions | Both work independently | ⬜ TODO |
| Invalid session ID | Error code INVALID_SESSION | ⬜ TODO |

**Action Required:** Systematic failure testing.

---

### 1.8 Correctness & Domain Adherence ⚠️ NEEDS TESTING

| Test Case | Expected Result | Status |
|-----------|----------------|--------|
| Ask product price | Correct price from store facts | ⬜ TODO |
| Ask unknown spec | "I don't have that info" | ⬜ TODO |
| Ask off-topic (homework) | Polite refusal, redirect to domain | ⬜ TODO |
| "Where is my order GM123?" | "I can't look up orders" | ⬜ TODO |
| Prompt injection attempt | Ignore, stay in character | ⬜ TODO |
| Multi-turn product switch | Remembers new product context | ⬜ TODO |
| Return policy question | Correct 14-day change-of-mind policy | ⬜ TODO |

**Action Required:** Adversarial and correctness testing.

---

## PART 2: DOCUMENTATION REQUIREMENTS

### 2.1 README.md Completeness ⚠️ NEEDS UPDATE

| Required Section | Present | Complete | Status |
|-----------------|---------|----------|--------|
| Setup instructions | ✅ Yes | ⚠️ Partial | Needs testing verification |
| Architecture diagram | ❌ No | ❌ No | **MISSING** |
| Model selection rationale | ✅ Yes | ✅ Yes | ✅ PASS |
| Latency benchmarks | ✅ Yes | ✅ Yes | ✅ PASS |
| Hardware specs | ✅ Yes | ✅ Yes | ✅ PASS |
| Known limitations | ⚠️ Stub | ❌ No | **INCOMPLETE** |
| Use-case description | ✅ Yes | ✅ Yes | ✅ PASS |
| 3+ example dialogues | ✅ Yes | ✅ Yes | ✅ PASS |
| Conversation flow | ✅ Yes | ✅ Yes | ✅ PASS |
| API/WebSocket schema | ❌ Stub | ❌ No | **MISSING** |

**Action Required:** Add architecture diagram, complete limitations section, document WebSocket API schema.

---

### 2.2 Test Cases & Results ❌ MISSING

| Deliverable | Present | Status |
|------------|---------|--------|
| Manual test cases documented | ❌ No | **MISSING** |
| Test results recorded | ❌ No | **MISSING** |
| Failure cases documented | ❌ No | **MISSING** |
| Concurrent session test | ❌ No | **MISSING** |

**Action Required:** Document all manual tests with inputs, outputs, pass/fail.

---

### 2.3 Source Code Quality ⚠️ NEEDS REVIEW

| Item | Status |
|------|--------|
| All code committed | ✅ PASS |
| .gitignore excludes models | ✅ PASS |
| No secrets in repo | ⬜ TODO (verify) |
| Code has docstrings | ✅ PASS (spot-checked) |
| Clear file organization | ✅ PASS |

---

## PART 3: BONUS WORK (Optional, +10%)

### 3.1 Deployment (NOT VIABLE)

❌ **Vercel deployment cannot work** because:
- Inference must remain local CPU-only (assignment requirement)
- Backend requires Ollama (cannot deploy to Vercel)
- Frontend alone without backend is non-functional

**Conclusion:** Do NOT pursue Vercel deployment bonus.

---

### 3.2 UX/Persona Polish (VIABLE IF TIME)

Potential small improvements if core requirements pass and time remains:

- [ ] Keyboard accessibility (Tab navigation, Focus indicators)
- [ ] Loading/empty state polish (Better welcome message)
- [ ] Improved error messages (More helpful troubleshooting)
- [ ] Mobile layout verification (Test on actual phone)
- [ ] Consistent GadgetMart tone under adversarial prompts (System prompt tuning)

**Decision:** Only pursue if ALL core requirements verified by 10:00 PM.

---

## PART 4: SUBMISSION CHECKLIST

### 4.1 Repository Status

- [ ] All code committed and pushed
- [ ] README.md complete
- [ ] docs/FINAL_AUDIT.md (this file) complete
- [ ] No uncommitted changes
- [ ] Repository is private
- [ ] Collaborator access granted (if required)

### 4.2 Deliverables Present

- [ ] Source code (backend, frontend, tests, scripts)
- [ ] Documentation (README, docs/)
- [ ] Benchmark results (scripts/benchmark_results.json)
- [ ] Test cases and results (to be created)
- [ ] .gitignore (models, caches, secrets excluded)

---

## PART 5: EXECUTION PLAN (By Time)

### ⏰ NOW - 8:00 PM: Core Verification (2 hours)

1. **Verify no prohibited features** (15 min)
   - grep for cloud APIs
   - Inspect ollama_client for tools/RAG
   - Confirm pure conversation flow

2. **Run manual conversation tests** (30 min)
   - Start backend + frontend
   - Test product questions, topic switching, memory
   - Test off-topic refusal
   - Test prompt injection resistance
   - Document inputs/outputs

3. **Run failure/edge case tests** (30 min)
   - Empty input, long input
   - Malformed JSON
   - Ollama not running
   - Concurrent sessions (2 browser tabs)
   - WebSocket disconnect
   - Document all results

4. **Fix critical failures** (45 min)
   - Only fix blocking issues
   - Retest after fixes
   - Document what was fixed

### ⏰ 8:00 PM - 9:30 PM: Documentation (1.5 hours)

1. **Add architecture diagram** (20 min)
   - ASCII or simple PNG showing components
   - User → Frontend → Backend → Ollama → LLM

2. **Complete README.md** (30 min)
   - Known limitations section (from tests)
   - API/WebSocket schema documentation
   - Final setup instructions verification

3. **Create test results document** (40 min)
   - docs/TEST_RESULTS.md
   - All manual tests with pass/fail
   - Failure cases and resolutions
   - Performance measurements

### ⏰ 9:30 PM - 10:30 PM: Final Verification (1 hour)

1. **Clean checkout test** (20 min)
   - Clone repo to temp directory
   - Follow README setup instructions
   - Verify system starts and works

2. **Final audit review** (20 min)
   - Mark all checklist items complete/incomplete
   - Identify any remaining gaps
   - Document unresolved limitations

3. **Buffer for last-minute fixes** (20 min)

### ⏰ 10:30 PM - 11:00 PM: Bonus (Optional, 30 min)

**ONLY if all core requirements pass:**
- Quick keyboard accessibility improvements
- Polish error messages
- Test on mobile viewport

**OTHERWISE:**
- Use this time for final documentation polish
- Prepare submission materials

### ⏰ 11:00 PM - 11:45 PM: Submission Prep (45 min)

1. Final commit and push
2. Verify GitHub repository is complete and private
3. Prepare viva talking points
4. Review assignment checklist one last time

### ⏰ 11:45 PM - 11:59 PM: SUBMIT (14 min buffer)

---

## CURRENT STATUS SUMMARY

**Completed:**
- ✅ Phase I: Business case, domain, dialogues
- ✅ Phase II: Model benchmarking (real results)
- ✅ Phase III: Conversation manager (code exists)
- ✅ Phase IV: Backend API (code exists)
- ✅ Phase V: Frontend (code exists, basic testing done)

**Needs Immediate Attention:**
- ⚠️ Manual testing of all core functionality
- ⚠️ Edge case and failure testing
- ⚠️ Architecture diagram (missing)
- ⚠️ API schema documentation (missing)
- ⚠️ Test results documentation (missing)
- ⚠️ Known limitations section (incomplete)

**Estimated Risk:** MEDIUM
- Code appears complete but needs verification
- Documentation gaps are fixable
- 4.5 hours remaining is sufficient IF testing reveals no major issues

**Recommendation:** Proceed with execution plan immediately. Prioritize testing and critical documentation. Skip bonus work if time-constrained.

---

## SIGN-OFF

**Audit Started:** [TIME]  
**Audit Completed:** [TIME]  
**Core Requirements Status:** [PASS/FAIL/INCOMPLETE]  
**Bonus Work Status:** [COMPLETED/NOT ATTEMPTED]  
**Ready for Submission:** [YES/NO]  
**Final Commit Hash:** [HASH]  

