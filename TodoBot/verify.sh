#!/bin/bash

# TodoBot Deployment Verification Script

set -e

echo "🔍 TodoBot Deployment Verification"
echo "=================================="

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

FAILED=0

# Check if release exists
echo -e "\n${YELLOW}1. Checking Helm release...${NC}"
if helm list | grep -q "^todobot"; then
    echo -e "${GREEN}✅ TodoBot release found${NC}"
    helm list | grep "^todobot"
else
    echo -e "${RED}❌ TodoBot release not found${NC}"
    FAILED=1
fi

# Check pods
echo -e "\n${YELLOW}2. Checking pods...${NC}"
PODS=$(kubectl get pods -l "app.kubernetes.io/instance=todobot" --no-headers 2>/dev/null | wc -l)
if [ "$PODS" -gt 0 ]; then
    echo -e "${GREEN}✅ Found $PODS pod(s)${NC}"
    kubectl get pods -l "app.kubernetes.io/instance=todobot"

    # Check pod status
    NOT_RUNNING=$(kubectl get pods -l "app.kubernetes.io/instance=todobot" --no-headers | grep -v "Running" | wc -l)
    if [ "$NOT_RUNNING" -gt 0 ]; then
        echo -e "${RED}⚠️  Warning: $NOT_RUNNING pod(s) not in Running state${NC}"
        FAILED=1
    fi
else
    echo -e "${RED}❌ No pods found${NC}"
    FAILED=1
fi

# Check services
echo -e "\n${YELLOW}3. Checking services...${NC}"
SERVICES=$(kubectl get svc -l "app.kubernetes.io/instance=todobot" --no-headers 2>/dev/null | wc -l)
if [ "$SERVICES" -gt 0 ]; then
    echo -e "${GREEN}✅ Found $SERVICES service(s)${NC}"
    kubectl get svc -l "app.kubernetes.io/instance=todobot"
else
    echo -e "${RED}❌ No services found${NC}"
    FAILED=1
fi

# Check backend health
echo -e "\n${YELLOW}4. Checking backend health...${NC}"
BACKEND_POD=$(kubectl get pods -l "app.kubernetes.io/component=backend,app.kubernetes.io/instance=todobot" -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)
if [ -n "$BACKEND_POD" ]; then
    echo "Backend pod: $BACKEND_POD"

    # Check if pod is running
    POD_STATUS=$(kubectl get pod "$BACKEND_POD" -o jsonpath='{.status.phase}')
    if [ "$POD_STATUS" = "Running" ]; then
        echo -e "${GREEN}✅ Backend pod is running${NC}"

        # Try health check
        echo "Testing health endpoint..."
        if kubectl exec "$BACKEND_POD" -- curl -sf http://localhost:8000/health > /dev/null 2>&1; then
            echo -e "${GREEN}✅ Backend health check passed${NC}"
        else
            echo -e "${RED}❌ Backend health check failed${NC}"
            FAILED=1
        fi
    else
        echo -e "${RED}❌ Backend pod status: $POD_STATUS${NC}"
        FAILED=1
    fi
else
    echo -e "${RED}❌ Backend pod not found${NC}"
    FAILED=1
fi

# Check frontend
echo -e "\n${YELLOW}5. Checking frontend...${NC}"
FRONTEND_POD=$(kubectl get pods -l "app.kubernetes.io/component=frontend,app.kubernetes.io/instance=todobot" -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)
if [ -n "$FRONTEND_POD" ]; then
    echo "Frontend pod: $FRONTEND_POD"
    POD_STATUS=$(kubectl get pod "$FRONTEND_POD" -o jsonpath='{.status.phase}')
    if [ "$POD_STATUS" = "Running" ]; then
        echo -e "${GREEN}✅ Frontend pod is running${NC}"
    else
        echo -e "${RED}❌ Frontend pod status: $POD_STATUS${NC}"
        FAILED=1
    fi
else
    echo -e "${RED}❌ Frontend pod not found${NC}"
    FAILED=1
fi

# Check database
echo -e "\n${YELLOW}6. Checking database...${NC}"
DB_POD=$(kubectl get pods -l "app.kubernetes.io/component=database,app.kubernetes.io/instance=todobot" -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)
if [ -n "$DB_POD" ]; then
    echo "Database pod: $DB_POD"
    POD_STATUS=$(kubectl get pod "$DB_POD" -o jsonpath='{.status.phase}')
    if [ "$POD_STATUS" = "Running" ]; then
        echo -e "${GREEN}✅ Database pod is running${NC}"

        # Test database connection
        echo "Testing database connection..."
        if kubectl exec "$DB_POD" -- pg_isready -U user > /dev/null 2>&1; then
            echo -e "${GREEN}✅ Database is accepting connections${NC}"
        else
            echo -e "${RED}❌ Database connection failed${NC}"
            FAILED=1
        fi
    else
        echo -e "${RED}❌ Database pod status: $POD_STATUS${NC}"
        FAILED=1
    fi
else
    echo -e "${RED}❌ Database pod not found${NC}"
    FAILED=1
fi

# Check ConfigMap and Secrets
echo -e "\n${YELLOW}7. Checking ConfigMap and Secrets...${NC}"
if kubectl get configmap todobot-config > /dev/null 2>&1; then
    echo -e "${GREEN}✅ ConfigMap found${NC}"
else
    echo -e "${RED}❌ ConfigMap not found${NC}"
    FAILED=1
fi

if kubectl get secret todobot-secrets > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Secret found${NC}"
else
    echo -e "${RED}❌ Secret not found${NC}"
    FAILED=1
fi

# Summary
echo -e "\n=================================="
if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ All checks passed!${NC}"
    echo -e "\n${YELLOW}Access TodoBot:${NC}"
    MINIKUBE_IP=$(minikube ip 2>/dev/null || echo "localhost")
    echo -e "Frontend: ${GREEN}http://$MINIKUBE_IP:30000${NC}"
    echo -e "Or run: ${GREEN}minikube service todobot-frontend${NC}"
    echo -e "\nBackend API (port-forward): ${GREEN}kubectl port-forward svc/todobot-backend 8000:8000${NC}"
    exit 0
else
    echo -e "${RED}❌ Some checks failed!${NC}"
    echo -e "\n${YELLOW}Troubleshooting:${NC}"
    echo "1. Check pod logs: kubectl logs -l 'app.kubernetes.io/instance=todobot' --all-containers"
    echo "2. Describe pods: kubectl describe pods -l 'app.kubernetes.io/instance=todobot'"
    echo "3. Check events: kubectl get events --sort-by='.lastTimestamp'"
    exit 1
fi
