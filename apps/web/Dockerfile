# Dockerfile for AtOdds API
# Phase 6: Multi-stage build for production deployment

# Build stage
FROM python:3.9-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt requirements-web.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir --user -r requirements.txt -r requirements-web.txt

# Runtime stage
FROM python:3.9-slim

WORKDIR /app

# Copy Python dependencies from builder
COPY --from=builder /root/.local /root/.local

# Copy application code
COPY packages/ ./packages/
COPY apps/web/ ./apps/web/
COPY data/ ./data/

# Make sure scripts are executable
RUN chmod +x apps/web/run_api.py

# Set Python path
ENV PATH=/root/.local/bin:$PATH
ENV PYTHONPATH=/app

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Run the application
CMD ["python", "apps/web/run_api.py"]
