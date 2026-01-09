# GAFTA Guardian - Architecture Documentation

## System Overview

GAFTA Guardian is a production-ready RAG (Retrieval-Augmented Generation) system designed for legal document analysis, specifically for GAFTA (Grain and Feed Trade Association) contracts and defaulters lists.

## Technology Stack

### Core Components

1. **LightRAG** (`lightrag-hku` v1.4.9.10)
   - Graph-based RAG system
   - Knowledge graph construction and querying
   - Entity and relationship extraction

2. **FastAPI** (Python 3.11)
   - REST API framework
   - Async request handling
   - Web interface serving

3. **Ollama**
   - Local LLM server
   - GPU-accelerated inference
   - Model: Llama 3.3 70B (40GB+)
   - Embedding: bge-m3 (1.2GB)

4. **Docker Compose**
   - Service orchestration
   - GPU passthrough
   - Volume management

## System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Client (Browser)                      │
│              http://SERVER_IP:8000                       │
└────────────────────┬────────────────────────────────────┘
                     │ HTTP/REST
                     ▼
┌─────────────────────────────────────────────────────────┐
│              FastAPI Container                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │  FastAPI Application (main.py)                  │   │
│  │  - POST /ingest                                 │   │
│  │  - POST /query                                  │   │
│  │  - GET /health                                  │   │
│  │  - GET / (web interface)                        │   │
│  └──────────────┬──────────────────────────────────┘   │
│                 │                                        │
│  ┌──────────────▼──────────────────────────────────┐   │
│  │  LightRAG Instance                               │   │
│  │  - Knowledge Graph Storage                       │   │
│  │  - Entity/Relationship Extraction                │   │
│  │  - Graph-based Query Processing                  │   │
│  └──────────────┬──────────────────────────────────┘   │
└──────────────────┼──────────────────────────────────────┘
                   │ HTTP (internal)
                   ▼
┌─────────────────────────────────────────────────────────┐
│              Ollama Container                            │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Ollama Server                                   │   │
│  │  - LLM: llama3.3:70b (GPU-accelerated)         │   │
│  │  - Embeddings: bge-m3                           │   │
│  │  - Port: 11434                                   │   │
│  └──────────────────────────────────────────────────┘   │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ▼
            ┌──────────┐
            │ NVIDIA   │
            │ H100 GPU │
            │ 80GB VRAM│
            └──────────┘
```

## Data Flow

### Document Ingestion Flow

```
1. Client → POST /ingest
   {
     "text": "Document content...",
     "doc_id": "unique_id"
   }

2. FastAPI → LightRAG.insert()
   - Text chunking
   - Entity extraction (via Ollama LLM)
   - Relationship extraction (via Ollama LLM)
   - Embedding generation (via Ollama bge-m3)
   - Graph construction

3. LightRAG → Storage
   - Entities → Vector DB
   - Relationships → Graph DB
   - Chunks → Key-Value Store
   - Metadata → JSON files
```

### Query Flow

```
1. Client → POST /query
   {
     "query": "Is Company X in defaulters?",
     "mode": "hybrid"
   }

2. FastAPI → LightRAG.query()
   - Query embedding (via Ollama bge-m3)
   - Entity matching
   - Graph traversal
   - Context retrieval
   - Answer generation (via Ollama LLM)

3. LightRAG → Response
   - Graph-based reasoning
   - Multi-hop relationship traversal
   - Contextual answer generation

4. FastAPI → Client
   {
     "answer": "Generated answer...",
     "query": "Original query",
     "mode": "hybrid"
   }
```

## Storage Architecture

### Persistent Storage

```
gafta-guardian/
├── ollama_data/          # Ollama models (40GB+)
│   └── models/
│       ├── llama3.3:70b/
│       └── bge-m3/
│
└── rag_data/             # LightRAG knowledge graph
    ├── vdb_entities.json      # Entity embeddings
    ├── vdb_relationships.json  # Relationship embeddings
    ├── vdb_chunks.json         # Text chunk embeddings
    ├── text_chunks.json        # Chunk metadata
    ├── full_entities.json      # Entity details
    ├── full_relations.json     # Relationship details
    └── doc_status.json         # Document processing status
```

### Storage Components

1. **Vector Databases** (nano-vectordb)
   - Entity embeddings (1024-dim from bge-m3)
   - Relationship embeddings
   - Chunk embeddings
   - Cosine similarity search

2. **Key-Value Store** (JSON files)
   - Text chunks
   - Full entity details
   - Full relationship details
   - LLM response cache

3. **Graph Storage**
   - Entity nodes
   - Relationship edges
   - Multi-hop traversal support

## Function Architecture

### LLM Function

```python
def _ollama_llm_internal(prompt, system_prompt=None, **kwargs):
    """Synchronous LLM function"""
    # HTTP POST to Ollama /api/chat
    # Returns: Generated text
```

**Current Issue**: LightRAG's async wrapper expects awaitable return, but sync function returns string directly.

### Embedding Function

```python
def _base_ollama_embedding(texts, **kwargs):
    """Synchronous embedding function"""
    # HTTP POST to Ollama /api/embeddings (per text)
    # Returns: List[List[float]] (embeddings)
```

**Wrapped in**: `EmbeddingFunc` dataclass (required by LightRAG)

## API Endpoints

### POST /ingest
- **Input**: `{"text": "...", "doc_id": "..."}`
- **Process**: Document ingestion into knowledge graph
- **Output**: `{"message": "Document ingested successfully", "doc_id": "...", "text_length": N}`
- **Async**: Uses `asyncio.to_thread()` for non-blocking

### POST /query
- **Input**: `{"query": "...", "mode": "hybrid"}`
- **Process**: Graph-based query processing
- **Output**: `{"answer": "...", "query": "...", "mode": "..."}`
- **Status**: Currently returns null due to async function compatibility issue

### GET /health
- **Output**: System health status
- **Checks**: API, Ollama connectivity, LightRAG initialization

### GET /
- **Output**: Web interface (index.html)

## Docker Services

### ollama Service
```yaml
image: ollama/ollama:latest
gpu: enabled (nvidia driver)
volumes:
  - ./ollama_data:/root/.ollama
ports:
  - "11434:11434"
```

### lightrag_api Service
```yaml
build: ./lightrag_api
depends_on: [ollama]
environment:
  OLLAMA_BASE_URL: http://ollama:11434
volumes:
  - ./rag_data:/data/rag_storage
ports:
  - "8000:8000"
```

## Known Issues & Limitations

### 1. Async Function Compatibility
**Issue**: LightRAG's `priority_limit_async_func_call` wrapper expects functions that return awaitables, but our sync functions return values directly.

**Error**: `"An asyncio.Future, a coroutine or an awaitable is required"`

**Impact**: Query endpoint returns null answers

**Potential Solutions**:
- Use LightRAG's built-in Ollama support (if available)
- Convert to proper async functions
- Use different LightRAG version
- Modify wrapper configuration

### 2. Model Size
**Issue**: Llama 3.3 70B is 40GB+, requires significant download time and storage.

**Mitigation**: Models stored in `ollama_data/` volume, persist across restarts.

### 3. GPU Memory Requirements
**Issue**: Requires 80GB+ VRAM for optimal performance.

**Mitigation**: Use smaller models or CPU fallback (slower).

## Performance Characteristics

- **Document Ingestion**: ~10-30 seconds per document (depends on size)
- **Query Processing**: ~5-15 seconds (depends on graph complexity)
- **GPU Utilization**: High during LLM inference
- **Memory**: ~60-80GB GPU memory for Llama 3.3 70B

## Security Considerations

1. **No Authentication**: API is currently open (add auth for production)
2. **Network Exposure**: Ports 8000 and 11434 exposed (use firewall)
3. **Data Privacy**: All processing happens locally (no external API calls)

## Scalability

### Horizontal Scaling
- Multiple Ollama instances (load balancing)
- Multiple LightRAG API instances (stateless)
- Shared storage backend

### Vertical Scaling
- Larger GPU (more VRAM)
- More CPU/RAM for preprocessing
- Faster storage (SSD for models)

## Future Enhancements

1. **Fix async function compatibility**
2. **Add authentication/authorization**
3. **Implement query caching**
4. **Batch processing support**
5. **Multi-tenant support**
6. **Advanced query modes**
7. **Export/import knowledge graphs**
8. **Monitoring and metrics**
