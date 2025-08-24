# Multi-stage Dockerfile for Forensic Reconciliation Platform
# Stage 1: Base Python environment
FROM python:3.11-slim-bullseye as base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    gcc \
    g++ \
    libpq-dev \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Create app user
RUN groupadd -r appuser && useradd -r -g appuser appuser

    # Stage 2: Dependencies
    FROM base as dependencies
    
    # Copy requirements first for better caching
    COPY requirements-minimal.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Stage 3: Development (for testing and debugging)
FROM dependencies as development

# Install development dependencies
RUN pip install --no-cache-dir pytest pytest-cov black flake8 mypy

# Copy source code
COPY . /app/
WORKDIR /app

# Change ownership to app user
RUN chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Default command
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

# Stage 4: Production
FROM dependencies as production

# Copy only necessary source code
COPY . /app/
WORKDIR /app

# Remove development files and caches
RUN find /app -type d -name "__pycache__" -exec rm -rf {} + && \
    find /app -type f -name "*.pyc" -delete && \
    find /app -type f -name "*.pyo" -delete && \
    find /app -type f -name "*.pyd" -delete && \
    find /app -type f -name ".coverage" -delete && \
    find /app -type d -name ".pytest_cache" -exec rm -rf {} + && \
    find /app -type d -name ".mypy_cache" -exec rm -rf {} + && \
    find /app -type d -name ".git" -exec rm -rf {} + && \
    find /app -type f -name "*.md" -delete && \
    find /app -type f -name "*.txt" ! -name "requirements.txt" -delete

# Create necessary directories
RUN mkdir -p /app/uploads /app/reports /app/logs

# Change ownership to app user
RUN chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Default command
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]

    # Stage 5: Cache (for build optimization)
    FROM base as cache
    COPY requirements-minimal.txt ./
    RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
        pip install --no-cache-dir -r requirements-minimal.txt
