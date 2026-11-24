# One-click deployment script for all 5 Kubernetes strategies on Windows Minikube
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " Deploying All 5 DevOps Deployment Strategies to Cluster  " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# 0. Base Infrastructure
Write-Host "`n[Base] Applying Namespace, ConfigMap, PVC..." -ForegroundColor Green
kubectl apply -f k8s/base/

# 1. Rolling Update
Write-Host "`n[Strategy 1] Deploying Rolling Update (v1)..." -ForegroundColor Green
kubectl apply -f k8s/01-rolling-update/deployment-v1.yaml
kubectl apply -f k8s/01-rolling-update/service.yaml

# 2. Blue-Green
Write-Host "`n[Strategy 2] Deploying Blue-Green..." -ForegroundColor Green
kubectl apply -f k8s/02-blue-green/deployment-blue.yaml
kubectl apply -f k8s/02-blue-green/deployment-green.yaml
kubectl apply -f k8s/02-blue-green/service-active.yaml
kubectl apply -f k8s/02-blue-green/service-preview.yaml

# 3. Canary
Write-Host "`n[Strategy 3] Deploying Canary Release..." -ForegroundColor Green
kubectl apply -f k8s/03-canary/deployment-stable.yaml
kubectl apply -f k8s/03-canary/deployment-canary.yaml
kubectl apply -f k8s/03-canary/service.yaml

# 4. Shadow Deployment
Write-Host "`n[Strategy 4] Deploying Shadow (Dark Launch)..." -ForegroundColor Green
kubectl apply -f k8s/04-shadow/deployment-primary.yaml
kubectl apply -f k8s/04-shadow/deployment-shadow.yaml
kubectl apply -f k8s/04-shadow/service-primary.yaml
kubectl apply -f k8s/04-shadow/service-shadow.yaml

# 5. A/B Testing
Write-Host "`n[Strategy 5] Deploying A/B Testing..." -ForegroundColor Green
kubectl apply -f k8s/05-ab-testing/deployment-variant-a.yaml
kubectl apply -f k8s/05-ab-testing/deployment-variant-b.yaml
kubectl apply -f k8s/05-ab-testing/service-variant-a.yaml
kubectl apply -f k8s/05-ab-testing/service-variant-b.yaml

Write-Host "`n=== Cluster Deployments and Services Status ===" -ForegroundColor Cyan
kubectl get deployments,services -n aceest-fitness -o wide
