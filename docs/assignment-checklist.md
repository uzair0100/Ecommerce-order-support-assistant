# Assignment 1 - Compliance Checklist

This document maps assignment requirements to implementation evidence and completion status.

---

## Core Requirements

### System Architecture

| Requirement | Implementation | Status | Evidence |
|------------|----------------|--------|----------|
| Frontend web chat interface | Phase V | ⬜ Pending | - |
| Backend FastAPI with REST + WebSocket | Phase IV | ⬜ Pending | - |
| Conversation Manager (session, history, prompts) | Phase III | ⬜ Pending | - |
| Local LLM Engine (quantized, CPU-only) | Phase II | ⬜ Pending | - |

### Phase I - Business Case Selection

| Requirement | Implementation | Status | Evidence |
|------------|----------------|--------|----------|
| Selected domain: E-Commerce Order Support | GadgetMart (UK electronics) | ✅ Complete | docs/store-facts.md, README.md |
| Written use-case description | Phase I | ✅ Complete | README.md - Use Case Description |
| At least 3 example dialogues | 4 dialogues created | ✅ Complete | README.md - Example Dialogues |
| Conversation flow with stages | Phase I | ✅ Complete | README.md - Conversation Flow Design |
| Handle topic changes mid-conversation | Phase I design | ✅ Complete | README.md - Topic Switching Behavior |
| Refuse irrelevant queries with strategy | Phase I design | ✅ Complete | README.md - Off-Topic Detection |

### Phase II - Local LLM Selection

| Requirement | Implementation | Status | Evidence |
|------------|----------------|--------|----------|
| Model: 0.5B-4B parameters, Q4 quantization | Phase II | ⬜ Pending | - |
| Ollama/llama.cpp/vLLM for local inference | Ollama selected | ✅ Complete | Local setup |
| Context memory management scheme | Phase III | ⬜ Pending | - |
| Latency benchmarks (tokens/sec, TTFT) | Phase II | ⬜ Pending | - |
| Benchmarks run on own hardware | Phase II | ⬜ Pending | - |

### Phase III - Conversation Manager

| Requirement | Implementation | Status | Evidence |
|------------|----------------|--------|----------|
| Maintain dialogue history per session | Phase III | ⬜ Pending | - |
| Enforce domain conversational policies | Phase III | ⬜ Pending | - |
| Clean turn-taking logic | Phase III | ⬜ Pending | - |
| Structured system prompts | Phase III | ⬜ Pending | - |
| Context faithfulness across turns | Phase III | ⬜ Pending | - |
| **No tools, agents, plugins, or RAG** | Design constraint | ✅ Enforced | Architecture |

### Phase IV - Backend API

| Requirement | Implementation | Status | Evidence |
|------------|----------------|--------|----------|
| WebSocket endpoint `/ws/chat` | Phase IV | ⬜ Pending | - |
| JSON request/response format | Phase IV | ⬜ Pending | - |
| Asynchronous request handling | Phase IV | ⬜ Pending | - |
| Streaming token output (word-by-word) | Phase IV | ⬜ Pending | - |
| Robust error handling (no crashes) | Phase IV | ⬜ Pending | - |
| Clear setup and run instructions | Phase IV | ⬜ Pending | - |

### Phase V - Web Interface

| Requirement | Implementation | Status | Evidence |
|------------|----------------|--------|----------|
| Real-time messaging with visible streaming | Phase V | ⬜ Pending | - |
| Conversation history visible in UI | Phase V | ⬜ Pending | - |
| Reset / new session control | Phase V | ⬜ Pending | - |
| Clean, usable UI (not confusing) | Phase V | ⬜ Pending | - |

### Phase VI - Production Readiness

| Requirement | Implementation | Status | Evidence |
|------------|----------------|--------|----------|
| Latency: TTFT and total response time | Phase VI testing | ⬜ Pending | - |
| Correctness: stays in character, follows policies | Phase VI testing | ⬜ Pending | - |
| Handles off-topic attempts | Phase VI testing | ⬜ Pending | - |
| Failure handling: malformed input, disconnect, concurrent | Phase VI testing | ⬜ Pending | - |
| System fails gracefully, no crashes | Phase VI testing | ⬜ Pending | - |

---

## System Requirements Compliance

| Requirement | Status | Notes |
|------------|--------|-------|
| ✅ Fully local inference (no cloud APIs) | Enforced | Ollama on local CPU |
| ✅ Instruction-tuned responses | Pending model | Qwen2.5:1.5b-instruct or phi3:3.8b |
| ✅ Context tracking across turns | Pending Phase III | Session-based memory |
| ✅ CPU-optimized inference | Enforced | Q4 quantization required |
| ✅ Streaming output over WebSocket | Pending Phase IV | FastAPI WebSocket |

---

## Deliverables Checklist

### Code & Repository

- [x] All source code in single GitHub repository
- [ ] Backend code (FastAPI)
- [ ] Frontend code (web chat)
- [ ] Scripts (benchmarking, testing)
- [ ] Tests and test cases
- [x] .gitignore (excludes models, secrets, caches)

### README.md Must Include:

- [ ] Setup instructions
- [ ] Architecture diagram
- [ ] Model selection rationale
- [ ] Latency benchmarks (with hardware specs)
- [ ] Known limitations
- [ ] Use-case description
- [ ] At least 3 example dialogues
- [ ] Conversation flow design
- [ ] API/WebSocket schema documentation

### Documentation:

- [x] docs/prompts.md (all Kiro prompts preserved)
- [x] docs/assignment-checklist.md (this file)
- [ ] Optional: Loom demo video

---

## Bonus (Choose One)

- [ ] **Cloud deployment** (Vercel free tier + public URL) ← **SELECTED**
- [ ] UX/persona polish (not selected)

---

## Evaluation Criteria

| Criterion | Weight | Status | Notes |
|-----------|--------|--------|-------|
| Correctness & Completeness | 50% | ⬜ Pending | All phases + tests |
| Viva (walkthrough + Q&A) | 25% | ⬜ Pending | Must explain all code |
| Real-time Behaviour & Performance | 25% | ⬜ Pending | Latency, streaming, failures |
| **Bonus** | +10% | ⬜ Pending | Vercel deployment |

---

## Prohibited Items - Compliance Gate

Before submission, verify **NONE** of these are present:

- [ ] ❌ Cloud model API calls (OpenAI, Anthropic, Cohere, etc.)
- [ ] ❌ Tool use or function calling
- [ ] ❌ RAG (retrieval-augmented generation)
- [ ] ❌ External database queries for orders
- [ ] ❌ Live inventory or shipping carrier APIs
- [ ] ❌ Return processing or refund approval logic
- [ ] ❌ Pet-care or other domain content from reference project
- [ ] ❌ Uncommitted model files or secrets in repository

---

## Phase Sign-Off

| Phase | Date Completed | Manual Test Pass | Ready for Next Phase |
|-------|----------------|------------------|---------------------|
| Phase 0: Setup | Sept 15, 2026 | ✅ | ✅ |
| Phase I: Business Case | Sept 15, 2026 | ⬜ Pending User Review | ⬜ |
| Phase II: Model Selection | - | - | ⬜ |
| Phase III: Conversation Manager | - | - | ⬜ |
| Phase IV: Backend API | - | - | ⬜ |
| Phase V: Web Interface | - | - | ⬜ |
| Phase VI: Evaluation | - | - | ⬜ |

---

## Notes & Risks

*(To be updated during implementation)*

- Hardware: Will document actual CPU specs during Phase II benchmarking
- Model choice: Need to benchmark both Qwen and Phi3 before final selection
- Concurrent sessions: Need to test CPU throughput limits during Phase VI
- Vercel deployment: May need to adjust for cold starts and request timeouts
