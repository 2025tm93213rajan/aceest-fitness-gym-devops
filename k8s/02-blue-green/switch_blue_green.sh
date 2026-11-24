#!/usr/bin/env bash
# Switch production traffic between Blue and Green deployments (Linux / Prayogshala)
set -e

TARGET="${1:-green}"
if [ "$TARGET" != "blue" ] && [ "$TARGET" != "green" ]; then
    echo "Usage: $0 [blue|green]"
    exit 1
fi

echo "Switching active production service selector to role: ${TARGET} ..."
kubectl patch service aceest-production-service -n aceest-fitness -p "{\"spec\":{\"selector\":{\"role\":\"${TARGET}\"}}}"
echo "Successfully switched production traffic to ${TARGET}!"
kubectl get service aceest-production-service -n aceest-fitness -o wide
