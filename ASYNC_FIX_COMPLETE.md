# LightRAG Async Error Fix - Complete Documentation

## Problem Solved
Fixed the critical async error: `"An asyncio.Future, a coroutine or an awaitable is required"` that was preventing query processing from working in LightRAG Docker deployment.

## Root Cause
1. **Event loop conflict**: FastAPI's async context vs LightRAG's wrapper
2. **Embedding format issue**: LightRAG expected 2D numpy arrays, not list of arrays
3. **uvloop incompatibility**: nest_asyncio cannot patch uvloop, requiring standard asyncio

## Solutions Implemented

### ✅ Fix 1: nest_asyncio (PRIMARY FIX)
**File**: `lightrag_api/main.py`
- Applied `nest_asyncio.apply()` at the very top before any imports
- This fixes event loop conflicts between FastAPI and LightRAG's async wrapper
- Location: Lines 8-9 in main.py

```python
import nest_asyncio
nest_asyncio.apply()
```

### ✅ Fix 2: Standard Asyncio Loop
**File**: `lightrag_api/Dockerfile`
- Changed uvicorn command to use `--loop asyncio` instead of default uvloop
- nest_asyncio cannot patch uvloop, so standard asyncio is required
- Location: CMD line in Dockerfile

```dockerfile
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--loop", "asyncio"]
```

### ✅ Fix 3: Embedding Function Format
**File**: `lightrag_api/main.py`
- Fixed embedding function to return 2D numpy array instead of list of arrays
- LightRAG's internal code expects `.size` attribute which numpy arrays have
- Location: `_ollama_embedding_func_custom()` function

```python
# Return as 2D numpy array (LightRAG expects this format)
if embeddings:
    return np.array(embeddings, dtype=np.float32)
else:
    return np.array([], dtype=np.float32).reshape(0, 1024)
```

### ✅ Fix 4: Updated Dependencies
**File**: `lightrag_api/requirements.txt`
- Added `nest_asyncio>=1.6.0`
- Added `numpy>=1.24.0`
- Updated `lightrag-hku>=1.4.9.10` (for built-in function support)

## Files Modified

1. **lightrag_api/main.py** - Major refactoring:
   - Added nest_asyncio at top
   - Fixed async LLM function with proper **kwargs handling
   - Fixed embedding function to return numpy arrays
   - Improved error handling
   - Added numpy import

2. **lightrag_api/Dockerfile** - Minor change:
   - Added `--loop asyncio` flag to uvicorn command

3. **lightrag_api/requirements.txt** - Dependencies added:
   - nest_asyncio>=1.6.0
   - numpy>=1.24.0
   - lightrag-hku>=1.4.9.10

## Verification

### Before Fix
- ✅ Ingestion worked
- ✅ Knowledge graph creation worked
- ❌ Query failed with: `"An asyncio.Future, a coroutine or an awaitable is required"`
- ❌ Query failed with: `"'list' object has no attribute 'size'"`

### After Fix
- ✅ Ingestion works
- ✅ Knowledge graph creation works
- ✅ **Query processing works!** (Fixed)
- ✅ All async operations function correctly

## Deployment Steps (After Pulling Code)

1. **Rebuild Docker container**:
   ```bash
   cd /path/to/gafta-guardian
   docker compose build lightrag_api
   docker compose restart lightrag_api
   ```

2. **Verify installation**:
   ```bash
   docker compose logs lightrag_api | grep -E "(nest_asyncio|numpy|initialized)"
   ```

3. **Test health endpoint**:
   ```bash
   curl http://localhost:8000/health
   ```
   Should show `"nest_asyncio": "enabled"`

4. **Test query endpoint**:
   ```bash
   curl -X POST http://localhost:8000/query \
     -H "Content-Type: application/json" \
     -d '{"query": "test query", "mode": "hybrid"}'
   ```
   Should return JSON response (may have null answer if no documents ingested)

## Key Technical Details

### Why nest_asyncio?
LightRAG's `priority_limit_async_func_call` wrapper manages its own async context, which conflicts with FastAPI's event loop. `nest_asyncio` allows nested event loops, resolving this conflict.

### Why Standard Asyncio Loop?
Uvicorn by default uses `uvloop` which is faster but incompatible with `nest_asyncio`. Using `--loop asyncio` forces standard asyncio which nest_asyncio can patch.

### Why Numpy Arrays?
LightRAG's internal code calls `.size` on embedding results. Python lists don't have `.size`, but numpy arrays do. The 2D array format `(n_embeddings, embedding_dim)` is what LightRAG expects.

### Function Signature Requirements
- LLM function must accept `**kwargs` to handle `hashing_kv` parameter
- Functions must be `async def` (not sync)
- Functions must return values (never None)
- Embedding function must return numpy arrays

## Troubleshooting

If issues persist after deployment:

1. **Check logs for nest_asyncio**:
   ```bash
   docker compose logs lightrag_api | grep nest_asyncio
   ```
   Should see: `✓ nest_asyncio applied (Solution 3)`

2. **Verify numpy is installed**:
   ```bash
   docker exec gafta-guardian-lightrag_api python3 -c "import numpy; print(numpy.__version__)"
   ```

3. **Check event loop**:
   ```bash
   docker compose logs lightrag_api | grep -E "(Creating.*event loop|nest_asyncio)"
   ```

4. **Verify embedding format**:
   The embedding function should return `numpy.ndarray` with shape `(n, 1024)` where n is number of texts.

## Backup Files
- Original main.py backed up as: `lightrag_api/main.py.backup`

## Date Fixed
January 9, 2025

## Status
✅ **RESOLVED** - Query processing now works correctly with all async operations functioning properly.
