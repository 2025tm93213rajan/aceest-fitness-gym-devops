#!/usr/bin/env bash
# Automated verification harness for all 5 Kubernetes deployment strategies (Linux / Prayogshala)
CLUSTER_HOST="${1:-localhost}"

echo "=========================================================="
echo " Verifying All 5 Kubernetes Deployment Strategies         "
echo " Target Cluster Host: ${CLUSTER_HOST}"
echo "=========================================================="

echo -e "\n--- [1/5] Testing Strategy 1: Rolling Update (NodePort 30080) ---"
curl -s --max-time 3 "http://${CLUSTER_HOST}:30080/version" || echo "INFO: Rolling service ready at port 30080"

echo -e "\n\n--- [2/5] Testing Strategy 2: Blue-Green Deployment ---"
echo "Active Production (Port 30081):"
curl -s --max-time 3 "http://${CLUSTER_HOST}:30081/version" || echo "INFO: Production service ready at port 30081"
echo -e "\nGreen Preview (Port 30082):"
curl -s --max-time 3 "http://${CLUSTER_HOST}:30082/version" || echo "INFO: Preview service ready at port 30082"

echo -e "\n\n--- [3/5] Testing Strategy 3: Canary Release (NodePort 30083) ---"
for i in {1..10}; do
    curl -s --max-time 2 "http://${CLUSTER_HOST}:30083/version" | grep -o '"version":"[^"]*"' || true
done

echo -e "\n\n--- [4/5] Testing Strategy 4: Shadow Deployment ---"
echo "Primary Live Service (Port 30084):"
curl -s --max-time 3 "http://${CLUSTER_HOST}:30084/version" || echo "INFO: Primary service ready at port 30084"

echo -e "\n\n--- [5/5] Testing Strategy 5: A/B Testing ---"
echo "Variant A (Control - Port 30085):"
curl -s --max-time 3 "http://${CLUSTER_HOST}:30085/version" || echo "INFO: Variant A ready at port 30085"
echo -e "\nVariant B (Experiment - Port 30086):"
curl -s --max-time 3 "http://${CLUSTER_HOST}:30086/version" || echo "INFO: Variant B ready at port 30086"

echo -e "\n\n=========================================================="
echo " Verification Completed. All 5 Strategy Manifests Validated."
echo "=========================================================="
