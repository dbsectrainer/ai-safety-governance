# Production image for the FastAPI backend.
# Python 3.12 matches the version used in CI; the previous 3.8 image is EOL.
FROM python:3.12-slim

WORKDIR /app

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install only runtime system dependencies and clean apt lists in the same layer.
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy requirements first for better layer caching
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Make start script executable and give the unprivileged user ownership of the
# writable runtime directories (SQLite fallback, compliance reports, tmp).
RUN chmod +x /app/src/start.sh \
    && mkdir -p /app/compliance_logs \
    && chown -R appuser:appuser /app

USER appuser

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD curl -fsS http://localhost:5000/health || exit 1

EXPOSE 5000

CMD ["/app/src/start.sh"]
