#!/bin/bash
# Luminaire Detection - Simple Start Script

echo "=== Starting Luminaire Detection ==="
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "Error: Docker is not running"
    exit 1
fi

# Check if image exists
if ! docker images | grep -q "luminaire-detection"; then
    echo "Error: luminaire-detection image not found"
    echo "Please build the image first"
    exit 1
fi

# Start using docker-compose
echo "Starting service..."
docker-compose up -d

echo ""
echo "Waiting for service to start..."
sleep 5

# Check status
if docker ps | grep -q "luminaire-detection"; then
    echo ""
    echo "✓ Service started successfully!"
    echo ""
    echo "Access the application at:"
    echo "  http://localhost:7860"
    echo "  http://$(hostname -I | awk '{print $1}'):7860"
    echo ""
    echo "View logs: docker-compose logs -f"
    echo "Stop service: docker-compose down"
else
    echo ""
    echo "✗ Service failed to start"
    echo "Check logs: docker-compose logs"
fi
