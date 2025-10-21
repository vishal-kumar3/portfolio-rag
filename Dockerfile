# Use Python 3.12 slim as base image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv and tomli
RUN pip install uv tomli

# Copy the application first
COPY . .

# Clean Python cache files
RUN find . -type d -name __pycache__ -exec rm -r {} +

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Create log directory and set permissions
RUN mkdir -p /app/logs && \
    touch /app/app.log && \
    chmod 777 /app/app.log && \
    mkdir -p vector_store/chroma_db && \
    chmod -R 777 vector_store

# Install dependencies
RUN uv pip install --system langchain-core>=0.1.27 && \
    uv pip install --system .

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
