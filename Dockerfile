# Base image
FROM python:3.11-slim

# Environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Work directory
WORKDIR /app

# System deps (safe minimal)
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
 && rm -rf /var/lib/apt/lists/*

# Copy requirements first (better cache)
COPY requirements.txt .

# Install python deps
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files
COPY . .

# Expose port (Railway auto-detect karta hai but still good)
EXPOSE 5000

# Start Flask app
CMD ["python", "app.py"]
