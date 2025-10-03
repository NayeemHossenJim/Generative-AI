# Use Python 3.10 base image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies required for some Python packages
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code and necessary files
COPY app.py .
COPY .env .
COPY PDF/ ./PDF/

# Create directories for vector stores
RUN mkdir -p faiss_index chroma_db

# Expose the Streamlit port
EXPOSE 8501

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Command to run Streamlit application
CMD ["streamlit", "run", "app.py", "--server.address", "0.0.0.0", "--server.port", "8501"]