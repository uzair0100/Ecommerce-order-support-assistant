# Final Model Selection

## Final Model Selection

### 1. Selected Model

The selected model for the GadgetMart E-Commerce Order Support Assistant is:

**Qwen2.5 1.5B Instruct**

Ollama model identifier:

```
qwen2.5:1.5b-instruct
```

The model uses Q4_K_M quantisation and contains approximately 1.5 billion parameters.

### 2. Candidates Considered

Two local LLMs were considered during the benchmarking phase:

- Qwen2.5 1.5B Instruct
- Phi-3 3.8B

Both models were executed locally using Ollama and CPU-only inference.

No cloud-based LLM API was used.

### 3. Selection Criteria

The final model was selected using the following criteria:

#### 3.1 Response correctness

The model must correctly answer questions about:

- Products
- Prices
- Product specifications
- Shipping
- Delivery
- Returns
- Tracking-status meanings

#### 3.2 Policy adherence

The model must follow the predefined GadgetMart policies rather than generating generic e-commerce policies.

#### 3.3 Hallucination control

The model should not invent:

- Product specifications
- Colours
- Order information
- Tracking information
- Refund information
- Store policies

#### 3.4 Capability honesty

The assistant must clearly state when it cannot perform an operation.

For example, it must not claim to have:

- Checked a customer's order
- Checked live tracking
- Processed a refund
- Created a return label
- Changed an order address

#### 3.5 Domain adherence

The assistant should remain focused on GadgetMart customer support.

It should not act as a general-purpose assistant for unrelated requests.

#### 3.6 Inference performance

Because the project must run locally on CPU hardware, inference speed is an important practical requirement.

A model that is technically capable but takes several minutes to respond is less suitable for an interactive customer-support application.

### 4. Hardware Environment

The final model was selected based on testing performed on the actual development machine.

| Component | Specification |
|-----------|--------------|
| CPU | Intel(R) Core(TM) i7-8650U CPU @ 1.90 GHz |
| RAM | 8 GB |
| GPU | Intel UHD Graphics 620 |
| Inference | 100% CPU |
| Ollama | 0.34.0 |
| Python | 3.11.9 |
| Operating System | Windows |

This is a relatively resource-constrained environment for running modern LLMs.

Consequently, a smaller model was preferred when its performance was sufficient for the assignment.

### 5. Why Qwen2.5 1.5B Was Selected

#### 5.1 Better inference speed

Qwen generally generated responses at approximately:

```
9–12 tokens/second
```

during the benchmark.

Phi-3 generally produced approximately:

```
3.8–4.8 tokens/second
```

for its completed tests.

This makes Qwen substantially more practical for interactive CPU-based inference.

#### 5.2 Lower resource requirements

Qwen contains approximately 1.5B parameters compared with Phi-3's 3.8B parameters.

The smaller model is better suited to the project's 8 GB RAM CPU-only environment.

A smaller model also reduces the computational burden of running multiple requests during development and testing.

#### 5.3 Complete benchmark execution

Qwen successfully completed all 12 benchmark prompts.

Phi-3 did not complete the full benchmark.

During the Phi-3 benchmark, P07 became stuck for an extended period. The benchmark had to be interrupted manually.

This was an important practical consideration because the final assistant is expected to respond interactively rather than remain occupied by a single request for an extended period.

#### 5.4 Sufficient instruction-following capability

Qwen successfully handled several important assistant requirements.

Examples include:

**Product information**

It correctly answered the headphone price and battery-life question.

**Catalogue restriction**

It correctly rejected smartphones because smartphones are outside the GadgetMart catalogue.

**Prompt injection**

It correctly resisted the request to ignore the system instructions and pretend that inventory had been checked.

**Delivery policy**

It correctly handled the standard dispatch and delivery policy in P12.

These results demonstrate that the model is capable of following the main system instructions sufficiently for the project.

### 6. Known Weaknesses

Qwen2.5 1.5B was not selected because it was perfect.

The benchmark identified several weaknesses.

**Shipping reasoning**

The model incorrectly calculated shipping for a £64.98 order.

The correct calculation is:

```
£34.99 + £29.99 = £64.98
```

Since GadgetMart provides free standard shipping for orders of £50 or more:

```
Shipping = Free
```

The model instead returned £4.99.

**Tracking capability**

The model incorrectly claimed information about a customer's order when given an order number.

This is a significant hallucination because the assistant has no live order-management capability.

**Return policies**

The model showed inconsistencies when explaining change-of-mind and faulty-item returns.

**Out-of-domain requests**

The model did not always maintain the GadgetMart-only scope when asked an unrelated question.

**Unsupported product information**

The model occasionally added information that was not included in the supplied store facts.

### 7. Mitigation Strategy

The identified weaknesses will be addressed through application-level controls and prompt engineering in later phases.

Possible mitigation strategies include:

- More explicit system-prompt instructions
- Clear separation of known and unknown information
- Stronger capability restrictions
- More explicit examples of correct and incorrect behaviour
- Conversation-manager rules
- Output validation for critical policy responses
- Testing with additional adversarial prompts

The model will not be allowed to access live order or payment systems in this assignment.

Therefore, when a user requests information that requires unavailable data, the assistant should clearly state the limitation and direct the customer to GadgetMart support.

### 8. Final Decision

Based on the benchmark, **Qwen2.5 1.5B Instruct** was selected as the final local LLM.

The decision was based on the overall balance of:

| Criterion | Qwen2.5 1.5B | Phi-3 3.8B |
|-----------|--------------|------------|
| Parameter size | 1.5B | 3.8B |
| Quantised | Yes | Yes |
| CPU inference | Yes | Yes |
| Benchmark completion | 12/12 | Incomplete |
| Typical generation speed | ~9–12 tok/s | ~3.8–4.8 tok/s |
| Basic product accuracy | Good | Good |
| Policy handling | Mixed | Mixed/Good on tested cases |
| Resource suitability | Better | Worse |
| Interactive CPU suitability | Better | Worse |

Although Phi-3 produced some strong individual responses, its inference performance was significantly slower on the available hardware.

For this project, practical local performance is important because the assistant must provide interactive responses through a web application.

Therefore, **Qwen2.5 1.5B** provides the best overall trade-off for the project's requirements and hardware.

### 9. Final Model Configuration

The selected model will be used through Ollama:

```
qwen2.5:1.5b-instruct
```

The benchmark used deterministic generation with:

```
temperature = 0
```

The model will receive the GadgetMart system prompt containing the store's catalogue, policies, capabilities, limitations, and behavioural rules.

The model will remain completely local and will not use a cloud LLM API.

### 10. Selection Summary

**Final choice: Qwen2.5 1.5B Instruct**

The model was selected because it:

- Fits the required local LLM approach
- Uses Q4 quantisation
- Runs on CPU
- Requires fewer resources than the 3.8B alternative
- Completed the full benchmark
- Provides substantially faster generation on the project hardware
- Demonstrated adequate instruction-following capability
- Is practical for integration into the remaining application phases

The benchmark also revealed areas requiring improvement, which will be considered during the conversation-manager and application-development phases.
