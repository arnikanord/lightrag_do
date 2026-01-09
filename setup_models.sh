#!/bin/bash
# Setup script to pull required Ollama models before starting the full stack

set -e

echo "=== Ollama Model Setup Script ==="
echo "This script will pull the required models for LightRAG"
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "Error: Docker is not running. Please start Docker first."
    exit 1
fi

# Check if NVIDIA GPU is available (optional check)
if command -v nvidia-smi &> /dev/null; then
    if nvidia-smi > /dev/null 2>&1; then
        echo "NVIDIA GPU detected"
        GPU_FLAG="--gpus all"
    else
        echo "Warning: nvidia-smi failed, but continuing anyway..."
        GPU_FLAG=""
    fi
else
    echo "Warning: nvidia-smi not found, continuing without GPU flag..."
    GPU_FLAG=""
fi

# Create ollama_data directory if it doesn't exist
mkdir -p ./ollama_data

echo "Step 1: Starting temporary Ollama container..."
docker run -d \
    $GPU_FLAG \
    -v $(pwd)/ollama_data:/root/.ollama \
    -p 11434:11434 \
    --name temp_ollama \
    ollama/ollama:latest

echo "Waiting for Ollama to be ready..."
sleep 15

# Wait for Ollama to be fully ready
for i in {1..30}; do
    if curl -f http://localhost:11434/api/tags > /dev/null 2>&1; then
        echo "Ollama is ready!"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "Error: Ollama failed to start after 30 attempts"
        docker stop temp_ollama && docker rm temp_ollama
        exit 1
    fi
    sleep 2
done

echo ""
echo "Step 2: Pulling llama3.3:70b model (this may take a while, ~40GB+)..."
docker exec temp_ollama ollama pull llama3.3:70b

echo ""
echo "Step 3: Pulling bge-m3 embedding model..."
docker exec temp_ollama ollama pull bge-m3

# Verify models were pulled
echo ""
echo "Step 4: Verifying models..."
docker exec temp_ollama ollama list

echo ""
echo "Step 5: Cleaning up temporary container..."
docker stop temp_ollama
docker rm temp_ollama

echo ""
echo "=== Setup Complete ==="
echo "Models are now available in ./ollama_data"
echo "You can now start the full stack with: docker-compose up -d --build"
echo ""
