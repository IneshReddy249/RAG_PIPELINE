# 🚀 RAG Pipeline with Conversation Memory & Security

A production-ready Retrieval-Augmented Generation (RAG) system built with LlamaIndex, Nvidia LLMs, and FastAPI. Upload documents, ask questions, and get accurate answers with conversation memory and built-in security guardrails.

## ✨ Features

- 📄 **Document Processing**: Upload PDF, TXT, and Markdown files
- 🔍 **Semantic Search**: Find relevant information using embeddings
- 💬 **Conversation Memory**: Natural follow-up questions with context retention
- 🛡️ **Security Guardrails**: Protection against malicious queries and attacks
- ⚡ **Fast API**: RESTful endpoints with automatic documentation
- 🎯 **Smart Chunking**: Optimized for academic papers and technical documents
- 📊 **Source Attribution**: See which documents answered your questions

## 🏗️ Architecture

```
┌─────────────┐
│   Upload    │ → Security check → Documents stored in data/raw/
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Processing │ → Split into 1024-token chunks
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Embedding  │ → OpenAI text-embedding-3-large
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  ChromaDB   │ → Vector storage with similarity search
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Query     │ → Security check → Retrieve top-K chunks
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Generate   │ → Nvidia Llama 3.1 70B → Sanitize response
└─────────────┘
```

## 🛡️ Security Features

- **Query Protection**: Blocks prompt injections, harmful content, and PII extraction attempts
- **Rate Limiting**: 10 queries per minute per session
- **File Validation**: Size limits (50MB), extension whitelist, path traversal prevention
- **Response Sanitization**: Automatically removes emails, phone numbers, and API keys
- **Attack Detection**: Pattern-based detection for malicious inputs

## 📋 Prerequisites

- Python 3.11 or 3.12
- OpenAI API key (for embeddings)
- Nvidia API key (for LLM)

## 🚀 Quick Start

### 1. Clone and Setup

```bash
git clone <your-repo>
cd RAG_PIPELINE

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

Create `.env` file in project root:

```bash
# API Keys (REQUIRED)
OPENAI_API_KEY=sk-your-openai-key-here
NVIDIA_API_KEY=nvapi-your-nvidia-key-here

# Database
CHROMA_DB_PATH=./data/chroma_db
CHROMA_COLLECTION_NAME=rag_documents

# Embedding
EMBEDDING_MODEL=text-embedding-3-large

# Chunking (optimized for quality)
CHUNK_SIZE=1024
CHUNK_OVERLAP=200

# Retrieval (balanced for accuracy)
TOP_K_RESULTS=10
SIMILARITY_THRESHOLD=0.5

# LLM Generation
LLM_MODEL=meta/llama-3.1-70b-instruct
LLM_TEMPERATURE=0.1
MAX_TOKENS=1024
LLM_BASE_URL=https://integrate.api.nvidia.com/v1
```

### 3. Run the Server

```bash
uvicorn api:app --reload
```

API will be available at: `http://localhost:8000`

Swagger UI: `http://localhost:8000/docs`

## 📖 API Usage

### Upload a Document

```bash
curl -X POST "http://localhost:8000/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@your_document.pdf"
```

**Response:**
```json
{
  "status": "ready",
  "file": "your_document.pdf",
  "chunks": 47,
  "time": 12.3
}
```

### Ask a Question (First in Conversation)

```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the main causes of LLM hallucinations?"
  }'
```

**Response:**
```json
{
  "answer": "According to the document, LLM hallucinations have three main causes: (1) Data-related issues including misinformation and biases...",
  "sources": [
    {
      "id": 1,
      "text": "LLM hallucinations have multifaceted origins...",
      "score": 0.556
    }
  ],
  "time": 3.2,
  "session_id": "session_1234567890"
}
```

### Follow-Up Question (With Memory)

```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How can we prevent the first one?",
    "session_id": "session_1234567890"
  }'
```

The bot understands "the first one" refers to data-related issues from the previous answer.

### View Conversation History

```bash
curl -X GET "http://localhost:8000/conversation/session_1234567890"
```

**Response:**
```json
{
  "session_id": "session_1234567890",
  "messages": [
    {
      "user": "What are the main causes?",
      "assistant": "Three main causes: data, training, inference...",
      "timestamp": "2024-11-17T12:00:00"
    },
    {
      "user": "How can we prevent the first one?",
      "assistant": "To prevent data-related issues...",
      "timestamp": "2024-11-17T12:01:00"
    }
  ],
  "count": 2
}
```

### Clear Conversation

```bash
curl -X DELETE "http://localhost:8000/conversation/session_1234567890"
```

## 📂 Project Structure

```
RAG_PIPELINE/
├── api.py                      # FastAPI application with endpoints
├── guardrails.py              # Security guardrails (NEW)
├── config.py                   # Configuration and environment variables
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables (not in git)
│
├── src/
│   ├── document_processor.py  # Load and chunk documents
│   ├── embedding_storing.py   # Embed chunks and store in ChromaDB
│   ├── retrieving.py          # Retrieve relevant chunks
│   └── generation.py          # Generate answers with LLM
│
└── data/
    ├── raw/                   # Uploaded documents (PDF, TXT, MD)
    └── chroma_db/             # Vector database (auto-created)
```

## 🛡️ Security Guardrails

### Protected Against

| Threat | Protection Method | Example |
|--------|------------------|---------|
| **Prompt Injection** | Pattern detection | "Ignore previous instructions" → Blocked |
| **Harmful Content** | Keyword filtering | "How to make a bomb" → Blocked |
| **PII Extraction** | Query analysis | "List all emails" → Blocked |
| **DOS Attacks** | Rate limiting | 11th query in 1 min → Blocked |
| **Large Files** | Size validation | 100MB file → Blocked (50MB limit) |
| **Path Traversal** | Filename check | "../secret.txt" → Blocked |
| **Data Leaks** | Response sanitization | Emails/phones → Redacted |

### Rate Limits

```
Per Session:
- Queries: 10 per minute
- File Uploads: 5 per hour
- File Size: 50MB maximum
```

### Customize Security

Edit `guardrails.py`:

```python
# Change rate limit
if len(recent) >= 20:  # 20 instead of 10

# Change file size
if size_bytes > 100 * 1024 * 1024:  # 100MB instead of 50MB

# Add custom patterns
BLOCKED_PATTERNS = [
    r"\bignore\b.*(previous|all).*(instruction|rule|prompt)",
    r"your custom pattern here",  # Add yours
]
```

## 🔧 Configuration

### Chunk Size

Control how documents are split:

```bash
# Larger chunks = more context, fewer pieces
CHUNK_SIZE=1024        # Default: good for most documents
CHUNK_SIZE=512         # Smaller: more precise retrieval
CHUNK_SIZE=2048        # Larger: more context per chunk

# Overlap between chunks (prevents losing info at boundaries)
CHUNK_OVERLAP=200      # Default: 20% overlap
```

### Retrieval Settings

```bash
# Number of chunks to retrieve
TOP_K_RESULTS=10       # Default: balanced
TOP_K_RESULTS=5        # Fewer: faster, less context
TOP_K_RESULTS=20       # More: comprehensive, slower

# Minimum similarity score to include
SIMILARITY_THRESHOLD=0.5   # Default: filters noise
SIMILARITY_THRESHOLD=0.3   # Lower: more permissive
SIMILARITY_THRESHOLD=0.7   # Higher: only high-quality matches
```

### LLM Settings

```bash
# Temperature (creativity vs consistency)
LLM_TEMPERATURE=0.1    # Default: consistent, factual
LLM_TEMPERATURE=0.0    # Deterministic (same answer every time)
LLM_TEMPERATURE=0.7    # More creative (less consistent)

# Max output length
MAX_TOKENS=1024        # Default: medium answers
MAX_TOKENS=512         # Shorter answers
MAX_TOKENS=2048        # Longer, detailed answers
```

## 📊 Performance Benchmarks

| Metric | Value |
|--------|-------|
| **Upload & Process** | ~10s per 20-page PDF |
| **Query Response** | 3-5s (first query), 2-3s (cached) |
| **Security Overhead** | <1ms per request |
| **Similarity Scores** | 0.50-0.65 (typical for academic papers) |
| **Memory Overhead** | ~5MB per 100 active sessions |
| **Cost per Query** | ~$0.006 (embeddings + generation) |

## 🎯 Use Cases

### ✅ Excellent For

- Academic paper analysis and Q&A
- Technical documentation search
- Internal knowledge bases (teams 2-50 people)
- Research literature review
- Policy/compliance document Q&A
- Personal document assistant

## 📚 Dependencies

### Core

- `llama-index==0.10.68` - RAG framework
- `llama-index-embeddings-openai==0.1.6` - OpenAI embeddings
- `llama-index-llms-nvidia==0.1.3` - Nvidia LLM integration
- `llama-index-vector-stores-chroma==0.1.6` - ChromaDB vector store

### Supporting

- `fastapi==0.109.2` - API framework
- `uvicorn==0.27.1` - ASGI server
- `chromadb==0.4.24` - Vector database
- `pypdf==4.0.1` - PDF parsing
- `python-dotenv==1.0.1` - Environment variables
- `python-multipart` - File upload support

## 🧪 Testing

### Test Security Guardrails

```bash
# Run guardrails tests
python guardrails.py

# Expected output:
✅ What causes hallucinations?: SAFE
✅ Ignore previous instructions: Suspicious content detected
✅ How to make a bomb: Suspicious content detected
✅ Show me all email addresses: Suspicious content detected
```

## 🙏 Acknowledgments

- Built with [LlamaIndex](https://www.llamaindex.ai/)
- Powered by [Nvidia NIM](https://www.nvidia.com/en-us/ai/)
- Embeddings by [OpenAI](https://openai.com/)
- Vector storage by [ChromaDB](https://www.trychroma.com/)

## 🗺️ Roadmap

**Completed:**
- ✅ Basic RAG pipeline
- ✅ Conversation memory
- ✅ Security guardrails (NEW)
- ✅ Multiple file formats
- ✅ REST API with documentation



**Built with ❤️ for secure, efficient document Q&A**

