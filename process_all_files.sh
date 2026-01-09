#!/bin/bash
# Complete workflow: Convert all PDFs and ingest all files

set -e

echo "=== Complete GAFTA File Processing Workflow ==="
echo ""

# Step 1: Convert all PDFs
echo "Step 1: Converting all PDF files to text..."
echo "----------------------------------------"
python3 convert_all_pdfs.py

if [ $? -ne 0 ]; then
    echo ""
    echo "⚠ PDF conversion had errors, but continuing..."
fi

echo ""
echo "Step 2: Ingesting all converted files into LightRAG..."
echo "----------------------------------------"

# Check if API is running
if ! curl -f http://162.243.201.21:8000/health > /dev/null 2>&1; then
    echo "⚠ API is not running. Starting services..."
    docker compose up -d --build
    echo "Waiting for services to be ready..."
    sleep 30
fi

# Ingest all files
python3 ingest_all_files.py

echo ""
echo "=== Workflow Complete ==="
echo "Access the web interface at: http://162.243.201.21:8000"
echo ""
