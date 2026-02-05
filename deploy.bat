@echo off
REM Deployment batch script for the Chat Agent Connector application

echo 🚀 Starting deployment of Chat Agent Connector...

REM Check if Docker is installed
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not installed or not in PATH. Please install Docker Desktop.
    exit /b 1
)

REM Check if Docker Compose is available
docker compose version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker Compose is not available.
    exit /b 1
)

REM Check for environment files
if not exist "backend\.env" (
    echo ⚠️  Warning: backend/.env file not found. Creating a sample file...
    echo # Database configuration > backend\.env
    echo DATABASE_URL=postgresql+asyncpg://username:password@localhost:5432/chatdb >> backend\.env
    echo. >> backend\.env
    echo # LLM Configuration >> backend\.env
    echo LLM_PROVIDER=openai >> backend\.env
    echo LLM_MODEL=gpt-4o >> backend\.env
    echo LLM_API_KEY=your_openai_api_key_here >> backend\.env
    echo. >> backend\.env
    echo # Server configuration >> backend\.env
    echo SERVER_HOST=0.0.0.0 >> backend\.env
    echo SERVER_PORT=8000 >> backend\.env
    echo LOG_LEVEL=INFO >> backend\.env
    echo Created sample backend/.env file. Please update with your actual values.
)

if not exist "frontend\.env.local" (
    echo ⚠️  Warning: frontend/.env.local file not found. Creating a sample file...
    echo NEXT_PUBLIC_API_URL=http://localhost:8000/api > frontend\.env.local
    echo BETTER_AUTH_SECRET=dev-secret-key-minimum-32-characters-long-for-development >> frontend\.env.local
    echo BETTER_AUTH_URL=http://localhost:3000 >> frontend\.env.local
    echo Created sample frontend/.env.local file. Please update with your actual values.
)

echo 🔧 Building and starting services...
docker compose up --build -d

echo ⏳ Waiting for services to start ^(this may take a minute^)...
timeout /t 30 /nobreak >nul

echo 🔍 Checking service status...
docker compose ps

echo ✅ Deployment completed!
echo.
echo Services are now running:
echo   - Backend API: http://localhost:8000
echo   - Health check: http://localhost:8000/health
echo   - Frontend: http://localhost:3000
echo.
echo To view logs: docker compose logs -f
echo To stop services: docker compose down