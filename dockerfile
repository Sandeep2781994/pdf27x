# Base image with Python
FROM python:3.10-slim

# Install system dependencies for OCR
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    ghostscript \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy all files to the container
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements-new.txt

# Expose Flask port
EXPOSE 5000

# Start the app (change this if needed)
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5000"]
