# pdf_tools.py

from PyPDF2 import PdfReader, PdfWriter
import io

import os
import tempfile
import ocrmypdf
import pytesseract
from pdf2image import convert_from_path
from tempfile import NamedTemporaryFile
from docx import Document
from PyPDF2 import PdfReader


pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'  # Docker path



def merge_pdf(files):
    merged_pdf = PdfWriter()
    for file in files:
        pdf = PdfReader(file)
        for page in pdf.pages:
            merged_pdf.add_page(page)
    output = io.BytesIO()
    merged_pdf.write(output)
    output.seek(0)
    return output




def pdf_to_word(pdf_path, word_path):
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            ocr_pdf_path = os.path.join(temp_dir, "ocr_output.pdf")
            
            # Add language support if needed (e.g., '--language eng+fra')
            ocrmypdf.ocr(
                input_file=pdf_path,
                output_file=ocr_pdf_path,
                force_ocr=True,
                optimize=1
            )
            
            reader = PdfReader(ocr_pdf_path)
            doc = Document()
            
            for page in reader.pages:
                if text := page.extract_text():
                    doc.add_paragraph(text)
            
            doc.save(word_path)
            return True
    except Exception as e:
        print(f"Error in pdf_to_word: {str(e)}")
        return False




def extract_pages(file, start_page, end_page):
    input_pdf = PdfReader(file)
    extracted_pdf = PdfWriter()
    for i in range(start_page - 1, end_page):
        extracted_pdf.add_page(input_pdf.pages[i])
    output = io.BytesIO()
    extracted_pdf.write(output)
    output.seek(0)
    return output




def rotate_pdf(file, rotation_angle, pages=None):
    input_pdf = PdfReader(file)
    output_pdf = PdfWriter()
    
    for i, page in enumerate(input_pdf.pages):
        if pages is None or (i + 1) in pages:
            page.rotate(rotation_angle)
        output_pdf.add_page(page)
    
    output = io.BytesIO()
    output_pdf.write(output)
    output.seek(0)
    return output




def ocr_pdf(file):
    try:
        # Use dpi=300 for better OCR accuracy
        images = convert_from_path(file, dpi=300)
        return '\n'.join(pytesseract.image_to_string(img) for img in images)
    except Exception as e:
        print(f"OCR Error: {str(e)}")
        return None




def add_bookmark_to_pdf(input_pdf, bookmarks):
    pdf_reader = PdfReader(input_pdf)
    pdf_writer = PdfWriter()
    
    for page_num in range(len(pdf_reader.pages)):
        pdf_writer.add_page(pdf_reader.pages[page_num])
    
    for title, page_num in bookmarks:
        pdf_writer.add_outline_item(title, page_num - 1)
    
    output_pdf = io.BytesIO()
    pdf_writer.write(output_pdf)
    output_pdf.seek(0)
    
    return output_pdf

