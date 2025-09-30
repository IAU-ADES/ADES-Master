#!/bin/bash
# Build script for ADES Validation Docker image

set -e

echo "Building ADES Validation Docker image..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "Warning: Docker Compose is not installed. You can still use 'docker build' and 'docker run' manually."
fi

# Build the image
docker build -f web/Dockerfile -t ades-validation .

echo "Build completed successfully!"
echo ""
echo "To run the service:"
echo "  docker run -p 8000:8000 ades-validation"
echo ""
echo "Or using Docker Compose:"
echo "  cd web && docker-compose up"