# GAFTA Guardian - Complete Setup Guide

## Overview
Production-ready LightRAG system with FastAPI wrapper, using Ollama with GPU-accelerated Llama 3.3 70B for legal document analysis.

## Architecture

```
┌─────────────────┐
│   FastAPI       │  Port 8000
│   LightRAG API  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│     Ollama      │  Port 11434
│  (Llama 3.3 70B)│  GPU-accelerated
│   (bge-m3)      │
└─────────────────┘
```

## Prerequisites

- **Server**: Ubuntu 22.04+ with NVIDIA GPU (H100 tested)
- **NVIDIA Driver**: Version 575+ (matching kernel module)
- **Docker**: 20.10+
- **Docker Compose**: v2.0+
- **NVIDIA Container Toolkit**: Installed and configured
- **GPU**: At least 80GB VRAM for Llama 3.3 70B

## Step 1: Server Setup

### 1.1 Install NVIDIA Driver

```bash
# Check current driver version
nvidia-smi

# If mismatch, run fix script
sudo bash fix_nvidia_driver.sh

# Reboot after driver installation
sudo reboot
```

### 1.2 Install Docker and NVIDIA Container Toolkit

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install NVIDIA Container Toolkit
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list

sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit
sudo systemctl restart docker

# Verify GPU access
docker run --rm --gpus all nvidia/cuda:11.0.3-base-ubuntu20.04 nvidia-smi
```

## Step 2: Clone and Setup Repository

```bash
# Clone repository
git clone <your-repo-url> gafta-guardian
cd gafta-guardian

# Create data directories
mkdir -p ollama_data rag_data
```

## Step 3: Pull Ollama Models

**Important**: Models are NOT stored in the repository. They must be pulled from Ollama.

```bash
# Start Ollama temporarily
docker run -d --gpus all \
  -v $(pwd)/ollama_data:/root/.ollama \
  -p 11434:11434 \
  --name temp_ollama \
  ollama/ollama:latest

# Wait for Ollama to start
sleep 10

# Pull LLM model (40GB+ - this will take time)
docker exec temp_ollama ollama pull llama3.3:70b

# Pull embedding model
docker exec temp_ollama ollama pull bge-m3

# Stop temporary container
docker stop temp_ollama && docker rm temp_ollama
```

**Alternative**: Use the setup script:
```bash
bash setup_models.sh
```

## Step 4: Start Services

```bash
# Build and start all services
docker compose up -d --build

# Check status
docker compose ps

# View logs
docker compose logs -f lightrag_api
```

## Step 5: Verify Installation

```bash
# Check health
curl http://localhost:8000/health

# Expected response:
# {
#   "api": "healthy",
#   "ollama": "healthy",
#   "lightrag_initialized": true,
#   "working_dir": "/data/rag_storage",
#   "ollama_url": "http://ollama:11434"
# }
```

## Step 6: Ingest Documents

### Option A: Using the web interface
1. Open `http://YOUR_SERVER_IP:8000` in browser
2. Upload or paste document text
3. Click "Ingest Document"

### Option B: Using API

```bash
# Single document
curl -X POST http://localhost:8000/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Your document text here",
    "doc_id": "document_001"
  }'
```

### Option C: Bulk ingestion

```bash
# Convert PDFs to text (if needed)
python3 convert_all_pdfs.py

# Ingest all text files
python3 ingest_all_files.py
```

## Step 7: Query the Knowledge Graph

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Is Company X in the defaulters list?",
    "mode": "hybrid"
  }'
```

## Configuration

### Environment Variables

Edit `docker-compose.yml` to customize:

- `OLLAMA_BASE_URL`: Ollama service URL (default: `http://ollama:11434`)
- `LLM_MODEL`: LLM model name (default: `llama3.3:70b`)
- `EMBEDDING_MODEL`: Embedding model name (default: `bge-m3`)

### Ports

- **8000**: FastAPI/LightRAG API
- **11434**: Ollama API

### Volumes

- `./ollama_data:/root/.ollama`: Ollama model storage
- `./rag_data:/data/rag_storage`: LightRAG knowledge graph persistence

## Troubleshooting

### GPU Not Accessible

```bash
# Check NVIDIA driver
nvidia-smi

# Check Docker GPU support
docker run --rm --gpus all nvidia/cuda:11.0.3-base-ubuntu20.04 nvidia-smi

# If issues, see fix_nvidia_driver.sh
```

### LightRAG Initialization Errors

- Ensure Ollama is healthy: `curl http://localhost:11434/api/tags`
- Check logs: `docker compose logs lightrag_api`
- Verify models are pulled: `docker exec gafta-guardian-ollama ollama list`

### Query Returns Null

- Check if documents were ingested successfully
- Verify Ollama is responding: `curl http://localhost:11434/api/chat`
- Review logs for async function errors

## Remote Access

To access from remote PC:

1. Update firewall rules:
```bash
sudo ufw allow 8000/tcp
sudo ufw allow 11434/tcp
```

2. Update `lightrag_api/static/index.html` with your server IP:
```javascript
const API_URL = 'http://YOUR_SERVER_IP:8000';
```

3. Access at: `http://YOUR_SERVER_IP:8000`

## Cost Optimization

- **Stop services when not in use**: `docker compose down`
- **Models persist in `ollama_data/`** - no need to re-download
- **Knowledge graph persists in `rag_data/`** - no need to re-ingest

## Backup Strategy

### What to Backup

1. **Code**: Already in Git repository
2. **Models**: `ollama_data/` directory (40GB+)
3. **Knowledge Graph**: `rag_data/` directory
4. **Configuration**: `docker-compose.yml`, environment files

### Backup Commands

```bash
# Backup models (large!)
tar -czf ollama_data_backup.tar.gz ollama_data/

# Backup knowledge graph
tar -czf rag_data_backup.tar.gz rag_data/

# Backup configuration
tar -czf config_backup.tar.gz docker-compose.yml *.sh *.py
```

## Restoration

1. Clone repository
2. Restore `ollama_data/` and `rag_data/` from backups
3. Run `docker compose up -d --build`
4. Verify with health check

## Known Issues

1. **Async Function Compatibility**: LightRAG's async wrapper has compatibility issues with custom functions. Query endpoint may return null until resolved.

2. **Model Download Time**: Llama 3.3 70B is 40GB+ and takes significant time to download.

3. **GPU Memory**: Requires 80GB+ VRAM for optimal performance.

## Next Steps for Development

1. Fix async function compatibility issue
2. Add query result caching
3. Implement batch query processing
4. Add authentication/authorization
5. Optimize embedding function calls

## Support

- LightRAG Documentation: https://github.com/HKUDS/LightRAG
- Ollama Documentation: https://ollama.ai/docs
- Issues: Check GitHub issues for known problems
