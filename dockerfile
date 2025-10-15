# Multi-stage build for smaller final image
FROM python:3.11-slim as builder

# Set environment variables for optimization
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Final stage
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/opt/venv/bin:$PATH"

# Install runtime dependencies only
RUN apt-get update && apt-get install -y \
    sqlite3 \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv

# Create app user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Set working directory
WORKDIR /usr/src/app

# Copy application code
COPY . .

# Create directories with proper permissions
RUN mkdir -p data logs backups \
    && chown -R appuser:appuser /usr/src/app

# Initialize database
RUN python init_db.py

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 5000

# Health check optimized for Pi Zero 2W
HEALTHCHECK --interval=60s --timeout=15s --start-period=30s --retries=2 \
    CMD curl -f http://localhost:5000/health || exit 1

# Run application with Pi Zero 2W optimized settings
CMD ["gunicorn", "--config", "gunicorn.conf.py", "app:app"]
