# GAFTA PDF Files Setup

## Quick Setup - Auto-Discover All PDFs

The system now **automatically discovers and converts ALL PDF files** in the project directory!

### Step 1: Place ALL Your PDFs
Simply copy **any and all** GAFTA PDF files to the project root:
```bash
cd /root/gafta-guardian

# Copy ALL your PDFs here - the script will find them automatically:
# - 1_2025.pdf
# - 2_2025.pdf  
# - 48_2025.pdf
# - 49_2025.pdf
# - Any other GAFTA contract PDFs
# - defaulters_on_gafta_awards_of_arbitration_2011-present.pdf
# - Any other PDFs you want to process
```

**The system will automatically:**
- Detect all `.pdf` files in the directory
- Identify defaulters PDFs (by keywords: "defaulters", "awards", "arbitration")
- Convert contract PDFs to `demo_files/gafta_contracts/`
- Convert defaulters PDFs to `demo_files/defaulters_list.txt`

### Step 2: Install PDF Library
```bash
pip install pdfplumber
# OR (alternative)
pip install PyPDF2
```

### Step 3: Convert All PDFs (Auto-Discovery)
```bash
# Option 1: Python script (recommended - auto-discovers all PDFs)
python3 convert_all_pdfs.py

# Option 2: Shell script (also auto-discovers)
chmod +x convert_all_pdfs.sh
./convert_all_pdfs.sh
```

The script will **automatically**:
- Find ALL `.pdf` files in the current directory
- Identify which are contracts vs defaulters (by filename keywords)
- Convert all contract PDFs to `demo_files/gafta_contracts/`
- Convert defaulters PDFs to `demo_files/defaulters_list.txt`
- Show success/failure status for each file

### Step 4: Ingest All Converted Files (Optional)
After conversion, automatically ingest all files:
```bash
# Auto-discovers and ingests all converted .txt files
python3 ingest_all_files.py
```

### Complete Workflow (One Command)
Or do everything at once:
```bash
# Converts all PDFs AND ingests all files automatically
./process_all_files.sh
```

### Step 4: Verify Converted Files
```bash
ls -lh demo_files/gafta_contracts/
cat demo_files/defaulters_list.txt | head -20
```

## File Structure After Conversion

```
/root/gafta-guardian/
├── 1_2025.pdf                                    ← Your original PDFs
├── 2_2025.pdf
├── 48_2025.pdf
├── 49_2025.pdf
├── defaulters_on_gafta_awards_of_arbitration_2011-present.pdf
├── demo_files/
│   ├── gafta_contracts/
│   │   ├── 1_2025.txt                           ← Converted text files
│   │   ├── 2_2025.txt
│   │   ├── 48_2025.txt
│   │   └── 49_2025.txt
│   └── defaulters_list.txt                       ← Converted defaulters list
└── convert_all_pdfs.py                           ← Batch converter
```

## Manual Conversion (One at a Time)

If you prefer to convert files individually:

```bash
# Convert contract PDFs
python3 convert_pdf_to_text.py 1_2025.pdf demo_files/gafta_contracts/1_2025.txt
python3 convert_pdf_to_text.py 2_2025.pdf demo_files/gafta_contracts/2_2025.txt
python3 convert_pdf_to_text.py 48_2025.pdf demo_files/gafta_contracts/48_2025.txt
python3 convert_pdf_to_text.py 49_2025.pdf demo_files/gafta_contracts/49_2025.txt

# Convert defaulters PDF
python3 convert_pdf_to_text.py defaulters_on_gafta_awards_of_arbitration_2011-present.pdf demo_files/defaulters_list.txt
```

## Troubleshooting

### PDF Conversion Fails
- **Image-based PDFs**: If PDFs are scanned images, you need OCR:
  ```bash
  sudo apt-get install tesseract-ocr
  pip install pytesseract pdf2image
  ```
  (OCR support can be added to the conversion script if needed)

- **Try different library**: 
  ```bash
  pip uninstall pdfplumber
  pip install PyPDF2
  ```

### Files Not Found
- Make sure PDFs are in `/root/gafta-guardian/` directory
- Check filenames match exactly (case-sensitive)
- Use `ls -la` to verify files exist

### Empty Text Files
- PDF might be image-based (scanned)
- Try OCR tools or manually extract text
- Check if PDF is password-protected

## Next Steps

After converting PDFs:

1. **Start the services**:
   ```bash
   docker-compose up -d --build
   ```

2. **Ingest documents** (via web interface or bulk script):
   ```bash
   # Via web: http://localhost:8000
   # OR via command line:
   python3 bulk_ingest.py demo_files/gafta_contracts demo_files/defaulters_list.txt
   ```

3. **Query the knowledge graph**:
   - Open browser: http://localhost:8000
   - Use the Query interface to ask questions about the contracts and defaulters
