# TodoBot Helm Deployment Script for Windows PowerShell
# This script helps deploy TodoBot to Minikube

$ErrorActionPreference = "Stop"

Write-Host "🚀 TodoBot Helm Deployment Script" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan

# Check if Minikube is running
Write-Host "`nChecking Minikube status..." -ForegroundColor Yellow
try {
    $minikubeStatus = minikube status 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Minikube not running"
    }
    Write-Host "✅ Minikube is running" -ForegroundColor Green
} catch {
    Write-Host "❌ Minikube is not running!" -ForegroundColor Red
    Write-Host "Start Minikube with: minikube start" -ForegroundColor Yellow
    exit 1
}

# Check if Helm is installed
Write-Host "`nChecking Helm installation..." -ForegroundColor Yellow
try {
    $helmVersion = helm version --short 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Helm not found"
    }
    Write-Host "✅ Helm is installed ($helmVersion)" -ForegroundColor Green
} catch {
    Write-Host "❌ Helm is not installed!" -ForegroundColor Red
    Write-Host "Install Helm from: https://helm.sh/docs/intro/install/" -ForegroundColor Yellow
    exit 1
}

# Build Docker images
Write-Host "`nBuilding Docker images..." -ForegroundColor Yellow
$buildImages = Read-Host "Do you want to build Docker images? (y/n)"
if ($buildImages -eq 'y' -or $buildImages -eq 'Y') {
    Write-Host "Building backend image..." -ForegroundColor Cyan
    Push-Location ..\backend
    docker build -t todobot-backend:latest .
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Backend image build failed" -ForegroundColor Red
        Pop-Location
        exit 1
    }
    Write-Host "✅ Backend image built" -ForegroundColor Green
    Pop-Location

    Write-Host "Building frontend image..." -ForegroundColor Cyan
    Push-Location ..\frontend
    docker build -t todobot-frontend:latest .
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Frontend image build failed" -ForegroundColor Red
        Pop-Location
        exit 1
    }
    Write-Host "✅ Frontend image built" -ForegroundColor Green
    Pop-Location

    # Load images into Minikube
    Write-Host "`nLoading images into Minikube..." -ForegroundColor Yellow
    minikube image load todobot-backend:latest
    minikube image load todobot-frontend:latest
    Write-Host "✅ Images loaded into Minikube" -ForegroundColor Green
} else {
    Write-Host "Skipping Docker image build" -ForegroundColor Yellow
}

# Check for API keys
Write-Host "`nChecking configuration..." -ForegroundColor Yellow
if (Test-Path "values-local.yaml") {
    $content = Get-Content "values-local.yaml" -Raw
    if ($content -match "your-api-key-here") {
        Write-Host "⚠️  WARNING: API key not configured in values-local.yaml" -ForegroundColor Red
        Write-Host "Please update 'secrets.llmApiKey' in values-local.yaml before deploying" -ForegroundColor Yellow
        $continue = Read-Host "Continue anyway? (y/n)"
        if ($continue -ne 'y' -and $continue -ne 'Y') {
            exit 1
        }
    }
}

# Deploy with Helm
Write-Host "`nDeploying TodoBot with Helm..." -ForegroundColor Yellow
$valuesFile = "values-local.yaml"
if (-not (Test-Path $valuesFile)) {
    Write-Host "values-local.yaml not found, using default values.yaml" -ForegroundColor Yellow
    $valuesFile = "values.yaml"
}

# Check if release exists
$releaseExists = $false
try {
    $helmList = helm list -o json | ConvertFrom-Json
    $releaseExists = $helmList | Where-Object { $_.name -eq "todobot" }
} catch {
    $releaseExists = $false
}

if ($releaseExists) {
    Write-Host "TodoBot release already exists. Upgrading..." -ForegroundColor Cyan
    helm upgrade todobot . -f $valuesFile
} else {
    Write-Host "Installing new TodoBot release..." -ForegroundColor Cyan
    helm install todobot . -f $valuesFile
}

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Helm deployment failed" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Helm deployment complete" -ForegroundColor Green

# Wait for pods to be ready
Write-Host "`nWaiting for pods to be ready..." -ForegroundColor Yellow
Write-Host "This may take a few minutes..." -ForegroundColor Cyan
try {
    kubectl wait --for=condition=ready pod -l "app.kubernetes.io/instance=todobot" --timeout=300s
    if ($LASTEXITCODE -ne 0) {
        throw "Pods not ready"
    }
} catch {
    Write-Host "❌ Pods did not become ready in time" -ForegroundColor Red
    Write-Host "Check pod status with: kubectl get pods -l 'app.kubernetes.io/instance=todobot'" -ForegroundColor Yellow
    exit 1
}

# Show deployment status
Write-Host "`n✅ All pods are ready!" -ForegroundColor Green
Write-Host "`nDeployment Status:" -ForegroundColor Yellow
kubectl get pods -l "app.kubernetes.io/instance=todobot"
Write-Host ""
kubectl get svc -l "app.kubernetes.io/instance=todobot"

# Get access URLs
Write-Host "`n==================================" -ForegroundColor Green
Write-Host "🎉 TodoBot Deployed Successfully!" -ForegroundColor Green
Write-Host "==================================" -ForegroundColor Green

$minikubeIp = minikube ip
Write-Host "`nAccess URLs:" -ForegroundColor Yellow
Write-Host "Frontend: http://${minikubeIp}:30000" -ForegroundColor Green
Write-Host "Or run: minikube service todobot-frontend" -ForegroundColor Green

Write-Host "`nBackend API:" -ForegroundColor Yellow
Write-Host "Run: kubectl port-forward svc/todobot-backend 8000:8000" -ForegroundColor Cyan
Write-Host "Then access:" -ForegroundColor Cyan
Write-Host "  - Health: http://localhost:8000/health" -ForegroundColor Green
Write-Host "  - API Docs: http://localhost:8000/docs" -ForegroundColor Green

Write-Host "`nMonitoring:" -ForegroundColor Yellow
Write-Host "View all logs: kubectl logs -l 'app.kubernetes.io/instance=todobot' --all-containers -f" -ForegroundColor Cyan
Write-Host "Backend logs: kubectl logs -l 'app.kubernetes.io/component=backend' -f" -ForegroundColor Cyan
Write-Host "Frontend logs: kubectl logs -l 'app.kubernetes.io/component=frontend' -f" -ForegroundColor Cyan
Write-Host "Database logs: kubectl logs -l 'app.kubernetes.io/component=database' -f" -ForegroundColor Cyan

Write-Host "`nManagement:" -ForegroundColor Yellow
Write-Host "Upgrade: helm upgrade todobot . -f $valuesFile" -ForegroundColor Cyan
Write-Host "Uninstall: helm uninstall todobot" -ForegroundColor Cyan

Write-Host "`nHappy coding! 🚀" -ForegroundColor Green
