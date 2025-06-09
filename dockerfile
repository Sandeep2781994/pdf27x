FROM python:3.9-slim

# Install system dependencies (including Tesseract and Poppler for pdf2image)
RUN apt-get update && \
    apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-eng \  # For English language (add others like 'tesseract-ocr-fra' for French)
    poppler-utils \      # Required for pdf2image
    libmagic1 \          # For file type detection
    && apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["gunicorn", "--bind", "0.0.0.0:$PORT", "--workers", "4", "app:app"]
