# UNICCON RAG-based LLM Chatbot

A robust, production-ready backend service for an intelligent FAQ chatbot powered by Large Language Models and Retrieval-Augmented Generation (RAG).

## Project Overview

This project implements a **RAG-based FAQ chatbot** backend for a fictional Edu-Tech organization ("Company X"). The system combines modern NLP techniques with FastAPI to deliver accurate, contextually relevant answers based on proprietary knowledge bases.

### Key Features

✅ **RAG Architecture**: Combines retrieval and generation for accurate, contextual answers  
✅ **FastAPI Framework**: High-performance async backend  
✅ **Multi-LLM Support**: OpenAI, Hugging Face, Cohere, and mock LLM for testing  
✅ **Vector Search**: FAISS-based semantic search with embedding models  
✅ **Document Ingestion**: Automatic chunking and indexing of FAQs  
✅ **RESTful API**: Easy-to-use endpoints for chat and document management  
✅ **Production Ready**: Comprehensive logging, error handling, and configuration  

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     FastAPI Application                      │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│  │   /api/chat  │      │   /upload    │      │  /health     │
│  │  Endpoint    │      │  Endpoint    │      │  Endpoint    │
│  └──────────────┘      └──────────────┘      └──────────────┘
│         │                     │
│         └─────────────────────┴─────────────────────────────┐
│                               │                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │              RAG Service Layer                          │ │
│  ├─────────────────────────────────────────────────────────┤ │
│  │                                                          │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐  │ │
│  │  │  Retrieval   │  │  Chunking    │  │  LLM        │  │ │
│  │  │  (FAISS)     │  │  Service     │  │  Service    │  │ │
│  │  └──────────────┘  └──────────────┘  └─────────────┘  │ │
│  │                                                          │ │
│  └────────────────────────────────────────────────────────┘ │
│                          │                                    │
│  ┌────────────────────────────────────────────────────────┐ │
│  │         Data & Indexing Layer                          │ │
│  ├─────────────────────────────────────────────────────────┤ │
│  │                                                          │ │
│  │  ┌──────────────────────────────────────────────────┐  │ │
│  │  │  Vector Store (FAISS + Embeddings)               │  │ │
│  │  │  - Sentence Transformers for embedding           │  │ │
│  │  │  - FAISS for efficient similarity search          │  │ │
│  │  └──────────────────────────────────────────────────┘  │ │
│  │                                                          │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## Tech Stack

| Component | Technology |
|-----------|------------|
| Framework | FastAPI 0.104+ |
| Server | Uvicorn |
| Embeddings | Sentence Transformers |
| Vector Search | FAISS |
| LLM Integration | LangChain Community |
| Text Processing | Python 3.8+ |

## Project Structure

```
uniccon/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application
│   ├── api/
│   │   ├── __init__.py
│   │   ├── router.py           # API router
│   │   └── chat.py             # Chat endpoints
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py           # Configuration management
│   │   └── logger.py           # Logging setup
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py          # Pydantic models
│   └── services/
│       ├── __init__.py
│       ├── rag_service.py      # Main RAG orchestration
│       ├── vector_store.py     # Vector store (FAISS)
│       ├── chunking.py         # Text chunking
│       └── llm_service.py      # LLM integration
├── data/
│   └── sample_faqs.py          # Sample FAQ data
├── logs/                        # Application logs
├── requirements.txt            # Python dependencies
├── .env.example               # Environment variables template
├── run.py                     # Application entry point
├── setup_kb.py               # Knowledge base setup
└── README.md                 # This file
```

## Installation & Setup

### Prerequisites

- Python 3.8+
- pip or conda
- Git

### Step 1: Clone Repository

```bash
cd c:\Users\JOHN EZE\Desktop
git clone https://github.com/uniccongroup/RAG-based-llm-test.git uniccon
cd uniccon
git checkout -b your-name  # Create your personal branch
```

### Step 2: Create Virtual Environment

```bash
# Using venv
python -m venv venv
venv\Scripts\activate

# Or using conda
conda create -n uniccon python=3.10
conda activate uniccon
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment

```bash
# Copy environment template
copy .env.example .env

# Edit .env with your settings (especially LLM credentials)
```

**Important Environment Variables:**
- `LLM_PROVIDER`: Choose from `huggingface`, `openai`, or `cohere`
- `HF_API_TOKEN`: Your Hugging Face API token (if using Hugging Face)
- `OPENAI_API_KEY`: Your OpenAI API key (if using OpenAI)
- `COHERE_API_KEY`: Your Cohere API key (if using Cohere)

### Step 5: Initialize Knowledge Base

```bash
python setup_kb.py
```

This will:
- Load sample FAQs
- Generate embeddings
- Create and save the vector index

### Step 6: Run Application

```bash
python run.py
```

The application will start at `http://localhost:8000`

## API Endpoints

### 1. Health Check
```http
GET /api/health
```

**Response:**
```json
{
  "status": "healthy",
  "message": "RAG Chatbot service is running"
}
```

### 2. Chat Endpoint
```http
POST /api/chat
Content-Type: application/json

{
  "query": "What are the admission requirements?",
  "session_id": "optional-session-123"
}
```

**Response:**
```json
{
  "query": "What are the admission requirements?",
  "answer": "To apply for our undergraduate programs, you need...",
  "sources": [
    "High school diploma or equivalent (GED)...",
    "Minimum 2.5 GPA..."
  ],
  "confidence": 0.85,
  "session_id": "optional-session-123"
}
```

### 3. Upload Documents
```http
POST /api/upload-documents
Content-Type: multipart/form-data

files: [file1.txt, file2.txt, ...]
```

**Response:**
```json
{
  "status": "success",
  "message": "Successfully indexed 45 chunks from 3 documents",
  "document_count": 3,
  "chunk_count": 45
}
```

### 4. Index Status
```http
GET /api/index-status
```

**Response:**
```json
{
  "indexed": true,
  "document_count": 125,
  "message": "Knowledge base is indexed with 125 documents"
}
```

## Usage Examples

### Using cURL

```bash
# Health check
curl http://localhost:8000/api/health

# Ask a question
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "What are the tuition costs?"}'

# Check index status
curl http://localhost:8000/api/index-status

# Upload documents
curl -X POST http://localhost:8000/api/upload-documents \
  -F "files=@faqs.txt" \
  -F "files=@policies.txt"
```

### Using Python

```python
import requests

BASE_URL = "http://localhost:8000"

# Chat with the bot
response = requests.post(
    f"{BASE_URL}/api/chat",
    json={"query": "How do I apply for admission?"}
)
print(response.json())

# Upload documents
with open("faqs.txt", "rb") as f:
    files = {"files": f}
    response = requests.post(
        f"{BASE_URL}/api/upload-documents",
        files=files
    )
print(response.json())
```

### Using FastAPI Interactive Docs

Visit: `http://localhost:8000/docs`

This provides an interactive Swagger UI for testing all endpoints.

## Configuration

### LLM Provider Options

#### 1. Hugging Face (Default, Free)
```bash
LLM_PROVIDER=huggingface
HF_MODEL_NAME=mistralai/Mistral-7B-Instruct-v0.1
HF_API_TOKEN=your_token_here
```

#### 2. OpenAI
```bash
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...
```

#### 3. Cohere
```bash
LLM_PROVIDER=cohere
COHERE_API_KEY=...
```

### RAG Configuration

```bash
# Text chunking
CHUNK_SIZE=500          # Chunk size in characters
CHUNK_OVERLAP=50        # Overlap between chunks

# Retrieval
TOP_K_RETRIEVAL=3       # Number of top results to retrieve
SIMILARITY_THRESHOLD=0.5 # Minimum similarity score

# Embedding model
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

## Development

### Running Tests (Optional)

```bash
# Create test files
pytest tests/
```

### Logging

Logs are stored in the `logs/` directory:
- `app.log`: Detailed application logs

Enable debug mode in `.env`:
```bash
DEBUG=True
LOG_LEVEL=DEBUG
```

### Adding Custom Documents

1. **Via API:**
   ```bash
   curl -X POST http://localhost:8000/api/upload-documents \
     -F "files=@your_document.txt"
   ```

2. **Programmatically:**
   ```python
   from app.services.rag_service import RAGService
   
   rag = RAGService()
   rag.index_documents(["Document 1", "Document 2"])
   rag.save_index("data/custom_index.pkl")
   ```

## Performance Considerations

- **Embedding Generation**: First-time indexing may take time depending on document size
- **Search Speed**: FAISS provides O(log n) search complexity
- **Memory**: Vector index is loaded in memory for fast retrieval
- **Scaling**: For large document sets, consider using FAISS GPU acceleration

## Deployment

### Docker

```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN python setup_kb.py

CMD ["python", "run.py"]
```

### HuggingFace Spaces

1. Create a new Space on HuggingFace
2. Push this repository to the Space
3. Add secrets for LLM API keys
4. Access via HuggingFace URL

### Cloud Platforms

- **AWS**: Deploy with Lambda + API Gateway or ECS
- **Google Cloud**: Use Cloud Run or App Engine
- **Azure**: Deploy with Container Instances or App Service
- **Heroku**: `git push heroku main`

## Troubleshooting

### Issue: "Vector store is empty"
**Solution**: Run `python setup_kb.py` to initialize the knowledge base

### Issue: LLM API errors
**Solution**: Check API keys in `.env` and ensure you have proper credentials

### Issue: Slow response times
**Solution**: 
- Reduce `CHUNK_SIZE`
- Decrease `TOP_K_RETRIEVAL`
- Use a smaller embedding model

### Issue: Out of memory
**Solution**: 
- Use FAISS GPU acceleration
- Implement batch processing
- Use a dedicated vector database (Pinecone, Weaviate)

## Contributing

1. Create a branch with your name: `git checkout -b your-name`
2. Make changes and commit: `git commit -m "feature description"`
3. Push to your branch: `git push origin your-name`
4. Create a Pull Request

**Note**: This is an individual task. Collaborations may lead to disqualification.

## Project Timeline

**Maximum Duration**: 3 days from receipt of task

**Milestones:**
- Day 1: Project setup, basic RAG implementation
- Day 2: Full API implementation, testing
- Day 3: Documentation, deployment preparation

## License

This project is part of the UNICCON GROUP AI Engineer evaluation.

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review API documentation at `/docs`
3. Check application logs in `logs/app.log`

---

**Project**: UNICCON RAG-based LLM Test  
**Status**: Active Development  
**Branch**: your-name  
**Last Updated**: March 2026
