# UI Health Check Fixes

## Issue
The UI was showing as "unhealthy" even though the API was working correctly.

## Root Causes

### 1. Hardcoded IP Address in HTML
The `lightrag_api/static/index.html` file had a hardcoded IP address (`162.243.201.21`) that didn't match the actual server IP.

**Fix:** Changed to use `window.location.origin` which automatically uses the current server.

### 2. Strict Health Check Condition
The UI health check required both `ollama === 'healthy'` AND `lightrag_initialized === true`. However, LightRAG initializes lazily on first request, so `lightrag_initialized` is `false` until a document is ingested or a query is made.

**Fix:** Updated condition to:
```javascript
if (data.ollama === 'healthy' && (data.lightrag_initialized || data.api === 'healthy'))
```

This allows the UI to show healthy when:
- Ollama is healthy AND
- Either LightRAG is initialized OR the API itself is healthy

### 3. Docker Compose GPU Configuration
Original docker-compose.yml used `deploy.resources.reservations.devices` which isn't compatible with docker-compose 1.29.2.

**Fix:** Changed to use `runtime: nvidia` with environment variables:
```yaml
runtime: nvidia
environment:
  - NVIDIA_VISIBLE_DEVICES=all
  - NVIDIA_DRIVER_CAPABILITIES=compute,utility
```

## Files Modified

1. `lightrag_api/static/index.html` - Fixed API_URL and health check condition
2. `docker-compose.yml` - Fixed GPU configuration for docker-compose 1.29.2
3. `/etc/docker/daemon.json` - Added nvidia runtime configuration

## Verification

After fixes, verify with:
```bash
curl http://YOUR_SERVER_IP:8000/health
```

Should return:
```json
{
    "api": "healthy",
    "ollama": "healthy",
    "lightrag_initialized": false,  // This is OK - initializes on first use
    "working_dir": "/data/rag_storage",
    "ollama_url": "http://ollama:11434",
    "nest_asyncio": "enabled"
}
```

The UI should now show "✓ System Healthy" when accessing http://YOUR_SERVER_IP:8000
