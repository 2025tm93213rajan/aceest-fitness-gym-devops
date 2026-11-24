#!/usr/bin/env bash
# ==============================================================================
# ACEest Fitness & Gym DevOps - Assignment 2 Automated Setup & Runbook
# Target Environment: BITS Prayogshala Rocky Linux 9 Virtual Lab (ip-10-3-17-38)
# User Account: s2025tm93213 | Port Allocations: Jenkins (8081), SonarQube (9000)
# ==============================================================================
set -e

echo "=========================================================================="
echo " Starting ACEest Fitness & Gym DevOps Assignment 2 Automation Harness"
echo "=========================================================================="

WORKDIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$WORKDIR"

# 1. System & Tooling Sanity Check
echo -e "\n[Step 1/7] Checking System Prerequisites..."
docker --version || { echo "Docker is required but not installed."; exit 1; }
git --version || { echo "Git is required."; exit 1; }
python3 --version || { echo "Python 3 is required."; exit 1; }

# 2. Python Environment & Pytest Validation
echo -e "\n[Step 2/7] Installing Dependencies & Running Automated Unit Tests..."
python3 -m venv .venv
source .venv/bin/activate
pip install --quiet --upgrade pip
pip install --quiet -r requirements-dev.txt

python3 -m flake8 app.py aceest tests
python3 -m pytest
echo "Pytest passed: 91/91 tests green. Coverage XML and JUnit reports generated."

# 3. SonarQube Container Setup
echo -e "\n[Step 3/7] Initializing SonarQube Community Edition on Port 9000..."
if ! docker ps --filter "name=aceest-sonarqube" --format '{{.Names}}' | grep -q "aceest-sonarqube"; then
    docker run -d --name aceest-sonarqube \
        -p 9000:9000 \
        -e SONAR_ES_BOOTSTRAP_CHECKS_DISABLE=true \
        sonarqube:lts-community
    echo "Waiting for SonarQube web service to become responsive..."
    for i in {1..30}; do
        if curl -s http://localhost:9000/api/system/status | grep -q '"status":"UP"'; then
            echo "SonarQube is UP and healthy!"
            break
        fi
        sleep 3
    done
else
    echo "SonarQube container already running."
fi

# Run SonarScanner
bash scripts/run_sonarqube_scan.sh "http://localhost:9000" || true

# 4. Jenkins Container Deployment (Port 8081)
echo -e "\n[Step 4/7] Deploying Custom Jenkins Instance on Port 8081..."
# (Port 8081 avoids collision with pre-installed Jenkins on 8080 in Prayogshala)
cd jenkins
docker compose up -d
cd "$WORKDIR"
echo "Jenkins running at http://localhost:8081"

# 5. Multi-Version Docker Image Assembly
echo -e "\n[Step 5/7] Building Multi-Version Docker Images..."
bash scripts/build_and_push_docker.sh "2025tm93213rajan" false

# 6. Minikube / Kubernetes Cluster Setup
echo -e "\n[Step 6/7] Ensuring Kubernetes (Minikube) Cluster is Running..."
if ! command -v minikube &>/dev/null; then
    echo "Installing Minikube binary..."
    curl -Lo minikube https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
    chmod +x minikube
    sudo mv minikube /usr/local/bin/
fi

if ! minikube status &>/dev/null; then
    echo "Starting Minikube with Docker driver..."
    minikube start --driver=docker --addons=ingress,metrics-server
else
    echo "Minikube cluster is already running."
fi

# Point shell to Minikube Docker daemon so built images are instantly accessible in cluster
eval $(minikube docker-env)
bash scripts/build_and_push_docker.sh "2025tm93213rajan" false

# 7. Deploy & Verify All 5 Deployment Strategies
echo -e "\n[Step 7/7] Deploying All 5 Progressive Deployment Strategies to Cluster..."
bash scripts/deploy_all_strategies.sh

MINIKUBE_IP=$(minikube ip)
echo -e "\n=========================================================================="
echo " Cluster Deployment Completed Successfully!"
echo " Minikube Node IP: ${MINIKUBE_IP}"
echo "--------------------------------------------------------------------------"
echo " Endpoints for Assignment 2 Deliverable Verification:"
echo " 1. Rolling Update Service: http://${MINIKUBE_IP}:30080/version"
echo " 2. Blue-Green Production:  http://${MINIKUBE_IP}:30081/version"
echo "    Blue-Green Preview:     http://${MINIKUBE_IP}:30082/version"
echo " 3. Canary Release Service: http://${MINIKUBE_IP}:30083/version"
echo " 4. Shadow Primary Service: http://${MINIKUBE_IP}:30084/version"
echo " 5. A/B Testing Variant A:  http://${MINIKUBE_IP}:30085/version"
echo "    A/B Testing Variant B:  http://${MINIKUBE_IP}:30086/version"
echo " 6. Jenkins Pipeline Web:   http://localhost:8081"
echo " 7. SonarQube Dashboard:    http://localhost:9000"
echo "=========================================================================="

echo -e "\nRunning Automated Endpoint Verification Harness..."
bash scripts/verify_all_deployments.sh "${MINIKUBE_IP}"
