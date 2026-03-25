# QUICKSTART GUIDE

## 🚀 Get Started in 5 Minutes

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Setup Environment
```bash
# For testing with mock LLM (no API key needed)
copy .env.example .env
# Edit .env if needed

# For production, update with your LLM credentials
# Supported providers:
# - Hugging Face (free): Set HF_API_TOKEN
# - OpenAI: Set OPENAI_API_KEY  
# - Cohere: Set COHERE_API_KEY
```

### Step 3: Initialize Knowledge Base
```bash
python setup_kb.py
```

Expected output:
```
INFO:__main__:Initializing RAG service...
INFO:__main__:Loading sample FAQs...
INFO:__main__:Indexing 1 document(s)...
✓ Knowledge base initialized successfully!
✓ Indexed 45 chunks
✓ Index saved to data/index.pkl
```

### Step 4: Run the Application
```bash
python run.py
```

Expected output:
```
INFO:app.core.logger:Starting UNICCON RAG Chatbot
INFO:app.core.logger:Debug mode: False
INFO:app.core.logger:Server running at http://0.0.0.0:8000
INFO:app.core.logger:API documentation at http://0.0.0.0:8000/docs
INFO:uvicorn.server:Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

### Step 5: Test the API

**Option A: Interactive Docs**
- Visit: http://localhost:8000/docs
- Click "Try it out" on any endpoint

**Option B: cURL**
```bash
# Test health
curl http://localhost:8000/api/health

# Ask a question
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"query":"What are the admission requirements?"}'
```

**Option C: Python**
```python
import requests

response = requests.post(
    "http://localhost:8000/api/chat",
    json={"query": "How much is tuition?"}
)
print(response.json())
```

## 📝 Example Queries to Try

The system includes sample FAQs about:
- Admissions (requirements, deadlines, fees)
- Courses (class size, online options, credits)
- Student Services (library, health, parking)
- Academic Support (tutoring, accommodations, grades)

Try these queries:
```
- "What are the admission requirements?"
- "How much does tuition cost?"
- "Are online courses available?"
- "What tutoring is available?"
- "How do I apply for financial aid?"
```

## 🔧 Configuration

### Key Settings (.env)

```bash
# LLM Provider
LLM_PROVIDER=huggingface              # Options: huggingface, openai, cohere
HF_MODEL_NAME=mistralai/Mistral-7B-Instruct-v0.1
HF_API_TOKEN=hf_your_token           # Get from huggingface.co

# RAG Settings
CHUNK_SIZE=500                        # Size of document chunks
TOP_K_RETRIEVAL=3                     # Number of results to retrieve
SIMILARITY_THRESHOLD=0.5              # Minimum relevance score

# Server
HOST=0.0.0.0
PORT=8000
DEBUG=False
```

## 📊 API Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/health` | Check service status |
| POST | `/api/chat` | Ask questions |
| POST | `/api/upload-documents` | Upload FAQs |
| GET | `/api/index-status` | Check KB status |

## 🐛 Troubleshooting

### "No module named 'fastapi'"
```bash
pip install -r requirements.txt --force-reinstall
```

### "Vector store is empty"
```bash
python setup_kb.py
```

### "Connection refused"
- Ensure the server is running: `python run.py`
- Check port 8000 is not in use

### Slow responses
- Reduce `TOP_K_RETRIEVAL` (default: 3)
- Increase `SIMILARITY_THRESHOLD` (default: 0.5)

## 📚 Documentation

- Full docs: See README_IMPLEMENTATION.md
- API docs: http://localhost:8000/docs (when running)
- Architecture: See README_IMPLEMENTATION.md

## 🎯 Next Steps

1. **Add Your Documents**
   ```bash
   curl -X POST http://localhost:8000/api/upload-documents \
     -F "files=@your_faqs.txt"
   ```

2. **Configure LLM**
   - Add your API key to .env
   - Change LLM_PROVIDER as needed

3. **Deploy**
   - Use Docker: `docker build -t chatbot .`
   - Deploy to HuggingFace Spaces
   - Push to cloud platform

## ✅ Checklist

- [ ] Dependencies installed
- [ ] Environment configured (.env)
- [ ] Knowledge base initialized (setup_kb.py)
- [ ] Server running (python run.py)
- [ ] Health check passes (curl /api/health)
- [ ] Successfully asked a question

---

**Happy building! 🎉**

For detailed documentation, see README_IMPLEMENTATION.md
