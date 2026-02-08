# TodoBot Helm Chart

This Helm chart deploys the TodoBot application (Frontend + Backend + Database) on Kubernetes/Minikube.

## Components

- **Frontend**: Next.js application (port 3000)
- **Backend**: FastAPI application (port 8000)
- **Database**: PostgreSQL 15 (port 5432)

## Prerequisites

- Kubernetes cluster (Minikube recommended for local development)
- Helm 3.x installed
- kubectl configured
- Docker images built and available:
  - `todobot-backend:latest`
  - `todobot-frontend:latest`

## Building Docker Images

Before deploying, build your Docker images:

```bash
# Build backend image
cd ../backend
docker build -t todobot-backend:latest .

# Build frontend image
cd ../frontend
docker build -t todobot-frontend:latest .

# If using Minikube, load images into Minikube
minikube image load todobot-backend:latest
minikube image load todobot-frontend:latest
```

## Quick Start

### 1. Install the Chart

```bash
# From the project root directory
helm install todobot ./TodoBot

# Or with custom values
helm install todobot ./TodoBot -f ./TodoBot/values-local.yaml
```

### 2. Check Deployment Status

```bash
# Check pods
kubectl get pods -l "app.kubernetes.io/instance=todobot"

# Wait for pods to be ready
kubectl wait --for=condition=ready pod -l "app.kubernetes.io/instance=todobot" --timeout=300s

# Check services
kubectl get svc -l "app.kubernetes.io/instance=todobot"
```

### 3. Access the Application

#### Frontend (NodePort)

```bash
# Get Minikube IP and access frontend
minikube service todobot-frontend

# Or manually:
minikube ip
# Then open: http://<minikube-ip>:30000
```

#### Backend API

```bash
# Port-forward backend
kubectl port-forward svc/todobot-backend 8000:8000

# Access:
# - Health: http://localhost:8000/health
# - API Docs: http://localhost:8000/docs
# - API: http://localhost:8000/api
```

## Configuration

### Important Values to Update

Before deploying to production, update these values in `values.yaml`:

```yaml
secrets:
  # Generate using: python -c "import secrets; print(secrets.token_hex(32))"
  betterAuthSecret: "your-32-character-secret-here"

  # Your LLM API key (OpenAI, Groq, etc.)
  llmApiKey: "your-llm-api-key-here"

  # Database password
  databasePassword: "strong-password-here"

backend:
  env:
    llmProvider: "openai"
    llmModel: "gpt-4o-mini"
    llmBaseUrl: "https://api.openai.com/v1"
```

### Using Groq (Free Alternative)

```yaml
backend:
  env:
    llmProvider: "openai"
    llmModel: "llama-3.3-70b-versatile"
    llmBaseUrl: "https://api.groq.com/openai/v1"

secrets:
  llmApiKey: "your-groq-api-key"
```

## Managing the Deployment

### Upgrade

```bash
# After updating values.yaml
helm upgrade todobot ./TodoBot

# With specific values file
helm upgrade todobot ./TodoBot -f ./TodoBot/values-local.yaml
```

### Uninstall

```bash
helm uninstall todobot

# If persistence was enabled, also delete PVC
kubectl delete pvc todobot-database-pvc
```

### View Logs

```bash
# Backend logs
kubectl logs -l "app.kubernetes.io/component=backend" -f

# Frontend logs
kubectl logs -l "app.kubernetes.io/component=frontend" -f

# Database logs
kubectl logs -l "app.kubernetes.io/component=database" -f
```

### Debugging

```bash
# Describe pods
kubectl describe pods -l "app.kubernetes.io/instance=todobot"

# Get events
kubectl get events --sort-by='.lastTimestamp'

# Shell into backend pod
kubectl exec -it deployment/todobot-backend -- /bin/sh

# Shell into database pod
kubectl exec -it deployment/todobot-database -- psql -U user -d chatdb
```

## Architecture

```
┌─────────────────┐
│   Frontend      │  (NodePort 30000)
│   (Next.js)     │
└────────┬────────┘
         │
         │ HTTP
         ▼
┌─────────────────┐
│   Backend       │  (ClusterIP 8000)
│   (FastAPI)     │
└────────┬────────┘
         │
         │ PostgreSQL
         ▼
┌─────────────────┐
│   Database      │  (ClusterIP 5432)
│   (PostgreSQL)  │
└─────────────────┘
```

## Persistence

By default, database persistence is **enabled** with a 1Gi PVC.

To disable persistence (data will be lost on pod restart):

```yaml
database:
  persistence:
    enabled: false
```

## Resource Limits

Default resource limits are set for local development. Adjust based on your needs:

```yaml
backend:
  resources:
    limits:
      cpu: "1000m"
      memory: "1Gi"
    requests:
      cpu: "500m"
      memory: "256Mi"

frontend:
  resources:
    limits:
      cpu: "2000m"
      memory: "2Gi"
    requests:
      cpu: "1000m"
      memory: "512Mi"

database:
  resources:
    limits:
      cpu: "500m"
      memory: "512Mi"
    requests:
      cpu: "250m"
      memory: "256Mi"
```

## Troubleshooting

### Pods stuck in Pending

```bash
kubectl describe pods -l "app.kubernetes.io/instance=todobot"
# Check events for resource constraints
```

### ImagePullBackOff

```bash
# Make sure images are loaded in Minikube
minikube image ls | grep todobot

# Reload images if needed
minikube image load todobot-backend:latest
minikube image load todobot-frontend:latest
```

### Database Connection Issues

```bash
# Check database pod is running
kubectl get pods -l "app.kubernetes.io/component=database"

# Check database logs
kubectl logs -l "app.kubernetes.io/component=database"

# Test database connection from backend
kubectl exec -it deployment/todobot-backend -- curl todobot-database:5432
```

### Frontend can't connect to Backend

Check the ConfigMap has the correct API URL:

```bash
kubectl get configmap todobot-config -o yaml
```

## Support

For issues and questions:
- Check logs: `kubectl logs -l "app.kubernetes.io/instance=todobot" --all-containers`
- Review events: `kubectl get events --sort-by='.lastTimestamp'`
- Describe resources: `kubectl describe all -l "app.kubernetes.io/instance=todobot"`

## License

MIT
