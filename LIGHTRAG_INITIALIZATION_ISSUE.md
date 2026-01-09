# LightRAG Initialization Issue

## Current Status

LightRAG is configured to use local Ollama with GPU-accelerated Llama 3.3 70B, but there's a compatibility issue with LightRAG version 1.4.9.10.

## Error

```
Failed to initialize LightRAG: replace() should be called on dataclass instances
```

This error occurs in LightRAG's `__post_init__` method when trying to process the custom LLM and embedding functions.

## Current Configuration

- **Ollama**: Running with GPU support at `http://ollama:11434`
- **LLM Model**: `llama3.3:70b` (GPU-accelerated)
- **Embedding Model**: `bge-m3`
- **LightRAG Version**: 1.4.9.10

## Solution Options

### Option 1: Downgrade LightRAG (Recommended)
Try an older version that might have better Ollama support:

```bash
docker exec gafta-guardian-lightrag_api pip install lightrag-hku==1.3.0
docker compose restart lightrag_api
```

### Option 2: Upgrade LightRAG
Try the latest version:

```bash
docker exec gafta-guardian-lightrag_api pip install --upgrade lightrag-hku
docker compose restart lightrag_api
```

### Option 3: Use LightRAG's Built-in Ollama Support
Check if LightRAG 1.4.9.10 has built-in Ollama support that doesn't require custom functions.

### Option 4: Wait for Fix
This appears to be a bug in LightRAG 1.4.9.10's handling of custom functions. The issue is in the dataclass replacement logic.

## Verification

Ollama is working correctly:
- ✅ Ollama service running
- ✅ GPU accessible
- ✅ Models can be pulled
- ✅ API endpoints responding

The issue is specifically with LightRAG's initialization when using custom LLM/embedding functions.

## Next Steps

1. Try downgrading/upgrading LightRAG
2. Check LightRAG GitHub for known issues
3. Consider using a different RAG library if the issue persists
