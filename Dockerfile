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

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies from pyproject.toml
RUN uv pip install --system $(python3 -c 'import tomli; print(" ".join(tomli.load(open("pyproject.toml", "rb"))["project"]["dependencies"]))')

# Copy the rest of the application
COPY app/ app/
COPY script/ script/

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
