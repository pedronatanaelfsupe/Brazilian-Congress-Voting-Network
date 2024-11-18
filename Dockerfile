# Dockerfile

# Use the official Python image
FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    python3-dev \
    libigraph-dev \
    libcairo2 \
    libjpeg-dev \
    libpng-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy the requirements file
COPY requirements.txt .

# Install wheel
RUN pip install --no-cache-dir wheel

# Install numpy first
RUN pip install --no-cache-dir numpy==1.21.4

# Install the rest of the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the project code
COPY depcom/ ./depcom/
COPY data/ ./data/

# Set the entry point
CMD ["python", "depcom/src/main.py"]
