# Use Python 3.9 (stable with Tesseract)
FROM python:3.9

# Install Tesseract-OCR and dependencies
RUN apt-get update && \
    apt-get install -y tesseract-ocr && \
    apt-get clean

# Set working directory
WORKDIR /app

# Copy files
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Run the app with Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:${PORT:-5000}", "app:app"]
