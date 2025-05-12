# Use an official Python runtime as a parent image
ARG PYTHON_VERSION=3.11
FROM python:${PYTHON_VERSION}-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV TZ=Etc/UTC
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Install system dependencies (if any - usually not needed for basic filesystem ops)
# RUN apt-get update && apt-get install -y --no-install-recommends \
#     some-dependency \
#     && apt-get clean \
#     && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy project code
COPY ./src /app/src
# COPY ./config /app/config # If config files exist

# Create a non-root user and group
RUN groupadd -r appuser && useradd --no-log-init -r -g appuser appuser

# Create a default directory for data mount point and set permissions
# This directory will be targeted by ALLOWED_PATHS by default
RUN mkdir /data && chown appuser:appuser /data

# Switch to non-root user
USER appuser

# Change workdir ownership (after user creation)
# WORKDIR /app # Already set, ensure ownership if needed (might not be necessary)
# RUN chown appuser:appuser /app # Careful with this, might break things if not done right

# Expose port
EXPOSE 8000

# Define the command to run the application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"] 