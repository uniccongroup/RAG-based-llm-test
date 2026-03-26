# Architecture Documentation

## System Overview

The Academy X RAG-based LLM Chatbot is a modern, distributed system that combines Large Language Models with Retrieval-Augmented Generation to provide accurate, contextually relevant answers to FAQs.

```
┌─────────────────────────────────────────────────────────────────┐
│                          Client Layer                            │
│    (Web UI, Mobile App, API Consumers)                           │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    API Gateway Layer                             │
│  • CORS Middleware                                              │
│  • Rate Limiting                                                │
│  • Authentication                                               │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    FastAPI Application                           │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │              API Endpoints Layer                            │ │
│  │  • /api/health          - Health checks                   │ │
│  │  • /api/chat            - Main chat endpoint              │ │
│  │  • /api/upload          - Document upload                │ │
│  │  • /api/index-status    - Index information              │ │
│  └────────────────────────────────────────────────────────────┘ │
│                              │                                    │
│                              ▼                                    │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │              RAG Service Layer                              │ │
│  │  (Core Business Logic)                                      │ │
│  │                                                              │ │
│  │  ┌──────────────────────────────────────────────────────┐  │ │
│  │  │  RAG Service                                          │  │ │
│  │  │  • Orchestrates the RAG pipeline                      │  │ │
│  │  │  • Coordinates retrieval & generation                │  │ │
│  │  │  • Manages context assembly                          │  │ │
│  │  │  • Handles session management                        │  │ │
│  │  └──────────────────────────────────────────────────────┘  │ │
│  │           │                    │                             │ │
│  │           ▼                    ▼                             │ │
│  │  ┌──────────────────────┐  ┌──────────────────────┐         │ │
│  │  │  Retrieval Service   │  │   LLM Service       │         │ │
│  │  │  • Query embedding   │  │  • Multi-provider   │         │ │
│  │  │  • Vector search     │  │  • Response gen     │         │ │
│  │  │  • Result ranking    │  │  • Prompt building  │         │ │
│  │  └──────────────────────┘  └──────────────────────┘         │ │
│  │                                                              │ │
│  └────────────────────────────────────────────────────────────┘ │
│                              │                                    │
│                              ▼                                    │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │           Data Processing Layer                             │ │
│  │                                                              │ │
│  │  ┌─────────────────────────────────────────────────────┐   │ │
│  │  │  Vector Store (In-Memory)                           │   │ │
│  │  │  • FAISS Index                                      │   │ │
│  │  │  • Document Embeddings                              │   │ │
│  │  │  • Similarity Search (O(log n))                     │   │ │
│  │  └─────────────────────────────────────────────────────┘   │ │
│  │                                                              │ │
│  │  ┌─────────────────────────────────────────────────────┐   │ │
│  │  │  Embedding Model                                    │   │ │
│  │  │  • Sentence Transformers                            │   │ │
│  │  │  • all-MiniLM-L6-v2 (default)                       │   │ │
│  │  │  • Generates embeddings for chunks & queries        │   │ │
│  │  └─────────────────────────────────────────────────────┘   │ │
│  │                                                              │ │
│  │  ┌─────────────────────────────────────────────────────┐   │ │
│  │  │  Text Chunking                                      │   │ │
│  │  │  • Splits documents into chunks                     │   │ │
│  │  │  • Handles overlapping sections                     │   │ │
│  │  │  • Preserves context                                │   │ │
│  │  └─────────────────────────────────────────────────────┘   │ │
│  │                                                              │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    External Services                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ Hugging Face │  │   OpenAI     │  │   Cohere     │          │
│  │  (LLMs)      │  │  (GPT-3.5)   │  │  (Command)   │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Storage Layer                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  File System Storage                                      │  │
│  │  • data/index.pkl - Serialized FAISS index              │  │
│  │  • logs/app.log - Application logs                      │  │
│  │  • .env - Configuration                                 │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Core Components

### 1. API Layer (`app/api/`)

**Files**: `chat.py`, `router.py`

**Responsibilities**:
- Handle HTTP requests/responses
- Request validation using Pydantic
- Error handling and response formatting
- Route management

**Key Endpoints**:
- `POST /api/chat` - Main chat interface
- `POST /api/upload-documents` - Document ingestion
- `GET /api/health` - Health check
- `GET /api/index-status` - Index status

### 2. RAG Service (`app/services/rag_service.py`)

**Responsibilities**:
- Orchestrates the RAG pipeline
- Manages retrieval and generation
- Assembles context for LLM
- Maintains service state

**Key Methods**:
```python
def index_documents(documents: List[str]) -> int
def retrieve(query: str) -> List[Tuple[str, float]]
def generate_answer(query: str, context: str) -> str
def answer_question(query: str) -> Tuple[str, List[str], float]
```

**RAG Pipeline**:
```
User Query
    ↓
Query Encoding (Embedding)
    ↓
Vector Search (Retrieval)
    ↓
Context Assembly
    ↓
Prompt Building
    ↓
LLM Generation
    ↓
Response Formatting
    ↓
Response to User
```

### 3. Vector Store (`app/services/vector_store.py`)

**Technology**: FAISS (Facebook AI Similarity Search)

**Responsibilities**:
- Manage document embeddings
- Perform efficient similarity search
- Persist and load indices
- Handle in-memory vector operations

**Operations**:
- `add_documents(docs)` - Add embedded documents
- `search(query, top_k)` - Find similar documents
- `save(path)` - Persist to disk
- `load(path)` - Load from disk

**Complexity**:
- Document addition: O(n) where n = number of documents
- Search: O(log n) with FAISS
- Memory: O(n * d) where d = embedding dimension (384 for all-MiniLM-L6-v2)

### 4. LLM Service (`app/services/llm_service.py`)

**Supported Providers**:
- **Hugging Face** (Default, Free)
- **OpenAI** (GPT-3.5, GPT-4)
- **Cohere** (Command models)
- **Mock** (Testing)

**Responsibilities**:
- Initialize LLM provider
- Build prompts
- Generate responses
- Handle provider-specific APIs

**Initialization Strategy**:
```
Try Configured Provider
    ↓
Success? → Use it
    ↓
Failure → Try next provider
    ↓
All failed → Use Mock LLM
```

### 5. Text Chunking (`app/services/chunking.py`)

**Responsibilities**:
- Split documents into manageable chunks
- Maintain semantic coherence
- Preserve context with overlaps

**Configuration**:
```
CHUNK_SIZE: 500 characters
CHUNK_OVERLAP: 50 characters
Result: ~50-100 token chunks (suitable for embeddings)
```

**Example**:
```
Document: "Lorem ipsum dolor sit amet consectetur..."
    ↓
Chunk 1: "Lorem ipsum dolor sit amet..." (0-500)
Chunk 2: "sit amet consectetur..." (450-950) ← 50 char overlap
Chunk 3: "adipiscing elit sed do..." (900-1400)
```

### 6. Configuration (`app/core/config.py`)

**Responsibilities**:
- Load environment variables
- Provide default configurations
- Validate settings

**Key Settings**:
- `LLM_PROVIDER` - Which LLM to use
- `CHUNK_SIZE/OVERLAP` - Text processing params
- `TOP_K_RETRIEVAL` - Number of docs to retrieve
- `SIMILARITY_THRESHOLD` - Minimum relevance score

### 7. Logging (`app/core/logger.py`)

**Responsibilities**:
- Setup application logging
- Configure file and console output
- Format log messages

**Log Levels**:
- DEBUG - Detailed information
- INFO - General information
- WARNING - Warning messages
- ERROR - Error messages
- CRITICAL - Critical errors

---

## Data Flow Diagrams

### Chat Request Flow

```
Client Request: POST /api/chat
    ↓
[Request Validation]
    ↓ Valid
[RAG Service: answer_question()]
    ├─→ [Vector Store: search(query)]
    │       ├─→ [Encode query]
    │       ├─→ [Search FAISS index]
    │       └─→ Return similar docs
    │
    ├─→ [Filter by threshold]
    │
    ├─→ [Assemble context]
    │
    └─→ [LLM Service: generate()]
            ├─→ [Build prompt]
            └─→ [Call LLM provider]
    ↓
[Format response]
    ↓
HTTP 200 OK + JSON Response
```

### Document Upload Flow

```
Client Request: POST /api/upload-documents (files)
    ↓
[Validate files]
    ├─ Check file type
    ├─ Check file size
    └─ Decode file content
    ↓
[For each document]
    ├─→ [Chunking Service: chunk_text()]
    │   └─→ Split into overlapping chunks
    │
    ├─→ [Embedding Model: encode()]
    │   └─→ Generate embeddings for chunks
    │
    └─→ [Vector Store: add_documents()]
            └─→ Add to FAISS index
    ↓
[Persist index to disk]
    ↓
[Return summary]
    ↓
HTTP 200 OK + JSON Response
```

### Initialization Flow

```
Application Start
    ↓
[Load Configuration from .env]
    ↓
[Initialize Logger]
    ↓
[Initialize RAG Service]
    ├─→ [Initialize Vector Store]
    │   └─→ Create FAISS index
    │
    ├─→ [Initialize LLM Service]
    │   └─→ Connect to LLM provider
    │
    └─→ [Load persisted index if exists]
    ↓
[Start FastAPI application]
    ↓
Ready to handle requests
```

---

## Design Patterns

### 1. Singleton Pattern
- **RAG Service**: Single instance shared across requests
- **Configuration**: Single instance of settings

### 2. Factory Pattern
- **LLM Service**: Creates appropriate LLM based on provider config

### 3. Service Layer Pattern
- Separates business logic (services) from API layer
- Easier testing and reusability

### 4. Dependency Injection
- RAG service injected into API routes
- Loose coupling between components

---

## Scalability Considerations

### Current Limitations
- **Single instance**: Not distributed
- **In-memory storage**: Limited by available RAM
- **Sequential processing**: No parallel requests handling

### Scaling Strategies

#### Horizontal Scaling
```
Load Balancer (Nginx/HAProxy)
    ↓
┌──────────┬──────────┬──────────┐
↓          ↓          ↓
API Pod 1  API Pod 2  API Pod 3
(FastAPI)  (FastAPI)  (FastAPI)
    ↓          ↓          ↓
    └──────────┬──────────┘
              ↓
      Shared Vector Database
      (Pinecone/Weaviate/Milvus)
```

#### Vector Database Migration
```
Current: In-memory FAISS
    ↓ Scale
Target: Cloud Vector DB
    • Pinecone (serverless)
    • Weaviate (self-hosted/cloud)
    • Milvus (self-hosted)
    • Qdrant
    • Chroma
```

#### Caching Layer
```
Request
    ↓
Check Cache (Redis)
    ├─ Hit → Return cached response
    └─ Miss → Process & cache result
```

---

## Security Considerations

### Current Status
- ✅ CORS enabled for all origins
- ✅ Input validation via Pydantic
- ✅ Error handling without info leakage
- ⚠️ No authentication
- ⚠️ No rate limiting
- ⚠️ No input sanitization for LLM injection

### Recommendations

1. **Authentication**
   - Implement JWT tokens
   - Add API key management

2. **Authorization**
   - Role-based access control
   - Document-level permissions

3. **Rate Limiting**
   - Per-IP rate limits
   - Per-user quotas
   - Token bucket algorithm

4. **Input Validation**
   - Sanitize LLM prompts
   - Prevent injection attacks
   - Validate file uploads

5. **Data Protection**
   - Encrypt sensitive data
   - Use HTTPS only
   - Implement audit logging

---

## Performance Optimization

### Current Performance
- Health check: ~1ms
- Chat with cached index: ~200-500ms
- Document upload: ~100ms per document (depends on size)
- LLM call: ~1-5s (depends on provider and model)

### Optimization Opportunities

1. **Caching**
   ```python
   # Cache frequent queries
   @cache(ttl=3600)  # 1 hour
   def answer_question(query: str) -> str:
       pass
   ```

2. **Batch Processing**
   ```python
   # Batch multiple queries
   def answer_batch(queries: List[str]) -> List[str]:
       pass
   ```

3. **Async Operations**
   ```python
   # Already using async/await
   async def chat(request: ChatRequest) -> ChatResponse:
       pass
   ```

4. **Index Optimization**
   - Use GPU acceleration: `faiss.GPU_DEFAULT_CONFIG`
   - Implement index compression
   - Use quantization

---

## Testing Strategy

### Unit Tests
- Test individual services
- Mock external dependencies
- Validate business logic

### Integration Tests
- Test service interactions
- Use test database
- Validate end-to-end flows

### API Tests (`test_api.py`)
- Test all endpoints
- Validate request/response schemas
- Check error handling

### Performance Tests
- Load testing with multiple concurrent requests
- Benchmark query response times
- Memory profiling

---

## Deployment Architecture

### Development
```
Single machine
    ↓
FastAPI + Uvicorn
    ↓
Local file storage
```

### Staging
```
Docker container
    ↓
Docker Compose + Nginx
    ↓
Persistent volume storage
```

### Production
```
Kubernetes cluster / Cloud platform
    ↓
Load balancer → Multiple replicas
    ↓
Cloud vector database
    ↓
CDN + Monitoring + Logging
```

---

## Monitoring & Observability

### Metrics to Track
- Request latency (p50, p95, p99)
- Error rates
- Document indexing speed
- LLM API costs
- Cache hit rate

### Logging
- Application logs in `logs/app.log`
- Request/response logging
- Error stack traces
- Performance metrics

### Recommended Tools
- **Monitoring**: Prometheus + Grafana
- **Logging**: ELK Stack or Datadog
- **Tracing**: Jaeger or Datadog APM
- **Error Tracking**: Sentry

---

## Future Enhancements

### Phase 2
- [ ] Conversation history management
- [ ] Multi-turn dialogue support
- [ ] User feedback mechanism
- [ ] Analytics dashboard

### Phase 3
- [ ] Multi-language support
- [ ] Document versioning
- [ ] Fine-tuning on Academy X data
- [ ] Reranking with cross-encoders

### Phase 4
- [ ] Multi-modal support (images, audio)
- [ ] Real-time streaming responses
- [ ] Advanced semantic search (metadata filtering)
- [ ] Hybrid search (keyword + semantic)

---

## Technology Stack Rationale

| Component | Technology | Why? |
|-----------|-----------|------|
| Framework | FastAPI | Modern, async, automatic docs |
| Server | Uvicorn | ASGI, high performance |
| Embeddings | Sentence Transformers | Lightweight, accurate |
| Vector Search | FAISS | Fast, efficient, scalable |
| LLM Integration | LangChain | Unified provider interface |
| Validation | Pydantic | Type safety, serialization |
| Logging | Python logging | Standard, no external deps |

---

**This architecture is designed to be scalable, maintainable, and production-ready!**
