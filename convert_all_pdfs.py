#!/usr/bin/env python3
"""
Batch convert all GAFTA PDF files to text
Handles multiple contract PDFs and the defaulters list
"""

import os
import sys
from pathlib import Path

# Import the conversion function from convert_pdf_to_text
try:
    import PyPDF2
    PDF_LIB = "PyPDF2"
except ImportError:
    try:
        import pdfplumber
        PDF_LIB = "pdfplumber"
    except ImportError:
        print("Error: No PDF library found. Installing pdfplumber...")
        os.system("pip install pdfplumber")
        try:
            import pdfplumber
            PDF_LIB = "pdfplumber"
        except ImportError:
            print("Failed to install. Please run: pip install pdfplumber")
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


def convert_pdf(pdf_path, output_path):
    """Convert a single PDF to text"""
    if not os.path.exists(pdf_path):
        return False, f"File not found: {pdf_path}"
    
    try:
        if PDF_LIB == "PyPDF2":
            text = extract_text_pypdf2(pdf_path)
        else:
            text = extract_text_pdfplumber(pdf_path)
        
        if not text.strip():
            return False, "No text extracted (PDF might be image-based)"
        
        # Write text file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(text)
        
        return True, f"Extracted {len(text)} characters"
    except Exception as e:
        return False, str(e)


def main():
    print("=== GAFTA PDF Batch Converter ===\n")
    
    # Auto-discover all PDF files in current directory
    current_dir = Path(".")
    all_pdfs = sorted([f for f in current_dir.glob("*.pdf") if f.is_file()])
    
    if not all_pdfs:
        print("⚠ No PDF files found in current directory!")
        print("Please place your PDF files in: /root/gafta-guardian/")
        return 1
    
    print(f"Found {len(all_pdfs)} PDF file(s):\n")
    for pdf in all_pdfs:
        print(f"  - {pdf.name}")
    print("")
    
    # Create output directory
    contracts_dir = Path("demo_files/gafta_contracts")
    contracts_dir.mkdir(parents=True, exist_ok=True)
    
    success_count = 0
    failed_count = 0
    
    # Special handling for defaulters PDF
    defaulters_keywords = ["defaulters", "awards", "arbitration"]
    defaulters_pdf = None
    contract_pdfs = []
    
    for pdf in all_pdfs:
        pdf_lower = pdf.name.lower()
        if any(keyword in pdf_lower for keyword in defaulters_keywords):
            defaulters_pdf = pdf
        else:
            contract_pdfs.append(pdf)
    
    # Convert contract PDFs
    if contract_pdfs:
        print("Converting GAFTA Contract PDFs...\n")
        for pdf_path in contract_pdfs:
            output_path = contracts_dir / f"{pdf_path.stem}.txt"
            print(f"Converting: {pdf_path.name} -> {output_path.name}")
            success, message = convert_pdf(str(pdf_path), str(output_path))
            if success:
                print(f"  ✓ Success: {message}\n")
                success_count += 1
            else:
                print(f"  ✗ Failed: {message}\n")
                failed_count += 1
    
    # Convert defaulters PDF
    if defaulters_pdf:
        print("Converting Defaulters PDF...\n")
        output_path = Path("demo_files/defaulters_list.txt")
        print(f"Converting: {defaulters_pdf.name} -> {output_path.name}")
        success, message = convert_pdf(str(defaulters_pdf), str(output_path))
        if success:
            print(f"  ✓ Success: {message}\n")
            success_count += 1
        else:
            print(f"  ✗ Failed: {message}\n")
            failed_count += 1
    else:
        print("⚠ No defaulters PDF found (looking for files with 'defaulters', 'awards', or 'arbitration' in name)\n")
    
    # Summary
    print("=== Conversion Summary ===")
    print(f"Total PDFs found: {len(all_pdfs)}")
    print(f"Successful conversions: {success_count}")
    print(f"Failed conversions: {failed_count}")
    print(f"\nConverted contract files: {contracts_dir}")
    if defaulters_pdf:
        print(f"Defaulters list: demo_files/defaulters_list.txt")
    
    if failed_count == 0:
        print("\n✓ All conversions successful!")
        return 0
    else:
        print(f"\n⚠ {failed_count} conversion(s) failed.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
