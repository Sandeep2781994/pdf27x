FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && \
    apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-eng \  # English language pack
    poppler-utils \     # Required for pdf2image
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . .
RUN pip install -r requirements.txt

CMD ["gunicorn", "--bind", "0.0.0.0:$PORT", "app:app"]
