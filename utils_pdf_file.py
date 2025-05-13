"""
"""
import fitz  # PyMuPDF
import pdfplumber

import logging
logging.getLogger("pdfminer").setLevel(logging.ERROR)

def extract_tables_from_pdf(filepath):
    with pdfplumber.open(filepath) as pdf:
        tables = []
        for page in pdf.pages:
            extracted_tables = page.extract_tables()
            tables.extend(extracted_tables)
        if len(tables) == 0:
            print('no tables found in ' + filepath)
        else:
            print(f'{len(tables)} tables found in ' + filepath)
        return tables

def extract_text_from_pdf_page(filepath, start_page=1, end_page=None):
    doc = fitz.open(filepath)
    total_pages = doc.page_count

    # 頁碼範圍保護（fitz 是 0-based）
    start_idx = max(start_page - 1, 0)
    end_idx = min(end_page if end_page is not None else total_pages, total_pages)

    text = ""
    for page_number in range(start_idx, end_idx):
        page = doc.load_page(page_number)
        text += page.get_text("text")
    doc.close()
    return text

def extract_text_from_pdf(filepath, method='pdfplumber'):
    """Extracts text from a PDF file specified by the file path.

    Args:
        filepath (str): Path to the PDF file.
        method (str): ['fitz', ]

    Returns:
        str: Extracted text from the PDF.
    """
    if method == 'fitz':
        with fitz.open(filepath) as pdf:
            text = ""
            for page_num in range(pdf.page_count):
                page = pdf[page_num]
                text += page.get_text("text")
    elif method == 'pdfplumber':
        with pdfplumber.open(filepath) as pdf:
            text = ""
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text
    else:
        raise ValueError(f"unknown method: {method}")
    return text