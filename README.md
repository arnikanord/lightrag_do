# GAFTA Guardian

Production-ready LightRAG system for legal document analysis using GPU-accelerated Llama 3.3 70B.

## 🚀 Quick Start

```bash
# 1. Clone repository
git clone <repo-url> gafta-guardian
cd gafta-guardian

# 2. Setup NVIDIA driver (if needed)
sudo bash fix_nvidia_driver.sh
sudo reboot

# 3. Pull models (40GB+ - takes time!)
bash setup_models.sh

# 4. Start services
docker compose up -d --build

# 5. Verify
curl http://localhost:8000/health
```

## 📋 Requirements

- **Server**: Ubuntu 22.04+ with NVIDIA GPU
- **GPU**: 80GB+ VRAM (H100 tested)
- **NVIDIA Driver**: 575+
- **Docker**: 20.10+ with GPU support
- **Storage**: 50GB+ for models

## 📁 Project Structure

```
gafta-guardian/
├── lightrag_api/          # FastAPI application
│   ├── main.py           # API endpoints
│   ├── Dockerfile        # Container definition
│   ├── requirements.txt  # Python dependencies
│   └── static/           # Web interface
├── docker-compose.yml    # Service orchestration
├── setup_models.sh       # Model download script
├── fix_nvidia_driver.sh  # Driver fix script
├── *.py                  # Utility scripts
└── *.md                  # Documentation
```

## 🔧 Configuration

### Environment Variables

- `OLLAMA_BASE_URL`: Ollama service URL (default: `http://ollama:11434`)
- `LLM_MODEL`: LLM model name (default: `llama3.3:70b`)
- `EMBEDDING_MODEL`: Embedding model (default: `bge-m3`)

### Ports

- **8000**: FastAPI/LightRAG API
- **11434**: Ollama API

## 📖 Documentation

- **[SETUP_GUIDE.md](SETUP_GUIDE.md)**: Complete setup instructions
- **[ARCHITECTURE.md](ARCHITECTURE.md)**: System architecture details
- **[DEPLOYMENT.md](DEPLOYMENT.md)**: Deployment checklist

## 🎯 Usage

### Ingest Documents

```bash
curl -X POST http://localhost:8000/ingest \
  -H "Content-Type: application/json" \
  -d '{"text": "Document content...", "doc_id": "doc_001"}'
```

### Query Knowledge Graph

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Is Company X in defaulters?", "mode": "hybrid"}'
```

### Web Interface

Open `http://YOUR_SERVER_IP:8000` in browser

## ⚠️ Known Issues

1. **Query Returns Null**: Async function compatibility issue with LightRAG wrapper. Documents are ingested successfully, but queries may return null until resolved.

2. **Model Download**: Llama 3.3 70B is 40GB+ and takes significant time to download.

## 💾 Backup & Restore

### Backup

```bash
# Models (40GB+)
tar -czf ollama_data_backup.tar.gz ollama_data/

# Knowledge graph
tar -czf rag_data_backup.tar.gz rag_data/
```

### Restore

```bash
tar -xzf ollama_data_backup.tar.gz
tar -xzf rag_data_backup.tar.gz
docker compose up -d
```

## 🔒 Security Notes

- No authentication implemented (add for production)
- Exposed ports: 8000, 11434 (use firewall)
- All processing is local (no external API calls)

## 💰 Cost Optimization

- **Stop when not in use**: `docker compose down`
- **Models persist**: No need to re-download
- **Graph persists**: No need to re-ingest

## 🐛 Troubleshooting

### GPU Not Working
```bash
nvidia-smi
docker run --rm --gpus all nvidia/cuda:11.0.3-base-ubuntu20.04 nvidia-smi
```

### Services Not Starting
```bash
docker compose logs -f
docker compose ps
```

### Health Check Fails
```bash
curl http://localhost:11434/api/tags  # Check Ollama
curl http://localhost:8000/health     # Check API
```

## 📝 Development Status

- ✅ LightRAG initialization: **Fixed**
- ✅ Document ingestion: **Working**
- ⚠️ Query endpoint: **Returns null** (async function issue)
- ✅ GPU acceleration: **Working**
- ✅ Model persistence: **Working**
- ✅ Knowledge graph persistence: **Working**

## 🔮 Next Steps

1. Fix async function compatibility
2. Add authentication
3. Implement query caching
4. Add batch processing
5. Performance optimization

## 📄 License

[Your License Here]

## 🙏 Acknowledgments

- [LightRAG](https://github.com/HKUDS/LightRAG) - Graph-based RAG system
- [Ollama](https://ollama.ai/) - Local LLM server
- [FastAPI](https://fastapi.tiangolo.com/) - Web framework
