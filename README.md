# E-Commerce Order Support Assistant

**Assignment 1 - NLP Course**  
**Domain:** E-Commerce Customer Support (Product Info, Shipping/Return Policy, Order Tracking Guidance)  
**Status:** Phase 0 - Repository Setup Complete

---

## Project Overview

This is a CPU-only, local conversational AI assistant for a fictional e-commerce store. It provides:

- **Product information** from a fixed catalog
- **Shipping and return policy** explanations
- **Order tracking guidance** (explains how to track and interprets user-supplied status messages)
- **Multi-turn conversation** with session memory
- **Streaming responses** via WebSocket

### Important Limitations

⚠️ **What This System Does NOT Do:**
- No live order database lookup or API integration
- No real-time inventory checks
- No return processing, refund approval, or shipment modifications
- No customer account access or authentication
- No retrieval-augmented generation (RAG) or tool use
- No cloud-based model inference

All responses come from:
1. Fixed store facts and policies embedded in the system prompt
2. User-supplied information within the conversation session
3. Local CPU inference using a quantized open-weight model

---

## Technology Stack (Planned)

- **Model:** TBD (Qwen 2.5 1.5B Instruct or Phi3 3.8B, Q4 quantization)
- **Inference:** Ollama (local CPU-only)
- **Backend:** FastAPI + WebSocket
- **Frontend:** Simple HTML/CSS/JavaScript chat interface
- **Deployment Bonus:** Vercel (planned)

---

## Repository Structure

```
/
├── backend/          (Phase IV - FastAPI application)
├── frontend/         (Phase V - Web chat UI)
├── scripts/          (Phase II - Benchmark and testing scripts)
├── docs/             (Documentation and planning artifacts)
│   ├── assignment-checklist.md
│   └── prompts.md
└── README.md         (This file)
```

---

## Development Phases

- [x] **Phase 0:** Repository setup and compliance baseline
- [ ] **Phase I:** Business case, store facts, and conversation design
- [ ] **Phase II:** Model selection and benchmarking
- [ ] **Phase III:** Conversation manager and prompt orchestration
- [ ] **Phase IV:** FastAPI backend with WebSocket streaming
- [ ] **Phase V:** Web-based chat interface
- [ ] **Phase VI:** Testing, evaluation, and final documentation

---

## Setup Instructions

*(Will be added after implementation phases)*

---

## Architecture

*(Will be added after Phase III)*

---

## Model Selection & Benchmarks

*(Will be added after Phase II)*

---

## Example Conversations

*(Will be added after Phase I)*

---

## API Documentation

*(Will be added after Phase IV)*

---

## Testing & Evaluation

*(Will be added after Phase VI)*

---

## Known Limitations

*(Will be documented during implementation)*

---

## License

This is an academic project for coursework. Not for production use.

---

## Acknowledgments

Built as part of NLP course Assignment 1.
