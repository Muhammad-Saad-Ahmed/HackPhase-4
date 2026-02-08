# TodoBot Helm Chart - Deployment Summary

## 📦 What Was Created

Your TodoBot Helm chart has been fully configured for Kubernetes/Minikube deployment!

### Helm Chart Structure

```
TodoBot/
├── Chart.yaml                    # Chart metadata
├── values.yaml                   # Default configuration
├── values-local.yaml             # Local development configuration
├── README.md                     # Helm chart documentation
├── DEPLOYMENT_GUIDE.md           # Comprehensive deployment guide
├── deploy.sh                     # Linux/macOS deployment script
├── deploy.ps1                    # Windows deployment script
├── verify.sh                     # Deployment verification script
└── templates/
    ├── _helpers.tpl              # Template helpers
    ├── NOTES.txt                 # Post-installation notes
    ├── backend-deployment.yaml   # Backend (FastAPI) deployment
    ├── backend-service.yaml      # Backend service
    ├── frontend-deployment.yaml  # Frontend (Next.js) deployment
    ├── frontend-service.yaml     # Frontend service
    ├── database-deployment.yaml  # PostgreSQL deployment
    ├── database-service.yaml     # Database service
    ├── database-pvc.yaml         # Database persistent volume claim
    ├── configmap.yaml            # Configuration map
    ├── secrets.yaml              # Secrets (passwords, API keys)
    ├── serviceaccount.yaml       # Service account
    ├── ingress.yaml              # Ingress (optional)
    ├── httproute.yaml            # HTTP route (optional)
    └── hpa.yaml                  # Horizontal pod autoscaler (optional)
```

## 🎯 Key Features

### Multi-Component Architecture

1. **Backend (FastAPI)**
   - Port: 8000
   - Health check: `/health`
   - API docs: `/docs`
   - ClusterIP service

2. **Frontend (Next.js)**
   - Port: 3000
   - NodePort: 30000 (for easy local access)
   - NodePort service

3. **Database (PostgreSQL 15)**
   - Port: 5432
   - Persistent storage (1Gi by default)
   - ClusterIP service

### Configuration Management

- **ConfigMap**: Non-sensitive configuration (LLM provider, API URLs)
- **Secrets**: Sensitive data (API keys, passwords, auth secrets)
- **Environment-specific values**: `values.yaml` (default), `values-local.yaml` (local dev)

### Resource Management

- CPU and memory limits for all components
- Configurable resource requests and limits
- Persistent volume for database

### Health & Monitoring

- Liveness and readiness probes
- Health check endpoints
- Comprehensive logging support

## 🚀 Quick Deployment

### Prerequisites

1. **Minikube** running:
   ```bash
   minikube start --cpus=4 --memory=8192
   ```

2. **Docker images** built:
   ```bash
   # Backend
   cd backend
   docker build -t todobot-backend:latest .

   # Frontend
   cd ../frontend
   docker build -t todobot-frontend:latest .

   # Load into Minikube
   minikube image load todobot-backend:latest
   minikube image load todobot-frontend:latest
   ```

### Deploy Now!

**Option 1: Automated (Recommended)**

Windows:
```powershell
cd TodoBot
.\deploy.ps1
```

Linux/macOS:
```bash
cd TodoBot
./deploy.sh
```

**Option 2: Manual**

```bash
cd TodoBot

# Update configuration
nano values-local.yaml  # Update secrets.llmApiKey

# Deploy
helm install todobot . -f values-local.yaml

# Wait for ready
kubectl wait --for=condition=ready pod -l "app.kubernetes.io/instance=todobot" --timeout=300s

# Access frontend
minikube service todobot-frontend
```

### Verify Deployment

```bash
cd TodoBot
./verify.sh
```

## 🔧 Configuration Guide

### Essential Configuration

Before deploying, update `values-local.yaml`:

```yaml
secrets:
  # REQUIRED: Your LLM API key
  llmApiKey: "your-api-key-here"

  # Generate using: python -c "import secrets; print(secrets.token_hex(32))"
  betterAuthSecret: "your-32-char-secret"

  # Database password
  databasePassword: "secure-password"

backend:
  env:
    llmProvider: "openai"  # openai, anthropic, groq
    llmModel: "gpt-4o-mini"
    llmBaseUrl: "https://api.openai.com/v1"
```

### LLM Provider Options

**OpenAI (Default):**
```yaml
llmProvider: "openai"
llmModel: "gpt-4o-mini"
llmBaseUrl: "https://api.openai.com/v1"
llmApiKey: "sk-..."
```

**Groq (Free, Fast):**
```yaml
llmProvider: "openai"
llmModel: "llama-3.3-70b-versatile"
llmBaseUrl: "https://api.groq.com/openai/v1"
llmApiKey: "gsk_..."
```

**Anthropic:**
```yaml
llmProvider: "anthropic"
llmModel: "claude-3-5-sonnet-20241022"
llmBaseUrl: "https://api.anthropic.com"
llmApiKey: "sk-ant-..."
```

## 📊 Accessing Your Application

### Frontend

```bash
# Automatic (easiest)
minikube service todobot-frontend

# Manual
minikube ip  # Get IP, then visit http://<IP>:30000

# Port forward
kubectl port-forward svc/todobot-frontend 3000:3000
# Visit http://localhost:3000
```

### Backend API

```bash
# Port forward
kubectl port-forward svc/todobot-backend 8000:8000

# Then access:
# - Health: http://localhost:8000/health
# - API Docs: http://localhost:8000/docs
# - API: http://localhost:8000/api
```

## 📝 Common Commands

### Deployment Management

```bash
# Install
helm install todobot ./TodoBot -f ./TodoBot/values-local.yaml

# Upgrade
helm upgrade todobot ./TodoBot -f ./TodoBot/values-local.yaml

# Uninstall
helm uninstall todobot

# List releases
helm list

# Get deployment status
helm status todobot
```

### Monitoring

```bash
# Check pods
kubectl get pods -l "app.kubernetes.io/instance=todobot"

# Check services
kubectl get svc -l "app.kubernetes.io/instance=todobot"

# View logs
kubectl logs -l "app.kubernetes.io/component=backend" -f
kubectl logs -l "app.kubernetes.io/component=frontend" -f
kubectl logs -l "app.kubernetes.io/component=database" -f

# Describe pod
kubectl describe pod <pod-name>

# Get events
kubectl get events --sort-by='.lastTimestamp'
```

### Troubleshooting

```bash
# Run verification script
cd TodoBot && ./verify.sh

# Check all resources
kubectl get all -l "app.kubernetes.io/instance=todobot"

# View ConfigMap
kubectl get configmap todobot-config -o yaml

# View Secrets (base64 encoded)
kubectl get secret todobot-secrets -o yaml

# Shell into backend
kubectl exec -it deployment/todobot-backend -- /bin/sh

# Database shell
kubectl exec -it deployment/todobot-database -- psql -U user -d chatdb
```

### Image Updates

```bash
# Rebuild images
cd backend && docker build -t todobot-backend:latest .
cd ../frontend && docker build -t todobot-frontend:latest .

# Reload into Minikube
minikube image load todobot-backend:latest
minikube image load todobot-frontend:latest

# Restart deployments
kubectl rollout restart deployment -l "app.kubernetes.io/instance=todobot"
```

## 🎨 Customization

### Change Service Types

```yaml
# Make backend accessible via NodePort
backend:
  service:
    type: NodePort
    nodePort: 30001

# Use LoadBalancer (cloud environments)
frontend:
  service:
    type: LoadBalancer
```

### Adjust Resources

```yaml
backend:
  resources:
    limits:
      cpu: "2000m"      # 2 CPU cores
      memory: "2Gi"     # 2GB RAM
    requests:
      cpu: "1000m"      # 1 CPU core
      memory: "512Mi"   # 512MB RAM
```

### Disable Database Persistence

```yaml
database:
  persistence:
    enabled: false  # Data lost on pod restart
```

### Enable Autoscaling

```yaml
autoscaling:
  enabled: true
  minReplicas: 1
  maxReplicas: 10
  targetCPUUtilizationPercentage: 80
```

## 🔐 Security Notes

### For Production

1. **Update all secrets** with strong random values
2. **Use external secrets manager** (Vault, AWS Secrets Manager)
3. **Enable RBAC** and least privilege access
4. **Use private container registry**
5. **Enable network policies**
6. **Configure TLS/SSL** for ingress
7. **Regular security scans** of images
8. **Backup strategy** for database

### Generate Secure Secrets

```bash
# Better Auth Secret (32+ characters)
python -c "import secrets; print(secrets.token_hex(32))"

# Or using OpenSSL
openssl rand -hex 32

# Database password
openssl rand -base64 32
```

## 📚 Documentation

- **README.md**: Helm chart overview and quick reference
- **DEPLOYMENT_GUIDE.md**: Comprehensive deployment and troubleshooting guide
- **values.yaml**: Default configuration with comments
- **values-local.yaml**: Local development configuration

## 🐛 Troubleshooting Quick Reference

| Issue | Solution |
|-------|----------|
| Pods in Pending state | Check resources: `kubectl describe pod <pod>` |
| ImagePullBackOff | Reload images: `minikube image load <image>:latest` |
| CrashLoopBackOff | Check logs: `kubectl logs <pod> --previous` |
| Database connection failed | Verify db pod: `kubectl logs -l component=database` |
| Can't access frontend | Check service: `minikube service todobot-frontend` |
| API errors | Check secrets: `kubectl get secret todobot-secrets -o yaml` |

## ✅ Next Steps

1. **Update configuration**: Edit `TodoBot/values-local.yaml`
2. **Set API key**: Add your LLM API key (OpenAI, Groq, etc.)
3. **Deploy**: Run `./deploy.ps1` (Windows) or `./deploy.sh` (Linux/macOS)
4. **Verify**: Run `./verify.sh`
5. **Access**: Visit the frontend URL shown after deployment
6. **Monitor**: Check logs and pod status as needed

## 🎉 Success!

Your TodoBot is now ready for Kubernetes deployment!

- All Helm templates created and configured
- Deployment scripts ready
- Verification tools in place
- Comprehensive documentation provided

For detailed instructions, see `TodoBot/DEPLOYMENT_GUIDE.md`

Happy deploying! 🚀
