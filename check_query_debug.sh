#!/bin/bash
# Debug script to check query status on server

echo "=== Query Debugging Script ==="
echo ""
cd /root/lightrag_do

echo "1. Checking recent query activity (last 50 lines):"
docker-compose logs lightrag_api --tail 50 | grep -E "POST.*query|query|Query|answer|response|error|Error|LLM|Processing" || echo "No recent query activity"

echo ""
echo "2. Checking for any errors:"
docker-compose logs lightrag_api --tail 100 | grep -i "error\|exception\|failed\|timeout\|stuck" | tail -20

echo ""
echo "3. Current container status:"
docker-compose ps

echo ""
echo "4. Checking active connections:"
docker exec gafta-guardian-lightrag_api netstat -tunap 2>/dev/null | grep :8000 || echo "Cannot check connections"

echo ""
echo "5. Testing API health:"
curl -s http://localhost:8000/health | python3 -m json.tool 2>/dev/null || curl -s http://localhost:8000/health

echo ""
echo "6. Last 20 lines of logs:"
docker-compose logs lightrag_api --tail 20

echo ""
echo "=== If query is stuck, you can try: ==="
echo "- Restart the API container: docker-compose restart lightrag_api"
echo "- Check GPU usage: nvidia-smi"
echo "- Check if Ollama is responding: curl http://localhost:11434/api/tags"
