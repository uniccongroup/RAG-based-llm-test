# Candidate Evaluation Report
## RAG-based LLM Chatbot Backend — Technical Assessment

**Reviewed by:** GitHub Copilot (technical review)
**Date:** 1 April 2026
**Repository:** https://github.com/uniccongroup/RAG-based-llm-test

---

## I. Candidate Overview

| # | Candidate Name | GitHub Branch | Review Status |
|---|---------------|---------------|---------------|
| Candidate 1 | Namshima Iordye | [Namshima-Iordye](https://github.com/uniccongroup/RAG-based-llm-test/tree/Namshima-Iordye) | **Pass** |
| Candidate 2 | John Eze | [john-eze](https://github.com/uniccongroup/RAG-based-llm-test/tree/john-eze) | **Pass** |
| Candidate 3 | Vulkkan | [vulkkan](https://github.com/uniccongroup/RAG-based-llm-test/tree/vulkkan) | **Fail** |

---

## II. Detailed Evaluation Criteria

> Scoring scale: **1 = Poor / Not Met** → **5 = Excellent / Fully Met**

| Evaluation Area | Criterion | Candidate 1 — Namshima Iordye (Score / 5) | Candidate 2 — John Eze (Score / 5) | Candidate 3 — Vulkkan (Score / 5) |
|---|---|:---:|:---:|:---:|
| **Framework Adherence** | Built entirely using FastAPI. | **5** | **5** | **5** |
| **Core Functionality** | Successfully implemented a dedicated RESTful endpoint (e.g., `/api/chat`). | **5** | **5** | **5** |
| **LLM Integration** | Integration with a selected LLM provider (e.g., OpenAI, Hugging Face, Cohere). | **5** | **5** | **3** |
| **Model Selection** | Used an appropriate model for LLM text generation. | **3** | **5** | **2** |
| **RAG Architecture: Data Ingestion** | Implemented a process to load, chunk, and embed the source documents (FAQ knowledge base). | **5** | **5** | **4** |
| **RAG Architecture: Retrieval** | Efficiency in searching the indexed knowledge base to find relevant document snippets based on query. | **5** | **5** | **4** |
| **RAG Architecture: Generation** | LLM generates coherent and accurate answers based on the retrieved context. | **5** | **4** | **2** |
| **Project Deliverable** | Submitted a complete, working backend application source code. | **4** | **5** | **2** |
| **Submission Adherence** | Hosted the completed project in a public GitHub repository. | **5** | **5** | **5** |
| | **Total** | **42 / 45** | **44 / 45** | **32 / 45** |

### Scoring Notes

**Candidate 1 — Namshima Iordye**
- *Model Selection (3/5):* The generation LLM is Google Gemini 2.5 Flash Lite, a proprietary closed-source model. While highly capable, the criterion specifies open-source or open-access model usage (e.g., Hugging Face). The embedding model (`sentence-transformers/all-MiniLM-L6-v2`) is open-source. A score of 3 reflects partial fulfilment — the integration quality is excellent but the model licence does not meet the open-source criterion.
- *Project Deliverable (4/5):* The application is functionally complete; the deduction reflects two gaps: the API response silently drops retrieved source documents, and the chat endpoint makes synchronous LLM/DB calls inside an `async def` handler, blocking the event loop under load.

**Candidate 2 — John Eze**
- *RAG Architecture: Generation (4/5):* Prompt engineering is solid and multi-provider support is commendable. One deduction is applied because relevance scores (`[Document 1 - Relevance: 0.87]`) are injected verbatim into the LLM context, potentially causing the model to expose internal retrieval metadata in its answers. The `MockLLM` fallback, while useful for testing, would produce misleading responses if accidentally activated in production.

**Candidate 3 — Vulkkan**
- *LLM Integration (3/5):* The only integration is a locally downloaded HuggingFace `text-generation` pipeline. No external LLM provider API (OpenAI, Cohere, Hugging Face Inference API) is used, contrary to the project requirements.
- *Model Selection (2/5):* The default model `gpt2-medium` (117 M parameters) is a base language model — it is not instruction-tuned and cannot follow RAG-style prompts. It will produce repetitive or incoherent output rather than grounded answers. The `clean_generated_text()` function is a symptomatic workaround that does not fix this root cause.
- *RAG Architecture: Generation (2/5):* As a direct consequence of the model choice, the generation step does not meet the requirement for "coherent and accurate answers based on retrieved context."
- *Project Deliverable (2/5):* The `Dockerfile` is empty (0 bytes), making containerised deployment impossible. The `requirements.txt` contains ~250 packages from an unrelated research environment (TensorFlow, OpenCV, Gradio, Streamlit, CUDA bindings, etc.), making `pip install` fail or install several GB of irrelevant software.

---

## III. Candidate Specific Analysis and Comments

---

### Candidate 1: Namshima Iordye

**Strengths:**

1. **Best-in-class security posture.** The submission implements production-grade prompt injection defences — a regex-based `INJECTION_PATTERNS` list covering English, French, and Spanish attack vectors; `sanitise_input()` for delimiter stripping; `contains_leakage()` output validation; and a 10-rule hardened system prompt with language lock, identity lock, delimiter immunity, and graceful deflection.
2. **Excellent RAG pipeline architecture.** LangChain's `RunnablePassthrough | ChatPromptTemplate | LLM | StrOutputParser` chain is correctly wired. Document metadata (filenames, chunk IDs) is deliberately stripped before reaching the LLM via `format_docs()`, then cleaned and returned separately via `clean_source_name()`.
3. **Managed cloud vector store (AstraDB).** Using a managed, scalable vector database is a production-appropriate choice. The `@lru_cache` singleton pattern correctly avoids re-initialising the AstraDB connection on every request.
4. **Pydantic-validated configuration.** All required secrets fail loudly on startup if missing — no silent misconfiguration is possible.
5. **Chat UI included.** A browser-based interface at `/` and `/ui` provides immediate usability beyond the raw API.

**Areas for Improvement:**

1. **Proprietary generation model.** Gemini is not open-source. An open-source instruction-tuned model (e.g., `google/flan-t5-large`, `mistralai/Mistral-7B-Instruct-v0.1` via HF Inference API) should be substituted to fully meet the criterion.
2. **Sources omitted from API response.** `answer_question()` computes and returns source document names, but they are silently discarded because `ChatResponse` has no `sources` field. Clients cannot show citations to users.
3. **Blocking event loop.** `chain.invoke()` is called synchronously inside an `async def` endpoint. Under concurrent load this blocks the event loop. Should use `chain.ainvoke()` or `asyncio.to_thread()`.
4. **No input length cap.** `ChatRequest.question` has no `max_length` constraint; an attacker or misconfigured client could send an arbitrarily large payload.
5. **CORS misconfiguration.** `allow_credentials=True` combined with `allow_origins=["*"]` is rejected by browsers (CORS spec forbids wildcard origin with credentials). Should be `allow_credentials=False` for a public API.

**Overall Recommendation:** **Advance to next stage.** The security architecture and RAG pipeline quality are production-grade. The LLM choice and the three medium-severity API issues are straightforward to fix and indicate the candidate understands the domain well.

---

### Candidate 2: John Eze

**Strengths:**

1. **Strongest overall code structure.** The codebase follows clean separation of concerns across `app/api/`, `app/core/`, `app/models/`, and `app/services/` packages. Each layer has a clearly defined responsibility with no cross-layer leakage.
2. **Multi-provider LLM support.** `LLMService` supports HuggingFace InferenceClient, OpenAI, and Cohere, all switchable via the `LLM_PROVIDER` environment variable. This fully satisfies the LLM integration requirement and goes beyond it.
3. **Resilient dual-backend vector store.** Automatic fallback from FAISS + sentence-transformers to scikit-learn TF-IDF when PyTorch is unavailable makes the service deployable in constrained environments without any code change.
4. **Index persistence and document upload.** `save_index()` / `load_index()` survive restarts; `POST /api/upload-documents` allows knowledge-base updates at runtime without restarting the service.
5. **Comprehensive documentation and tests.** `ARCHITECTURE.md` documents every design decision. `test_api.py` covers health, chat, empty input, and index status scenarios.
6. **Greeting detection optimisation.** `_is_greeting()` short-circuits vector store lookup for simple pleasantries, reducing unnecessary retrieval overhead.

**Areas for Improvement:**

1. **CORS security misconfiguration (High severity).** `allow_credentials=True` + `allow_origins=["*"]` violates the CORS specification and will be rejected by browsers. This must be fixed before any browser-based client is deployed.
2. **Retrieval score leakage into LLM context.** `_prepare_context()` formats chunks as `[Document 1 - Relevance: 0.87]\ntext...`. The LLM may reference these synthetic labels in answers. Metadata should be stripped from the context string before sending to the LLM.
3. **Non-standard FAISS similarity conversion.** The L2 distance to similarity conversion `1 / (1 + d)` is non-linear. Using `IndexFlatIP` with L2-normalised embeddings would give true cosine similarity scores in [0, 1].
4. **Unpinned LangChain version.** `langchain>=0.1.0` permits major-version upgrades. LangChain has a history of breaking API changes between minor versions.
5. **No input length cap on chat endpoint.** As with the other submissions, no `max_length` guard exists on `ChatRequest.question`.

**Overall Recommendation:** **Advance to next stage (top candidate).** This is the most complete and deployable submission. The issues identified are all straightforward fixes. The architecture, documentation quality, and test coverage demonstrate strong engineering practices.

---

### Candidate 3: Vulkkan

**Strengths:**

1. **Sound retrieval infrastructure.** The FAISS implementation correctly uses `IndexFlatIP` with L2-normalised embeddings, giving true cosine similarity scores — a better design choice than what was seen in the other submissions.
2. **Paragraph-aware, semantically clean chunking.** `_split_into_chunks()` preferentially breaks at paragraph (`\n\n`) and sentence boundaries rather than arbitrary character positions, producing higher-quality chunks for retrieval.
3. **Asynchronous ingestion.** `ingest_documents()` correctly offloads the blocking FAISS index build to `loop.run_in_executor`, keeping the event loop responsive during startup.
4. **PDF support.** `load_pdf()` via PyMuPDF handles multi-page PDF ingestion natively.
5. **Good schema design.** `SourceChunk` carries `content`, `source`, and `score` — the response model is richer than the other submissions in terms of attribution data.
6. **Fully offline operation.** No external API keys are required. The pipeline can run in air-gapped environments.

**Areas for Improvement:**

1. **Critical: Incorrect model choice.** `gpt2-medium` is a base language model (117 M parameters) with no instruction-following capability. It will not answer questions from a provided context. This is the single most important issue and renders the generation step non-functional for the intended use case. Must be replaced with an instruction-tuned model (e.g., `google/flan-t5-base`, `TinyLlama/TinyLlama-1.1B-Chat-v1.0`) or use the HuggingFace Inference API.
2. **Critical: Bloated `requirements.txt`.** ~250 packages are listed from a full research environment, including TensorFlow, OpenCV, Gradio, Streamlit, CUDA bindings, and dozens of others totalling several GB. This makes the project impossible to install in a standard environment.
3. **Empty Dockerfile.** The containerisation file is 0 bytes. The service cannot be deployed via Docker, which is a standard requirement for backend services.
4. **`early_stopping=True` bug.** This flag only affects beam search, not sampling. It is silently ignored when `do_sample=True` — giving a false impression that early stopping is active.
5. **Thread-unsafe embedding singleton.** The `_embedding_model` global uses manual `None`-checking without a lock. Concurrent calls to `ingest_documents` could trigger redundant model loading.

**Overall Recommendation:** **Do not advance at this stage.** While the retrieval and chunking implementations show good understanding, the two critical issues (non-functional generation model and unusable `requirements.txt`) indicate the submission is not ready for production. The candidate should be invited to address these issues before a follow-up review is considered.

---

## IV. Final Summary and Recommendation

| # | Candidate Name | Total Score (Out of 45) | Summary Notes | Recommended Next Step |
|---|---------------|:---:|---|:---:|
| Candidate 2 | **John Eze** | **44 / 45** | Strongest overall submission. Excellent code structure, multi-provider LLM, resilient dual-backend vector store, index persistence, document upload, full test suite, and documentation. One CORS security issue and minor context formatting issue require prompt fixes. | **Recommend — Advance** |
| Candidate 1 | **Namshima Iordye** | **42 / 45** | Best security architecture of the three. Production-quality prompt injection defences, hardened system prompt, and clean LangChain pipeline. Main gaps are use of a proprietary LLM (Gemini vs. required open-source) and a missing `sources` field in the API response. Both are fixable. | **Recommend — Advance** |
| Candidate 3 | **Vulkkan** | **32 / 45** | Sound retrieval infrastructure and paragraph-aware chunking show strong RAG fundamentals. However, the generation model choice (`gpt2-medium`) renders the core functionality non-functional, and the bloated `requirements.txt` and empty Dockerfile prevent deployment. Critical issues must be resolved before the submission is production-ready. | **Reject — Invite to Resubmit** |

---

### Recommendation Summary

**Both John Eze (44/45) and Namshima Iordye (42/45) are recommended to advance to the next stage.**

- **John Eze** is the top-ranked candidate. The submission demonstrates production engineering practices — modular architecture, resilient fallbacks, documentation, and tests — that go significantly beyond the minimum requirements. **Priority invite for next stage.**

- **Namshima Iordye** is a strong second candidate with standout security awareness. The prompt injection defences and output validation pipeline reflect a thoughtful understanding of LLM-specific risks. The use of Gemini instead of an open-source model is the primary deduction; switching to a Hugging Face hosted model (which the LangChain integration already supports) is a minor change.

- **Vulkkan** should **not advance** at this time. The fundamental model selection issue means the submitted chatbot cannot perform the core task (question answering from context). The candidate should be encouraged to resubmit after replacing `gpt2-medium` with an instruction-tuned model and cleaning up `requirements.txt` and the Dockerfile. The retrieval and chunking code is well-designed and would serve as a strong foundation if the generation layer is corrected.
