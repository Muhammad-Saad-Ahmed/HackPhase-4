# TodoBot - Quick Start Guide

## ⚡ 5-Minute Deployment

### Prerequisites Check

```bash
# Check Minikube
minikube status

# Check Helm
helm version

# Check kubectl
kubectl version --client
```

### Step 1: Start Minikube (if not running)

```bash
minikube start --cpus=4 --memory=8192
```

### Step 2: Build & Load Images

```bash
# Build backend
cd backend
docker build -t todobot-backend:latest .

# Build frontend
cd ../frontend
docker build -t todobot-frontend:latest .

# Load into Minikube
minikube image load todobot-backend:latest
minikube image load todobot-frontend:latest
```

### Step 3: Configure

```bash
cd ../TodoBot

# Edit values-local.yaml
# Update: secrets.llmApiKey with your API key
```

**Minimum required:**
```yaml
secrets:
  llmApiKey: "your-actual-api-key-here"
```

### Step 4: Deploy

**Windows:**
```powershell
.\deploy.ps1
```

**Linux/macOS:**
```bash
./deploy.sh
```

**Manual:**
```bash
helm install todobot . -f values-local.yaml
```

### Step 5: Access

```bash
# Frontend
minikube service todobot-frontend

# Or get URL
minikube ip  # Then visit http://<IP>:30000
```

## 🎯 Common Commands

### View Status
```bash
kubectl get pods -l "app.kubernetes.io/instance=todobot"
```

### View Logs
```bash
# Backend
kubectl logs -l "app.kubernetes.io/component=backend" -f

# Frontend
kubectl logs -l "app.kubernetes.io/component=frontend" -f
```

### Access Backend API
```bash
kubectl port-forward svc/todobot-backend 8000:8000
# http://localhost:8000/docs
```

### Verify Deployment
```bash
./verify.sh
```

### Update After Code Changes
```bash
# Rebuild images
cd backend && docker build -t todobot-backend:latest . && cd ..
cd frontend && docker build -t todobot-frontend:latest . && cd ..

# Reload
minikube image load todobot-backend:latest
minikube image load todobot-frontend:latest

# Restart
kubectl rollout restart deployment -l "app.kubernetes.io/instance=todobot"
```

### Cleanup
```bash
helm uninstall todobot
kubectl delete pvc todobot-database-pvc  # if persistence enabled
```

## 🔧 LLM Provider Quick Config

### OpenAI
```yaml
backend:
  env:
    llmProvider: "openai"
    llmModel: "gpt-4o-mini"
    llmBaseUrl: "https://api.openai.com/v1"
secrets:
  llmApiKey: "sk-..."
```

### Groq (Free)
```yaml
backend:
  env:
    llmProvider: "openai"
    llmModel: "llama-3.3-70b-versatile"
    llmBaseUrl: "https://api.groq.com/openai/v1"
secrets:
  llmApiKey: "gsk_..."
```

## 🐛 Quick Troubleshooting

### Pods not starting?
```bash
kubectl describe pods -l "app.kubernetes.io/instance=todobot"
kubectl logs -l "app.kubernetes.io/instance=todobot" --all-containers
```

### Images not found?
```bash
minikube image ls | grep todobot
# If missing: minikube image load <image>:latest
```

### Can't access frontend?
```bash
minikube service list
minikube service todobot-frontend
```

### Database issues?
```bash
kubectl logs -l "app.kubernetes.io/component=database"
kubectl exec -it deployment/todobot-database -- pg_isready -U user
```

## 📖 Full Documentation

For detailed information, see:
- `DEPLOYMENT_GUIDE.md` - Comprehensive deployment guide
- `README.md` - Helm chart documentation
- `../HELM_DEPLOYMENT_SUMMARY.md` - Complete feature overview

## 🎉 That's it!

Your TodoBot should now be running!

Visit the frontend URL and start chatting with your AI-powered Todo assistant!
