# Query Stuck - Immediate Diagnostic Steps

## Problem
The UI query appears to be stuck/running indefinitely. This can happen if:
1. The query is still processing (normal, can take 1-3 minutes)
2. The query timed out but UI didn't handle it (FIXED in UI)
3. The server is stuck processing

## Immediate Checks (Run on Server)

### 1. Check if query is still processing
```bash
cd /root/lightrag_do
docker-compose logs lightrag_api --tail 50 | grep -E "POST.*query|query|Query|answer|response|LLM"
```

### 2. Check for errors
```bash
docker-compose logs lightrag_api --tail 100 | grep -i "error\|exception\|failed\|timeout" | tail -20
```

### 3. Test API directly
```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "test query", "mode": "hybrid"}' \
  --max-time 60
```

### 4. Check container status
```bash
docker-compose ps
docker stats --no-stream
```

### 5. Check GPU usage (should be active if processing)
```bash
nvidia-smi
```

## Fix Applied

I've fixed the UI to:
1. **Add 3-minute timeout** (180 seconds) - prevents infinite hanging
2. **Better error handling** - shows specific timeout messages
3. **Progress indicator** - tells user it may take 1-3 minutes
4. **Better response formatting** - cleaner display of results

## To Apply the Fix

The container needs to be rebuilt to apply the UI fix:

```bash
cd /root/lightrag_do
docker-compose build lightrag_api
docker-compose up -d lightrag_api
```

## If Query is Actually Stuck

If the query is stuck on the server (not just UI timeout):

1. **Check logs for stuck process:**
   ```bash
   docker-compose logs lightrag_api --tail 200 | grep -A 10 -B 10 "query"
   ```

2. **Restart the API container:**
   ```bash
   docker-compose restart lightrag_api
   ```

3. **If still stuck, check Ollama:**
   ```bash
   curl http://localhost:11434/api/tags
   docker-compose restart ollama
   ```

## Expected Query Times

- Simple queries: **30-60 seconds**
- Complex queries (3 documents): **40-90 seconds**
- Very complex queries: **1-3 minutes** (now with proper timeout)

If a query takes longer than 3 minutes, it may be stuck and should be restarted.
