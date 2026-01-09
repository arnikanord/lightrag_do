# Deployment Checklist

## Pre-Deployment

- [ ] Server with Ubuntu 22.04+
- [ ] NVIDIA GPU with 80GB+ VRAM
- [ ] NVIDIA Driver 575+ installed
- [ ] Docker and Docker Compose installed
- [ ] NVIDIA Container Toolkit installed
- [ ] Git repository cloned

## Deployment Steps

1. **Server Setup**
   ```bash
   sudo bash fix_nvidia_driver.sh  # If needed
   sudo reboot
   ```

2. **Clone Repository**
   ```bash
   git clone <repo-url> gafta-guardian
   cd gafta-guardian
   ```

3. **Create Directories**
   ```bash
   mkdir -p ollama_data rag_data
   ```

4. **Pull Models** (40GB+ download)
   ```bash
   bash setup_models.sh
   # OR manually:
   docker run -d --gpus all -v $(pwd)/ollama_data:/root/.ollama -p 11434:11434 --name temp_ollama ollama/ollama
   docker exec temp_ollama ollama pull llama3.3:70b
   docker exec temp_ollama ollama pull bge-m3
   docker stop temp_ollama && docker rm temp_ollama
   ```

5. **Start Services**
   ```bash
   docker compose up -d --build
   ```

6. **Verify**
   ```bash
   curl http://localhost:8000/health
   ```

7. **Configure Remote Access** (if needed)
   ```bash
   sudo ufw allow 8000/tcp
   # Update static/index.html with server IP
   ```

## Post-Deployment

- [ ] Health check passes
- [ ] Test document ingestion
- [ ] Test query endpoint
- [ ] Verify GPU usage: `nvidia-smi`
- [ ] Check logs: `docker compose logs -f`

## Backup Before Destroying

```bash
# Backup models (40GB+)
tar -czf ollama_data_backup.tar.gz ollama_data/

# Backup knowledge graph
tar -czf rag_data_backup.tar.gz rag_data/

# Backup code (already in Git)
git add .
git commit -m "Save implementation"
git push
```

## Restoration

1. Clone repository
2. Extract backups:
   ```bash
   tar -xzf ollama_data_backup.tar.gz
   tar -xzf rag_data_backup.tar.gz
   ```
3. Start services: `docker compose up -d`
4. Verify: `curl http://localhost:8000/health`
