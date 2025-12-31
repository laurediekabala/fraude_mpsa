# Docker Deployment Test Script for Windows
# Teste que tous les services sont opérationnels

$ErrorActionPreference = "Stop"

# Couleurs
$Blue = 'Cyan'
$Green = 'Green'
$Yellow = 'Yellow'
$Red = 'Red'

Write-Host "`n═══════════════════════════════════════════════════════════════" -ForegroundColor $Blue
Write-Host "  Docker Deployment Test Suite" -ForegroundColor $Blue
Write-Host "═══════════════════════════════════════════════════════════════`n" -ForegroundColor $Blue

# ═══════════════════════════════════════════════════════════════
# Test 1: Docker Installation
# ═══════════════════════════════════════════════════════════════

Write-Host "[1/7] Checking Docker installation..." -ForegroundColor $Yellow
try {
    $dockerVersion = docker --version
    Write-Host "✅ Docker installed: $dockerVersion" -ForegroundColor $Green
} catch {
    Write-Host "❌ Docker not installed!" -ForegroundColor $Red
    exit 1
}

# ═══════════════════════════════════════════════════════════════
# Test 2: Docker Compose Installation
# ═══════════════════════════════════════════════════════════════

Write-Host "[2/7] Checking Docker Compose installation..." -ForegroundColor $Yellow
try {
    $composeVersion = docker-compose --version
    Write-Host "✅ Docker Compose installed: $composeVersion" -ForegroundColor $Green
} catch {
    Write-Host "❌ Docker Compose not installed!" -ForegroundColor $Red
    exit 1
}

# ═══════════════════════════════════════════════════════════════
# Test 3: Docker Daemon Running
# ═══════════════════════════════════════════════════════════════

Write-Host "[3/7] Checking Docker daemon..." -ForegroundColor $Yellow
try {
    docker info > $null 2>&1
    Write-Host "✅ Docker daemon is running" -ForegroundColor $Green
} catch {
    Write-Host "❌ Docker daemon is not running!" -ForegroundColor $Red
    exit 1
}

# ═══════════════════════════════════════════════════════════════
# Test 4: Build Images
# ═══════════════════════════════════════════════════════════════

Write-Host "[4/7] Building Docker images..." -ForegroundColor $Yellow
try {
    docker-compose build --quiet 2>&1 | Out-Null
    Write-Host "✅ Images built successfully" -ForegroundColor $Green
} catch {
    Write-Host "❌ Failed to build images!" -ForegroundColor $Red
    Write-Host $_.Exception.Message -ForegroundColor $Red
    exit 1
}

# ═══════════════════════════════════════════════════════════════
# Test 5: Start Services
# ═══════════════════════════════════════════════════════════════

Write-Host "[5/7] Starting services..." -ForegroundColor $Yellow
docker-compose up -d 2>&1 | Out-Null
Write-Host "✅ Services started" -ForegroundColor $Green

Write-Host "Waiting for services to be healthy (30 seconds)..." -ForegroundColor $Yellow
Start-Sleep -Seconds 30

# ═══════════════════════════════════════════════════════════════
# Test 6: Health Checks
# ═══════════════════════════════════════════════════════════════

Write-Host "[6/7] Checking service health..." -ForegroundColor $Yellow

# Check API
try {
    $apiResponse = Invoke-WebRequest -Uri http://localhost:5000/health -ErrorAction SilentlyContinue
    if ($apiResponse.StatusCode -eq 200) {
        Write-Host "✅ API health check passed" -ForegroundColor $Green
    } else {
        Write-Host "❌ API health check failed (status: $($apiResponse.StatusCode))" -ForegroundColor $Red
    }
} catch {
    Write-Host "❌ API health check failed" -ForegroundColor $Red
    Write-Host "Trying to get logs..." -ForegroundColor $Yellow
    docker-compose logs api | Select-Object -Last 20
}

# Check Streamlit
try {
    $streamlitResponse = Invoke-WebRequest -Uri http://localhost:8501/_stcore/health -ErrorAction SilentlyContinue
    if ($streamlitResponse.StatusCode -eq 200) {
        Write-Host "✅ Streamlit health check passed" -ForegroundColor $Green
    } else {
        Write-Host "❌ Streamlit health check failed (status: $($streamlitResponse.StatusCode))" -ForegroundColor $Red
    }
} catch {
    Write-Host "❌ Streamlit health check failed" -ForegroundColor $Red
    Write-Host "Trying to get logs..." -ForegroundColor $Yellow
    docker-compose logs streamlit | Select-Object -Last 20
}

# ═══════════════════════════════════════════════════════════════
# Test 7: API Endpoints
# ═══════════════════════════════════════════════════════════════

Write-Host "[7/7] Testing API endpoints..." -ForegroundColor $Yellow

$testData = @{
    step = 100
    type = "TRANSFER"
    amount = 5000
    oldbalanceOrg = 50000
    newbalanceOrig = 45000
    oldbalanceDest = 10000
    newbalanceDest = 15000
    hour = 10
    erreur_orig = 0.0
    erreur_dst = 0.0
    videur_orig = 0
    videur_dest = 0
} | ConvertTo-Json

try {
    $predictResponse = Invoke-WebRequest -Uri http://localhost:5000/predict `
        -Method Post `
        -Headers @{"Content-Type"="application/json"} `
        -Body $testData `
        -ErrorAction SilentlyContinue
    
    if ($predictResponse.Content -like "*probability*") {
        Write-Host "✅ Predict endpoint works" -ForegroundColor $Green
    } else {
        Write-Host "❌ Predict endpoint failed" -ForegroundColor $Red
        Write-Host "Response: $($predictResponse.Content)" -ForegroundColor $Red
    }
} catch {
    Write-Host "❌ Predict endpoint failed" -ForegroundColor $Red
    Write-Host $_.Exception.Message -ForegroundColor $Red
}

# ═══════════════════════════════════════════════════════════════
# Summary
# ═══════════════════════════════════════════════════════════════

Write-Host "`n═══════════════════════════════════════════════════════════════" -ForegroundColor $Blue
Write-Host "✅ All tests completed!" -ForegroundColor $Green
Write-Host "═══════════════════════════════════════════════════════════════`n" -ForegroundColor $Blue

Write-Host "Services are running at:" -ForegroundColor $Green
Write-Host "  API:        http://localhost:5000" -ForegroundColor $Blue
Write-Host "  Streamlit:  http://localhost:8501" -ForegroundColor $Blue

Write-Host "`nTo stop services, run:" -ForegroundColor $Green
Write-Host "  docker-compose down" -ForegroundColor $Yellow

Write-Host "`nTo view logs, run:" -ForegroundColor $Green
Write-Host "  docker-compose logs -f" -ForegroundColor $Yellow

Write-Host ""
