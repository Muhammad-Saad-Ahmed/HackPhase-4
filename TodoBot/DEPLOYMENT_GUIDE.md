# TodoBot Kubernetes Deployment Guide

Complete guide for deploying TodoBot to Kubernetes (Minikube) using Helm.

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Start](#quick-start)
3. [Manual Deployment](#manual-deployment)
4. [Configuration](#configuration)
5. [Accessing the Application](#accessing-the-application)
6. [Monitoring & Troubleshooting](#monitoring--troubleshooting)
7. [Maintenance](#maintenance)

## Prerequisites

### Required Tools

- **Minikube** (or any Kubernetes cluster)
  ```bash
  # Install Minikube
  # Windows (PowerShell as Administrator):
  choco install minikube

  # macOS:
  brew install minikube

  # Linux:
  curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
  sudo install minikube-linux-amd64 /usr/local/bin/minikube
  ```

- **kubectl** (Kubernetes CLI)
  ```bash
  # Verify installation
  kubectl version --client
  ```

- **Helm 3.x**
  ```bash
  # Install Helm
  # Windows:
  choco install kubernetes-helm

  # macOS:
  brew install helm

  # Linux:
  curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
  ```

- **Docker** (for building images)
  ```bash
  docker --version
  ```

### Start Minikube

```bash
# Start Minikube with recommended resources
minikube start --cpus=4 --memory=8192 --disk-size=20g

# Verify Minikube is running
minikube status

# Enable metrics (optional)
minikube addons enable metrics-server
```

## Quick Start

### Option 1: Automated Deployment (Recommended)

**Windows (PowerShell):**
```powershell
cd TodoBot
.\deploy.ps1
```

**Linux/macOS:**
```bash
cd TodoBot
chmod +x deploy.sh
./deploy.sh
```

The script will:
1. Check prerequisites
2. Build Docker images
3. Load images into Minikube
4. Deploy with Helm
5. Wait for pods to be ready
6. Display access URLs

### Option 2: Quick Manual Deployment

```bash
# 1. Build and load images
cd backend
docker build -t todobot-backend:latest .
minikube image load todobot-backend:latest

cd ../frontend
docker build -t todobot-frontend:latest .
minikube image load todobot-frontend:latest

# 2. Deploy with Helm
cd ../TodoBot
helm install todobot . -f values-local.yaml

# 3. Wait for pods
kubectl wait --for=condition=ready pod -l "app.kubernetes.io/instance=todobot" --timeout=300s

# 4. Access frontend
minikube service todobot-frontend
```

## Manual Deployment

### Step 1: Configure Values

Edit `values-local.yaml` and update:

```yaml
secrets:
  # REQUIRED: Your LLM API key
  llmApiKey: "sk-..."  # OpenAI, Groq, etc.

  # Generate a secure secret (32+ characters)
  betterAuthSecret: "your-secure-secret-here"

  # Database password
  databasePassword: "your-db-password"

backend:
  env:
    llmProvider: "openai"  # or "anthropic", "groq"
    llmModel: "gpt-4o-mini"
    llmBaseUrl: "https://api.openai.com/v1"
```

**Generate Better Auth Secret:**
```bash
# Using Python
python -c "import secrets; print(secrets.token_hex(32))"

# Using OpenSSL
openssl rand -hex 32
```

### Step 2: Build Docker Images

```bash
# Backend
cd ../backend
docker build -t todobot-backend:latest .

# Frontend
cd ../frontend
docker build -t todobot-frontend:latest --build-arg NEXT_PUBLIC_API_URL=http://todobot-backend:8000/api .

# Return to TodoBot directory
cd ../TodoBot
```

### Step 3: Load Images into Minikube

```bash
minikube image load todobot-backend:latest
minikube image load todobot-frontend:latest

# Verify images are loaded
minikube image ls | grep todobot
```

### Step 4: Deploy with Helm

```bash
# Install
helm install todobot . -f values-local.yaml

# Or upgrade if already installed
helm upgrade todobot . -f values-local.yaml
```

### Step 5: Verify Deployment

```bash
# Check pods
kubectl get pods -l "app.kubernetes.io/instance=todobot"

# Check services
kubectl get svc -l "app.kubernetes.io/instance=todobot"

# Run verification script
chmod +x verify.sh
./verify.sh
```

## Configuration

### Component Configuration

#### Backend (FastAPI)

```yaml
backend:
  enabled: true
  replicaCount: 1
  image:
    repository: todobot-backend
    tag: latest
  service:
    type: ClusterIP
    port: 8000
  resources:
    limits:
      cpu: "1000m"
      memory: "1Gi"
    requests:
      cpu: "500m"
      memory: "256Mi"
```

#### Frontend (Next.js)

```yaml
frontend:
  enabled: true
  replicaCount: 1
  image:
    repository: todobot-frontend
    tag: latest
  service:
    type: NodePort
    port: 3000
    nodePort: 30000  # Access via this port
  resources:
    limits:
      cpu: "2000m"
      memory: "2Gi"
```

#### Database (PostgreSQL)

```yaml
database:
  enabled: true
  image:
    repository: postgres
    tag: "15-alpine"
  persistence:
    enabled: true  # Set to false for testing
    size: 1Gi
```

### LLM Provider Configuration

**OpenAI:**
```yaml
backend:
  env:
    llmProvider: "openai"
    llmModel: "gpt-4o-mini"
    llmBaseUrl: "https://api.openai.com/v1"
secrets:
  llmApiKey: "sk-..."
```

**Groq (Free Alternative):**
```yaml
backend:
  env:
    llmProvider: "openai"
    llmModel: "llama-3.3-70b-versatile"
    llmBaseUrl: "https://api.groq.com/openai/v1"
secrets:
  llmApiKey: "gsk_..."
```

**Anthropic:**
```yaml
backend:
  env:
    llmProvider: "anthropic"
    llmModel: "claude-3-5-sonnet-20241022"
    llmBaseUrl: "https://api.anthropic.com"
secrets:
  llmApiKey: "sk-ant-..."
```

## Accessing the Application

### Frontend

**Method 1: Minikube Service (Easiest)**
```bash
minikube service todobot-frontend
# Opens browser automatically
```

**Method 2: NodePort**
```bash
# Get Minikube IP
minikube ip

# Access at http://<minikube-ip>:30000
# Example: http://192.168.49.2:30000
```

**Method 3: Port Forward**
```bash
kubectl port-forward svc/todobot-frontend 3000:3000
# Access at http://localhost:3000
```

### Backend API

```bash
# Port forward backend
kubectl port-forward svc/todobot-backend 8000:8000

# Access:
# - Health: http://localhost:8000/health
# - API Docs: http://localhost:8000/docs
# - API: http://localhost:8000/api
```

### Database (Direct Access)

```bash
# Get database pod name
kubectl get pods -l "app.kubernetes.io/component=database"

# Connect to PostgreSQL
kubectl exec -it <database-pod-name> -- psql -U user -d chatdb
```

## Monitoring & Troubleshooting

### View Logs

```bash
# All logs
kubectl logs -l "app.kubernetes.io/instance=todobot" --all-containers -f

# Backend logs
kubectl logs -l "app.kubernetes.io/component=backend" -f

# Frontend logs
kubectl logs -l "app.kubernetes.io/component=frontend" -f

# Database logs
kubectl logs -l "app.kubernetes.io/component=database" -f
```

### Check Pod Status

```bash
# Get pod status
kubectl get pods -l "app.kubernetes.io/instance=todobot"

# Detailed pod information
kubectl describe pods -l "app.kubernetes.io/instance=todobot"

# Get events
kubectl get events --sort-by='.lastTimestamp' | grep todobot
```

### Common Issues

#### Pods in Pending State

```bash
# Check why pod is pending
kubectl describe pod <pod-name>

# Common causes:
# - Insufficient resources
# - PVC not bound
# - Image not available
```

**Solution:**
```bash
# Check node resources
kubectl top nodes

# Check PVC status
kubectl get pvc

# Verify images are loaded
minikube image ls | grep todobot
```

#### ImagePullBackOff Error

```bash
# Check image status
kubectl describe pod <pod-name> | grep -A 10 Events

# Reload images
minikube image load todobot-backend:latest
minikube image load todobot-frontend:latest
```

#### CrashLoopBackOff

```bash
# Check logs for error
kubectl logs <pod-name> --previous

# Common causes:
# - Missing environment variables
# - Database connection failed
# - Application error
```

**Check Secrets:**
```bash
kubectl get secret todobot-secrets -o yaml
kubectl describe configmap todobot-config
```

#### Database Connection Issues

```bash
# Check database pod
kubectl get pods -l "app.kubernetes.io/component=database"

# Test database connection
kubectl exec -it <database-pod> -- pg_isready -U user

# Check database logs
kubectl logs -l "app.kubernetes.io/component=database"
```

## Maintenance

### Update Configuration

```bash
# Edit values-local.yaml
nano values-local.yaml

# Upgrade deployment
helm upgrade todobot . -f values-local.yaml
```

### Update Docker Images

```bash
# Rebuild images
cd ../backend
docker build -t todobot-backend:latest .

cd ../frontend
docker build -t todobot-frontend:latest .

# Reload into Minikube
minikube image load todobot-backend:latest
minikube image load todobot-frontend:latest

# Restart pods to use new images
kubectl rollout restart deployment -l "app.kubernetes.io/instance=todobot"
```

### Scale Components

```bash
# Scale backend
kubectl scale deployment todobot-backend --replicas=2

# Or update values.yaml
helm upgrade todobot . --set backend.replicaCount=2
```

### Backup Database

```bash
# Get database pod
DB_POD=$(kubectl get pods -l "app.kubernetes.io/component=database" -o jsonpath='{.items[0].metadata.name}')

# Backup
kubectl exec $DB_POD -- pg_dump -U user chatdb > backup.sql

# Restore
kubectl exec -i $DB_POD -- psql -U user chatdb < backup.sql
```

### Uninstall

```bash
# Uninstall Helm release
helm uninstall todobot

# Delete PVC (if persistence enabled)
kubectl delete pvc todobot-database-pvc

# Verify cleanup
kubectl get all -l "app.kubernetes.io/instance=todobot"
```

## Advanced Configuration

### Enable Ingress

```yaml
ingress:
  enabled: true
  className: "nginx"
  hosts:
    - host: todobot.local
      paths:
        - path: /
          pathType: Prefix
          backend: frontend
        - path: /api
          pathType: Prefix
          backend: backend
```

**Install Nginx Ingress Controller:**
```bash
minikube addons enable ingress

# Add to /etc/hosts
echo "$(minikube ip) todobot.local" | sudo tee -a /etc/hosts
```

### Enable Autoscaling

```yaml
autoscaling:
  enabled: true
  minReplicas: 1
  maxReplicas: 10
  targetCPUUtilizationPercentage: 80
```

### Resource Monitoring

```bash
# Enable metrics server
minikube addons enable metrics-server

# View resource usage
kubectl top nodes
kubectl top pods -l "app.kubernetes.io/instance=todobot"
```

## Production Considerations

Before deploying to production:

1. **Update all secrets** with strong, randomly generated values
2. **Enable database persistence** and configure backups
3. **Configure resource limits** based on load testing
4. **Set up monitoring** (Prometheus, Grafana)
5. **Configure ingress** with TLS/SSL
6. **Use external database** for better reliability
7. **Implement autoscaling** based on metrics
8. **Set up CI/CD** for automated deployments

## Support

For issues:
1. Check logs: `kubectl logs -l "app.kubernetes.io/instance=todobot" --all-containers`
2. Run verification: `./verify.sh`
3. Check events: `kubectl get events`
4. Review configuration: `kubectl get configmap todobot-config -o yaml`

## References

- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Helm Documentation](https://helm.sh/docs/)
- [Minikube Documentation](https://minikube.sigs.k8s.io/docs/)
