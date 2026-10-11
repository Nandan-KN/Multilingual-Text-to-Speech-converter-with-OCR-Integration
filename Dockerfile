# Production Dockerfile for Multilingual Vision Voice Canvas
FROM python:3.12-slim

# Set non-interactive debian frontend
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# Install system dependencies & Tesseract OCR with Indic language packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-eng \
    tesseract-ocr-hin \
    tesseract-ocr-tel \
    tesseract-ocr-kan \
    tesseract-ocr-osd \
    libgl1 \
    libglib2.0-0 \
    curl \
    fonts-indic \
    fonts-deva \
    fonts-telu \
    fonts-knda \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy dependency specifications and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Expose ports for both Gradio (7860) and Streamlit (8501)
EXPOSE 7860
EXPOSE 8501

# Default command launches the Flashy Gradio interface
CMD ["python", "gradio_app.py"]
