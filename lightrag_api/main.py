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
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import asyncio
from lightrag import LightRAG, QueryParam
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

# Add CORS middleware to allow browser access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (change to specific domains in production)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Environment variables

# Environment variables - Support for both Ollama and OpenAI bindings
LLM_BINDING = os.getenv("LLM_BINDING", "ollama")
LLM_BINDING_HOST = os.getenv("LLM_BINDING_HOST", os.getenv("OLLAMA_BASE_URL", "http://ollama:11434"))
LLM_MODEL = os.getenv("LLM_MODEL", "llama3.3:70b")

EMBEDDING_BINDING = os.getenv("EMBEDDING_BINDING", "ollama")
EMBEDDING_BINDING_HOST = os.getenv("EMBEDDING_BINDING_HOST", os.getenv("OLLAMA_BASE_URL", "http://ollama:11434"))
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "bge-m3")

LIGHTRAG_API_KEY = os.getenv("LIGHTRAG_API_KEY", "")
WORKING_DIR = os.getenv("WORKING_DIR", "/data/rag_storage")
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "32000"))

os.makedirs(WORKING_DIR, exist_ok=True)


# Custom embedding function

async def _ollama_embedding_func_custom(texts: List[str]) -> List:
    async with httpx.AsyncClient(timeout=300.0) as client:
        embeddings = []
        max_retries = 3
        retry_delay = 1.0  # seconds
        
        for text in texts:
            success = False
            last_error = None
            
            for attempt in range(max_retries):
                try:
                    response = await client.post(
                        f"{OLLAMA_BASE_URL}/api/embeddings",
                        json={"model": EMBEDDING_MODEL, "prompt": text}
                    )
                    response.raise_for_status()
                    result = response.json()
                    embedding = result.get("embedding", [])
                    if embedding and len(embedding) > 0:
                        embeddings.append(np.array(embedding, dtype=np.float32))
                        success = True
                        break
                    else:
                        last_error = "Empty embedding returned"
                except httpx.HTTPStatusError as e:
                    last_error = f"HTTP {e.response.status_code}: {e.response.text[:100]}"
                    if e.response.status_code >= 500 and attempt < max_retries - 1:
                        # Server error - retry after delay
                        await asyncio.sleep(retry_delay * (attempt + 1))
                        continue
                    else:
                        break
                except Exception as e:
                    last_error = f"{type(e).__name__}: {str(e)}"
                    if attempt < max_retries - 1:
                        await asyncio.sleep(retry_delay * (attempt + 1))
                        continue
                    else:
                        break
            
            if not success:
                print(f"Warning: Embedding failed after {max_retries} attempts: {last_error}")
                # Fallback to zero vector (1024 dim for bge-m3)
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
        async with httpx.AsyncClient(timeout=180.0) as client:  # Reduced timeout from 300s to 180s (3 min)
            response = await client.post(
                f"{OLLAMA_BASE_URL}/api/chat",
                json={
                    "model": LLM_MODEL,
                    "messages": messages,
                    "stream": False,
                    "options": {
                        "num_ctx": 16384,  # Reduced from 32768 to 16384 for faster processing (still large enough)
                        "temperature": 0.7,  # Add temperature for consistency
                        "top_p": 0.9,  # Nucleus sampling
                    }
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


# OpenAI-compatible LLM function
async def _openai_llm_async_custom(
    prompt: str,
    system_prompt: Optional[str] = None,
    history_messages: List = [],
    keyword_extraction: bool = False,
    **kwargs
) -> str:
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.extend(history_messages)
    messages.append({"role": "user", "content": prompt})

    try:
        headers = {"Authorization": f"Bearer {LIGHTRAG_API_KEY}"} if LIGHTRAG_API_KEY else {}
        async with httpx.AsyncClient(timeout=180.0) as client:
            response = await client.post(
                f"{LLM_BINDING_HOST}/chat/completions" if not LLM_BINDING_HOST.endswith("/chat/completions") else LLM_BINDING_HOST,
                headers=headers,
                json={
                    "model": LLM_MODEL,
                    "messages": messages,
                    "stream": False,
                    "max_tokens": MAX_TOKENS,
                    "temperature": kwargs.get("temperature", 0.7),
                    "top_p": kwargs.get("top_p", 0.9),
                }
            )
            response.raise_for_status()
            result = response.json()
            choices = result.get("choices", [])
            if choices:
                return choices[0].get("message", {}).get("content", "")
            return ""
    except Exception as e:
        print(f"Error in OpenAI LLM call: {e}")
        import traceback
        traceback.print_exc()
        return ""

# OpenAI-compatible Embedding function
async def _openai_embedding_func_custom(texts: List[str]) -> List[np.ndarray]:
    headers = {"Authorization": f"Bearer {LIGHTRAG_API_KEY}"} if LIGHTRAG_API_KEY else {}
    async with httpx.AsyncClient(timeout=300.0) as client:
        try:
            # Check if using Azure or standard OpenAI format
            # Standard: /embeddings
            url = f"{EMBEDDING_BINDING_HOST}/embeddings" if not EMBEDDING_BINDING_HOST.endswith("/embeddings") else EMBEDDING_BINDING_HOST
            
            response = await client.post(
                url,
                headers=headers,
                json={
                    "model": EMBEDDING_MODEL,
                    "input": texts
                }
            )
            response.raise_for_status()
            result = response.json()
            data = result.get("data", [])
            # Sort by index to ensure order matches input
            data.sort(key=lambda x: x.get("index", 0))
            return np.array([item["embedding"] for item in data], dtype=np.float32)
        except Exception as e:
            print(f"Error in OpenAI Embedding call: {e}")
            # Fallback to zeros if everything fails
            return np.zeros((len(texts), 768), dtype=np.float32)

# Use custom functions (built-in may not work with HTTP endpoints in Docker)
# Select functions based on binding
if LLM_BINDING.lower() == "openai":
    llm_func = _openai_llm_async_custom
    print(f"Using OpenAI-compatible LLM binding: {LLM_BINDING_HOST} ({LLM_MODEL})")
else:
    llm_func = _ollama_llm_async_custom
    print(f"Using Ollama LLM binding: {LLM_BINDING_HOST} ({LLM_MODEL})")

if EMBEDDING_BINDING.lower() == "openai":
    embedding_func = EmbeddingFunc(
        func=_openai_embedding_func_custom,
        embedding_dim=768, # Common for noms/bert, but adjust if needed
        max_token_size=8192
    )
    print(f"Using OpenAI-compatible Embedding binding: {EMBEDDING_BINDING_HOST} ({EMBEDDING_MODEL})")
else:
    embedding_func = EmbeddingFunc(
        func=_ollama_embedding_func_custom,
        embedding_dim=1024,
        max_token_size=8192
    )
    print(f"Using Ollama Embedding binding: {EMBEDDING_BINDING_HOST} ({EMBEDDING_MODEL})")


lightrag = None
print(f"LightRAG will be initialized on first request.")
print(f"  Binding: {LLM_BINDING}, URL: {LLM_BINDING_HOST}, Model: {LLM_MODEL}")

class IngestRequest(BaseModel):
    text: str
    doc_id: str

class QueryRequest(BaseModel):
    query: str
    mode: str = "hybrid"
    # Optional query parameters for dynamic adjustment
    query_edges_top_k: Optional[int] = None
    query_edges_cosine: Optional[float] = None
    query_nodes_top_k: Optional[int] = None
    query_nodes_cosine: Optional[float] = None
    chunk_top_k: Optional[int] = None
    chunk_cosine: Optional[float] = None
    enable_rerank: Optional[bool] = None

@app.get("/health")
async def health_check():
    backend_status = False
    backend_error = None
    
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            if LLM_BINDING.lower() == "openai":
                # For OpenAI check models endpoint
                url = f"{LLM_BINDING_HOST}/models" if not LLM_BINDING_HOST.endswith("/chat/completions") else LLM_BINDING_HOST.replace("/chat/completions", "/models")
                response = await client.get(url, headers={"Authorization": f"Bearer {LIGHTRAG_API_KEY}"} if LIGHTRAG_API_KEY else {})
            else:
                # For Ollama check tags
                response = await client.get(f"{LLM_BINDING_HOST}/api/tags")
                
            backend_status = response.status_code == 200
            if not backend_status:
                backend_error = f"HTTP {response.status_code}"
    except Exception as e:
        backend_status = False
        backend_error = str(e)
    
    status = {
        "api": "healthy",
        "llm_binding": LLM_BINDING,
        "backend": "healthy" if backend_status else "unhealthy",
        "lightrag_initialized": lightrag is not None,
        "working_dir": WORKING_DIR,
        "llm_host": LLM_BINDING_HOST,
        "nest_asyncio": "enabled"
    }
    if not backend_status:
        status["backend_error"] = backend_error
    return status

def _initialize_lightrag():
    global lightrag
    if lightrag is None:
        try:
            lightrag = LightRAG(
                working_dir=WORKING_DIR,
                llm_model_func=llm_func,
                llm_model_name=LLM_MODEL,
                embedding_func=embedding_func,
                default_embedding_timeout=300,
                embedding_func_max_async=4,
            )
            print("✓ LightRAG instance created with increased embedding timeout (300s)")
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
        # Default optimized parameters (if not provided by user)
        default_params = {
            "query_edges_top_k": 20,
            "query_edges_cosine": 0.2,
            "query_nodes_top_k": 20,
            "query_nodes_cosine": 0.2,
            "chunk_top_k": 10,
            "chunk_cosine": 0.2,
            "enable_rerank": False,
        }
        
        # Use user-provided parameters or defaults
        user_params = {
            "query_edges_top_k": request.query_edges_top_k,
            "query_edges_cosine": request.query_edges_cosine,
            "query_nodes_top_k": request.query_nodes_top_k,
            "query_nodes_cosine": request.query_nodes_cosine,
            "chunk_top_k": request.chunk_top_k,
            "chunk_cosine": request.chunk_cosine,
            "enable_rerank": request.enable_rerank,
        }
        
        # Merge user params with defaults (user params override defaults)
        query_params = {k: user_params[k] if user_params[k] is not None else default_params[k] 
                       for k in default_params.keys()}
        
        # Prepare QueryParam
        qp = QueryParam(
            mode=request.mode,
            top_k=query_params.get("query_nodes_top_k", 20),
            chunk_top_k=query_params.get("chunk_top_k", 10),
            enable_rerank=query_params.get("enable_rerank", False)
        )
        
        # Execute query
        if asyncio.iscoroutinefunction(lightrag.query):
            response = await lightrag.query(request.query, param=qp)
        else:
            response = await asyncio.to_thread(lightrag.query, request.query, param=qp)
        
        return {
            "answer": response, 
            "query": request.query, 
            "mode": request.mode,
            "parameters_used": {
                "top_k": qp.top_k,
                "chunk_top_k": qp.chunk_top_k,
                "enable_rerank": qp.enable_rerank,
                "mode": qp.mode
            }
        }
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"Query error:\n{error_trace}")
        raise HTTPException(status_code=500, detail=f"Failed to process query: {str(e)}\n\n{error_trace}")

@app.get("/graph")
async def get_graph(limit: int = 100):
    """Get knowledge graph data for visualization (entities and relations)"""
    global lightrag
    if lightrag is None:
        try:
            _initialize_lightrag()
            await lightrag.initialize_storages()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to initialize LightRAG: {str(e)}")
    
    try:
        entities = []
        relations = []
        
        # Try multiple methods to access LightRAG storage
        try:
            # Method 1: Try to access storage attributes directly
            if hasattr(lightrag, 'entity_storage') and lightrag.entity_storage:
                entity_storage = lightrag.entity_storage
                # Check if it's a dict-like structure
                if hasattr(entity_storage, '__iter__'):
                    for i, (key, entity) in enumerate(list(entity_storage.items() if hasattr(entity_storage, 'items') else entity_storage)[:limit]):
                        if isinstance(entity, dict):
                            entities.append({
                                "id": entity.get("entity_name", entity.get("id", key if isinstance(key, str) else f"entity_{i}")),
                                "name": entity.get("entity_name", entity.get("name", str(key))),
                                "description": entity.get("entity_desc", entity.get("description", "")),
                                "type": entity.get("type", "entity")
                            })
            
            if hasattr(lightrag, 'relation_storage') and lightrag.relation_storage:
                relation_storage = lightrag.relation_storage
                if hasattr(relation_storage, '__iter__'):
                    for i, (key, rel) in enumerate(list(relation_storage.items() if hasattr(relation_storage, 'items') else relation_storage)[:limit]):
                        if isinstance(rel, dict):
                            relations.append({
                                "from": rel.get("head_entity", rel.get("head", rel.get("from", ""))),
                                "to": rel.get("tail_entity", rel.get("tail", rel.get("to", ""))),
                                "relation": rel.get("relation_name", rel.get("relation", rel.get("relation_type", ""))),
                                "description": rel.get("description", "")
                            })
            
            # Method 2: Try to read from GraphML file
            if len(entities) == 0:
                graph_file = os.path.join(WORKING_DIR, "graph_chunk_entity_relation.graphml")
                if os.path.exists(graph_file):
                    try:
                        import networkx as nx
                        G = nx.read_graphml(graph_file)
                        
                        count = 0
                        for node_id, data in G.nodes(data=True):
                            if count >= limit:
                                break
                            
                            # Skip chunk nodes if we only want entities
                            # Entities usually have quotes or specific formatting, chunks are hashes
                            if data.get('d') and 'chunk' in data.get('d', ''):
                                continue
                                
                            entities.append({
                                "id": node_id.strip('"'),
                                "name": node_id.strip('"'),
                                "description": data.get("description", data.get("desc", "")).strip('"'),
                                "type": "entity"
                            })
                            count += 1
                            
                        count = 0
                        for u, v, data in G.edges(data=True):
                            if count >= limit:
                                break
                            
                            relations.append({
                                "from": u.strip('"'),
                                "to": v.strip('"'),
                                "relation": data.get("label", data.get("relation", "related")),
                                "description": data.get("description", "")
                            })
                            count += 1
                    except Exception as e:
                        print(f"Error reading GraphML: {e}")
            
            # Legacy JSON fallback
            if len(entities) == 0 and len(relations) == 0:
                entity_file = os.path.join(WORKING_DIR, "kv_store_full_entities.json")
                relation_file = os.path.join(WORKING_DIR, "kv_store_full_relations.json")
                
                if os.path.exists(entity_file):
                    with open(entity_file, 'r', encoding='utf-8') as f:
                        entity_data = json.load(f)
                        if isinstance(entity_data, dict):
                            for key, entity in list(entity_data.items())[:limit]:
                                entities.append({
                                    "id": entity.get("entity_name", key),
                                    "name": entity.get("entity_name", entity.get("name", key)),
                                    "description": entity.get("entity_desc", entity.get("description", "")),
                                    "type": entity.get("type", "entity")
                                })
                        elif isinstance(entity_data, list):
                            for i, entity in enumerate(entity_data[:limit]):
                                entities.append({
                                    "id": entity.get("entity_name", entity.get("id", f"entity_{i}")),
                                    "name": entity.get("entity_name", entity.get("name", f"Entity {i}")),
                                    "description": entity.get("entity_desc", entity.get("description", "")),
                                    "type": entity.get("type", "entity")
                                })
                
                if os.path.exists(relation_file):
                    with open(relation_file, 'r', encoding='utf-8') as f:
                        relation_data = json.load(f)
                        if isinstance(relation_data, dict):
                            for key, rel in list(relation_data.items())[:limit]:
                                relations.append({
                                    "from": rel.get("head_entity", rel.get("head", rel.get("from", ""))),
                                    "to": rel.get("tail_entity", rel.get("tail", rel.get("to", ""))),
                                    "relation": rel.get("relation_name", rel.get("relation", rel.get("relation_type", ""))),
                                    "description": rel.get("description", "")
                                })
                        elif isinstance(relation_data, list):
                            for i, rel in enumerate(relation_data[:limit]):
                                relations.append({
                                    "from": rel.get("head_entity", rel.get("head", rel.get("from", ""))),
                                    "to": rel.get("tail_entity", rel.get("tail", rel.get("to", ""))),
                                    "relation": rel.get("relation_name", rel.get("relation", rel.get("relation_type", ""))),
                                    "description": rel.get("description", "")
                                })
        
        except Exception as e:
            print(f"Warning: Could not access graph storage: {e}")
            import traceback
            traceback.print_exc()
        
        # Ensure we have valid data (nodes need IDs, edges need from/to)
        valid_entities = []
        valid_relations = []
        entity_ids = set()
        
        for entity in entities:
            if entity.get("id") or entity.get("name"):
                entity_id = entity.get("id") or entity.get("name")
                if entity_id not in entity_ids:
                    entity_ids.add(entity_id)
                    valid_entities.append({
                        "id": entity_id,
                        "name": entity.get("name", entity_id),
                        "description": entity.get("description", ""),
                        "type": entity.get("type", "entity")
                    })
        
        for rel in relations:
            from_id = rel.get("from", "").strip()
            to_id = rel.get("to", "").strip()
            if from_id and to_id and from_id in entity_ids and to_id in entity_ids:
                valid_relations.append({
                    "from": from_id,
                    "to": to_id,
                    "relation": rel.get("relation", ""),
                    "description": rel.get("description", "")
                })
        
        return {
            "nodes": valid_entities,
            "edges": valid_relations,
            "node_count": len(valid_entities),
            "edge_count": len(valid_relations)
        }
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"Graph retrieval error:\n{error_trace}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve graph: {str(e)}")

@app.get("/graph/query")
async def get_query_graph(query: str, mode: str = "hybrid", limit: int = 50):
    """Get graph data for a specific query (entities and relations relevant to the query)"""
    global lightrag
    if lightrag is None:
        try:
            _initialize_lightrag()
            await lightrag.initialize_storages()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to initialize LightRAG: {str(e)}")
    
    try:
        # Execute query to get relevant entities and relations
        # LightRAG's query internally retrieves entities/relations - we need to capture them
        # For now, return the full graph (can be enhanced later to filter by query relevance)
        full_graph = await get_graph(limit=limit)
        return full_graph
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        raise HTTPException(status_code=500, detail=f"Failed to get query graph: {str(e)}")

@app.get("/")
async def root():
    static_dir = os.path.join(os.path.dirname(__file__), "static")
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    else:
        return {
            "name": "LightRAG API", 
            "version": "1.0.0", 
            "endpoints": {
                "ingest": "POST /ingest", 
                "query": "POST /query", 
                "health": "GET /health",
                "graph": "GET /graph",
                "graph/query": "GET /graph/query?query=...&mode=..."
            }, 
            "docs": "/docs"
        }
