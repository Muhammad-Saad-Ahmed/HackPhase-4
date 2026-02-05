#!/bin/bash
# Deployment script for the Chat Agent Connector application

set -e  # Exit on any error

echo "🚀 Starting deployment of Chat Agent Connector..."

# Check if Docker is installed
if ! [ -x "$(command -v docker)" ]; then
  echo "❌ Docker is not installed. Please install Docker first."
  exit 1
fi

# Check if Docker Compose is installed
if ! [ -x "$(command -v docker-compose)" ]; then
  echo "⚠️  Docker Compose is not installed. Trying docker compose (newer versions)..."
  if ! [ -x "$(command -v docker compose)" ]; then
    echo "❌ Neither docker-compose nor docker compose is available."
    exit 1
  fi
  COMPOSE_CMD="docker compose"
else
  COMPOSE_CMD="docker-compose"
fi

# Check for environment files
if [ ! -f "./backend/.env" ]; then
  echo "⚠️  Warning: backend/.env file not found. Creating a sample file..."
  cat > ./backend/.env << EOF
# Database configuration
DATABASE_URL=postgresql+asyncpg://username:password@localhost:5432/chatdb

# LLM Configuration
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o
LLM_API_KEY=your_openai_api_key_here

# Server configuration
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
LOG_LEVEL=INFO
EOF
  echo "Created sample backend/.env file. Please update with your actual values."
fi

if [ ! -f "./frontend/.env.local" ]; then
  echo "⚠️  Warning: frontend/.env.local file not found. Creating a sample file..."
  cat > ./frontend/.env.local << EOF
NEXT_PUBLIC_API_URL=http://localhost:8000/api
BETTER_AUTH_SECRET=dev-secret-key-minimum-32-characters-long-for-development
BETTER_AUTH_URL=http://localhost:3000
EOF
  echo "Created sample frontend/.env.local file. Please update with your actual values."
fi

echo "🔧 Building and starting services..."
$COMPOSE_CMD up --build -d

echo "⏳ Waiting for services to start (this may take a minute)..."
sleep 30

echo "🔍 Checking service status..."
$COMPOSE_CMD ps

echo "✅ Deployment completed!"
echo ""
echo "Services are now running:"
echo "  - Backend API: http://localhost:8000"
echo "  - Health check: http://localhost:8000/health"
echo "  - Frontend: http://localhost:3000"
echo ""
echo "To view logs: $COMPOSE_CMD logs -f"
echo "To stop services: $COMPOSE_CMD down"