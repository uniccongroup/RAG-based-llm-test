# Design Philosophy

## The Case for Simplicity in RAG Systems

### Why Not Microservices?

This chatbot doesn't need 10 services talking to each other. A single, well-structured FastAPI app is:
- **Faster** (no network hops)
- **Easier to deploy** (one container)
- **Simpler to debug** (one log file)

### Why Flat Structure?

```text
app/
├── rag/ # All RAG logic together - easy to trace
├── models/ # Simple schemas - no ORM needed
├── data/ # Knowledge base - visible and editable
└── main.py # Entry point - clear and concise
```

### Why Not Dependency Injection?

While DI is valuable in large systems, this project benefits from:
- **Explicit imports** - see exactly what each file uses
- **No magic** - everything is where you expect it
- **Easy refactoring** - change one file, see immediate impact

### When Would I Add Complexity?

Complexity is introduced **only when it solves a real problem**:

| Complexity | Added When |
|------------|------------|
| Multiple LLM providers | Second provider is needed |
| Message queues | Asynchronous processing required |
| Redis cache | 100+ QPS with latency requirements |
| Service abstraction | Second similar service emerges |

### The Result
A codebase that:
- **Works** (tested and proven)
- **Is maintainable** (any developer can modify it)
- **Is extensible** (can evolve with requirements)
- **Is understandable** (no hidden complexity)

___

## Model Selection: gpt2-medium

**Chosen for the right balance of capability and constraints:**

| Factor | Why gpt2-medium? |
|--------|------------------|
| **Resources** | Runs on 2GB RAM, no GPU needed |
| **Speed** | 500-1000ms per query—real-time capable |
| **Cost** | $0—no API fees, fully local |
| **Privacy** | Data never leaves your infrastructure |
| **Accuracy** | Sufficient for FAQ tasks with RAG grounding |
| **Flexibility** | Model-agnostic—swap by changing .env |


**Trade-offs acknowledged:**
- Occasional hallucinations (acceptable for non-critical FAQs)
- Not instruction-tuned (mitigated by prompt engineering)
- Smaller context window (handled by RAG retrieval)
