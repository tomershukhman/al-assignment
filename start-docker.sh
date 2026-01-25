#!/bin/bash

# Math Solving Assistant - Docker Startup Script
# This script spins up the entire environment (backend + frontend)

set -e  # Exit on error

echo "🚀 Starting Math Solving Assistant..."
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found!"
    echo "📝 Please create a .env file with your API keys."
    echo "   You can copy .env.example and fill in your keys:"
    echo "   cp .env.example .env"
    exit 1
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker is not running!"
    echo "   Please start Docker Desktop and try again."
    exit 1
fi

# Stop existing containers if running
echo "🛑 Stopping existing containers..."
docker-compose down 2>/dev/null || true

# Build and start services
echo ""
echo "🏗️  Building Docker images..."
docker-compose build

echo ""
echo "🎬 Starting services..."
docker-compose up -d

echo ""
echo "⏳ Waiting for services to be healthy..."
sleep 5

# Wait for backend health check
echo "   Checking backend..."
timeout=60
elapsed=0
while [ $elapsed -lt $timeout ]; do
    if docker-compose ps | grep -q "backend.*healthy"; then
        echo "   ✅ Backend is ready!"
        break
    fi
    sleep 2
    elapsed=$((elapsed + 2))
done

# Wait for frontend health check
echo "   Checking frontend..."
timeout=30
elapsed=0
while [ $elapsed -lt $timeout ]; do
    if docker-compose ps | grep -q "frontend.*healthy"; then
        echo "   ✅ Frontend is ready!"
        break
    fi
    sleep 2
    elapsed=$((elapsed + 2))
done

echo ""
echo "✨ Math Solving Assistant is now running!"
echo ""
echo "📱 Access the application:"
echo "   Frontend:  http://localhost:3000"
echo "   Backend:   http://localhost:8000"
echo "   API Docs:  http://localhost:8000/docs"
echo ""
echo "📋 Useful commands:"
echo "   View logs:        docker-compose logs -f"
echo "   Stop services:    docker-compose down"
echo "   Restart:          docker-compose restart"
echo ""
