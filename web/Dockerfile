# ADES Validation Web Service Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies for lxml
RUN apt-get update && apt-get install -y \
    build-essential \
    libxml2-dev \
    libxslt-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY web/requirements.txt ./web-requirements.txt
COPY Python/requirements.txt ./ades-requirements.txt
RUN pip install --no-cache-dir -r ades-requirements.txt -r web-requirements.txt

# Copy the ADES-Master project files needed for the web service
COPY Python/ ./Python/
COPY xml/ ./xml/
COPY xslt/ ./xslt/
COPY web/ ./web/

# Create a non-root user
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/ || exit 1

# Run the application
CMD ["python", "web/app.py"]