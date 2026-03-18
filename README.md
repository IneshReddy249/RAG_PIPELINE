# RAG Pipeline with Conversation Memory & Security

Production RAG system built with LlamaIndex, NVIDIA LLMs, and FastAPI. 
Upload documents, ask questions, get accurate answers with conversation 
memory and security guardrails.

This project sits at the application layer above inference engines — 
contrasting with the GPU-level optimization work in my other repos. 
It demonstrates how optimized inference infrastructure gets consumed 
in a real system, and what application-level concerns (retrieval quality, 
security, session management) look like in practice.

---

## Features

- **Document Processing** — PDF, TXT, and Markdown ingestion
- **Semantic Search** — Embedding-based retrieval via ChromaDB
- **Conversation Memory** — Multi-turn Q&A with session context
- **Security Guardrails** — Prompt injection, PII extraction, rate limiting
- **Source Attribution** — Every answer cites which chunks it used
- **REST API** — FastAPI with auto-generated Swagger docs

---

## Architecture
```
Upload → Security check → data/raw/
       ↓
Processing → 1024-token chunks with 200-token overlap
       ↓
Embedding → OpenAI text-embedding-3-large → ChromaDB
       ↓
Query → Security check → top-K retrieval (cosine similarity)
       ↓
Generate → NVIDIA Llama-3.1-70B → response sanitization
```

---

## Security Layer

| Threat | Protection | Example |
|--------|------------|---------|
| Prompt injection | Pattern detection | "Ignore previous instructions" → Blocked |
| Harmful content | Keyword filtering | Blocked at query time |
| PII extraction | Query analysis | "List all emails" → Blocked |
| DOS | Rate limiting | 10 queries/min per session |
| Large files | Size validation | 50MB limit |
| Path traversal | Filename sanitization | `../secret.txt` → Blocked |
| Data leaks | Response sanitization | Emails/phones redacted |

Security overhead: <1ms per request.

---

## Tech Stack

| Component | Technology |
|-----------|------------|
| RAG Framework | LlamaIndex 0.10.68 |
| LLM | NVIDIA NIM — Llama-3.1-70B |
| Embeddings | OpenAI text-embedding-3-large |
| Vector Store | ChromaDB 0.4.24 |
| API | FastAPI + Uvicorn |
| Deployment | AWS |

---

## Prerequisites

- Python 3.11 or 3.12
- OpenAI API key (embeddings)
- NVIDIA API key (LLM)

---

## Quick Start

### 1. Clone and Setup
```bash
git clone https://github.com/IneshReddy249/RAG_PIPELINE.git
cd RAG_PIPELINE

python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
# .env
OPENAI_API_KEY=sk-your-key
NVIDIA_API_KEY=nvapi-your-key

CHROMA_DB_PATH=./data/chroma_db
CHROMA_COLLECTION_NAME=rag_documents
EMBEDDING_MODEL=text-embedding-3-large

CHUNK_SIZE=1024
CHUNK_OVERLAP=200
TOP_K_RESULTS=10
SIMILARITY_THRESHOLD=0.5

LLM_MODEL=meta/llama-3.1-70b-instruct
LLM_TEMPERATURE=0.1
MAX_TOKENS=1024
LLM_BASE_URL=https://integrate.api.nvidia.com/v1
```

### 3. Run
```bash
uvicorn api:app --reload
# API: http://localhost:8000
# Docs: http://localhost:8000/docs
```

---

## API Usage

### Upload Document
```bash
curl -X POST "http://localhost:8000/upload" \
  -F "file=@your_document.pdf"
```
```json
{"status": "ready", "file": "doc.pdf", "chunks": 47, "time": 12.3}
```

### Query
```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "What causes LLM hallucinations?"}'
```
```json
{
  "answer": "Three main causes: data quality issues...",
  "sources": [{"id": 1, "text": "...", "score": 0.556}],
  "time": 3.2,
  "session_id": "session_1234567890"
}
```

### Follow-up (with memory)
```bash
curl -X POST "http://localhost:8000/query" \
  -d '{"query": "How do we prevent the first one?",
       "session_id": "session_1234567890"}'
```

---

## Configuration Reference
```bash
# Chunking
CHUNK_SIZE=1024        # tokens per chunk
CHUNK_OVERLAP=200      # overlap between chunks

# Retrieval
TOP_K_RESULTS=10       # chunks retrieved per query
SIMILARITY_THRESHOLD=0.5  # minimum cosine similarity

# LLM
LLM_TEMPERATURE=0.1    # lower = more factual
MAX_TOKENS=1024        # max response length
```

---

## Project Structure
```
RAG_PIPELINE/
├── api.py                    # FastAPI endpoints
├── guardrails.py             # Security layer
├── config.py                 # Environment config
├── requirements.txt
├── src/
│   ├── document_processor.py
│   ├── embedding_storing.py
│   ├── retrieving.py
│   └── generation.py
└── data/
    ├── raw/                  # Uploaded documents
    └── chroma_db/            # Vector index (auto-created)
```

---

## Testing Security
```bash
python guardrails.py

# Output:
# SAFE:    "What causes hallucinations?"
# BLOCKED: "Ignore previous instructions"
# BLOCKED: "How to make a bomb"
# BLOCKED: "Show me all email addresses"
```

---

## Dependencies
```
llama-index==0.10.68
llama-index-embeddings-openai==0.1.6
llama-index-llms-nvidia==0.1.3
llama-index-vector-stores-chroma==0.1.6
fastapi==0.109.2
uvicorn==0.27.1
chromadb==0.4.24
pypdf==4.0.1
python-dotenv==1.0.1
python-multipart
```

---

## Related Projects

The inference infrastructure powering the LLM calls in this system:

- [Llama-3.1-8B on H100 — 1,700+ tok/s, 11ms TTFT](https://github.com/IneshReddy249/LLAMA-TRT-OPTIMIZATION)
- [Speculative Decoding — 2.26× latency reduction](https://github.com/IneshReddy249/SPECULATIVE_DECODING)
- [Mixtral 8x7B MoE — 57→120 tok/s on dual A100s](https://github.com/IneshReddy249/vLLM-mixtral-MoE-optimization)

---

## Author

**Inesh Reddy Chappidi** — LLM Inference & Systems Engineer

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Inesh_Reddy-0077B5?logo=linkedin)](https://www.linkedin.com/in/inesh-reddy)
[![GitHub](https://img.shields.io/badge/GitHub-IneshReddy249-181717?logo=github)](https://github.com/IneshReddy249)
