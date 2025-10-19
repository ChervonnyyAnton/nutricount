# Multi-stage build optimized for Raspberry Pi 4 Model B 2018 ARM64
# Raspberry Pi OS Lite 64-bit optimized
FROM python:3.11-slim as builder

# Set environment variables for optimization
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install build dependencies optimized for ARM64
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    libffi-dev \
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

# Install runtime dependencies optimized for Raspberry Pi OS Lite 64-bit
RUN apt-get update && apt-get install -y \
    sqlite3 \
    curl \
    ca-certificates \
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

# Switch to non-root user before initializing database
USER appuser

# Initialize database as appuser
RUN python init_db.py

# Expose port
EXPOSE 5000

# Health check optimized for Pi 4 Model B 2018 ARM64
HEALTHCHECK --interval=30s --timeout=10s --start-period=20s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Run application with Pi 4 Model B 2018 ARM64 optimized settings
CMD ["gunicorn", "--config", "gunicorn.conf.py", "app:app"]
