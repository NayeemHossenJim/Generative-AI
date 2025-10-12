# Use official Python 3.11 slim image for stability
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install system dependencies and Python packages
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && pip install --no-cache-dir -r requirements.txt \
    && apt-get remove -y build-essential \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

# Copy application code
COPY . .

# Create directories for vector stores if they don't exist
RUN mkdir -p chroma_db faiss_index

# Expose FastAPI default port
EXPOSE 8000

# Run FastAPI app with uvicorn
CMD ["uvicorn", "FastAPI:app", "--host", "0.0.0.0", "--port", "8000"]

# Build command: docker build -t pdf-chatbot .
# docker login
# docker push jimaifsd/pdf_chatbot_with_whatsapp_ui:latest
# docker run -p 8000:8000 jimaifsd/pdf_chatbot_with_whatsapp_ui:latest