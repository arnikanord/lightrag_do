# Troubleshooting Guide

## Common Issues and Solutions

### 1. UI Shows as Unhealthy

**Symptoms:** Browser UI shows red "⚠ System Unhealthy" status

**Causes & Solutions:**

#### a) Health Check Endpoint Issue
```bash
# Test health endpoint
curl http://YOUR_SERVER_IP:8000/health

# Expected response:
# {"api":"healthy","ollama":"healthy","lightrag_initialized":false,...}
```

**Solution:** Ensure both `api` and `ollama` show "healthy". `lightrag_initialized: false` is normal - LightRAG initializes on first use.

#### b) API_URL Configuration Issue
Check that `lightrag_api/static/index.html` uses:
```javascript
const API_URL = window.location.origin;
```

**Fix:** Rebuild container if needed:
```bash
docker-compose down
docker-compose build --no-cache lightrag_api
docker-compose up -d
```

#### c) CORS or Network Issues
Check browser console for errors. Verify services are accessible:
```bash
# From server
curl http://localhost:8000/health

# From external machine  
curl http://YOUR_SERVER_IP:8000/health
```

### 2. GPU Not Working / Ollama Slow

**Symptoms:** Ollama runs slowly, GPU not detected in container

**Solution:**
```bash
# 1. Verify NVIDIA driver
nvidia-smi

# 2. Verify nvidia-container-runtime installed
which nvidia-container-runtime

# 3. Check Docker daemon.json
cat /etc/docker/daemon.json
# Should contain nvidia runtime configuration

# 4. Restart Docker
systemctl restart docker

# 5. Test GPU in container
docker run --rm --runtime=nvidia nvidia/cuda:12.0.0-base-ubuntu22.04 nvidia-smi

# 6. Verify Ollama detects GPU
docker exec gafta-guardian-ollama nvidia-smi
docker-compose logs ollama | grep -i gpu
```

### 3. Docker Compose GPU Runtime Error

**Error:** `unknown or invalid runtime name: nvidia`

**Solution:**
1. Install nvidia-container-toolkit:
   ```bash
   # Usually pre-installed on GPU droplets, but verify:
   dpkg -l | grep nvidia-container-toolkit
   ```

2. Configure Docker daemon:
   ```bash
   cat > /etc/docker/daemon.json << 'JSON'
   {
     "runtimes": {
       "nvidia": {
         "path": "nvidia-container-runtime",
         "runtimeArgs": []
       }
     }
   }
   JSON
   
   systemctl restart docker
   ```

3. Verify runtime available:
   ```bash
   docker info | grep -i runtime
   # Should show: nvidia
   ```

### 4. Models Not Found / Ollama Models Missing

**Symptoms:** API returns errors about missing models

**Solution:**
```bash
# Check models in Ollama
docker exec gafta-guardian-ollama ollama list

# Should show:
# llama3.3:70b
# bge-m3:latest

# If missing, re-run setup:
cd /root/lightrag_do
bash setup_models.sh
```

### 5. Port Already in Use

**Error:** `port is already allocated` or `bind: address already in use`

**Solution:**
```bash
# Check what's using the ports
ss -tlnp | grep -E ':(8000|11434)'

# Stop existing containers
docker-compose down

# If still in use, stop manually
docker stop $(docker ps -q --filter "publish=8000")
docker stop $(docker ps -q --filter "publish=11434")
```

### 6. LightRAG Initialization Errors

**Symptoms:** Query/ingest endpoints return initialization errors

**Solution:**
```bash
# Check logs
docker-compose logs lightrag_api | grep -i error

# Verify Ollama is accessible from container
docker exec gafta-guardian-lightrag_api curl http://ollama:11434/api/tags

# Test initialization with a simple ingest
curl -X POST http://YOUR_SERVER_IP:8000/ingest \
  -H "Content-Type: application/json" \
  -d '{"text": "Test document", "doc_id": "test_001"}'
```

### 7. Health Check Fails After Rebuild

**Symptoms:** Container health check fails, shows as unhealthy in `docker ps`

**Solution:**
```bash
# Check container logs
docker-compose logs lightrag_api

# Verify health check command works
docker exec gafta-guardian-lightrag_api python -c "import requests; requests.get('http://localhost:8000/health')"

# If fails, check if requests module is installed
docker exec gafta-guardian-lightrag_api pip list | grep requests
```

### 8. Static Files Not Updating

**Symptoms:** HTML changes not reflected after rebuild

**Solution:**
```bash
# Force rebuild without cache
docker-compose build --no-cache lightrag_api

# Or rebuild specific step
docker-compose build --no-cache --progress=plain lightrag_api 2>&1 | grep -A 5 "COPY static"

# Verify files in container
docker exec gafta-guardian-lightrag_api cat /app/static/index.html | grep API_URL
```

## Verification Checklist

After setup, verify everything works:

- [ ] `nvidia-smi` shows GPU
- [ ] `docker info | grep runtime` shows `nvidia`
- [ ] `docker exec gafta-guardian-ollama nvidia-smi` works
- [ ] `curl http://YOUR_SERVER_IP:8000/health` returns healthy status
- [ ] `curl http://YOUR_SERVER_IP:11434/api/tags` returns models list
- [ ] Browser UI at `http://YOUR_SERVER_IP:8000` shows "System Healthy"
- [ ] Models listed: `docker exec gafta-guardian-ollama ollama list`
- [ ] Can ingest: `curl -X POST http://YOUR_SERVER_IP:8000/ingest ...`
- [ ] Can query: `curl -X POST http://YOUR_SERVER_IP:8000/query ...`

## Getting Help

If issues persist:
1. Check all logs: `docker-compose logs`
2. Check system resources: `df -h`, `free -h`, `nvidia-smi`
3. Verify network connectivity: `ping`, `curl`
4. Review configuration files: `docker-compose.yml`, `/etc/docker/daemon.json`
