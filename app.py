from flask import Flask, render_template, request, send_file, redirect, url_for, flash, render_template, jsonify
from pdf_tools import merge_pdf, pdf_to_word, extract_pages, rotate_pdf, ocr_pdf, add_bookmark_to_pdf
import os, ocrmypdf, io, tempfile, subprocess
from PyPDF2 import PdfReader, PdfWriter
import uuid
from threading import Thread
import logging


UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Initialize Flask app
app = Flask(__name__, template_folder='templates', static_url_path='/static')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/merge', methods=['POST'])
def merge():
    if 'files[]' not in request.files:
        return "No files uploaded"
    files = request.files.getlist('files[]')
    merged_pdf = merge_pdf(files)
    return send_file(merged_pdf, as_attachment=True, mimetype='application/pdf', download_name='merged.pdf')

@app.route('/convert', methods=['POST'])
def convert():
    if 'file' not in request.files:
        flash("No file part")
        return redirect(url_for('index'))
    
    file = request.files['file']
    if file.filename == '':
        flash("No selected file")
        return redirect(url_for('index'))

    if file:
        pdf_path = os.path.join('/tmp', file.filename)
        file.save(pdf_path)

        word_path = os.path.join('/tmp', file.filename.rsplit('.', 1)[0] + '.docx')
        pdf_to_word(pdf_path, word_path)

        return send_file(word_path, as_attachment=True, download_name=os.path.basename(word_path))

@app.route('/extract', methods=['POST'])
def extract():
    file = request.files['file']
    start_page = int(request.form['start_page'])
    end_page = int(request.form['end_page'])
    extracted_pdf = extract_pages(file, start_page, end_page)
    return send_file(extracted_pdf, as_attachment=True, mimetype='application/pdf', download_name='extracted.pdf')

@app.route('/rotate', methods=['POST'])
def rotate():
    file = request.files['file']
    rotation_angle = int(request.form['rotation_angle'])
    pages = request.form.get('pages', '')
    
    try:
        if pages:
            pages = list(map(int, pages.split(',')))
        else:
            pages = None
    except ValueError:
        flash("Invalid page numbers")
        return redirect(url_for('index'))

    rotated_pdf = rotate_pdf(file, rotation_angle, pages)
    return send_file(rotated_pdf, as_attachment=True, mimetype='application/pdf', download_name='rotated.pdf')


# Compress PDF

@app.route("/compress_pdf", methods=["GET", "POST"])
def compress_pdf():
    if request.method == "POST":
        if "pdf_file" not in request.files:
            return "No file part in the request", 400

        file = request.files["pdf_file"]
        if file.filename == "":
            return "No selected file", 400

        compression_level = request.form.get("compression_level", "ebook")
        pdf_setting = PDF_SETTINGS.get(compression_level, "/ebook")

        input_filename = file.filename
        input_filepath = os.path.join(UPLOAD_FOLDER, input_filename)
        file.save(input_filepath)

        compressed_filename = "compressed_" + input_filename
        output_filepath = os.path.join(UPLOAD_FOLDER, compressed_filename)

        gs_command = [
            "gs",
            "-sDEVICE=pdfwrite",
            "-dCompatibilityLevel=1.4",
            f"-dPDFSETTINGS={pdf_setting}",
            "-dNOPAUSE",
            "-dQUIET",
            "-dBATCH",
            f"-sOutputFile={output_filepath}",
            input_filepath
        ]

        try:
            subprocess.run(gs_command, check=True)
        except subprocess.CalledProcessError as e:
            if os.path.exists(input_filepath):
                os.remove(input_filepath)
            return f"Error compressing PDF: {e}", 500

        return send_file(output_filepath, as_attachment=True)

    return render_template("index.html")





# OCR Processing

processing_status = {}
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def run_ocr(input_path, output_path, task_id):
    """Run OCRmyPDF with resource-optimized settings and logging."""
    try:
        logging.info(f"Starting OCR for task {task_id}")

        result = subprocess.run([
            "ocrmypdf",
            "--force-ocr",
            "--jobs", "1",                      # Prevent memory overload
            "--oversample", "200",              # Lower DPI rendering
            "--tesseract-timeout", "180",
            "--jpeg-quality", "70",
            "--pdfa-image-compression", "jpeg",
            "--skip-big", "20",                 # Skip images over 20MB
            # "--clean",                         # Optional: remove if crashing
            # "--optimize", "1",                 # Optional: skip to reduce CPU/RAM
            # "--fast-web-view", "5",            # Optional: remove if crashing
            input_path,
            output_path
        ], check=True, timeout=600)

        processing_status[task_id] = "done"
        logging.info(f"OCR completed for task {task_id}")

    except subprocess.TimeoutExpired:
        processing_status[task_id] = "timeout"
        logging.error(f"OCR timed out for task {task_id}")

    except subprocess.CalledProcessError as e:
        processing_status[task_id] = "error"
        logging.error(f"OCR failed for task {task_id}: {e}")






@app.route("/process", methods=["POST"])
def process_file():
    file = request.files["file"]
    if file:
        task_id = str(uuid.uuid4())
        input_path = os.path.join(UPLOAD_FOLDER, f"{task_id}.pdf")
        output_path = os.path.join(OUTPUT_FOLDER, f"{task_id}_ocr.pdf")
        file.save(input_path)

        processing_status[task_id] = "processing"
        Thread(target=run_ocr, args=(input_path, output_path, task_id)).start()

        return jsonify({"task_id": task_id})
    return jsonify({"error": "No file uploaded"}), 400

@app.route("/status/<task_id>")
def status(task_id):
    status = processing_status.get(task_id, "unknown")
    return jsonify({"status": status})

@app.route("/download/<task_id>")
def download(task_id):
    output_path = os.path.join(OUTPUT_FOLDER, f"{task_id}_ocr.pdf")
    if os.path.exists(output_path):
        return send_file(output_path, as_attachment=True)
    return "File not found.", 404


if __name__ == '__main__':
    app.run(debug=True, threaded=True)
