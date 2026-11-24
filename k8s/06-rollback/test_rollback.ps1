# Demonstration script for Kubernetes automated rollback mechanism
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " Kubernetes Rollback Demonstration (aceest-rolling)      " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

Write-Host "`n1. Current Revision History:" -ForegroundColor Yellow
kubectl rollout history deployment/aceest-rolling -n aceest-fitness

Write-Host "`n2. Triggering bad deployment (deployment-broken.yaml)..." -ForegroundColor Yellow
kubectl apply -f k8s/06-rollback/deployment-broken.yaml

Write-Host "`nWaiting for deployment status to stall/fail (timeout 15s)..." -ForegroundColor Yellow
kubectl rollout status deployment/aceest-rolling -n aceest-fitness --timeout=15s

Write-Host "`n3. Defect detected! Initiating automated rollback to previous revision..." -ForegroundColor Red
kubectl rollout undo deployment/aceest-rolling -n aceest-fitness

Write-Host "`n4. Waiting for rollback completion..." -ForegroundColor Green
kubectl rollout status deployment/aceest-rolling -n aceest-fitness --timeout=60s

Write-Host "`n5. Rollback succeeded! Restored stable deployment state:" -ForegroundColor Green
kubectl get deployment aceest-rolling -n aceest-fitness -o wide
