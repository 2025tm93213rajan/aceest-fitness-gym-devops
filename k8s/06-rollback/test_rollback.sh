#!/usr/bin/env bash
# Demonstration script for Kubernetes automated rollback mechanism (Linux / Prayogshala)
set -e

echo "=========================================================="
echo " Kubernetes Rollback Demonstration (aceest-rolling)      "
echo "=========================================================="

echo -e "\n1. Current Revision History:"
kubectl rollout history deployment/aceest-rolling -n aceest-fitness || true

echo -e "\n2. Triggering bad deployment (deployment-broken.yaml)..."
kubectl apply -f k8s/06-rollback/deployment-broken.yaml

echo -e "\nWaiting for deployment status to fail (timeout 15s)..."
set +e
kubectl rollout status deployment/aceest-rolling -n aceest-fitness --timeout=15s
EXIT_CODE=$?
set -e

if [ $EXIT_CODE -ne 0 ]; then
    echo -e "\n3. Defect detected! Initiating automated rollback to previous revision..."
    kubectl rollout undo deployment/aceest-rolling -n aceest-fitness
    echo -e "\n4. Waiting for rollback completion..."
    kubectl rollout status deployment/aceest-rolling -n aceest-fitness --timeout=60s
    echo -e "\n5. Rollback succeeded! Restored stable deployment state:"
    kubectl get deployment aceest-rolling -n aceest-fitness -o wide
fi
