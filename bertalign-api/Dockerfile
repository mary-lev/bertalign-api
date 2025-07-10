# Use Python slim base for smaller image size
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies needed for building packages
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better Docker layer caching
COPY requirements-api.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --default-timeout=120 -r requirements-api.txt

# Pre-download the LaBSE model during build time to avoid cold start delays
# RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('LaBSE')"

# Copy application code
COPY . .

# Create non-root user for security
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port 8080 (Cloud Run default)
EXPOSE 8080

# Command to run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]