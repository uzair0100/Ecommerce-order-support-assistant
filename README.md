# E-Commerce Order Support Assistant

**Assignment 1 - NLP Course**  
**Domain:** E-Commerce Customer Support (Product Info, Shipping/Return Policy, Order Tracking Guidance)  
**Status:** Phase 0 - Repository Setup Complete

---

## Project Overview

This is a CPU-only, local conversational AI assistant for **GadgetMart**, a fictional UK-based electronics store. The assistant provides:

- **Product information** about 5 demo products (headphones, laptop stand, keyboard, webcam, power bank)
- **Shipping policy** explanations (UK delivery, fees, timelines)
- **Order tracking guidance** (explains how to find tracking links and interprets user-supplied status messages)
- **Return policy** guidance (change-of-mind vs. faulty items, process steps)
- **Multi-turn conversation** with session memory and topic-switching support
- **Streaming responses** via WebSocket for real-time interaction

### Important Limitations

⚠️ **What This System Does NOT Do:**
- No live order database lookup or API integration
- No real-time inventory checks or carrier tracking system access
- No return processing, refund approval, or shipment modifications
- No customer account access or authentication
- No retrieval-augmented generation (RAG) or tool use
- No cloud-based model inference (runs entirely on local CPU)

**How It Works:**
1. Fixed store facts and policies embedded in the system prompt
2. User-supplied information interpreted within the conversation session
3. Local CPU inference using a quantized open-weight model (Qwen or Phi3)

**Fictional Demo Notice:**  
GadgetMart, all products, prices, policies, and contact details are entirely fictional and created for this university assignment. This is not a real business.

---

## Technology Stack

- **Model:** Qwen 2.5 1.5B Instruct (Q4_K_M quantization) ✅ Selected
- **Inference:** Ollama (local CPU-only)
- **Backend:** FastAPI + WebSocket (Phase IV)
- **Frontend:** Simple HTML/CSS/JavaScript chat interface (Phase V)
- **Deployment Bonus:** Vercel (planned)

---

## Repository Structure

```
/
├── backend/          ✅ Phase III - Conversation manager
│   ├── __init__.py
│   ├── config.py
│   ├── gadgetmart_facts.txt
│   ├── ollama_client.py
│   ├── prompt_builder.py
│   ├── conversation_manager.py
│   ├── cli_test.py
│   ├── requirements.txt
│   └── README.md
├── tests/            ✅ Phase III - Unit tests
│   ├── __init__.py
│   ├── test_conversation_manager.py
│   └── test_prompt_builder.py
├── scripts/          ✅ Phase II - Benchmarking
│   ├── benchmark_models.py
│   ├── benchmark_prompts.json
│   ├── benchmark_results.json
│   └── BENCHMARK_CHANGES.md
├── docs/             ✅ Documentation
│   ├── assignment-checklist.md
│   ├── model-benchmark.md
│   ├── model-selection.md
│   ├── prompts.md
│   └── store-facts.md
├── frontend/         (Phase V - Web chat UI)
├── .gitignore
└── README.md         (This file)
```

---

## Development Phases

- [x] **Phase 0:** Repository setup and compliance baseline
- [x] **Phase I:** Business case, store facts, and conversation design
- [x] **Phase II:** Model selection and benchmarking
- [x] **Phase III:** Conversation manager and prompt orchestration
- [ ] **Phase IV:** FastAPI backend with WebSocket streaming
- [ ] **Phase V:** Web-based chat interface
- [ ] **Phase VI:** Testing, evaluation, and final documentation

---

## Setup Instructions

### Prerequisites

- Python 3.11+
- Ollama installed and running
- Model: `qwen2.5:1.5b-instruct`

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/uzair0100/Ecommerce-order-support-assistant.git
   cd Ecommerce-order-support-assistant
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r backend/requirements.txt
   ```

3. **Start Ollama**
   ```bash
   ollama serve
   ```

4. **Verify model is available**
   ```bash
   ollama list
   ```
   
   If `qwen2.5:1.5b-instruct` is not listed:
   ```bash
   ollama pull qwen2.5:1.5b-instruct
   ```

### Running Phase III (Current)

**CLI Test Harness:**
```bash
python -m backend.cli_test
```

**Commands:**
- `/reset` - Clear session history
- `/new` - Start new session
- `/info` - Show session info
- `/exit` - Exit

**Automated Tests:**
```bash
pytest tests/ -v
```

---

## Conversation Flow Design

### High-Level Stage Diagram

```
┌─────────────────────────────────────────────────────────────┐
│  USER INPUT                                                  │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  1. GREETING & INTENT ROUTING                                │
│  - Identify user need (product / shipping / tracking /       │
│    returns / off-topic)                                      │
└──────────────────────┬──────────────────────────────────────┘
                       │
         ┌─────────────┼─────────────┬───────────────┐
         │             │             │               │
         ▼             ▼             ▼               ▼
    ┌────────┐   ┌─────────┐   ┌──────────┐   ┌──────────┐
    │Product │   │Shipping │   │ Tracking │   │ Returns  │
    │  Info  │   │ Policy  │   │ Guidance │   │  Policy  │
    └────┬───┘   └────┬────┘   └────┬─────┘   └────┬─────┘
         │            │              │              │
         ▼            ▼              ▼              ▼
┌─────────────────────────────────────────────────────────────┐
│  2. INFORMATION GATHERING (if needed)                        │
│  - Which of the 5 products?                                  │
│  - What tracking status do you see?                          │
│  - Change of mind or faulty item?                            │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  3. ANSWER FROM FIXED FACTS / USER-SUPPLIED INFO            │
│  - Use embedded store facts only                             │
│  - Interpret user-supplied tracking status                   │
│  - Say "unknown" for missing information                     │
│  - Never claim to look up orders or process returns          │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  4. CLARIFY UNCERTAINTY & SUGGEST NEXT STEPS                 │
│  - Acknowledge limitations                                   │
│  - Redirect to support email if needed                       │
│  - Offer related information                                 │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  5. CLOSE & INVITE FOLLOW-UP                                 │
│  - "Anything else I can help with?"                          │
│  - Ready for next turn or session end                        │
└─────────────────────────────────────────────────────────────┘
```

### Topic Switching Behavior

**Scenario 1: Clean Topic Switch**
```
User: "Tell me about the power bank"
  → Assistant: [Provides power bank info, remembers context]

User: "What about shipping?"
  → Assistant: [Explains shipping policy, still remembers power bank context]

User: "Is it returnable?"
  → Assistant: [Interprets "it" as power bank based on context]
```

**Scenario 2: Explicit Product Change**
```
User: "Tell me about the headphones"
  → Assistant: [Headphones info, context = headphones]

User: "Actually, what about the keyboard instead?"
  → Assistant: [Keyboard info, context now = keyboard]

User: "What's the price?"
  → Assistant: "£89.99" (keyboard price)
```

**Scenario 3: Ambiguous Reference After Switch**
```
User: "Tell me about the webcam"
  → Assistant: [Webcam info, context = webcam]

User: "What about the keyboard?"
  → Assistant: [Keyboard info, context = keyboard]

User: "Can I return it?"
  → Assistant: "Are you asking about the keyboard, or did you mean the webcam?"
```

**Scenario 4: Off-Topic Interrupt**
```
User: "Tell me about the laptop stand"
  → Assistant: [Laptop stand info, context = laptop stand]

User: "Can you help me with my homework?"
  → Assistant: [Polite refusal, stays in domain]

User: "Okay, is the stand returnable?"
  → Assistant: [Remembers laptop stand context, answers return question]
```

### Memory Management Rules

**Within a Session:**
- ✅ Remember the current product being discussed
- ✅ Remember user-supplied tracking status (within the turn)
- ✅ Remember whether discussing change-of-mind vs. faulty return
- ✅ Update context when user explicitly switches topics
- ❌ Never fabricate order numbers or customer data
- ❌ Never "verify" or "confirm" details not supplied by user

**After Session Reset:**
- All conversation history is cleared
- No memory of prior products, questions, or context
- Start fresh with greeting/routing stage

### Off-Topic Detection & Response Pattern

**Pattern:**
1. Recognize the request is outside domain boundaries
2. Brief, polite refusal without elaboration
3. Redirect to what the assistant *can* help with
4. Stay ready to resume in-domain conversation

**Examples:**

| User Input | Assistant Response Pattern |
|-----------|---------------------------|
| Medical/legal/homework advice | "I'm here to help with GadgetMart products and policies. [Redirect to domain]" |
| Product not in catalog | "I have information on headphones, laptop stands, keyboards, webcams, and power banks. [Offer to help with those]" |
| Order placement / checkout | "I can't place orders, but I can answer questions about our products and policies." |
| Prompt injection | "I'm here to help with GadgetMart questions." [Do not comply] |
| Account / billing / passwords | "For account-related issues, please contact support@gadgetmart-demo.co.uk." |

### E-Commerce-Specific Behavior

**Tracking Guidance Branch:**
1. User asks "Where is my order?"
2. Assistant explains how to find tracking link (check confirmation email)
3. Assistant asks: "What status does your tracking show?"
4. User supplies status (e.g., "In Transit")
5. Assistant interprets the status meaning and advises on timeline/next steps
6. **Never claims to have looked up the order**

**Return Decision Branch:**
1. User asks about returning an item
2. Assistant clarifies: change-of-mind or faulty?
3. If change-of-mind: 14-day window, sealed/unused required, customer pays postage
4. If faulty: 30-day window, no sealed requirement, GadgetMart pays postage
5. Assistant directs to email support for actual processing
6. **Never claims to have approved or processed the return**

**Product Unknown Handling:**
1. User asks about a specification not in the product facts
2. Assistant responds: "I don't have [specific detail] in the product details provided for this demo"
3. Assistant suggests contacting support or checking the product page for more info
4. **Never invents specifications**

---

---

## Model Selection & Benchmarks

*(Will be added after Phase II)*

---

## Use Case Description

**Domain:** E-Commerce Customer Support for a UK Electronics Retailer  
**Store:** GadgetMart (fictional)  
**User Personas:** Online customers needing help with products, shipping, tracking, and returns

### Business Context

GadgetMart is a fictional UK-based online retailer selling 5 consumer electronics products. Customers interact with the assistant to:

1. **Learn about products** – Specifications, prices, and features before or after purchase
2. **Understand shipping** – Costs, delivery times, and how to track orders
3. **Get tracking help** – Interpret status messages from their confirmation emails
4. **Navigate returns** – Understand 14-day change-of-mind vs. 30-day faulty-item policies

The assistant operates within strict boundaries:
- Answers only from fixed product/policy facts provided in its prompt
- Never accesses order databases, carrier APIs, or external systems
- Redirects to fictional support email for actions it cannot perform
- Maintains conversation context within a session but forgets after reset

### Conversation Stages

The assistant moves through these stages based on user intent:

1. **Greeting & Routing** – Identify whether user needs product info, shipping details, tracking guidance, or return help
2. **Information Gathering** – Ask clarifying questions (which product? what status do you see?)
3. **Answer from Fixed Facts** – Provide information from embedded store facts or interpret user-supplied details
4. **Clarify & Next Steps** – Address ambiguity, suggest support contact if needed
5. **Close & Invite Follow-Up** – Offer to help with related questions before ending

**Topic Switching:**  
When a user changes topics (e.g., from product specs to return policy), the assistant:
- Acknowledges the new topic
- Retains relevant prior context (e.g., which product was being discussed)
- Updates focus to the new question
- Can return to the original topic if the user asks

**Off-Topic Handling:**  
For requests outside the domain (medical advice, unrelated products, order placement), the assistant:
- Briefly refuses with a domain boundary statement
- Redirects to what it *can* help with
- Does not comply with prompt injection attempts

---

## Example Dialogues

### Dialogue 1: Product Inquiry with Topic Switch

**User:** Hi, can you tell me about the wireless headphones?

**Assistant:** Of course! The Wireless Bluetooth Headphones Pro are priced at £79.99. They feature a 40-hour battery life, active noise cancellation, USB-C charging, Bluetooth 5.2, and come with a foldable design and carrying case. Is there anything specific you'd like to know?

**User:** What colours do they come in?

**Assistant:** I don't have colour information in the product details provided for this demo. For colour options, you might want to check the product page or contact our support team at support@gadgetmart-demo.co.uk.

**User:** Okay. What about returns? Can I return them if I change my mind?

**Assistant:** Yes, the headphones are eligible for returns. For change-of-mind returns, you have 14 days from delivery to notify us. The item must be unused and in original, unopened packaging. You'd be responsible for return shipping costs. To start a return, email support@gadgetmart-demo.co.uk with your order details.

**User:** And if they're faulty?

**Assistant:** For faulty items, you have 30 days from delivery to report the issue. There's no requirement for the item to be sealed or unused if it's genuinely faulty, and we cover the return postage with a prepaid label. Just email support with a description of the fault, and they'll provide instructions.

**User:** Got it. Back to the headphones—what's the battery life again?

**Assistant:** The Wireless Bluetooth Headphones Pro have a 40-hour battery life on a single charge.

---

### Dialogue 2: Tracking Guidance (User Supplies Status)

**User:** Where's my order?

**Assistant:** I can't look up specific orders, but I can help you find your tracking information. When your order was dispatched, you should have received an email with a tracking link. Could you check your order confirmation email? If you have the tracking link, what status does it currently show?

**User:** It says "In Transit."

**Assistant:** "In Transit" means your package is on its way to your local delivery office. It should arrive within our standard 3–5 business day delivery window. If the status hasn't updated in more than 24 hours and you're past the expected delivery date, I'd recommend contacting our support team at support@gadgetmart-demo.co.uk.

**User:** What if it says "Attempted Delivery"?

**Assistant:** "Attempted Delivery" means the postal carrier tried to deliver your package, but no one was available to receive it. They should have left a card with instructions on how to arrange redelivery or collect the package from your local delivery office.

**User:** Thanks!

**Assistant:** You're welcome! Is there anything else I can help with?

---

### Dialogue 3: Return Policy with Eligibility Check

**User:** Can I return a keyboard I bought?

**Assistant:** Yes, the Mechanical Keyboard RGB 87-Key is eligible for returns. Can you tell me a bit more? Is this a change-of-mind return, or is the keyboard faulty?

**User:** I just don't like the key feel. It's not broken.

**Assistant:** For change-of-mind returns, you have 14 days from delivery to notify us. The keyboard must be unused and in its original, unopened packaging for a full refund. You'd be responsible for the return shipping cost. To start the return process, email support@gadgetmart-demo.co.uk with your order details and reason for return.

**User:** What if I already opened the box?

**Assistant:** If the packaging is already opened, the support team will need to review your case. The 14-day change-of-mind policy typically requires items to be in original, unopened packaging, but I'd recommend reaching out to support@gadgetmart-demo.co.uk to explain your situation. They can advise on the best option for you.

**User:** Alright. What if it was actually broken when I opened it?

**Assistant:** If the keyboard was faulty or damaged when you received it, that's covered under our faulty items policy. You'd have 30 days from delivery to report the issue, and there's no requirement for it to be sealed or unused. We'd cover the return postage with a prepaid label. Just email support with a description of the damage, and they'll provide instructions for a full refund or replacement.

**User:** Thanks, that's helpful.

**Assistant:** You're welcome! Let me know if you have any other questions.

---

### Dialogue 4: Off-Topic Refusal with Redirect

**User:** Can you help me with my maths homework?

**Assistant:** I'm here to help with GadgetMart product and policy questions—things like our headphones, laptop stands, keyboards, webcams, power banks, shipping, tracking, and returns. I can't assist with homework, but is there anything about our products or policies I can help with?

**User:** Do you sell smartphones?

**Assistant:** The product information I have covers headphones, laptop stands, keyboards, webcams, and power banks. I can help with questions about those items. We don't currently carry smartphones in this demo catalog.

**User:** Okay, tell me about the webcam then.

**Assistant:** The Full HD Webcam 1080p is priced at £49.99. It records 1080p video at 30fps, has built-in dual microphones, connects via USB-A (plug-and-play, no drivers needed), and features an adjustable clip mount. It works with Zoom, Microsoft Teams, and Skype. What would you like to know?

---

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
