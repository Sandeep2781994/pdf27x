# Base image
FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    gcc \
    make \
    build-essential \
    libjpeg-dev \
    zlib1g-dev \
    libtiff-dev \
    libpng-dev \
    libfreetype6-dev \
    libgs-dev \
    ghostscript \
    tesseract-ocr \
    poppler-utils \
    qpdf \
    git \
    && rm -rf /var/lib/apt/lists/*

# Upgrade Ghostscript to latest (10.03.0+)
RUN curl -L https://github.com/ArtifexSoftware/ghostpdl-downloads/releases/download/gs10030/ghostscript-10.03.0.tar.gz -o gs.tar.gz \
    && tar -xvzf gs.tar.gz \
    && cd ghostscript-10.03.0 \
    && ./configure \
    && make -j"$(nproc)" \
    && make install \
    && cd .. && rm -rf ghostscript-10.03.0 gs.tar.gz

# Verify version
RUN gs --version  # should show 10.03.0

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app files
COPY . /app
WORKDIR /app

# Run with Gunicorn (production ready)
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
