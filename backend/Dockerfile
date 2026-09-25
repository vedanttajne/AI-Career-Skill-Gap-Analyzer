FROM python:3.12-slim

# Install Tesseract OCR and required system libraries
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libglib2.0-0 \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy backend files from repository root
COPY backend/requirements.txt /app/requirements.txt
COPY backend /app

# Install Python dependencies
RUN pip install --no-cache-dir -r /app/requirements.txt

# Start FastAPI
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}