# Base image with Python
FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-eng \
    poppler-utils \
    unpaper \
    wget \
    build-essential \
    libpng-dev \
    libjpeg-dev \
    zlib1g-dev \
    ghostscript \
    && rm -rf /var/lib/apt/lists/*

# Remove manual Ghostscript build and use packaged version
# (The package manager version is more likely to work with system libraries)

WORKDIR /app
COPY . .

# Install Python dependencies including ocrmypdf
RUN pip install --no-cache-dir -r requirements-new.txt ocrmypdf

EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
