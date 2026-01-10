# Quick Restore Guide - LightRAG Docker Deployment

## Prerequisites
- Docker and Docker Compose installed
- Git repository cloned
- GPU-enabled server (optional, for faster Ollama)

## Fast Restoration Steps

### 1. Clone Repository
```bash
git clone https://github.com/arnikanord/lightrag_do.git gafta-guardian
cd gafta-guardian
```

### 2. Set Up Directory Structure
```bash
mkdir -p ollama_data rag_data
```

### 3. Pull Ollama Models (if not in backup)
```bash
# Start temporary Ollama container
docker run -d --gpus all -v $(pwd)/ollama_data:/root/.ollama -p 11434:11434 --name temp_ollama ollama/ollama:latest

# Wait for Ollama to start
sleep 5

# Pull required models
docker exec temp_ollama ollama pull llama3.3:70b
docker exec temp_ollama ollama pull bge-m3

# Stop and remove temp container
docker stop temp_ollama && docker rm temp_ollama
```

### 4. Start Services
```bash
docker compose up -d
```

### 5. Verify Installation
```bash
# Check service status
docker compose ps

# Check logs
docker compose logs -f lightrag_api

# Verify health
curl http://localhost:8000/health
```

### 6. Test Query Endpoint
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "test", "mode": "hybrid"}'
```

## Important Notes

### Async Fixes Applied
The code includes all async error fixes:
- ✅ nest_asyncio for event loop compatibility
- ✅ Standard asyncio loop (not uvloop)
- ✅ Numpy array embeddings
- ✅ Proper async function signatures

### Configuration Files
- `docker-compose.yml` - Service definitions
- `lightrag_api/Dockerfile` - Uses `--loop asyncio` (critical!)
- `lightrag_api/requirements.txt` - Includes nest_asyncio and numpy
- `lightrag_api/main.py` - Has all async fixes applied

### Environment Variables
- `OLLAMA_BASE_URL` - Default: `http://ollama:11434`
- Models: `llama3.3:70b` (LLM), `bge-m3` (Embedding)

### Ports
- 8000 - FastAPI/Web interface
- 11434 - Ollama API

## Restore from Backup

If you have backup files:

1. **Restore models**:
   ```bash
   tar -xzf ollama_data_backup.tar.gz
   ```

2. **Restore RAG data**:
   ```bash
   tar -xzf rag_data_backup.tar.gz
   ```

3. **Start services**:
   ```bash
   docker compose up -d
   ```

## Troubleshooting

### Container won't start
- Check logs: `docker compose logs lightrag_api`
- Verify requirements: `docker compose build lightrag_api`

### Query returns errors
- Verify nest_asyncio is applied (check logs)
- Check Ollama connectivity: `curl http://localhost:11434/api/tags`
- Verify models are pulled: `docker exec gafta-guardian-ollama ollama list`

### Embedding errors
- Verify numpy is installed
- Check embedding function returns numpy arrays
- Verify embedding model is available

## Documentation
- Full async fix details: See `ASYNC_FIX_COMPLETE.md`
- Architecture: See `ARCHITECTURE.md`
- Setup guide: See `SETUP_GUIDE.md`

## Important Fixes Applied

### UI Health Check Fix
The UI has been updated to correctly show health status. The health check now works even when LightRAG hasn't been initialized yet (it initializes lazily on first request).

### Docker GPU Configuration
For docker-compose 1.29.2, ensure `/etc/docker/daemon.json` contains:
```json
{
  "runtimes": {
    "nvidia": {
      "path": "nvidia-container-runtime",
      "runtimeArgs": []
    }
  }
}
```

Then restart Docker:
```bash
systemctl restart docker
```

### HTML Static Files
The `lightrag_api/static/index.html` uses `window.location.origin` to automatically detect the server URL. No hardcoded IPs needed.

## Troubleshooting UI Shows Unhealthy

If UI shows unhealthy:

1. Check health endpoint:
   ```bash
   curl http://YOUR_SERVER_IP:8000/health
   ```

2. Verify both `api` and `ollama` show "healthy"

3. `lightrag_initialized: false` is normal - it initializes on first document ingest or query

4. Check container logs:
   ```bash
   docker-compose logs lightrag_api
   ```

5. Rebuild if needed:
   ```bash
   docker-compose down
   docker-compose build --no-cache lightrag_api
   docker-compose up -d
   ```
