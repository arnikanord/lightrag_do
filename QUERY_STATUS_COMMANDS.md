# Query Status Monitoring Commands

Use these commands on the server to check query status and activity.

## Quick Status Check

```bash
# Check if there's an active query being processed
cd /root/lightrag_do
docker-compose logs lightrag_api --tail 30 | grep -E "POST.*query|query|Query|LLM|answer|response"
```

## Real-time Query Monitoring

```bash
# Watch query activity in real-time (Ctrl+C to stop)
cd /root/lightrag_do
docker-compose logs -f lightrag_api | grep --line-buffered -E "POST.*query|GET.*query|query|Query|answer|response|error|Error|LLM|Processing"
```

## Check Recent Activity

```bash
# Last 50 lines of logs
cd /root/lightrag_do
docker-compose logs lightrag_api --tail 50
```

## Check for Errors

```bash
# Check for any errors in query processing
cd /root/lightrag_do
docker-compose logs lightrag_api --tail 100 | grep -i "error\|exception\|failed\|timeout"
```

## Test Query via CLI

```bash
# Simple query test
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "What are the main topics?", "mode": "hybrid"}' \
  --max-time 120

# More complex query
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "What are the main topics covered in these documents?", "mode": "hybrid"}' \
  --max-time 300
```

## Check Container Status

```bash
# Check if containers are running properly
cd /root/lightrag_do
docker-compose ps

# Check resource usage
docker stats gafta-guardian-lightrag_api gafta-guardian-ollama --no-stream
```

## Query Modes Available

- `hybrid` - Hybrid retrieval mode (recommended)
- `naive` - Naive retrieval mode
- `local` - Local retrieval mode
- `global` - Global retrieval mode

## Expected Query Times

- Simple queries: **30-60 seconds**
- Complex queries (with 3 documents): **40-90 seconds**
- The query time depends on:
  - Query complexity
  - Number of documents in the knowledge graph
  - LLM processing time
  - Embedding retrieval time

## If Query Takes Too Long

If a query is taking more than 2-3 minutes:

1. Check logs for errors:
   ```bash
   docker-compose logs lightrag_api --tail 100 | tail -20
   ```

2. Check GPU utilization:
   ```bash
   nvidia-smi
   ```

3. Restart containers if needed:
   ```bash
   cd /root/lightrag_do
   docker-compose restart lightrag_api
   ```
