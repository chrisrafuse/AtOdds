FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements-web.txt .
RUN pip install --no-cache-dir -r requirements-web.txt

# Copy application code
COPY . .

# Expose default port (Railway overrides via $PORT)
EXPOSE 8000

# Use exec form so SIGTERM is handled correctly
CMD ["python", "-m", "apps.web.run_api"]
