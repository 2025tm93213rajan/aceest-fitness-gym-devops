#!/usr/bin/env bash
# One-click deployment script for all 5 Kubernetes strategies (Linux / Prayogshala)
set -e

echo "=========================================================="
echo " Deploying All 5 DevOps Deployment Strategies to Cluster  "
echo "=========================================================="

# 0. Base Infrastructure
echo -e "\n[Base] Applying Namespace, ConfigMap, PVC..."
kubectl apply -f k8s/base/

# 1. Rolling Update
echo -e "\n[Strategy 1] Deploying Rolling Update (v1)..."
kubectl apply -f k8s/01-rolling-update/deployment-v1.yaml
kubectl apply -f k8s/01-rolling-update/service.yaml

# 2. Blue-Green
echo -e "\n[Strategy 2] Deploying Blue-Green..."
kubectl apply -f k8s/02-blue-green/deployment-blue.yaml
kubectl apply -f k8s/02-blue-green/deployment-green.yaml
kubectl apply -f k8s/02-blue-green/service-active.yaml
kubectl apply -f k8s/02-blue-green/service-preview.yaml

# 3. Canary
echo -e "\n[Strategy 3] Deploying Canary Release..."
kubectl apply -f k8s/03-canary/deployment-stable.yaml
kubectl apply -f k8s/03-canary/deployment-canary.yaml
kubectl apply -f k8s/03-canary/service.yaml

# 4. Shadow Deployment
echo -e "\n[Strategy 4] Deploying Shadow (Dark Launch)..."
kubectl apply -f k8s/04-shadow/deployment-primary.yaml
kubectl apply -f k8s/04-shadow/deployment-shadow.yaml
kubectl apply -f k8s/04-shadow/service-primary.yaml
kubectl apply -f k8s/04-shadow/service-shadow.yaml

# 5. A/B Testing
echo -e "\n[Strategy 5] Deploying A/B Testing..."
kubectl apply -f k8s/05-ab-testing/deployment-variant-a.yaml
kubectl apply -f k8s/05-ab-testing/deployment-variant-b.yaml
kubectl apply -f k8s/05-ab-testing/service-variant-a.yaml
kubectl apply -f k8s/05-ab-testing/service-variant-b.yaml

echo -e "\n=== Cluster Deployments and Services Status ==="
kubectl get deployments,services -n aceest-fitness -o wide
