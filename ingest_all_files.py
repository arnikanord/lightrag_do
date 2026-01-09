#!/usr/bin/env python3
"""
Automatically discover and ingest all converted text files
Finds all .txt files in demo_files/gafta_contracts/ and defaulters_list.txt
"""

import os
import sys
import glob
import requests
import time
from pathlib import Path

API_URL = os.getenv("LIGHTRAG_API_URL", "http://162.243.201.21:8000")
INGEST_ENDPOINT = f"{API_URL}/ingest"
HEALTH_ENDPOINT = f"{API_URL}/health"


def check_api_health():
    """Check if the API is healthy"""
    try:
        response = requests.get(HEALTH_ENDPOINT, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data.get("ollama") == "healthy" and data.get("lightrag_initialized", False)
        return False
    except Exception as e:
        print(f"Error checking API health: {e}")
        return False


def ingest_file(file_path, doc_id=None):
    """Ingest a single text file"""
    if not os.path.exists(file_path):
        return False, f"File not found: {file_path}"
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        return False, f"Error reading file: {e}"
    
    if not content.strip():
        return False, "File is empty"
    
    if doc_id is None:
        doc_id = Path(file_path).stem
    
    try:
        response = requests.post(
            INGEST_ENDPOINT,
            json={"text": content, "doc_id": doc_id},
            timeout=300
        )
        
        if response.status_code == 200:
            result = response.json()
            return True, f"Successfully ingested ({result.get('text_length', 0)} characters)"
        else:
            return False, f"HTTP {response.status_code}: {response.text}"
    except requests.exceptions.Timeout:
        return False, "Timeout (document may be too large)"
    except Exception as e:
        return False, str(e)


def main():
    print("=== Auto-Ingest All Converted Files ===\n")
    
    # Check API health
    print("Checking API health...")
    if not check_api_health():
        print("✗ API is not healthy. Please ensure:")
        print("  1. Docker Compose services are running: docker-compose up -d")
        print("  2. Ollama is ready and models are loaded")
        print("  3. LightRAG API is accessible")
        sys.exit(1)
    print("✓ API is healthy\n")
    
    # Find all contract files
    contracts_dir = Path("demo_files/gafta_contracts")
    contract_files = []
    if contracts_dir.exists():
        contract_files = sorted(contracts_dir.glob("*.txt"))
    
    # Find defaulters file
    defaulters_file = Path("demo_files/defaulters_list.txt")
    
    total_files = len(contract_files) + (1 if defaulters_file.exists() else 0)
    
    if total_files == 0:
        print("⚠ No text files found!")
        print("Please convert PDFs first: python3 convert_all_pdfs.py")
        sys.exit(1)
    
    print(f"Found {total_files} file(s) to ingest:\n")
    for f in contract_files:
        print(f"  - {f.name} (contract)")
    if defaulters_file.exists():
        print(f"  - {defaulters_file.name} (defaulters)")
    print("")
    
    success_count = 0
    failed_count = 0
    
    # Ingest contract files
    if contract_files:
        print("Ingesting GAFTA Contracts...\n")
        for file_path in contract_files:
            doc_id = file_path.stem
            print(f"Ingesting: {file_path.name} as '{doc_id}'...")
            success, message = ingest_file(str(file_path), doc_id)
            if success:
                print(f"  ✓ {message}\n")
                success_count += 1
            else:
                print(f"  ✗ Failed: {message}\n")
                failed_count += 1
            time.sleep(1)  # Small delay between requests
    
    # Ingest defaulters file
    if defaulters_file.exists():
        print("Ingesting Defaulters List...\n")
        print(f"Ingesting: {defaulters_file.name} as 'gafta_defaulters'...")
        success, message = ingest_file(str(defaulters_file), "gafta_defaulters")
        if success:
            print(f"  ✓ {message}\n")
            success_count += 1
        else:
            print(f"  ✗ Failed: {message}\n")
            failed_count += 1
    
    # Summary
    print("=== Ingestion Summary ===")
    print(f"Total files: {total_files}")
    print(f"Successful: {success_count}")
    print(f"Failed: {failed_count}")
    
    if failed_count == 0:
        print("\n✓ All files ingested successfully!")
        print("\nYou can now query the knowledge graph at: http://localhost:8000")
        return 0
    else:
        print(f"\n⚠ {failed_count} file(s) failed to ingest.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
