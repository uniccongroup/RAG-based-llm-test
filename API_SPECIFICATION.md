# API Specification

## Base URL
```
http://localhost:8000
http://your-domain.com
```

## Authentication
Currently, no authentication is required. For production, implement JWT or API keys.

---

## Endpoints

### 1. Health Check

**Endpoint**: `GET /api/health`

**Description**: Check if the service is running and healthy.

**Parameters**: None

**Response** (200 OK):
```json
{
  "status": "healthy",
  "message": "RAG Chatbot service is running"
}
```

**Example**:
```bash
curl http://localhost:8000/api/health
```

---

### 2. Chat (Main Endpoint)

**Endpoint**: `POST /api/chat`

**Description**: Send a question and get an LLM-generated answer based on retrieved context.

**Request Body**:
```json
{
  "query": "What are the admission requirements?",
  "session_id": "optional-user-session-123"
}
```

**Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| query | string | Yes | User's question (max 1000 chars) |
| session_id | string | No | Optional session identifier for conversation tracking |

**Response** (200 OK):
```json
{
  "query": "What are the admission requirements?",
  "answer": "To apply for our undergraduate programs, you need a high school diploma, minimum 2.5 GPA, and SAT/ACT scores.",
  "sources": [
    "High school diploma or equivalent (GED)...",
    "Minimum 2.5 GPA..."
  ],
  "confidence": 0.85,
  "session_id": "optional-user-session-123"
}
```

**Response Fields**:
| Field | Type | Description |
|-------|------|-------------|
| query | string | Echo of the user's query |
| answer | string | LLM-generated answer |
| sources | array | Relevant document snippets used for context |
| confidence | number | Confidence score (0-1) based on relevance |
| session_id | string | Session ID if provided in request |

**Error Responses**:
```json
// 400 - Empty query
{
  "detail": "Query cannot be empty"
}

// 503 - Knowledge base not indexed
{
  "detail": "Knowledge base is not indexed. Please upload documents first."
}

// 500 - Server error
{
  "detail": "Internal server error: <error message>"
}
```

**Examples**:

**cURL**:
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How much is tuition?",
    "session_id": "user123"
  }'
```

**Python**:
```python
import requests

response = requests.post(
    "http://localhost:8000/api/chat",
    json={
        "query": "What courses are available?",
        "session_id": "user123"
    }
)
print(response.json())
```

**JavaScript**:
```javascript
fetch('http://localhost:8000/api/chat', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    query: 'How do I apply?',
    session_id: 'user123'
  })
})
.then(r => r.json())
.then(data => console.log(data))
```

---

### 3. Upload Documents

**Endpoint**: `POST /api/upload-documents`

**Description**: Upload and index FAQ documents for the knowledge base.

**Request**:
- Content-Type: `multipart/form-data`
- Files: Text files (.txt, .md) or PDFs

**Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| files | File[] | Yes | One or more document files |

**Response** (200 OK):
```json
{
  "status": "success",
  "message": "Successfully indexed 45 chunks from 3 documents",
  "document_count": 3,
  "chunk_count": 45
}
```

**Response Fields**:
| Field | Type | Description |
|-------|------|-------------|
| status | string | "success" or "error" |
| message | string | Descriptive status message |
| document_count | integer | Number of documents processed |
| chunk_count | integer | Total number of chunks created |

**Error Responses**:
```json
// 400 - No files provided
{
  "detail": "No files provided"
}

// 400 - No valid documents
{
  "detail": "No valid documents to process"
}

// 500 - Server error
{
  "detail": "Error uploading documents: <error message>"
}
```

**Examples**:

**cURL**:
```bash
curl -X POST http://localhost:8000/api/upload-documents \
  -F "files=@faqs.txt" \
  -F "files=@policies.txt"
```

**Python**:
```python
import requests

files = [
    ('files', open('faqs.txt', 'rb')),
    ('files', open('policies.txt', 'rb'))
]

response = requests.post(
    "http://localhost:8000/api/upload-documents",
    files=files
)
print(response.json())
```

**JavaScript**:
```javascript
const formData = new FormData();
formData.append('files', document.getElementById('file1').files[0]);
formData.append('files', document.getElementById('file2').files[0]);

fetch('http://localhost:8000/api/upload-documents', {
  method: 'POST',
  body: formData
})
.then(r => r.json())
.then(data => console.log(data))
```

---

### 4. Index Status

**Endpoint**: `GET /api/index-status`

**Description**: Get the current status of the knowledge base index.

**Parameters**: None

**Response** (200 OK):
```json
{
  "indexed": true,
  "document_count": 125,
  "message": "Knowledge base is indexed with 125 documents"
}
```

**Response Fields**:
| Field | Type | Description |
|-------|------|-------------|
| indexed | boolean | Whether knowledge base is indexed |
| document_count | integer | Number of indexed documents |
| message | string | Human-readable status message |

**Examples**:

**cURL**:
```bash
curl http://localhost:8000/api/index-status
```

**Python**:
```python
import requests

response = requests.get("http://localhost:8000/api/index-status")
print(response.json())
```

---

## Root Endpoint

**Endpoint**: `GET /`

**Description**: Get API information.

**Response**:
```json
{
  "message": "Welcome to UNICCON RAG-based LLM Chatbot",
  "version": "1.0.0",
  "docs_url": "/docs",
  "health_check": "/api/health"
}
```

---

## Interactive API Documentation

### Swagger UI
Visit: `http://localhost:8000/docs`

### ReDoc
Visit: `http://localhost:8000/redoc`

---

## Request/Response Examples

### Example 1: Ask a Question

**Request**:
```http
POST /api/chat HTTP/1.1
Host: localhost:8000
Content-Type: application/json

{
  "query": "What is the deadline for fall semester admission?",
  "session_id": "session-001"
}
```

**Response**:
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "query": "What is the deadline for fall semester admission?",
  "answer": "The application deadline for the fall semester is June 30. Make sure to submit all required documents including your application form, high school transcripts, test scores, and one letter of recommendation.",
  "sources": [
    "What is the application deadline? A: Application deadlines vary by program: - Fall semester: June 30...",
    "Required documents: 1. Application form 2. High school transcripts 3. Test scores..."
  ],
  "confidence": 0.92,
  "session_id": "session-001"
}
```

### Example 2: Upload Multiple Documents

**Request**:
```http
POST /api/upload-documents HTTP/1.1
Host: localhost:8000
Content-Type: multipart/form-data; boundary=----WebKitFormBoundary

------WebKitFormBoundary
Content-Disposition: form-data; name="files"; filename="admissions_faq.txt"
Content-Type: text/plain

[File content...]
------WebKitFormBoundary
Content-Disposition: form-data; name="files"; filename="academic_policies.txt"
Content-Type: text/plain

[File content...]
------WebKitFormBoundary--
```

**Response**:
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "status": "success",
  "message": "Successfully indexed 156 chunks from 2 documents",
  "document_count": 2,
  "chunk_count": 156
}
```

---

## Error Handling

All endpoints follow these error conventions:

**HTTP Status Codes**:
| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request successful |
| 400 | Bad Request | Invalid input |
| 500 | Server Error | Internal server error |
| 503 | Service Unavailable | Knowledge base not indexed |

**Error Response Format**:
```json
{
  "detail": "Error description"
}
```

---

## Rate Limiting (Future)

Currently unlimited. For production, consider implementing:
- 100 requests per minute per IP
- 10 document uploads per hour per IP
- 1000 requests per day per API key

---

## Data Formats

### Supported Document Types
- `.txt` - Plain text files
- `.md` - Markdown files
- `.pdf` - PDF documents (text extraction)

### File Size Limits
- Single file: 10 MB
- Total upload: 50 MB
- Recommended: Keep files under 2 MB

---

## Sample Responses

### Successful Chat

```json
{
  "query": "How do I find a roommate?",
  "answer": "The Residential Life Office maintains a roommate matching service. You can complete a questionnaire to be matched with compatible roommates. Housing is guaranteed for first-year students. Visit the Residential Life office or check the student portal for more information.",
  "sources": [
    "How do I find a roommate? The Residential Life Office maintains a roommate matching service. You can complete a questionnaire to be matched with compatible roommates. Housing is guaranteed for first-year students."
  ],
  "confidence": 0.88,
  "session_id": null
}
```

### Health Check

```json
{
  "status": "healthy",
  "message": "RAG Chatbot service is running"
}
```

### Index Status - Indexed

```json
{
  "indexed": true,
  "document_count": 45,
  "message": "Knowledge base is indexed with 45 documents"
}
```

### Index Status - Not Indexed

```json
{
  "indexed": false,
  "document_count": 0,
  "message": "Knowledge base is not indexed"
}
```

---

## Best Practices

1. **Use Session IDs**: Track conversations with session_id
2. **Check Index Status**: Before making chat requests, verify knowledge base is indexed
3. **Handle Errors**: Implement retry logic with exponential backoff
4. **Monitor Confidence**: Use confidence score to filter low-quality responses
5. **Cache Responses**: Cache frequent queries for better performance
6. **Batch Operations**: Upload multiple documents at once instead of individually

---

## Future Enhancements

- Authentication & API keys
- Rate limiting
- Response caching
- Conversation history
- User feedback mechanism
- Analytics & reporting
- Multi-language support
- Document deletion/update

---

**For more information, visit the interactive API docs at `/docs`**
