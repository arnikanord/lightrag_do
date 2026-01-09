"""
FastAPI wrapper for LightRAG system
Provides endpoints for document ingestion and graph-based queries
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os
import asyncio
from lightrag import LightRAG
import httpx
from typing import Optional, Dict, Any, List
import json

app = FastAPI(title="LightRAG API", version="1.0.0")

# Serve static files (web interface)
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
    
    @app.get("/")
    async def serve_index():
        """Serve the web interface"""
        return FileResponse(os.path.join(static_dir, "index.html"))

# Environment variables
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434")
WORKING_DIR = "/data/rag_storage"
LLM_MODEL = "llama3.3:70b"
EMBEDDING_MODEL = "bge-m3"

# Ensure working directory exists
os.makedirs(WORKING_DIR, exist_ok=True)


# Create Ollama LLM function using functools.partial (has .func attribute)
from functools import partial

def _ollama_llm_internal(prompt: str, system_prompt: Optional[str] = None, 
                        base_url: str = OLLAMA_BASE_URL, 
                        model: str = LLM_MODEL, **kwargs) -> str:
    """Internal LLM function for Ollama - uses local GPU-accelerated Llama (sync)"""
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})
    
    # Use synchronous httpx client
    with httpx.Client(timeout=300.0) as client:
        response = client.post(
            f"{base_url}/api/chat",
            json={
                "model": model,
                "messages": messages,
                "stream": False
            }
        )
        response.raise_for_status()
        result = response.json()
        return result.get("message", {}).get("content", "")


async def _ollama_embedding_internal(texts: List[str], 
                               base_url: str = OLLAMA_BASE_URL,
                               model: str = EMBEDDING_MODEL, **kwargs) -> List[List[float]]:
    """Internal embedding function for Ollama (async)"""
    async with httpx.AsyncClient(timeout=60.0) as client:
        embeddings = []
        for text in texts:
            response = await client.post(
                f"{base_url}/api/embeddings",
                json={
                    "model": model,
                    "prompt": text
                }
            )
            response.raise_for_status()
            result = response.json()
            embeddings.append(result.get("embedding", []))
        return embeddings


# Use LightRAG's EmbeddingFunc class directly (it's a dataclass)
from lightrag.utils import EmbeddingFunc

# Create the base embedding function
def _base_ollama_embedding(texts: List[str], base_url: str = OLLAMA_BASE_URL, 
                           model: str = EMBEDDING_MODEL, **kwargs) -> List[List[float]]:
    """Base embedding function that will be wrapped"""
    with httpx.Client(timeout=60.0) as client:
        embeddings = []
        for text in texts:
            response = client.post(
                f"{base_url}/api/embeddings",
                json={"model": model, "prompt": text}
            )
            response.raise_for_status()
            result = response.json()
            embeddings.append(result.get("embedding", []))
        return embeddings

# Create a closure-based embedding function (async)
def _create_ollama_embedding_func():
    """Create async embedding function with bound parameters"""
    async def embedding_func(texts: List[str], **kwargs) -> List[List[float]]:
        return await _base_ollama_embedding(texts, base_url=OLLAMA_BASE_URL, model=EMBEDDING_MODEL, **kwargs)
    return embedding_func

# Create sync wrappers that return coroutines (LightRAG's wrapper will await them)
def _ollama_llm_wrapper(prompt: str, system_prompt: Optional[str] = None, **kwargs):
    """Sync wrapper that returns coroutine for LLM function"""
    # Return coroutine directly, don't await - LightRAG's wrapper will await it
    def sync_call():
        return _ollama_llm_internal(prompt, system_prompt, base_url=OLLAMA_BASE_URL, model=LLM_MODEL, **kwargs)
    return asyncio.to_thread(sync_call)

def _ollama_embedding_wrapper(texts: List[str], **kwargs):
    """Sync wrapper that returns coroutine for embedding function"""
    # Return coroutine directly, don't await - LightRAG's wrapper will await it
    def sync_call():
        return _base_ollama_embedding(texts, base_url=OLLAMA_BASE_URL, model=EMBEDDING_MODEL, **kwargs)
    return asyncio.to_thread(sync_call)

# Create functions using LightRAG's EmbeddingFunc dataclass
ollama_llm_func = _ollama_llm_wrapper
ollama_embedding_func = EmbeddingFunc(func=_ollama_embedding_wrapper, embedding_dim=1024)


# Initialize LightRAG - delay initialization until first use to avoid errors
# LightRAG will be initialized lazily when first needed
lightrag = None
print(f"LightRAG will be initialized on first request. Ollama URL: {OLLAMA_BASE_URL}, Model: {LLM_MODEL}")


# Request models
class IngestRequest(BaseModel):
    text: str
    doc_id: str


class QueryRequest(BaseModel):
    query: str
    mode: str = "hybrid"


# Health check endpoint
@app.get("/health")
async def health_check():
    """Check if the API and Ollama backend are healthy"""
    try:
        # Check Ollama connectivity
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{OLLAMA_BASE_URL}/api/tags")
            ollama_status = response.status_code == 200
    except Exception as e:
        ollama_status = False
        ollama_error = str(e)
    
    status = {
        "api": "healthy",
        "ollama": "healthy" if ollama_status else "unhealthy",
        "lightrag_initialized": lightrag is not None,
        "working_dir": WORKING_DIR,
        "ollama_url": OLLAMA_BASE_URL
    }
    
    if not ollama_status:
        status["ollama_error"] = ollama_error
    
    status_code = 200 if ollama_status and lightrag is not None else 503
    return status


@app.post("/ingest")
async def ingest_document(request: IngestRequest):
    """
    Ingest a document into the LightRAG knowledge graph
    
    Args:
        request: IngestRequest with text and doc_id
        
    Returns:
        Success message with doc_id
    """
    global lightrag
    
    # Lazy initialization if needed
    if lightrag is None:
        try:
            lightrag = LightRAG(
                working_dir=WORKING_DIR,
                llm_model_func=ollama_llm_func,
                llm_model_name=LLM_MODEL,
                embedding_func=ollama_embedding_func,
            )
            # Initialize storages (required for insert/query to work)
            await lightrag.initialize_storages()
            print("LightRAG initialized and storages ready!")
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            print(f"LightRAG initialization error:\n{error_trace}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to initialize LightRAG: {str(e)}\n\nTraceback:\n{error_trace}"
            )
    
    if not request.text or not request.text.strip():
        raise HTTPException(
            status_code=400,
            detail="Text cannot be empty"
        )
    
    if not request.doc_id or not request.doc_id.strip():
        raise HTTPException(
            status_code=400,
            detail="doc_id cannot be empty"
        )
    
    try:
        # Run ingestion in thread pool to avoid blocking
        await asyncio.to_thread(lightrag.insert, request.text, request.doc_id)
        return {
            "message": "Document ingested successfully",
            "doc_id": request.doc_id,
            "text_length": len(request.text)
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to ingest document: {str(e)}"
        )


@app.post("/query")
async def query_document(request: QueryRequest):
    """
    Query the LightRAG knowledge graph
    
    Args:
        request: QueryRequest with query string and mode (default: "hybrid")
        
    Returns:
        Answer from LightRAG
    """
    global lightrag
    
    # Lazy initialization if needed
    if lightrag is None:
        try:
            lightrag = LightRAG(
                working_dir=WORKING_DIR,
                llm_model_func=ollama_llm_func,
                llm_model_name=LLM_MODEL,
                embedding_func=ollama_embedding_func,
            )
            # Initialize storages (required for insert/query to work)
            await lightrag.initialize_storages()
            print("LightRAG initialized and storages ready!")
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            print(f"LightRAG initialization error:\n{error_trace}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to initialize LightRAG: {str(e)}\n\nTraceback:\n{error_trace}"
            )
    
    if not request.query or not request.query.strip():
        raise HTTPException(
            status_code=400,
            detail="Query cannot be empty"
        )
    
    # Validate mode
    valid_modes = ["hybrid", "naive", "local", "global"]
    if request.mode not in valid_modes:
        raise HTTPException(
            status_code=400,
            detail=f"Mode must be one of: {', '.join(valid_modes)}"
        )
    
    try:
        # Run query in thread pool to avoid blocking (LightRAG.query doesn't accept mode parameter)
        response = await asyncio.to_thread(lightrag.query, request.query)
        return {
            "answer": response,
            "query": request.query,
            "mode": request.mode
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process query: {str(e)}"
        )


@app.get("/")
async def root():
    """Serve the web interface"""
    static_dir = os.path.join(os.path.dirname(__file__), "static")
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    else:
        # Fallback to JSON if HTML not found
        return {
            "name": "LightRAG API",
            "version": "1.0.0",
            "endpoints": {
                "ingest": "POST /ingest",
                "query": "POST /query",
                "health": "GET /health"
            },
            "docs": "/docs"
        }
