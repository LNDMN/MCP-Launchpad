FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    MEMORY_STORAGE_PORT=8000 \
    MEMORY_STORAGE_DATA_DIR=/data \
    MEMORY_STORAGE_LOG_LEVEL=INFO \
    MEMORY_STORAGE_BACKUP_INTERVAL=60 \
    MEMORY_STORAGE_AUTH_ENABLED=false \
    MEMORY_STORAGE_AUTH_KEY=""

# Set working directory
WORKDIR /app

# Create data directory
RUN mkdir -p /data

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create a non-root user and change ownership
RUN useradd -m appuser && \
    chown -R appuser:appuser /app /data

# Switch to non-root user
USER appuser

# Expose the port
EXPOSE ${MEMORY_STORAGE_PORT}

# Start the application
CMD ["python", "app.py"] 