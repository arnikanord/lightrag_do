"""
FastAPI wrapper for LightRAG system
Provides endpoints for document ingestion and graph-based queries
"""

# CRITICAL: Apply nest_asyncio FIRST before any other imports
# This fixes event loop conflicts between FastAPI and LightRAG
# Note: Using --loop asyncio in uvicorn (not uvloop) so nest_asyncio works
import nest_asyncio
nest_asyncio.apply()

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os
import asyncio
from lightrag import LightRAG
from lightrag.utils import EmbeddingFunc
import httpx
from typing import Optional, Dict, Any, List
import json
import numpy as np

# Try to import built-in Ollama functions
try:
    from lightrag.llm import ollama_model_complete, ollama_embedding as ollama_embedding_builtin
    BUILTIN_FUNCTIONS_AVAILABLE = True
except ImportError:
    BUILTIN_FUNCTIONS_AVAILABLE = False

app = FastAPI(title="LightRAG API", version="1.0.0")
print("✓ nest_asyncio applied (Solution 3)")

# Environment variables
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434")
WORKING_DIR = "/data/rag_storage"
LLM_MODEL = "llama3.3:70b"
EMBEDDING_MODEL = "bge-m3"

os.makedirs(WORKING_DIR, exist_ok=True)

# Custom embedding function

async def _ollama_embedding_func_custom(texts: List[str]) -> List:
    async with httpx.AsyncClient(timeout=60.0) as client:
        embeddings = []
        for text in texts:
            try:
                response = await client.post(
                    f"{OLLAMA_BASE_URL}/api/embeddings",
                    json={"model": EMBEDDING_MODEL, "prompt": text}
                )
                response.raise_for_status()
                result = response.json()
                embedding = result.get("embedding", [])
                embeddings.append(np.array(embedding if embedding else [0.0] * 1024, dtype=np.float32))
            except Exception as e:
                print(f"Error in embedding call: {e}")
                embeddings.append(np.array([0.0] * 1024, dtype=np.float32))
        # Return as 2D numpy array (LightRAG expects this format)
        if embeddings:
            return np.array(embeddings, dtype=np.float32)
        else:
            return np.array([], dtype=np.float32).reshape(0, 1024)

# Custom LLM function - CRITICAL: Must accept **kwargs
async def _ollama_llm_async_custom(
    prompt: str, 
    system_prompt: Optional[str] = None,
    history_messages: List = [],
    keyword_extraction: bool = False,
    **kwargs
) -> str:
    hashing_kv = kwargs.pop("hashing_kv", None)
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.extend(history_messages)
    messages.append({"role": "user", "content": prompt})
    
    try:
        async with httpx.AsyncClient(timeout=300.0) as client:
            response = await client.post(
                f"{OLLAMA_BASE_URL}/api/chat",
                json={
                    "model": LLM_MODEL,
                    "messages": messages,
                    "stream": False,
                    "options": {"num_ctx": 32768}
                }
            )
            response.raise_for_status()
            result = response.json()  # NOT awaitable - synchronous call
            content = result.get("message", {}).get("content", "")
            return content if content else ""
    except Exception as e:
        print(f"Error in LLM call: {e}")
        import traceback
        traceback.print_exc()
        return ""

# Use custom functions (built-in may not work with HTTP endpoints in Docker)
USE_BUILTIN = False
ollama_llm_func = _ollama_llm_async_custom
ollama_embedding_func = EmbeddingFunc(
    func=_ollama_embedding_func_custom,
    embedding_dim=1024,
    max_token_size=8192
)

lightrag = None
print(f"LightRAG will be initialized on first request.")
print(f"  Ollama URL: {OLLAMA_BASE_URL}, Model: {LLM_MODEL}")

class IngestRequest(BaseModel):
    text: str
    doc_id: str

class QueryRequest(BaseModel):
    query: str
    mode: str = "hybrid"

@app.get("/health")
async def health_check():
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{OLLAMA_BASE_URL}/api/tags")
            ollama_status = response.status_code == 200
            ollama_error = None
    except Exception as e:
        ollama_status = False
        ollama_error = str(e)
    
    status = {
        "api": "healthy",
        "ollama": "healthy" if ollama_status else "unhealthy",
        "lightrag_initialized": lightrag is not None,
        "working_dir": WORKING_DIR,
        "ollama_url": OLLAMA_BASE_URL,
        "nest_asyncio": "enabled"
    }
    if not ollama_status:
        status["ollama_error"] = ollama_error
    return status

def _initialize_lightrag():
    global lightrag
    if lightrag is None:
        try:
            lightrag = LightRAG(
                working_dir=WORKING_DIR,
                llm_model_func=ollama_llm_func,
                llm_model_name=LLM_MODEL,
                embedding_func=ollama_embedding_func,
            )
            print("✓ LightRAG instance created")
        except Exception as e:
            import traceback
            print(f"✗ LightRAG initialization error:\n{traceback.format_exc()}")
            raise

@app.post("/ingest")
async def ingest_document(request: IngestRequest):
    global lightrag
    if lightrag is None:
        try:
            _initialize_lightrag()
            await lightrag.initialize_storages()
            print("✓ LightRAG initialized and storages ready!")
        except Exception as e:
            import traceback
            raise HTTPException(status_code=500, detail=f"Failed to initialize LightRAG: {str(e)}\n\n{traceback.format_exc()}")
    
    if not request.text or not request.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")
    if not request.doc_id or not request.doc_id.strip():
        raise HTTPException(status_code=400, detail="doc_id cannot be empty")
    
    try:
        if asyncio.iscoroutinefunction(lightrag.insert):
            result = await lightrag.insert(request.text, request.doc_id)
        else:
            result = await asyncio.to_thread(lightrag.insert, request.text, request.doc_id)
        return {"message": "Document ingested successfully", "doc_id": request.doc_id, "text_length": len(request.text)}
    except Exception as e:
        import traceback
        print(f"Ingest error:\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Failed to ingest document: {str(e)}")

@app.post("/query")
async def query_document(request: QueryRequest):
    global lightrag
    if lightrag is None:
        try:
            _initialize_lightrag()
            await lightrag.initialize_storages()
            print("✓ LightRAG initialized and storages ready!")
        except Exception as e:
            import traceback
            raise HTTPException(status_code=500, detail=f"Failed to initialize LightRAG: {str(e)}\n\n{traceback.format_exc()}")
    
    if not request.query or not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    
    valid_modes = ["hybrid", "naive", "local", "global"]
    if request.mode not in valid_modes:
        raise HTTPException(status_code=400, detail=f"Mode must be one of: {', '.join(valid_modes)}")
    
    try:
        if asyncio.iscoroutinefunction(lightrag.query):
            response = await lightrag.query(request.query)
        else:
            response = await asyncio.to_thread(lightrag.query, request.query)
        return {"answer": response, "query": request.query, "mode": request.mode}
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"Query error:\n{error_trace}")
        raise HTTPException(status_code=500, detail=f"Failed to process query: {str(e)}\n\n{error_trace}")

@app.get("/")
async def root():
    static_dir = os.path.join(os.path.dirname(__file__), "static")
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    else:
        return {"name": "LightRAG API", "version": "1.0.0", "endpoints": {"ingest": "POST /ingest", "query": "POST /query", "health": "GET /health"}, "docs": "/docs"}
