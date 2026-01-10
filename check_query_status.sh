#!/bin/bash
# Script to check query status and logs

echo "=== Checking Recent Query Activity ==="
echo ""
cd /root/lightrag_do

echo "1. Recent query-related logs (last 50 lines):"
docker-compose logs lightrag_api --tail 50 | grep -E "POST.*query|GET.*query|query|Query|LLM|Processing" || echo "No recent query activity found"

echo ""
echo "2. Current API container status:"
docker-compose ps lightrag_api

echo ""
echo "3. Real-time logs (Press Ctrl+C to stop):"
echo "   Watching for query activity..."
docker-compose logs -f lightrag_api | grep --line-buffered -E "POST.*query|GET.*query|query|Query|answer|response|error|Error" || true
