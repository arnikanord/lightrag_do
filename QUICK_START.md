# Quick Start - Using Your Real GAFTA Files

## Complete Workflow (Easiest)

### One-Command Setup
```bash
cd /root/gafta-guardian

# 1. Place ALL your PDF files in this directory
# 2. Install PDF library
pip install pdfplumber

# 3. Run complete workflow (converts + ingests)
./process_all_files.sh
```

This will:
- Auto-discover ALL PDF files
- Convert them to text
- Start services if needed
- Ingest all files into LightRAG
- Ready to query!

## Step-by-Step Setup

### Step 1: Place Your PDFs
Put **ALL** your GAFTA PDF files in `/root/gafta-guardian/`:
- Any contract PDFs (e.g., `1_2025.pdf`, `49_2025.pdf`, etc.)
- Defaulters PDF (any file with "defaulters", "awards", or "arbitration" in name)
- **The system auto-discovers all PDFs - no need to specify filenames!**

### Step 2: Convert All PDFs
```bash
cd /root/gafta-guardian
pip install pdfplumber
python3 convert_all_pdfs.py
```

This automatically finds and converts ALL PDF files.

### Step 3: Start Services
```bash
docker-compose up -d --build
```

Wait for services to be ready (check logs):
```bash
docker logs -f gafta-guardian-lightrag_api-1
```

### Step 4: Ingest All Files
```bash
# Auto-discovers and ingests all converted files
python3 ingest_all_files.py
```

### Step 5: Open Browser
Navigate to: **http://localhost:8000** (or http://YOUR_SERVER_IP:8000)

## Testing in Browser

### The Web Interface Provides:

1. **System Status** - Top of page shows if everything is healthy

2. **Ingest Documents Tab**:
   - Upload `.txt` files OR paste text directly
   - Supports PDF upload (basic extraction)
   - Enter Document ID
   - Click "Ingest Document"
   - Wait for confirmation (1-5 minutes per document)

3. **Query Knowledge Graph Tab**:
   - Enter questions like:
     - "Is VECTOR GULF TRADING LLC in the defaulters list?"
     - "What awards are associated with companies from Dubai?"
     - "What are the Force Majeure requirements in GAFTA 49?"
     - "What are the payment terms in Contract 1?"
   - Select mode: "Hybrid" (recommended)
   - Click "Execute Query"
   - Wait for response (5-30 seconds)

## File Structure

```
/root/gafta-guardian/
├── *.pdf                                    ← PUT ALL YOUR PDFs HERE
├── convert_all_pdfs.py                      ← Auto-discovers & converts all PDFs
├── ingest_all_files.py                      ← Auto-discovers & ingests all .txt files
├── process_all_files.sh                      ← Complete workflow (convert + ingest)
├── demo_files/
│   ├── gafta_contracts/                     ← Auto-generated from PDFs
│   │   ├── 1_2025.txt
│   │   ├── 2_2025.txt
│   │   └── ... (all your contracts)
│   └── defaulters_list.txt                  ← Auto-generated from defaulters PDF
└── lightrag_api/static/index.html           ← Web interface
```

## Adding More Files Later

Just add more PDFs to the directory and run:
```bash
# Convert new PDFs
python3 convert_all_pdfs.py

# Ingest new files
python3 ingest_all_files.py
```

The system will automatically:
- Find new PDFs
- Convert them
- Skip already-converted files (or overwrite if you want)
- Ingest only new files

## Troubleshooting

**PDF won't convert?**
- PDF might be scanned (image-based). Install OCR:
  ```bash
  sudo apt-get install tesseract-ocr
  pip install pytesseract pdf2image
  ```

**Can't access web interface?**
- Check if port 8000 is open: `curl http://localhost:8000/health`
- Check firewall: `sudo ufw allow 8000`
- View logs: `docker logs gafta-guardian-lightrag_api-1`

**Services not starting?**
- Check GPU: `nvidia-smi`
- Check Docker: `docker ps`
- View all logs: `docker-compose logs`

## Example Queries to Try

After ingesting your files, try these queries:

- "List all defaulters from 2025"
- "What companies from Dubai are in the defaulters list?"
- "What are the Force Majeure requirements in GAFTA 49?"
- "Compare payment terms between Contract 1 and Contract 49"
- "What are the arbitration procedures in GAFTA contracts?"
- "Which companies have awards from September 2025?"
