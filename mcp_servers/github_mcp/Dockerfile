# Use an official Python runtime as a parent image
ARG PYTHON_VERSION=3.11
FROM python:${PYTHON_VERSION}-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV TZ=Etc/UTC
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Install git and other dependencies that might be needed by GitHub tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    ca-certificates \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy project code
# Assuming the official server code will be placed in src/
COPY ./src /app/src

# Create a non-root user
RUN groupadd -r appuser && useradd --no-log-init -r -g appuser appuser
# Optional: Create a directory for secrets if using GITHUB_TOKEN_PATH
RUN mkdir -p /run/secrets && chown appuser:appuser /run/secrets

USER appuser
WORKDIR /app

# Expose port (defaulting to 8000, can be overridden by MCP_PORT env var)
EXPOSE 8000

# Define the command to run the application
# This assumes the entry point is src/main.py and uses uvicorn
# Adjust if the official GitHub MCP server uses a different entry point/runner
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"] 