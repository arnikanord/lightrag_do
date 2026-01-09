#!/usr/bin/env python3
"""
Bulk ingestion script for LightRAG
Ingests multiple documents from text files into the LightRAG system
"""

import requests
import glob
import os
import sys
import time
from pathlib import Path
from typing import Optional

# Configuration
API_URL = os.getenv("LIGHTRAG_API_URL", "http://162.243.201.21:8000")
INGEST_ENDPOINT = f"{API_URL}/ingest"
HEALTH_ENDPOINT = f"{API_URL}/health"


def check_api_health() -> bool:
    """Check if the API is healthy and ready"""
    try:
        response = requests.get(HEALTH_ENDPOINT, timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            print(f"API Status: {health_data}")
            return health_data.get("ollama") == "healthy" and health_data.get("lightrag_initialized", False)
        return False
    except Exception as e:
        print(f"Error checking API health: {e}")
        return False


def ingest_file(file_path: str, doc_id: Optional[str] = None) -> bool:
    """
    Ingest a single text file into LightRAG
    
    Args:
        file_path: Path to the text file
        doc_id: Optional document ID (defaults to filename)
        
    Returns:
        True if successful, False otherwise
    """
    if not os.path.exists(file_path):
        print(f"Error: File not found: {file_path}")
        return False
    
    # Read file content
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return False
    
    if not content.strip():
        print(f"Warning: File {file_path} is empty, skipping...")
        return False
    
    # Use filename as doc_id if not provided
    if doc_id is None:
        doc_id = os.path.basename(file_path)
    
    # Ingest document
    try:
        print(f"Ingesting {file_path} as doc_id='{doc_id}'...")
        response = requests.post(
            INGEST_ENDPOINT,
            json={"text": content, "doc_id": doc_id},
            timeout=300  # 5 minute timeout for large documents
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Successfully ingested {doc_id} ({result.get('text_length', 0)} characters)")
            return True
        else:
            print(f"✗ Failed to ingest {doc_id}: {response.status_code} - {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print(f"✗ Timeout while ingesting {doc_id} (document may be too large)")
        return False
    except Exception as e:
        print(f"✗ Error ingesting {doc_id}: {e}")
        return False


def main():
    """Main ingestion function"""
    print("=== LightRAG Bulk Ingestion Script ===")
    print(f"API URL: {API_URL}")
    print("")
    
    # Check API health
    print("Checking API health...")
    if not check_api_health():
        print("Error: API is not healthy. Please ensure:")
        print("1. Docker Compose services are running: docker-compose up -d")
        print("2. Ollama is ready and models are loaded")
        print("3. LightRAG API is accessible")
        sys.exit(1)
    
    print("")
    
    # Get directories from command line or use defaults
    if len(sys.argv) > 1:
        gafta_contracts_dir = sys.argv[1]
    else:
        gafta_contracts_dir = "./gafta_contracts"
    
    if len(sys.argv) > 2:
        defaulters_file = sys.argv[2]
    else:
        defaulters_file = "./defaulters_list.txt"
    
    success_count = 0
    fail_count = 0
    
    # Ingest GAFTA Contracts
    if os.path.exists(gafta_contracts_dir):
        print(f"=== Ingesting GAFTA Contracts from {gafta_contracts_dir} ===")
        contract_files = glob.glob(os.path.join(gafta_contracts_dir, "*.txt"))
        
        if not contract_files:
            print(f"No .txt files found in {gafta_contracts_dir}")
        else:
            for file_path in contract_files:
                if ingest_file(file_path):
                    success_count += 1
                else:
                    fail_count += 1
                # Small delay to avoid overwhelming the API
                time.sleep(1)
    else:
        print(f"Warning: GAFTA contracts directory not found: {gafta_contracts_dir}")
    
    print("")
    
    # Ingest Defaulters List
    if os.path.exists(defaulters_file):
        print(f"=== Ingesting Defaulters List: {defaulters_file} ===")
        if ingest_file(defaulters_file, doc_id="gafta_defaulters_2023"):
            success_count += 1
        else:
            fail_count += 1
    else:
        print(f"Warning: Defaulters list file not found: {defaulters_file}")
    
    print("")
    print("=== Ingestion Summary ===")
    print(f"Successful: {success_count}")
    print(f"Failed: {fail_count}")
    print(f"Total: {success_count + fail_count}")
    
    if fail_count > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
