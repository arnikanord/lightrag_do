#!/bin/bash
# Batch convert all GAFTA PDF files to text

set -e

echo "=== GAFTA PDF Batch Converter ==="
echo ""

# Check if PDF library is installed
if ! python3 -c "import pdfplumber" 2>/dev/null && ! python3 -c "import PyPDF2" 2>/dev/null; then
    echo "Installing PDF library..."
    pip install pdfplumber || pip install PyPDF2
fi

# Directory for converted files
OUTPUT_DIR="demo_files/gafta_contracts"
mkdir -p "$OUTPUT_DIR"

# Auto-discover all PDF files
echo "Looking for PDF files in current directory..."
PDF_FILES=($(ls *.pdf 2>/dev/null))

if [ ${#PDF_FILES[@]} -eq 0 ]; then
    echo "⚠ No PDF files found in current directory!"
    echo "Please place your PDF files in: $(pwd)"
    exit 1
fi

echo "Found ${#PDF_FILES[@]} PDF file(s):"
for pdf in "${PDF_FILES[@]}"; do
    echo "  - $pdf"
done
echo ""

SUCCESS=0
FAILED=0

# Separate defaulters PDF from contract PDFs
DEFAULTERS_PDF=""
CONTRACT_PDFS=()

for pdf_file in "${PDF_FILES[@]}"; do
    pdf_lower=$(echo "$pdf_file" | tr '[:upper:]' '[:lower:]')
    if [[ "$pdf_lower" == *"defaulters"* ]] || [[ "$pdf_lower" == *"awards"* ]] || [[ "$pdf_lower" == *"arbitration"* ]]; then
        DEFAULTERS_PDF="$pdf_file"
    else
        CONTRACT_PDFS+=("$pdf_file")
    fi
done

# Convert contract PDFs
if [ ${#CONTRACT_PDFS[@]} -gt 0 ]; then
    echo "Converting GAFTA Contract PDFs..."
    echo ""
    for pdf_file in "${CONTRACT_PDFS[@]}"; do
        output_file="${OUTPUT_DIR}/${pdf_file%.pdf}.txt"
        echo "Converting: $pdf_file -> $output_file"
        if python3 convert_pdf_to_text.py "$pdf_file" "$output_file"; then
            echo "✓ Success: $pdf_file"
            ((SUCCESS++))
        else
            echo "✗ Failed: $pdf_file"
            ((FAILED++))
        fi
        echo ""
    done
fi

# Convert defaulters PDF
if [ -n "$DEFAULTERS_PDF" ]; then
    echo "Converting Defaulters PDF..."
    echo "Converting: $DEFAULTERS_PDF -> demo_files/defaulters_list.txt"
    if python3 convert_pdf_to_text.py "$DEFAULTERS_PDF" "demo_files/defaulters_list.txt"; then
        echo "✓ Success: $DEFAULTERS_PDF"
        ((SUCCESS++))
    else
        echo "✗ Failed: $DEFAULTERS_PDF"
        ((FAILED++))
    fi
    echo ""
else
    echo "⚠ No defaulters PDF found (looking for files with 'defaulters', 'awards', or 'arbitration' in name)"
    echo ""
fi

echo "=== Conversion Summary ==="
echo "Successful: $SUCCESS"
echo "Failed: $FAILED"
echo ""
echo "Converted files are in: $OUTPUT_DIR"
echo ""

if [ $FAILED -eq 0 ]; then
    echo "✓ All conversions successful!"
    exit 0
else
    echo "⚠ Some conversions failed. Check the errors above."
    exit 1
fi
