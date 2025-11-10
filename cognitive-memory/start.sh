#!/bin/bash

# Cognitive Memory System - Quick Start Script

set -e

echo "🧠 Cognitive Memory System - Quick Start"
echo "========================================"
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

echo "✓ Docker is running"

# Check if .env exists, if not create from example
if [ ! -f .env ]; then
    echo "Creating .env file from .env.example..."
    cp .env.example .env
    echo "✓ .env file created"
else
    echo "✓ .env file exists"
fi

# Stop existing containers
echo ""
echo "Stopping existing containers..."
docker-compose down > /dev/null 2>&1 || true

# Build and start services
echo ""
echo "Building and starting services..."
docker-compose up --build -d

# Wait for services to be healthy
echo ""
echo "Waiting for services to be healthy..."
sleep 5

# Check health
echo ""
echo "Checking service health..."

# Check PostgreSQL
if docker exec memory_db pg_isready -U intelligence > /dev/null 2>&1; then
    echo "✓ PostgreSQL is ready"
else
    echo "⚠ PostgreSQL is not ready yet"
fi

# Check API
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✓ API is responding"
else
    echo "⚠ API is starting up..."
    sleep 5
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "✓ API is now ready"
    else
        echo "❌ API failed to start. Check logs with: docker-compose logs app"
    fi
fi

echo ""
echo "========================================"
echo "🚀 Cognitive Memory System is running!"
echo "========================================"
echo ""
echo "API Documentation: http://localhost:8000/docs"
echo "API Health:        http://localhost:8000/health"
echo "PostgreSQL:        localhost:5432"
echo "Redis:             localhost:6379"
echo ""
echo "View logs:         docker-compose logs -f"
echo "Stop services:     docker-compose down"
echo ""
echo "Test the API:"
echo 'curl -X POST http://localhost:8000/process \\'
echo '  -H "Content-Type: application/json" \\'
echo '  -d '"'"'{"context": "optimize database", "decision": "add index"}'"'"
echo ""
