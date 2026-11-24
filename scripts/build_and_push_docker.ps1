# Script to build and push multi-version container images to Docker Hub
param(
    [string]$DockerUser = "2025tm93213rajan",
    [switch]$Push = $false
)

$imageName = "$DockerUser/aceest-fitness"
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " Building Multi-Version Docker Images for $imageName" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# 1. Build v1.0.0 (Baseline Release)
Write-Host "`n[1/4] Building aceest-fitness:v1.0.0 ..." -ForegroundColor Green
docker build --build-arg APP_VERSION=1.0.0 --build-arg APP_RELEASE=v1-core -t "${imageName}:v1.0.0" -t "aceest-fitness:v1.0.0" .

# 2. Build v2.0.0 (Enhanced Release with Analytics)
Write-Host "`n[2/4] Building aceest-fitness:v2.0.0 and :latest ..." -ForegroundColor Green
docker build --build-arg APP_VERSION=2.0.0 --build-arg APP_RELEASE=v2-analytics -t "${imageName}:v2.0.0" -t "${imageName}:latest" -t "aceest-fitness:v2.0.0" -t "aceest-fitness:latest" .

# 3. Build v2.1.0-canary (Canary Release)
Write-Host "`n[3/4] Building aceest-fitness:canary ..." -ForegroundColor Green
docker build --build-arg APP_VERSION=2.1.0-canary --build-arg APP_RELEASE=v2.1-canary -t "${imageName}:canary" -t "aceest-fitness:canary" .

# 4. Build Test Target Image
Write-Host "`n[4/4] Building aceest-fitness:test target ..." -ForegroundColor Green
docker build --target test -t "aceest-fitness:test" .

Write-Host "`n=== Local Image Inventory ===" -ForegroundColor Cyan
docker images | Select-String "aceest-fitness"

if ($Push) {
    Write-Host "`n=== Pushing Versioned Images to Docker Hub ===" -ForegroundColor Yellow
    docker push "${imageName}:v1.0.0"
    docker push "${imageName}:v2.0.0"
    docker push "${imageName}:canary"
    docker push "${imageName}:latest"
    Write-Host "Successfully pushed all versions to Docker Hub repository: $imageName" -ForegroundColor Green
} else {
    Write-Host "`n[NOTE] Pass '-Push' parameter to automatically push to Docker Hub once logged in." -ForegroundColor DarkGray
}
