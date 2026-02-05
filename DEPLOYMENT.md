# Deployment Guide

This document provides instructions for deploying the application using Docker and Docker Compose.

## Prerequisites

- Docker Engine (version 20.10 or higher)
- Docker Compose (version 2.0 or higher)
- Access to a PostgreSQL database (for production)
- LLM API key (OpenAI or compatible provider)

## Environment Variables

Before deployment, create the necessary environment files:

### Backend (.env)

Create `backend/.env` with the following variables:

```bash
# Database configuration
DATABASE_URL=postgresql+asyncpg://username:password@host:5432/database_name

# LLM Configuration
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o
LLM_API_KEY=your_openai_api_key_here
LLM_BASE_URL=  # Leave empty for OpenAI, specify for other providers

# Server configuration
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
LOG_LEVEL=INFO
```

### Frontend (.env.local)

Create `frontend/.env.local` with the following variables:

```bash
NEXT_PUBLIC_API_URL=https://your-domain.com/api
BETTER_AUTH_SECRET=your-production-auth-secret-here
BETTER_AUTH_URL=https://your-domain.com
```

## Docker Deployment

### Development Deployment

To run the application in development mode:

```bash
# From the project root
docker-compose up --build
```

The services will be available at:
- Backend API: http://localhost:8000
- Frontend: http://localhost:3000

### Production Deployment

For production deployment, use the production compose file:

```bash
# Build and start services
docker-compose -f docker-compose.prod.yml up --build -d

# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Stop services
docker-compose -f docker-compose.prod.yml down
```

## Deployment to Cloud Platforms

### Deploy to AWS ECS

1. Build and push images to ECR:
```bash
aws ecr get-login-password --region your-region | docker login --username AWS --password-stdin your-account-id.dkr.ecr.your-region.amazonaws.com

docker build -t your-app-backend ./backend
docker tag your-app-backend:latest your-account-id.dkr.ecr.your-region.amazonaws.com/your-app-backend:latest
docker push your-account-id.dkr.ecr.your-region.amazonaws.com/your-app-backend:latest
```

2. Update docker-compose.prod.yml to use your ECR images and deploy using AWS Copilot or ECS CLI.

### Deploy to Google Cloud Run

1. Build container images:
```bash
gcloud builds submit --tag gcr.io/PROJECT-ID/backend ./backend
gcloud builds submit --tag gcr.io/PROJECT-ID/frontend ./frontend
```

2. Deploy services:
```bash
gcloud run deploy backend --image gcr.io/PROJECT-ID/backend --platform managed --port 8000 --set-env-vars="DATABASE_URL=..."
gcloud run deploy frontend --image gcr.io/PROJECT-ID/frontend --platform managed --port 3000 --set-env-vars="NEXT_PUBLIC_API_URL=..."
```

### Deploy to Azure Container Apps

1. Create container apps environment:
```bash
az containerapp env create --name my-environment --resource-group my-resource-group --location eastus
```

2. Deploy containers using the Azure CLI.

## Configuration for Different Environments

### Database Setup

For production, ensure your database is properly configured:

1. Set up PostgreSQL with appropriate user permissions
2. Configure connection pooling if needed
3. Set up backup and monitoring

### SSL/TLS Configuration

For production deployments, configure SSL/TLS:

1. Use a reverse proxy like nginx with SSL termination
2. Or configure SSL directly in your cloud platform
3. Update API URLs to use HTTPS

### Health Checks

The application includes health checks:
- Backend: `GET /health` endpoint
- Docker health check configured in Dockerfile

## Scaling

### Horizontal Scaling

Both backend and frontend can be scaled horizontally:

```bash
# Scale backend to 3 instances
docker-compose up --scale backend=3

# Scale frontend to 2 instances
docker-compose up --scale frontend=2
```

### Load Balancing

Configure load balancing at the infrastructure level or use cloud load balancers.

## Monitoring and Logging

### Docker Logs

Access application logs:
```bash
docker-compose logs backend
docker-compose logs frontend
```

### Structured Logging

The backend uses structured logging with configurable log levels.

## Backup and Recovery

### Database Backups

Regular database backups are essential for production environments:
```bash
# Example backup command
pg_dump --dbname=postgresql+asyncpg://username:password@host:5432/database_name > backup.sql
```

## Troubleshooting

### Common Issues

1. **Database Connection Issues**
   - Verify DATABASE_URL is correctly configured
   - Check network connectivity to database
   - Ensure database user has proper permissions

2. **LLM API Issues**
   - Verify LLM_API_KEY is correct
   - Check rate limits with your provider
   - Ensure proper network access to LLM provider

3. **Frontend-Backend Communication**
   - Verify NEXT_PUBLIC_API_URL is correctly set
   - Check CORS configuration in backend

### Debugging Commands

```bash
# Check running containers
docker-compose ps

# Check container logs
docker-compose logs [service-name]

# Execute commands in running container
docker-compose exec backend bash
docker-compose exec frontend bash
```

## Security Considerations

1. **Secrets Management**
   - Never commit secrets to version control
   - Use environment variables or secret management systems
   - Rotate secrets regularly

2. **Network Security**
   - Use private networks for internal communication
   - Implement proper firewall rules
   - Use SSL/TLS for all communications

3. **Container Security**
   - Run containers as non-root users
   - Keep base images updated
   - Scan images for vulnerabilities