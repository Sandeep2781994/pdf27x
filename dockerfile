# Base image with Python - Updated to 3.11-slim for potentially newer system dependencies
# (You could also try python:3.12-slim if 3.11-slim still gives the Ghostscript warning)
FROM python:3.11-slim

# Install system dependencies
# apt-get update is run first to ensure package lists are current
# -y flag automatically confirms installation prompts
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
    # Clean up apt cache to reduce image size and improve security
    && rm -rf /var/lib/apt/lists/*

# Set the working directory inside the container
WORKDIR /app

# Copy all local files into the container's /app directory
COPY . .

# Install Python dependencies from requirements-new.txt
# --no-cache-dir reduces image size by not storing pip's cache
# ocrmypdf is explicitly installed as it's a core dependency for your app
RUN pip install --no-cache-dir -r requirements-new.txt ocrmypdf

# Expose the port that your Flask application will listen on
EXPOSE 5000

# Command to run the application using Gunicorn
# Gunicorn is a production-ready WSGI server
# --bind 0.0.0.0:5000 makes the app accessible on port 5000 from outside the container
# app:app specifies the Flask application instance (app object in app.py module)
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
