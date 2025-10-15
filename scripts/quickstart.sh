#!/bin/bash
# Quick start script for first-time setup

echo "🥗 Nutrition Tracker - Quick Start"
echo "=================================="

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Please install Docker first."
    exit 1
fi

echo "✅ Docker found"

# Check docker-compose
if ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose not found. Please install Docker Compose."
    exit 1
fi

echo "✅ Docker Compose found"

# Create directories
echo "📁 Creating directories..."
mkdir -p data logs backups

# Copy env file if not exists
if [ ! -f .env ]; then
    echo "📝 Creating .env from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your configuration!"
fi

# Build and start
echo "🏗️  Building and starting containers..."
docker compose up -d --build

# Wait for app to start
echo "⏳ Waiting for application to start..."
sleep 10

# Health check
if curl -sf http://localhost:5000/health > /dev/null; then
    echo ""
    echo "✅ Application is running!"
    echo "🌐 Open http://localhost:5000 in your browser"
    echo ""
    echo "📚 Useful commands:"
    echo "  make logs      - View logs"
    echo "  make down      - Stop application"
    echo "  make backup    - Create backup"
    echo "  make health    - Check health"
else
    echo ""
    echo "⚠️  Application started but health check failed"
    echo "Check logs with: docker compose logs"
fi
