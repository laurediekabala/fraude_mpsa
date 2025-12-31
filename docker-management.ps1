# Docker Management Script for Windows PowerShell
# Usage: ./docker-management.ps1 <command>

param(
    [string]$Command = "help",
    [switch]$Force
)

# Couleurs
$Colors = @{
    Blue   = 'Cyan'
    Green  = 'Green'
    Yellow = 'Yellow'
    Red    = 'Red'
}

function Write-Title {
    param([string]$Text)
    Write-Host "`n═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
    Write-Host "  $Text" -ForegroundColor Cyan
    Write-Host "═══════════════════════════════════════════════════════════════`n" -ForegroundColor Cyan
}

function Write-Info {
    param([string]$Text, [string]$Color = 'Cyan')
    Write-Host "ℹ️  $Text" -ForegroundColor $Color
}

function Write-Success {
    param([string]$Text)
    Write-Host "✅ $Text" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Text)
    Write-Host "⚠️  $Text" -ForegroundColor Yellow
}

function Write-Error-Custom {
    param([string]$Text)
    Write-Host "❌ $Text" -ForegroundColor Red
}

# ═══════════════════════════════════════════════════════════════
# HELP
# ═══════════════════════════════════════════════════════════════

function Show-Help {
    Write-Title "Fraude Detection System - Docker Management"
    
    Write-Host "Development:" -ForegroundColor Green
    Write-Host "  ./docker-management.ps1 build           - Build les images Docker"
    Write-Host "  ./docker-management.ps1 up              - Démarrer tous les services"
    Write-Host "  ./docker-management.ps1 down            - Arrêter tous les services"
    Write-Host "  ./docker-management.ps1 restart         - Redémarrer tous les services"
    Write-Host "  ./docker-management.ps1 logs            - Voir les logs (suivi)"
    Write-Host "  ./docker-management.ps1 logs-api        - Logs de l'API"
    Write-Host "  ./docker-management.ps1 logs-web        - Logs de Streamlit"
    
    Write-Host "`nTesting:" -ForegroundColor Green
    Write-Host "  ./docker-management.ps1 test            - Tester la connexion API"
    Write-Host "  ./docker-management.ps1 status          - Voir le statut"
    Write-Host "  ./docker-management.ps1 health          - Vérifier la santé"
    
    Write-Host "`nDatabase & Cleanup:" -ForegroundColor Green
    Write-Host "  ./docker-management.ps1 clean           - Nettoyer les ressources"
    Write-Host "  ./docker-management.ps1 clean-volumes   - Supprimer les volumes (⚠️)"
    Write-Host "  ./docker-management.ps1 reset           - Reset complet"
    
    Write-Host "`nAdmin:" -ForegroundColor Green
    Write-Host "  ./docker-management.ps1 shell-api       - Shell du conteneur API"
    Write-Host "  ./docker-management.ps1 shell-web       - Shell de Streamlit"
    Write-Host "  ./docker-management.ps1 stats           - Utilisation ressources"
    Write-Host "`n"
}

# ═══════════════════════════════════════════════════════════════
# BUILD & DEPLOYMENT
# ═══════════════════════════════════════════════════════════════

function Invoke-Build {
    Write-Title "Building Docker Images"
    docker-compose build
    Write-Success "Build completed!"
}

function Invoke-Up {
    Write-Title "Starting Services"
    Invoke-Build
    Write-Info "Starting containers..."
    docker-compose up -d
    
    Write-Info "Waiting for health checks (30 seconds)..." Yellow
    Start-Sleep -Seconds 30
    
    Write-Success "Services started!"
    Write-Host "📊 API:        http://localhost:5000" -ForegroundColor Blue
    Write-Host "🎨 Streamlit:  http://localhost:8501" -ForegroundColor Blue
}

function Invoke-Down {
    Write-Title "Stopping Services"
    docker-compose down
    Write-Success "Services stopped!"
}

function Invoke-Restart {
    Write-Title "Restarting Services"
    docker-compose restart
    Write-Success "Services restarted!"
}

# ═══════════════════════════════════════════════════════════════
# LOGS & MONITORING
# ═══════════════════════════════════════════════════════════════

function Get-Logs {
    Write-Info "Showing logs (Ctrl+C to stop)..." Yellow
    docker-compose logs -f
}

function Get-LogsApi {
    Write-Info "API logs (Ctrl+C to stop)..." Yellow
    docker-compose logs -f api
}

function Get-LogsWeb {
    Write-Info "Streamlit logs (Ctrl+C to stop)..." Yellow
    docker-compose logs -f streamlit
}

function Get-Status {
    Write-Title "Service Status"
    docker-compose ps
}

function Get-Health {
    Write-Title "Health Check"
    
    try {
        $apiHealth = (Invoke-WebRequest -Uri http://localhost:5000/health -ErrorAction SilentlyContinue).StatusCode
        $apiStatus = if ($apiHealth -eq 200) { "✅ Up" } else { "❌ Down" }
    } catch {
        $apiStatus = "❌ Down"
    }
    
    try {
        $streamlitHealth = (Invoke-WebRequest -Uri http://localhost:8501/_stcore/health -ErrorAction SilentlyContinue).StatusCode
        $streamlitStatus = if ($streamlitHealth -eq 200) { "✅ Up" } else { "❌ Down" }
    } catch {
        $streamlitStatus = "❌ Down"
    }
    
    Write-Host "API:       $apiStatus" -ForegroundColor Blue
    Write-Host "Streamlit: $streamlitStatus" -ForegroundColor Blue
}

# ═══════════════════════════════════════════════════════════════
# TESTING
# ═══════════════════════════════════════════════════════════════

function Invoke-Test {
    Write-Title "Testing API"
    Invoke-Up
    Write-Info "Testing endpoint..." Yellow
    
    try {
        $response = Invoke-WebRequest -Uri http://localhost:5000/health
        Write-Success "API Test Passed!"
        Write-Host $response.Content
    } catch {
        Write-Error-Custom "API Test Failed!"
        Write-Error-Custom $_.Exception.Message
    }
}

# ═══════════════════════════════════════════════════════════════
# CLEANUP
# ═══════════════════════════════════════════════════════════════

function Invoke-Clean {
    Write-Title "Cleaning Up Docker Resources"
    docker-compose down
    docker image prune -f
    docker container prune -f
    Write-Success "Cleanup completed!"
}

function Invoke-CleanVolumes {
    Write-Warning "This will delete all volumes and data!"
    $confirm = Read-Host "Continue? (y/n)"
    
    if ($confirm -eq 'y') {
        docker-compose down -v
        Write-Success "Volumes deleted!"
    } else {
        Write-Info "Operation cancelled"
    }
}

function Invoke-Reset {
    Write-Title "Resetting Docker Environment"
    Invoke-Clean
    Invoke-CleanVolumes
    docker system prune -a -f
    Write-Success "Full reset completed!"
}

# ═══════════════════════════════════════════════════════════════
# ADMIN
# ═══════════════════════════════════════════════════════════════

function Invoke-ShellApi {
    Write-Info "Opening API container shell..." Yellow
    docker exec -it fraude_api bash
}

function Invoke-ShellWeb {
    Write-Info "Opening Streamlit container shell..." Yellow
    docker exec -it fraude_streamlit bash
}

function Get-Stats {
    Write-Title "Docker Container Stats"
    docker stats --no-stream
}

function Backup-Baseline {
    Write-Title "Backing up Baseline"
    try {
        docker cp fraude_api:/app/api_flask/drift_baseline.json ./drift_baseline.backup.json 2>$null
        Write-Success "Backup completed!"
    } catch {
        Write-Warning "Baseline not found"
    }
}

# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════

switch ($Command.ToLower()) {
    "help"           { Show-Help }
    "build"          { Invoke-Build }
    "up"             { Invoke-Up }
    "down"           { Invoke-Down }
    "restart"        { Invoke-Restart }
    "logs"           { Get-Logs }
    "logs-api"       { Get-LogsApi }
    "logs-web"       { Get-LogsWeb }
    "status"         { Get-Status }
    "health"         { Get-Health }
    "test"           { Invoke-Test }
    "clean"          { Invoke-Clean }
    "clean-volumes"  { Invoke-CleanVolumes }
    "reset"          { Invoke-Reset }
    "shell-api"      { Invoke-ShellApi }
    "shell-web"      { Invoke-ShellWeb }
    "stats"          { Get-Stats }
    "backup"         { Backup-Baseline }
    default {
        Write-Error-Custom "Unknown command: $Command"
        Write-Info "Use './docker-management.ps1 help' for available commands"
    }
}
