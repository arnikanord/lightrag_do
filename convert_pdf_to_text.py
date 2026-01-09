#!/usr/bin/env python3
"""
Convert PDF files to text for LightRAG ingestion
Supports the GAFTA defaulters list PDF
"""

import sys
import os
from pathlib import Path

try:
    import PyPDF2
    PDF_LIB = "PyPDF2"
except ImportError:
    try:
        import pdfplumber
        PDF_LIB = "pdfplumber"
    except ImportError:
        print("Error: No PDF library found. Please install one:")
        print("  pip install PyPDF2")
        print("  OR")
        print("  pip install pdfplumber")
        sys.exit(1)


def extract_text_pypdf2(pdf_path):
    """Extract text using PyPDF2"""
    text = ""
    with open(pdf_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        for page_num, page in enumerate(pdf_reader.pages):
            text += f"\n--- Page {page_num + 1} ---\n"
            text += page.extract_text()
    return text


def extract_text_pdfplumber(pdf_path):
    """Extract text using pdfplumber (better quality)"""
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages):
            text += f"\n--- Page {page_num + 1} ---\n"
            page_text = page.extract_text()
            if page_text:
                text += page_text
    return text


def convert_pdf_to_text(pdf_path, output_path=None):
    """
    Convert PDF to text file
    
    Args:
        pdf_path: Path to PDF file
        output_path: Optional output path (defaults to same name with .txt extension)
    """
    if not os.path.exists(pdf_path):
        print(f"Error: PDF file not found: {pdf_path}")
        return False
    
    print(f"Converting {pdf_path} to text...")
    print(f"Using library: {PDF_LIB}")
    
    try:
        if PDF_LIB == "PyPDF2":
            text = extract_text_pypdf2(pdf_path)
        else:
            text = extract_text_pdfplumber(pdf_path)
        
        if not text.strip():
            print("Warning: No text extracted from PDF. The PDF might be image-based (scanned).")
            print("You may need OCR software like Tesseract.")
            return False
        
        # Determine output path
        if output_path is None:
            output_path = str(Path(pdf_path).with_suffix('.txt'))
        
        # Write text file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(text)
        
        print(f"✓ Successfully converted to: {output_path}")
        print(f"  Extracted {len(text)} characters from PDF")
        return True
        
    except Exception as e:
        print(f"Error converting PDF: {e}")
        return False


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 convert_pdf_to_text.py <pdf_file> [output_file]")
        print("\nExample:")
        print("  python3 convert_pdf_to_text.py defaulters_on_gafta_awards_of_arbitration_2011-present.pdf")
        print("  python3 convert_pdf_to_text.py defaulters.pdf demo_files/defaulters_list.txt")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    success = convert_pdf_to_text(pdf_path, output_path)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
