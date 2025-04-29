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
    # Create a temporary directory to store the OCR result
    with tempfile.TemporaryDirectory() as temp_dir:
        # Perform OCR on the PDF
        ocr_pdf_path = os.path.join(temp_dir, "ocr_output.pdf")
        ocrmypdf.ocr(pdf_path, ocr_pdf_path, force_ocr=True)
        
        # Read the OCR'd PDF
        reader = PdfReader(ocr_pdf_path)
        text_content = []
        
        for page in reader.pages:
            text_content.append(page.extract_text())
        
        # Create a Word document
        doc = Document()
        
        for page_text in text_content:
            doc.add_paragraph(page_text)
        
        # Save the Word document
        doc.save(word_path)





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
    # Convert PDF pages to images
    images = convert_from_path(file)

    # Perform OCR on each image and extract text
    extracted_text = []
    for img in images:
        text = pytesseract.image_to_string(img)
        extracted_text.append(text)

    # Combine extracted text from all pages
    combined_text = '\n'.join(extracted_text)

    return combined_text





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

