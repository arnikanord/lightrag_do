# LightRAG API Access Commands - Server IP: 162.243.112.87

## Health Check Commands

### Check LightRAG API Health
```bash
curl http://162.243.112.87:8000/health
```

### Check Ollama API
```bash
curl http://162.243.112.87:11434/api/tags
```

## Web Interface

### Open in Browser
- **LightRAG Web UI**: http://162.243.112.87:8000
- **Ollama API**: http://162.243.112.87:11434

## API Usage Examples

### 1. Ingest Documents
```bash
curl -X POST http://162.243.112.87:8000/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Your document content here...",
    "doc_id": "doc_001"
  }'
```

### 2. Query Knowledge Graph
```bash
curl -X POST http://162.243.112.87:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Your question here",
    "mode": "hybrid"
  }'
```

### 3. Test Query (Simple)
```bash
curl -X POST http://162.243.112.87:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "test", "mode": "hybrid"}'
```

### 4. Check Service Status
```bash
curl http://162.243.112.87:8000/health | python3 -m json.tool
```

### 5. List Ollama Models
```bash
curl http://162.243.112.87:11434/api/tags | python3 -m json.tool
```

## Quick Test from Local Machine

### Windows PowerShell
```powershell
# Health check
Invoke-RestMethod -Uri "http://162.243.112.87:8000/health"

# Query
Invoke-RestMethod -Uri "http://162.243.112.87:8000/query" `
  -Method Post `
  -ContentType "application/json" `
  -Body '{"query":"test","mode":"hybrid"}'
```

### Linux/Mac Terminal
```bash
# Health check
curl http://162.243.112.87:8000/health

# Query
curl -X POST http://162.243.112.87:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query":"test","mode":"hybrid"}'
```

## Server Management Commands (SSH into server)

### Check Service Status
```bash
ssh root@162.243.112.87 "cd /root/lightrag_do && docker-compose ps"
```

### View Logs
```bash
ssh root@162.243.112.87 "cd /root/lightrag_do && docker-compose logs -f lightrag_api"
```

### Restart Services
```bash
ssh root@162.243.112.87 "cd /root/lightrag_do && docker-compose restart"
```

### Stop Services
```bash
ssh root@162.243.112.87 "cd /root/lightrag_do && docker-compose down"
```

### Start Services
```bash
ssh root@162.243.112.87 "cd /root/lightrag_do && docker-compose up -d"
```

### Check GPU Status
```bash
ssh root@162.243.112.87 "nvidia-smi"
```
