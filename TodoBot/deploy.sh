#!/bin/bash

# TodoBot Helm Deployment Script
# This script helps deploy TodoBot to Minikube

set -e

echo "🚀 TodoBot Helm Deployment Script"
echo "=================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Minikube is running
echo -e "\n${YELLOW}Checking Minikube status...${NC}"
if ! minikube status &> /dev/null; then
    echo -e "${RED}❌ Minikube is not running!${NC}"
    echo "Start Minikube with: minikube start"
    exit 1
fi
echo -e "${GREEN}✅ Minikube is running${NC}"

# Check if Helm is installed
echo -e "\n${YELLOW}Checking Helm installation...${NC}"
if ! command -v helm &> /dev/null; then
    echo -e "${RED}❌ Helm is not installed!${NC}"
    echo "Install Helm from: https://helm.sh/docs/intro/install/"
    exit 1
fi
echo -e "${GREEN}✅ Helm is installed ($(helm version --short))${NC}"

# Build Docker images
echo -e "\n${YELLOW}Building Docker images...${NC}"
read -p "Do you want to build Docker images? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Building backend image..."
    cd ../backend
    docker build -t todobot-backend:latest .
    echo -e "${GREEN}✅ Backend image built${NC}"

    echo "Building frontend image..."
    cd ../frontend
    docker build -t todobot-frontend:latest .
    echo -e "${GREEN}✅ Frontend image built${NC}"

    cd ../TodoBot

    # Load images into Minikube
    echo -e "\n${YELLOW}Loading images into Minikube...${NC}"
    minikube image load todobot-backend:latest
    minikube image load todobot-frontend:latest
    echo -e "${GREEN}✅ Images loaded into Minikube${NC}"
else
    echo "Skipping Docker image build"
fi

# Check for API keys
echo -e "\n${YELLOW}Checking configuration...${NC}"
if grep -q "your-api-key-here" values-local.yaml 2>/dev/null; then
    echo -e "${RED}⚠️  WARNING: API key not configured in values-local.yaml${NC}"
    echo "Please update 'secrets.llmApiKey' in values-local.yaml before deploying"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Deploy with Helm
echo -e "\n${YELLOW}Deploying TodoBot with Helm...${NC}"
VALUES_FILE="values-local.yaml"
if [ ! -f "$VALUES_FILE" ]; then
    echo -e "${YELLOW}values-local.yaml not found, using default values.yaml${NC}"
    VALUES_FILE="values.yaml"
fi

# Check if release exists
if helm list | grep -q "^todobot"; then
    echo "TodoBot release already exists. Upgrading..."
    helm upgrade todobot . -f "$VALUES_FILE"
else
    echo "Installing new TodoBot release..."
    helm install todobot . -f "$VALUES_FILE"
fi

echo -e "${GREEN}✅ Helm deployment complete${NC}"

# Wait for pods to be ready
echo -e "\n${YELLOW}Waiting for pods to be ready...${NC}"
echo "This may take a few minutes..."
kubectl wait --for=condition=ready pod -l "app.kubernetes.io/instance=todobot" --timeout=300s || {
    echo -e "${RED}❌ Pods did not become ready in time${NC}"
    echo "Check pod status with: kubectl get pods -l 'app.kubernetes.io/instance=todobot'"
    exit 1
}

# Show deployment status
echo -e "\n${GREEN}✅ All pods are ready!${NC}"
echo -e "\n${YELLOW}Deployment Status:${NC}"
kubectl get pods -l "app.kubernetes.io/instance=todobot"
echo ""
kubectl get svc -l "app.kubernetes.io/instance=todobot"

# Get access URLs
echo -e "\n${GREEN}=================================="
echo "🎉 TodoBot Deployed Successfully!"
echo -e "==================================${NC}"

MINIKUBE_IP=$(minikube ip)
echo -e "\n${YELLOW}Access URLs:${NC}"
echo -e "Frontend: ${GREEN}http://$MINIKUBE_IP:30000${NC}"
echo -e "Or run: ${GREEN}minikube service todobot-frontend${NC}"

echo -e "\n${YELLOW}Backend API:${NC}"
echo "Run: kubectl port-forward svc/todobot-backend 8000:8000"
echo -e "Then access:"
echo -e "  - Health: ${GREEN}http://localhost:8000/health${NC}"
echo -e "  - API Docs: ${GREEN}http://localhost:8000/docs${NC}"

echo -e "\n${YELLOW}Monitoring:${NC}"
echo "View all logs: kubectl logs -l 'app.kubernetes.io/instance=todobot' --all-containers -f"
echo "Backend logs: kubectl logs -l 'app.kubernetes.io/component=backend' -f"
echo "Frontend logs: kubectl logs -l 'app.kubernetes.io/component=frontend' -f"
echo "Database logs: kubectl logs -l 'app.kubernetes.io/component=database' -f"

echo -e "\n${YELLOW}Management:${NC}"
echo "Upgrade: helm upgrade todobot . -f $VALUES_FILE"
echo "Uninstall: helm uninstall todobot"

echo -e "\n${GREEN}Happy coding! 🚀${NC}"
