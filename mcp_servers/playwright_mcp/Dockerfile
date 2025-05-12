# Use an official Python runtime as a parent image
ARG PYTHON_VERSION=3.11
FROM python:${PYTHON_VERSION}-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
# Set timezone to avoid interactive prompts
ENV TZ=Etc/UTC
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Install system dependencies required by Playwright and browsers
RUN apt-get update && apt-get install -y --no-install-recommends \\\
    # Playwright dependencies\n    libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 libgbm1 libatspi2.0-0 libxkbcommon0 libx11-xcb1 libxcb-dri3-0 libxcomposite1 libxdamage1 libxext6 libxfixes3 libxrandr2 libxtst6 curl wget \\\
    # Other useful tools\n    ca-certificates fonts-liberation \\\
    # Clean up\n    && apt-get clean \\\
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers
# RUN playwright install --with-deps # This installs browsers & OS dependencies. Dependencies installed above.
RUN playwright install chromium # Or specify other browsers like firefox, webkit

# Copy project code
COPY ./src /app/src
# If config files exist, copy them too
# COPY ./config /app/config

# Expose port (adjust if the app uses a different port)
EXPOSE 8000

# Define the command to run the application (assuming FastAPI with uvicorn)
# Adjust 'src.main:app' to your actual application entry point
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"] 