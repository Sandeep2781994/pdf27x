# Base image with Python
FROM python:3.10-slim

# Install build dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    poppler-utils \
    unpaper \
    wget \
    build-essential \
    libpng-dev \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Ghostscript 10.03.0 from source
RUN wget https://github.com/ArtifexSoftware/ghostpdl-downloads/releases/download/gs10030/ghostscript-10.03.0.tar.gz && \
    tar -xvzf ghostscript-10.03.0.tar.gz && \
    cd ghostscript-10.03.0 && \
    ./configure && \
    make && make install && \
    cd .. && rm -rf ghostscript-10.03.0*

# Set the working directory in the container
WORKDIR /app

# Copy app files to the container
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements-new.txt

# Expose Flask port
EXPOSE 5000

# Run with Gunicorn (production ready)
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
