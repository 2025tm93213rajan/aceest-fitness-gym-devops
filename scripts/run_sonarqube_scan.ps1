# Script to execute tests, generate coverage, and run SonarScanner locally on Windows
param(
    [string]$SonarHost = "http://localhost:9000",
    [string]$SonarToken = ""
)

Write-Host "=== 1. Running Pytest and Generating XML Coverage ===" -ForegroundColor Cyan
$py = "C:\Users\RAJAN\AppData\Local\Programs\Python\Python312\python.exe"
if (!(Test-Path $py)) {
    $py = "python"
}

& $py -m pytest

if ($LASTEXITCODE -ne 0) {
    Write-Host "Tests failed. Aborting SonarQube scan." -ForegroundColor Red
    exit 1
}

Write-Host "=== 2. Running SonarScanner CLI ===" -ForegroundColor Cyan
$argsList = @(
    "-Dsonar.host.url=$SonarHost"
)
if ($SonarToken -ne "") {
    $argsList += "-Dsonar.token=$SonarToken"
}

sonar-scanner @argsList
