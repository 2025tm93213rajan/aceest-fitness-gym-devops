#!/usr/bin/env bash
# Script to execute tests, generate coverage, and run SonarScanner on Linux / Prayogshala
set -e

SONAR_HOST="${1:-http://localhost:9000}"
SONAR_TOKEN="${2:-}"

echo "=== 1. Executing Pytest & Generating Coverage Reports ==="
python3 -m pytest

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
