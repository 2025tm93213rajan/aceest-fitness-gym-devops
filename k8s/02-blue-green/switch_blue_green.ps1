# Switch production traffic between Blue and Green deployments
param(
    [ValidateSet("blue", "green")][string]$Target = "green"
)

Write-Host "Switching active production service selector to role: $Target ..." -ForegroundColor Cyan
kubectl patch service aceest-production-service -n aceest-fitness -p "{\`"spec\`":{\`"selector\`":{\`"role\`":\`"$Target\`"}}}"
Write-Host "Successfully switched production traffic to $Target!" -ForegroundColor Green
kubectl get service aceest-production-service -n aceest-fitness -o wide
