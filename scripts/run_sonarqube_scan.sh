#!/usr/bin/env bash
# Script to execute tests, generate coverage, and run SonarScanner on Linux / Prayogshala
set -e

SONAR_HOST="${1:-http://localhost:9000}"
SONAR_TOKEN="${2:-}"

echo "=== 1. Executing Pytest & Generating Coverage Reports ==="
if command -v pytest &>/dev/null || python3 -m pytest --version &>/dev/null 2>&1; then
    python3 -m pytest || true
else
    echo "Using Docker test image for Pytest execution..."
    docker run --rm -v "$(pwd)/reports:/app/reports" aceest-fitness:test python -m pytest || true
fi

echo "=== 2. Running SonarScanner CLI ==="
ARGS=("-Dsonar.host.url=$SONAR_HOST")
if [ -n "$SONAR_TOKEN" ]; then
    ARGS+=("-Dsonar.token=$SONAR_TOKEN")
fi

if command -v sonar-scanner &>/dev/null; then
    sonar-scanner "${ARGS[@]}"
else
    echo "Local sonar-scanner not found, executing via official Docker container..."
    docker run --rm --network host \
        -v "$(pwd):/usr/src" \
        sonarsource/sonar-scanner-cli "${ARGS[@]}"
fi
