# Code Review — RAG-based LLM Chatbot Submissions

This document reviews three candidate branches against the project requirements:
a FastAPI RAG-powered FAQ chatbot backend for an EduTech organisation.

---

## Branch Summary

| Branch | Author | LLM | Vector Store | Status |
|--------|--------|-----|--------------|--------|
| `Namshima-Iordye` | Namshima Iordye | Google Gemini 2.5 Flash | AstraDB (cloud) | ✅ Functional |
| `john-eze` | John Eze | HuggingFace InferenceClient | FAISS / TF-IDF fallback | ✅ Functional |
| `vulkkan` | Vulkkan | gpt2-medium (local) | FAISS + local embeddings | ⚠️ Partially functional |

---

## Branch: `Namshima-Iordye`

### Architecture
- **Framework**: FastAPI with `asynccontextmanager` lifespan
- **Embeddings**: `sentence-transformers/all-MiniLM-L6-v2` via `langchain-huggingface`
- **Vector Store**: AstraDB (managed cloud vector DB via `langchain-astradb`)
- **LLM**: Google Gemini 2.5 Flash Lite via `langchain-google-genai`
- **Chain**: LangChain `RunnablePassthrough` | `ChatPromptTemplate` | `StrOutputParser`

### Strengths

1. **Robust prompt injection protection** — one of the strongest security implementations
   reviewed. The `INJECTION_PATTERNS` list covers English, French, and Spanish attack
   vectors, delimiter injection (`---`, `###`, `[INST]`), and role-play/persona hijacking.

2. **Output leakage detection** — `contains_leakage()` validates the LLM response before
   returning it to the client, acting as a safety net against accidental system-prompt
   leakage.

3. **Input sanitisation** — `sanitise_input()` strips angle brackets and common delimiter
   patterns before the question reaches the LLM.

4. **Hardened system prompt** — the 10-rule system prompt is thorough: language lock,
   scope restriction, identity lock, delimiter immunity, and multilingual protection.
   Graceful deflection is used instead of exposing that an attack was detected.

5. **Source name cleaning** — `clean_source_name()` strips internal filenames (e.g.
   `03_BrightPath_Student_Policies.docx` → `Student Policies`) before surfacing them
   to the UI, preventing metadata leakage via the response JSON.

6. **`@lru_cache` singletons** — embeddings, vector store, retriever, and chain are all
   lazily loaded and cached, avoiding redundant re-initialisation across requests.

7. **Pydantic-settings config** — all required secrets (`google_api_key`,
   `astra_db_api_endpoint`, `astra_db_application_token`) fail loudly on startup if
   missing, preventing silent misconfiguration.

### Issues

| Severity | Location | Issue |
|----------|----------|-------|
| Medium | `app/main.py` | `ChatRequest` has commented-out `min_length=0` and `max_length=500` — no upper-bound validation means a single request could pass an arbitrarily long question to the LLM, increasing cost and latency. Uncomment or set `max_length`. |
| Medium | `app/main.py` | `ChatResponse` does not expose retrieved sources in the API response. The `answer_question()` function returns `{"answer", "success", "sources"}` but the `ChatResponse` model only contains `answer`, `success`, `session_id`. Sources are silently dropped. |
| Low | `requirements.txt` | `torch==2.6.0+cpu` uses a platform-specific version suffix. This will fail on pip in non-CPU environments (e.g. Linux with CUDA, macOS Apple Silicon). Use `torch==2.6.0` or manage via a separate `torch` install step with the appropriate index URL. |
| Low | `app/rag.py` | The `format_docs` docstring mentions that "metadata is retrieved separately in `answer_question()`" but this is only true when calling `answer_question()` directly. The RAG chain itself (`get_rag_chain()`) could in principle be called alone and would include no source attribution. Consider adding a brief note in `get_rag_chain()` too. |
| Low | `app/main.py` | `@app.post("/api/chat")` calls `answer_question()` synchronously in a blocking manner inside an `async def` endpoint. Since `answer_question()` makes network calls to AstraDB and Gemini, this blocks the event loop. Wrap it with `asyncio.to_thread()` or use an async LangChain invocation (`chain.ainvoke()`). |
| Info | `app/rag.py` | `get_rag_chain()` re-instantiates `HuggingFaceEmbeddings` internally instead of calling `get_embeddings()`. This duplicates the loading step when both `get_embeddings()` and `get_rag_chain()` are called. |

### Recommendations

- Add `max_length=500` (or similar) back to `ChatRequest.question`.
- Add `sources: list[str]` to `ChatResponse` and pass them from `answer_question()`.
- Replace `chain.invoke(clean_question)` with `await chain.ainvoke(clean_question)` (or
  `asyncio.to_thread`) to avoid blocking the event loop.
- Add a `.env.example` file so contributors know which environment variables are required
  without having to read the Pydantic settings class.

---

## Branch: `john-eze`

### Architecture
- **Framework**: FastAPI with `asynccontextmanager` lifespan, separate `app/api/`,
  `app/core/`, `app/models/`, `app/services/` package structure
- **Embeddings**: `sentence-transformers/all-MiniLM-L6-v2` (FAISS primary) or TF-IDF
  (scikit-learn fallback — activates automatically when PyTorch/FAISS unavailable)
- **Vector Store**: In-memory FAISS index with pickle persistence; auto-falls back to
  TF-IDF
- **LLM**: HuggingFace `InferenceClient` (primary), OpenAI, Cohere, or MockLLM fallback
- **Chat Endpoint**: `POST /api/chat`

### Strengths

1. **Well-structured codebase** — clear separation of concerns into `api/`, `core/`,
   `models/`, and `services/` packages. Each layer has a single responsibility.

2. **Dual-backend vector store** — graceful automatic fallback from FAISS +
   sentence-transformers to TF-IDF when PyTorch is unavailable. This makes the service
   deployable in constrained environments without code changes.

3. **Multi-provider LLM support** — `LLMService` supports HuggingFace (via
   `InferenceClient`), OpenAI, and Cohere, with a `MockLLM` fallback for testing. The
   provider is configurable via `LLM_PROVIDER` env var.

4. **Greeting detection** — `_is_greeting()` short-circuits the vector store lookup for
   simple greetings, avoiding unnecessary retrieval overhead.

5. **Index persistence** — `save_index()` / `load_index()` allow the FAISS index to
   survive restarts, avoiding re-indexing on every startup.

6. **`/api/upload-documents` endpoint** — allows new FAQ documents to be ingested without
   restarting the service, satisfying the project's real-time update requirement.

7. **ARCHITECTURE.md** — thorough documentation of the system design decisions.

8. **`test_api.py`** — includes a test suite covering health, chat, empty input, and
   index status, making it easy to validate the service after deployment.

### Issues

| Severity | Location | Issue |
|----------|----------|-------|
| **High** | `app/main.py` | `allow_credentials=True` combined with `allow_origins=["*"]` is a [CORS security misconfiguration](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS/Errors/CORSNotSupportingCredentials). Browsers will reject credentialed cross-origin requests when the origin is a wildcard. Either set `allow_credentials=False` (for a public API) or restrict `allow_origins` to a specific list of trusted origins. |
| Medium | `app/services/rag_service.py` | `_prepare_context()` injects relevance scores into the context string: `f"[Document {i} - Relevance: {score:.2f}]\n{doc}"`. This exposes internal retrieval scores to the LLM, which may reference them in answers (e.g., "Based on document 2 with relevance 0.87..."). Strip metadata before passing to the LLM. |
| Medium | `app/services/vector_store.py` | The FAISS L2-distance-to-similarity conversion `1 / (1 + d)` is non-standard and compresses the score range non-linearly. For normalised embeddings, an inner-product (IP) index gives scores naturally in `[0, 1]`. Consider using `faiss.IndexFlatIP` with `normalize_L2` for more interpretable similarity scores. |
| Low | `app/services/llm_service.py` | The `_setup_openai()` and `_setup_cohere()` methods use the deprecated `langchain_community` LLM classes (`from langchain_community.llms import OpenAI`). These are not pinned in `requirements.txt` and may break with LangChain updates. Consider using the provider-specific packages (`langchain-openai`, `langchain-cohere`). |
| Low | `app/api/chat.py` | No maximum input length enforced on `ChatRequest.question`. Very long inputs are passed directly to the LLM, increasing latency and API cost. |
| Low | `requirements.txt` | `langchain>=0.1.0` is unpinned and allows major-version upgrades. LangChain has a history of breaking changes between minor versions. Pin to a tested minor version range (e.g. `langchain>=0.1.0,<0.3.0`). |
| Info | `app/services/llm_service.py` | `MockLLM` responses are keyword-match based and will produce misleading output if used in production. Ensure it is clearly disabled outside of test environments. |

### Recommendations

- Fix the CORS configuration: set `allow_credentials=False` or restrict `allow_origins`.
- Strip score metadata from the context before sending to the LLM in `_prepare_context()`.
- Add `max_length` validation to `ChatRequest.question`.
- Consider replacing `IndexFlatL2` with `IndexFlatIP` + L2 normalisation for cleaner
  similarity semantics.

---

## Branch: `vulkkan`

### Architecture
- **Framework**: FastAPI with `asynccontextmanager` lifespan
- **Embeddings**: `sentence-transformers/all-MiniLM-L6-v2` (local, via
  `sentence_transformers`)
- **Vector Store**: In-memory FAISS (`IndexFlatIP`) with cosine similarity via
  L2-normalised embeddings
- **LLM**: Local HuggingFace `text-generation` pipeline; defaults to `gpt2-medium`
- **Data**: Plain `.txt` and `.pdf` documents in `app/data/`

### Strengths

1. **Fully offline/local operation** — no external API keys required. The entire RAG
   pipeline runs on local hardware, making it suitable for air-gapped environments.

2. **Paragraph-aware chunking** — `_split_into_chunks()` prefers paragraph (`\n\n`) and
   sentence boundaries over arbitrary character positions, producing semantically cleaner
   chunks than a naïve fixed-size split.

3. **Asynchronous ingestion** — `ingest_documents()` offloads the blocking embedding and
   FAISS index build to a thread pool executor via `loop.run_in_executor`, keeping the
   event loop responsive during startup.

4. **PDF support** — `load_pdf()` via PyMuPDF supports multi-page PDF ingestion alongside
   plain text files.

5. **Correct FAISS usage** — `IndexFlatIP` with L2-normalised embeddings gives true
   cosine similarity scores in `[0, 1]` without the non-linear transformation required
   by `IndexFlatL2`.

6. **Structured module separation** — separate `app/rag/` package with
   `ingestion.py`, `retrieval.py`, `generation.py`, and `cache.py`.

7. **Good schema design** — `SourceChunk` model with `content`, `source`, and `score`
   fields provides rich context attribution in the chat response.

### Issues

| Severity | Location | Issue |
|----------|----------|-------|
| **Critical** | `requirements.txt` | The file lists ~250 packages (5 393 bytes) clearly exported from a full development/research environment. It includes unrelated packages such as `tensorflow`, `opencv-python`, `gradio`, `streamlit`, `boto3`, `spacy`, `taipy`, `ultralytics`, CUDA bindings, and dozens of others. A `pip install -r requirements.txt` will attempt to install several GB of unnecessary software. The file must be trimmed to the actual runtime dependencies. |
| **Critical** | `app/rag/generation.py` | `HF_MODEL_NAME` defaults to `"gpt2-medium"` — a 117 M-parameter base language model that is **not instruction-tuned**. It does not follow instructions, cannot answer questions from a context paragraph, and will produce repetitive or incoherent text. The `clean_generated_text()` function and related workarounds exist because of this fundamental model mismatch. Replace with an instruction-tuned model (e.g. `google/flan-t5-base`, `TinyLlama/TinyLlama-1.1B-Chat-v1.0`, or use the HuggingFace Inference API instead). |
| High | `app/rag/generation.py` | `early_stopping=True` only affects **beam-search** decoding. When `do_sample=True` (as set), `early_stopping` is silently ignored. Remove it or switch to beam search if early stopping is desired. |
| High | `Dockerfile` | The Dockerfile is **empty** (0 bytes). The service cannot be containerised. A complete Dockerfile is required for deployment. |
| Medium | `app/rag/generation.py` | `MAX_NEW_TOKENS=80` is very low. Even for a small model, 80 tokens is often insufficient for a complete answer. Set to at least 256 for instruction-tuned models. |
| Medium | `app/rag/generation.py` | `clean_generated_text()` is a complex post-processing workaround compensating for gpt2's poor output. The emoji removal regex `[^\w\s.,!?-]` also strips unicode characters, breaking support for non-ASCII output. This entire function should become unnecessary once an instruction-tuned model is used. |
| Medium | `app/main.py` | The module-level docstring mentions `mistralai/Mistral-7B-Instruct-v0.1` as the model, but `generation.py` defaults to `gpt2-medium`. This inconsistency will confuse operators and should be corrected. |
| Low | `app/rag/cache.py` | Cache module exists but its integration with the rest of the application is not evident from the reviewed code. Ensure it is actually used and tested. |
| Low | `app/rag/ingestion.py` | `_embedding_model` is a module-level global using manual `None` checking instead of `functools.lru_cache` or a class. This is thread-unsafe if `ingest_documents` is called concurrently. Use `lru_cache(maxsize=1)` instead. |
| Info | `tests/` | The tests directory exists but its contents were not reviewed. Ensure tests cover at least the `/api/chat` endpoint and the ingestion pipeline. |

### Recommendations

- **Replace `gpt2-medium` immediately** — this is the most critical issue. Even
  `google/flan-t5-base` (250 M params, instruction-tuned) will produce significantly
  better answers for RAG tasks. If compute is constrained, use the HuggingFace Inference
  API (free tier) instead of loading models locally.
- **Trim `requirements.txt`** to actual runtime dependencies. Recommended minimal set:
  `fastapi`, `uvicorn[standard]`, `pydantic`, `sentence-transformers`, `faiss-cpu`,
  `pymupdf`, `numpy`.
- **Complete the Dockerfile** — add a multi-stage build with a slim Python base image.
- Remove `early_stopping=True` when `do_sample=True`.
- Replace the global `_embedding_model` singleton with `@lru_cache(maxsize=1)`.

---

## Cross-Cutting Observations

### Security

| Issue | Branches Affected |
|-------|------------------|
| `allow_credentials=True` + `allow_origins=["*"]` | `john-eze`, `Namshima-Iordye` |
| No maximum input length validation | All three |
| No rate limiting on the `/api/chat` endpoint | All three |
| Secrets loaded from `.env` — no validation that `.env` is excluded from version control | `john-eze`, `Namshima-Iordye` |

### Code Quality

| Observation | Branch |
|-------------|--------|
| Best module structure | `john-eze` |
| Best security/prompt hardening | `Namshima-Iordye` |
| Best local/offline design | `vulkkan` |
| Best chunking algorithm | `vulkkan` |
| Best documentation | `john-eze` |

### Missing Requirements

The task specification requires a `/api/chat` endpoint. All three branches satisfy this.
The specification also implies document ingestion. Status per branch:

| Requirement | `Namshima-Iordye` | `john-eze` | `vulkkan` |
|-------------|:-----------------:|:----------:|:---------:|
| FastAPI framework | ✅ | ✅ | ✅ |
| `/api/chat` endpoint | ✅ | ✅ | ✅ |
| RAG architecture | ✅ | ✅ | ✅ |
| Data ingestion / indexing | ✅ (AstraDB) | ✅ (FAISS/TF-IDF) | ✅ (FAISS) |
| Retrieval | ✅ | ✅ | ✅ |
| LLM generation | ✅ (Gemini) | ✅ (HF/OpenAI/Cohere) | ⚠️ (gpt2-medium) |
| LLM provider integration | ✅ | ✅ | ⚠️ (local only) |
| Health check endpoint | ✅ `/health` | ✅ `/api/health` | ✅ `/health` |
| Working Dockerfile | ✅ | ✅ | ❌ (empty) |

---

## Overall Ranking

1. **`john-eze`** — Best overall submission. Well-structured, multi-provider, dual
   vector-store backend with fallback, document upload, index persistence, and a test
   suite. Fix the CORS misconfiguration and the context score leakage before production.

2. **`Namshima-Iordye`** — Strongest security posture. The prompt injection defences,
   output validation, and hardened system prompt are production-quality. The main gaps
   are the missing `sources` field in the API response and the blocking event loop
   call pattern.

3. **`vulkkan`** — Good architecture and chunking, but the choice of `gpt2-medium` as the
   generation model fundamentally undermines answer quality, and the bloated
   `requirements.txt` makes the project impractical to install. Both issues are fixable
   and the underlying retrieval infrastructure is sound.
