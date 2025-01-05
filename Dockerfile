# Use Python 3.9 instead of 3.8
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy requirements first
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy everything else
COPY . .

# Create a directory for environment files
RUN mkdir -p /app/env

# Command to run when starting the container
CMD ["python", "main.py"]