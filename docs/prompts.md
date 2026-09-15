# Kiro Prompts Log

This document preserves all prompts used with Kiro (or other AI assistants) during the development of this project, as required for the viva.

---

## Phase 0 - Repository Setup

### Prompt 0.1 - Initial Setup
**Date:** September 15, 2026  
**Tool:** Kiro AI Assistant  
**Context:** Starting Phase 0 with clean workspace

**Prompt:**
> Act as a senior Python/FastAPI developer helping with Assignment 1. Read the attached assignment and this scope before editing. Create the smallest clean repository structure for an E-Commerce Order Support Assistant. The domain is approved; the old PetCare project is reference material only. Do not copy pet-care content, add tool/RAG/cloud-model dependencies, or implement product/order integrations. Prepare a compliance checklist mapped to assignment requirements, a place to preserve all prompts, a suitable `.gitignore`, and a brief README stub. Show the files you propose and explain each one before generating them. Keep code minimal and explain every change.

**Output:**
- Created `.gitignore` excluding models, secrets, caches, virtual environments
- Created `README.md` stub with domain statement, planned structure, and phase checklist
- Created `docs/assignment-checklist.md` mapping all assignment requirements to implementation
- Created `docs/prompts.md` (this file) to preserve all Kiro prompts

**Rationale:**
Established clean baseline with no prohibited dependencies, clear domain boundaries, and traceability for all AI-assisted work.

---

## Phase I - Business Case & Store Facts

### Prompt 1.1 - Store Design and Phase I Materials
**Date:** September 15, 2026  
**Tool:** Kiro AI Assistant  
**Context:** User approved GadgetMart concept with corrections; implementing Phase I deliverables

**Prompt:**
> Use only the approved E-Commerce Order Support Assistant domain. Draft a compact fictional store fact sheet for GadgetMart (UK-based, 5 products: headphones, laptop stand, keyboard, webcam, power bank). Include exact specifications for each product with clearly marked unknown fields. Write explicit UK-aligned shipping policy (free over £50, £4.99 under, 3-5 days, Royal Mail tracking) and return policy (14-day change-of-mind sealed/unused, 30-day faulty no seal requirement, support email for processing). Create use-case description, conversation flow with stage diagram and topic-switching rules, and 4 example dialogues covering: (1) product inquiry with topic switch, (2) tracking guidance with user-supplied status, (3) return policy with change-of-mind vs. faulty distinction, (4) off-topic refusal with redirect. Mark all content as fictional demo. Ensure assistant never claims to look up orders, access tracking systems, or process returns—tools and RAG are prohibited. Update README with all Phase I materials, create docs/store-facts.md reference document, and update docs/prompts.md with this prompt.

**Output:**
- Created `docs/store-facts.md` with complete GadgetMart product catalog, policies, boundaries, and testing scenarios
- Updated `README.md` with:
  - Use case description
  - 4 example dialogues (product inquiry, tracking guidance, return policy, off-topic)
  - Conversation flow diagram with stages and topic-switching behavior
  - Memory management rules
  - E-commerce-specific branch handling
- Updated `docs/prompts.md` with this Phase I prompt

**Key Design Decisions:**
- 5 products with realistic specs and explicitly marked unknowns for uncertainty testing
- UK-specific policies aligned with distance selling regulations (14-day cancellation)
- Separate faulty-item path (30 days, no sealed requirement) to test context distinction
- Tracking guidance asks user to supply status, never claims database access
- Return guidance explains process, never claims to approve or process
- Topic-switching scenarios test context retention and ambiguous reference handling
- Off-topic handling with brief refusal and domain redirect

**Compliance Check:**
✅ No tools, RAG, or cloud APIs  
✅ No live order lookup or carrier API access  
✅ No return processing or refund approval  
✅ All facts are fixed and fictional  
✅ Clear boundaries documented  

**Rationale:**
Phase I establishes the complete domain knowledge and conversation design that will be embedded in the system prompt (Phase III) and tested throughout implementation. The store facts are detailed enough for realistic conversations while simple enough for a university project. The policies create good test cases for multi-turn context, topic switching, and honesty about system limitations.

---

## Phase II - Model Selection & Benchmarking

*(Prompts will be added as Phase II begins)*

---

## Phase III - Conversation Manager

*(Prompts will be added as Phase III begins)*

---

## Phase IV - Backend API

*(Prompts will be added as Phase IV begins)*

---

## Phase V - Web Interface

*(Prompts will be added as Phase V begins)*

---

## Phase VI - Evaluation & Documentation

*(Prompts will be added as Phase VI begins)*

---

## Notes

- Each prompt includes date, context, full prompt text, output summary, and rationale
- Edits made to AI-generated code are tracked in git commit messages
- For viva: be prepared to explain why each prompt was structured that way and what alternatives were considered


### Prompt 3.1 - Phase III Implementation
**Date:** September 15, 2026  
**Tool:** Kiro AI Assistant  
**Context:** Implementing conversation manager after Phase I & II completion

**Prompt:**
> Structure: Use backend/ with conversation_manager.py, prompt_builder.py, ollama_client.py, and config.py. Keep GadgetMart facts in separate gadgetmart_facts.txt. Memory: Set num_ctx=4096, keep latest user message + compact summary + ~8 turns, trim oldest first. Testing: Create CLI harness for manual testing AND pytest tests for trimming, topic switches, reset, session isolation. Ollama: Use /api/chat endpoint with role messages, temperature=0, stream=false for Phase III. Design client to support streaming in Phase IV. Storage: In-memory dictionary with per-session turn guard. Document sessions disappear on restart.

**Output:**
- Created `backend/` directory structure with all Phase III components
- `backend/config.py` - Configuration with Ollama settings, memory limits
- `backend/gadgetmart_facts.txt` - Fixed store facts (separate from code)
- `backend/ollama_client.py` - HTTP client using /api/chat endpoint
- `backend/prompt_builder.py` - System prompt construction, history trimming, session summaries
- `backend/conversation_manager.py` - Session orchestration with thread-safe turn-taking
- `backend/cli_test.py` - Interactive CLI test harness
- `backend/requirements.txt` - Python dependencies
- `backend/README.md` - Complete Phase III documentation
- `tests/test_conversation_manager.py` - Pytest tests for sessions, trimming, isolation
- `tests/test_prompt_builder.py` - Pytest tests for prompt building, summaries
- Updated main `README.md` with Phase III setup instructions

**Key Implementation Details:**
- In-memory session storage using dictionary
- Per-session threading.Lock() for turn-taking guard
- Ollama /api/chat endpoint (structured messages)
- Session summary tracks: current product, tracking status, return type
- Never summarizes claimed order status as verified
- History trimming removes oldest complete turn pairs
- Temperature=0 for deterministic responses
- num_ctx=4096 (explicit context window)
- Stream support designed in, implementation deferred to Phase IV

**Compliance Check:**
✅ No tools, agents, plugins, or RAG  
✅ No persistent database (in-memory only)  
✅ Fixed GadgetMart facts (no retrieval)  
✅ Structured prompts with conversation history  
✅ Turn-taking logic (thread-safe)  
✅ Context faithfulness (session summaries)  
✅ Bounded memory with trimming  

**Rationale:**
Phase III provides the core conversation orchestration needed before adding the WebSocket API in Phase IV. Separation of concerns (manager, prompt builder, client) makes the system testable and allows Phase IV to add streaming without rewriting the core logic. The CLI harness enables manual multi-turn testing while pytest tests catch regressions in key behaviors (trimming, isolation, reset).

---

## Phase IV - Backend API Implementation

*(Prompts will be added as Phase IV begins)*

---
