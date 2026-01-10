#!/bin/bash
# Fix script to rebuild lightrag_api container
# This resolves the ContainerConfig KeyError issue

cd /root/lightrag_do

echo "=== Fixing container rebuild issue ==="
echo ""

echo "1. Stopping lightrag_api container..."
docker-compose stop lightrag_api

echo ""
echo "2. Removing lightrag_api container..."
docker-compose rm -f lightrag_api

echo ""
echo "3. Removing old image (if exists)..."
docker rmi lightrag_do-lightrag_api:latest 2>/dev/null || echo "   No old image to remove"

echo ""
echo "4. Building new lightrag_api container..."
docker-compose build --no-cache lightrag_api

echo ""
echo "5. Starting services..."
docker-compose up -d lightrag_api

echo ""
echo "6. Waiting for container to be healthy..."
sleep 10

echo ""
echo "7. Checking container status..."
docker-compose ps lightrag_api

echo ""
echo "8. Checking logs (last 20 lines)..."
docker-compose logs lightrag_api --tail 20

echo ""
echo "=== Rebuild complete! ==="
