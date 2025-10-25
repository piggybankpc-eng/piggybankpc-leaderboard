# PiggyBankPC Leaderboard - Production Dockerfile
# Multi-stage build for optimized and secure deployment

FROM python:3.11-slim as builder

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Final production stage
FROM python:3.11-slim

# Install runtime dependencies only (curl for health checks)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Create non-root user for security
RUN groupadd -r piggybank && useradd -r -g piggybank -u 1000 piggybank

# Create app directory
WORKDIR /app

# Copy application files with correct ownership
COPY --chown=piggybank:piggybank . .

# Create necessary directories with correct permissions
RUN mkdir -p /app/instance /app/uploads /app/logs && \
    chown -R piggybank:piggybank /app/instance /app/uploads /app/logs

# Set environment variables
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Switch to non-root user
USER piggybank

# Expose port
EXPOSE 5555

# Health check for container monitoring
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:5555/health || exit 1

# Run with Gunicorn (production WSGI server)
CMD ["gunicorn", \
     "--bind", "0.0.0.0:5555", \
     "--workers", "4", \
     "--threads", "2", \
     "--worker-class", "sync", \
     "--worker-tmp-dir", "/dev/shm", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "--log-level", "info", \
     "--timeout", "120", \
     "app:app"]
