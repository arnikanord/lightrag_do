# Demo Setup Guide

## Step 1: Convert PDF to Text

If you have the GAFTA defaulters PDF file, convert it to text:

```bash
cd /root/gafta-guardian

# Install PDF library (choose one)
pip install PyPDF2
# OR (better quality)
pip install pdfplumber

# Convert the PDF
python3 convert_pdf_to_text.py defaulters_on_gafta_awards_of_arbitration_2011-present.pdf demo_files/defaulters_list.txt
```

**Note**: If the PDF is scanned (image-based), you'll need OCR:
```bash
# Install Tesseract OCR
sudo apt-get install tesseract-ocr
pip install pytesseract pdf2image

# Then use OCR-based extraction (we can add this if needed)
```

## Step 2: Place Your GAFTA Contracts

Place your GAFTA contract text files in:
```
demo_files/gafta_contracts/
```

Example:
- `demo_files/gafta_contracts/gafta_49.txt`
- `demo_files/gafta_contracts/gafta_100.txt`
- etc.

## Step 3: Access the Web Interface

Once your Docker services are running:

1. **Open in browser**: http://localhost:8000 (or http://YOUR_SERVER_IP:8000)

2. **The web interface provides**:
   - System health status
   - Document upload and ingestion
   - Query interface for the knowledge graph

3. **Upload files**:
   - Click "Upload & Ingest Document" tab
   - Upload your text files or paste content
   - Click "Ingest Document"

4. **Query the knowledge graph**:
   - Click "Query Knowledge Graph" tab
   - Enter your question
   - Select query mode (Hybrid recommended)
   - Click "Execute Query"

## Step 4: Bulk Ingestion (Alternative)

If you prefer command-line bulk ingestion:

```bash
cd /root/gafta-guardian
python3 bulk_ingest.py demo_files/gafta_contracts demo_files/defaulters_list.txt
```

## Quick Test

After ingesting documents, try queries like:

- "Is VECTOR GULF TRADING LLC listed in the defaulters list?"
- "What awards are associated with companies from Dubai?"
- "List all defaulters from 2025"
- "What are the Force Majeure requirements in GAFTA 49?"

## File Locations Summary

```
/root/gafta-guardian/
├── demo_files/
│   ├── gafta_contracts/          ← Place your GAFTA contract .txt files here
│   └── defaulters_list.txt       ← Converted PDF text goes here
├── convert_pdf_to_text.py        ← Use this to convert PDF to text
└── bulk_ingest.py                 ← Use this for bulk ingestion
```

## Troubleshooting

### PDF conversion fails
- The PDF might be image-based (scanned). Use OCR tools.
- Try `pdfplumber` instead of `PyPDF2` for better extraction.

### Web interface not loading
- Check if services are running: `docker ps`
- Check API health: `curl http://localhost:8000/health`
- View logs: `docker logs gafta-guardian-lightrag_api-1`

### Files not found
- Make sure you're placing files in the correct directories
- Use absolute paths if needed: `/root/gafta-guardian/demo_files/...`
