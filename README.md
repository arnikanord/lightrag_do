# GAFTA Guardian (LightRAG with Remote GPU)

LightRAG system for GAFTA legal document analysis, configured to use a remote Centron GPU for LLM and Embedding inference.

## 🚀 Quick Start

### 1. Requirements
- Docker & Docker Compose
- Access to the Remote Centron GPU (ensure IP is reachable)

### 2. Configuration
Copy the example environment file and configure it:

```bash
cp .env.example .env
```

Edit `.env` to set your API key and Remote GPU IP (already configured for demo):
```ini
LLM_BINDING=openai
LLM_BINDING_HOST=http://188.64.60.19:11434/v1
LLM_MODEL=mistral-small:24b

EMBEDDING_BINDING=openai
EMBEDDING_BINDING_HOST=http://188.64.60.19:11434/v1
EMBEDDING_MODEL=nomic-embed-text:latest
```

### 3. Start Service
```bash
docker-compose up -d --build
```
The service will be available at `http://localhost:9621`.

## 📁 Usage

### Web Interface
Visit `http://localhost:9621` to:
- check system health
- ingest documents (text/PDF)
- query the knowledge graph
- visualize the graph structure

### API Endpoints
- **Health Check**: `GET /health`
- **Ingest**: `POST /ingest`
- **Query**: `POST /query`
- **Graph**: `GET /graph`

## 🛠 Project Structure
- `lightrag_api/` - FastAPI application code
- `rag_data/` - Persistent storage for LightRAG (GraphML, JSON, Vector DB)
- `docker-compose.yml` - Container configuration

## 🔍 Visualisation
The system uses `networkx` to generate graph visualizations from the underlying GraphML storage.
