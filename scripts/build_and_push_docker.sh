#!/usr/bin/env bash
# Script to build and push multi-version container images to Docker Hub (Linux / Prayogshala)
set -e

DOCKER_USER="${1:-2025tm93213rajan}"
PUSH_IMAGES="${2:-false}"
IMAGE_NAME="${DOCKER_USER}/aceest-fitness"

echo "=========================================================="
echo " Building Multi-Version Docker Images for ${IMAGE_NAME}"
echo "=========================================================="

# 1. Build v1.0.0 (Baseline Release)
echo -e "\n[1/4] Building aceest-fitness:v1.0.0 ..."
docker build --build-arg APP_VERSION=1.0.0 --build-arg APP_RELEASE=v1-core \
    -t "${IMAGE_NAME}:v1.0.0" -t "aceest-fitness:v1.0.0" .

# 2. Build v2.0.0 (Enhanced Release with Analytics)
echo -e "\n[2/4] Building aceest-fitness:v2.0.0 and :latest ..."
docker build --build-arg APP_VERSION=2.0.0 --build-arg APP_RELEASE=v2-analytics \
    -t "${IMAGE_NAME}:v2.0.0" -t "${IMAGE_NAME}:latest" -t "aceest-fitness:v2.0.0" -t "aceest-fitness:latest" .

# 3. Build v2.1.0-canary (Canary Release)
echo -e "\n[3/4] Building aceest-fitness:canary ..."
docker build --build-arg APP_VERSION=2.1.0-canary --build-arg APP_RELEASE=v2.1-canary \
    -t "${IMAGE_NAME}:canary" -t "aceest-fitness:canary" .

# 4. Build Test Target Image
echo -e "\n[4/4] Building aceest-fitness:test target ..."
docker build --target test -t "aceest-fitness:test" .

echo -e "\n=== Local Image Inventory ==="
docker images | grep "aceest-fitness" || true

if [ "$PUSH_IMAGES" = "true" ] || [ "$PUSH_IMAGES" = "--push" ]; then
    echo -e "\n=== Pushing Versioned Images to Docker Hub ==="
    docker push "${IMAGE_NAME}:v1.0.0"
    docker push "${IMAGE_NAME}:v2.0.0"
    docker push "${IMAGE_NAME}:canary"
    docker push "${IMAGE_NAME}:latest"
    echo "Successfully pushed all versions to Docker Hub repository: ${IMAGE_NAME}"
else
    echo -e "\n[NOTE] Pass 'true' or '--push' as second argument to push images to Docker Hub."
fi
