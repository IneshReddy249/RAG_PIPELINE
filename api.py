#!/usr/bin/env python3
"""RAG API with Minimal Security Guardrails"""

from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import time
import shutil
from datetime import datetime
from collections import defaultdict
import config
from src.document_processor import process_documents
from src.embedding_storing import embed_and_store, load_existing_index, initialize_vector_store
from src.retrieving import retrieve_and_format
from src.generation import initialize_llm
from guardrails import Guardrails

class QueryRequest(BaseModel):
    query: str
    top_k: Optional[int] = None
    session_id: Optional[str] = None

class QueryResponse(BaseModel):
    answer: str
    sources: List[Dict[str, Any]]
    time: float
    session_id: str

app = FastAPI(title="RAG API")
_index = _llm = None
_conversations = defaultdict(list)
_guards = Guardrails()

@app.on_event("startup")
async def startup():
    global _index, _llm
    config.RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
    try:
        _index = load_existing_index()
    except:
        pass
    _llm = initialize_llm()
    print("✅ Server ready with security guardrails")

@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    """Upload document with security checks"""
    global _index, _guards
    start = time.time()
    
    # Read and validate file
    file_path = config.RAW_DATA_DIR / file.filename
    file_size = 0
    
    with file_path.open("wb") as f:
        while chunk := await file.read(8192):
            file_size += len(chunk)
            f.write(chunk)
    
    # Security check
    is_safe, reason = _guards.check_upload(file.filename, file_size)
    if not is_safe:
        file_path.unlink()
        raise HTTPException(400, f"Upload blocked: {reason}")
    
    # Process
    nodes = process_documents()
    _index = embed_and_store(nodes)
    
    return {
        "status": "ready",
        "file": file.filename,
        "chunks": len(nodes),
        "time": round(time.time() - start, 2)
    }

@app.post("/query", response_model=QueryResponse)
async def query(req: QueryRequest):
    """Query with security checks"""
    global _index, _llm, _conversations, _guards
    start = time.time()
    
    if not _index:
        raise HTTPException(400, "Upload a document first")
    
    session_id = req.session_id or f"session_{int(time.time())}"
    
    # Security check
    is_safe, reason = _guards.check_query(req.query, session_id)
    if not is_safe:
        raise HTTPException(400, f"Query blocked: {reason}")
    
    # Retrieve
    if req.top_k:
        config.TOP_K = req.top_k
    
    retrieval = retrieve_and_format(req.query, _index)
    if not retrieval["context"]:
        raise HTTPException(404, "No relevant context found")
    
    # Build prompt with history
    conversation = _conversations[session_id]
    history = ""
    if conversation:
        history = "\n\nPrevious conversation:\n"
        for msg in conversation[-4:]:
            history += f"User: {msg['user']}\nAssistant: {msg['assistant']}\n\n"
    
    prompt = f"""Answer using the context below.{history}
Context: {retrieval["context"]}

Question: {req.query}
Answer:"""
    
    # Generate
    response = _llm.complete(prompt)
    answer = _guards.sanitize(response.text.strip())
    
    # Save history
    conversation.append({
        "user": req.query,
        "assistant": answer,
        "timestamp": datetime.utcnow().isoformat()
    })
    
    if len(conversation) > 10:
        conversation.pop(0)
    
    return QueryResponse(
        answer=answer,
        sources=[{
            "id": i + 1,
            "text": n.text[:150] + "...",
            "score": round(n.score, 3)
        } for i, n in enumerate(retrieval["nodes"])],
        time=round(time.time() - start, 2),
        session_id=session_id
    )

@app.get("/conversation/{session_id}")
async def get_conversation(session_id: str):
    """Get conversation history"""
    if session_id not in _conversations:
        raise HTTPException(404, "Session not found")
    return {
        "session_id": session_id,
        "messages": _conversations[session_id],
        "count": len(_conversations[session_id])
    }

@app.delete("/conversation/{session_id}")
async def clear_conversation(session_id: str):
    """Clear conversation"""
    if session_id in _conversations:
        del _conversations[session_id]
        return {"status": "cleared"}
    raise HTTPException(404, "Session not found")

@app.get("/")
async def root():
    vs = initialize_vector_store()
    return {
        "name": "RAG API with Security",
        "chunks": vs._collection.count(),
        "sessions": len(_conversations),
        "security": ["Rate limiting", "Content filtering", "Sanitization"],
        "endpoints": ["/upload", "/query", "/conversation/{id}", "/docs"]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)