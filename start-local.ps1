# Script pour démarrer rapidement l'application en mode local
# Utilisation: .\start-local.ps1

$ErrorActionPreference = "Continue"

# Couleurs
$Yellow = 'Yellow'
$Green = 'Green'
$Red = 'Red'
$Cyan = 'Cyan'

Write-Host "============================================" -ForegroundColor $Cyan
Write-Host "🐍 FRAUDE MPSA - Démarrage Local (Python)" -ForegroundColor $Cyan
Write-Host "============================================" -ForegroundColor $Cyan
Write-Host ""

# Déterminer le répertoire du script
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = $ScriptDir

Write-Host "📁 Répertoire: $ProjectRoot" -ForegroundColor $Green
Write-Host ""

# Vérifier Python
Write-Host "🔍 Vérification de Python..." -ForegroundColor $Cyan
try {
    $PythonVersion = python --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ $PythonVersion" -ForegroundColor $Green
    } else {
        Write-Host "❌ Python non trouvé!" -ForegroundColor $Red
        Write-Host "   Installez Python 3.11+ depuis python.org"
        exit 1
    }
} catch {
    Write-Host "❌ Erreur lors de la vérification de Python" -ForegroundColor $Red
    exit 1
}

Write-Host ""

# Vérifier/Créer venv
Write-Host "🔍 Vérification de l'environnement virtual..." -ForegroundColor $Cyan
$VenvPath = Join-Path $ProjectRoot ".venv"
$PythonExe = Join-Path $VenvPath "Scripts\python.exe"

if (Test-Path $PythonExe) {
    Write-Host "✅ Virtual environment trouvé" -ForegroundColor $Green
} else {
    Write-Host "⚠️  Virtual environment non trouvé" -ForegroundColor $Yellow
    Write-Host "📦 Création du virtual environment..." -ForegroundColor $Cyan
    
    python -m venv $VenvPath
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Virtual environment créé" -ForegroundColor $Green
    } else {
        Write-Host "❌ Impossible de créer le virtual environment" -ForegroundColor $Red
        exit 1
    }
}

Write-Host ""

# Activer venv
Write-Host "🔧 Activation du virtual environment..." -ForegroundColor $Cyan
& "$VenvPath\Scripts\Activate.ps1"

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Virtual environment activé" -ForegroundColor $Green
} else {
    Write-Host "❌ Erreur lors de l'activation" -ForegroundColor $Red
    exit 1
}

Write-Host ""

# Vérifier les dépendances
Write-Host "📦 Vérification des dépendances..." -ForegroundColor $Cyan
$RequirementsFile = Join-Path $ProjectRoot "requirements.txt"

if (-not (Test-Path $RequirementsFile)) {
    Write-Host "❌ requirements.txt non trouvé!" -ForegroundColor $Red
    exit 1
}

# Vérifier si flask est installé
try {
    python -c "import flask" 2>&1 > $null
    if ($LASTEXITCODE -ne 0) {
        throw "Flask not installed"
    }
    Write-Host "✅ Dépendances OK" -ForegroundColor $Green
} catch {
    Write-Host "⚠️  Installation des dépendances..." -ForegroundColor $Yellow
    pip install --upgrade pip > $null 2>&1
    pip install -r $RequirementsFile
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Dépendances installées" -ForegroundColor $Green
    } else {
        Write-Host "❌ Erreur lors de l'installation des dépendances" -ForegroundColor $Red
        exit 1
    }
}

Write-Host ""
Write-Host "============================================" -ForegroundColor $Cyan
Write-Host "🚀 Démarrage des services" -ForegroundColor $Cyan
Write-Host "============================================" -ForegroundColor $Cyan
Write-Host ""

# Vérifier les ports disponibles
function Test-Port {
    param([int]$Port)
    $TCPClient = New-Object Net.Sockets.TcpClient
    try {
        $TCPClient.Connect("127.0.0.1", $Port)
        $TCPClient.Close()
        return $true
    } catch {
        return $false
    }
}

Write-Host "🔍 Vérification des ports..." -ForegroundColor $Cyan

$FlaskPort = 5000
$StreamlitPort = 8501

if (Test-Port $FlaskPort) {
    Write-Host "⚠️  Port $FlaskPort déjà utilisé!" -ForegroundColor $Yellow
    $FlaskPort = 5001
    Write-Host "   Utilisation du port $FlaskPort à la place" -ForegroundColor $Yellow
}

if (Test-Port $StreamlitPort) {
    Write-Host "⚠️  Port $StreamlitPort déjà utilisé!" -ForegroundColor $Yellow
    $StreamlitPort = 8502
    Write-Host "   Utilisation du port $StreamlitPort à la place" -ForegroundColor $Yellow
}

Write-Host ""

# Démarrer l'API Flask
Write-Host "📊 Démarrage de l'API Flask..." -ForegroundColor $Cyan
Write-Host "   Port: $FlaskPort" -ForegroundColor $Green

$FlaskScript = Join-Path $ProjectRoot "api_flask\app.py"
Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "cd '$ProjectRoot'; .\.venv\Scripts\Activate.ps1; python '$FlaskScript' --port=$FlaskPort"
)

# Attendre un peu
Start-Sleep -Seconds 3

Write-Host "✅ API Flask démarrée" -ForegroundColor $Green
Write-Host ""

# Démarrer Streamlit
Write-Host "🎨 Démarrage de Streamlit..." -ForegroundColor $Cyan
Write-Host "   Port: $StreamlitPort" -ForegroundColor $Green

$StreamlitScript = Join-Path $ProjectRoot "streamlit\app.py"
Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "cd '$ProjectRoot'; .\.venv\Scripts\Activate.ps1; streamlit run '$StreamlitScript' --server.port=$StreamlitPort --server.address=localhost"
)

Write-Host "✅ Streamlit démarrée" -ForegroundColor $Green
Write-Host ""

Write-Host "============================================" -ForegroundColor $Cyan
Write-Host "✅ Services en cours d'exécution" -ForegroundColor $Cyan
Write-Host "============================================" -ForegroundColor $Cyan
Write-Host ""
Write-Host "📊 API Flask:      http://localhost:$FlaskPort" -ForegroundColor $Green
Write-Host "🎨 Streamlit:      http://localhost:$StreamlitPort" -ForegroundColor $Green
Write-Host ""
Write-Host "💡 Commandes utiles:" -ForegroundColor $Yellow
Write-Host "   - Ctrl+C pour arrêter une service"
Write-Host "   - Fermer les fenêtres PowerShell pour arrêter complètement"
Write-Host ""
Write-Host "🚀 Prêt à utiliser! Ouvrez votre navigateur et visitez l'URL ci-dessus." -ForegroundColor $Cyan
Write-Host ""

# Garder la fenêtre ouverte
Write-Host "Appuyez sur Ctrl+C pour fermer..." -ForegroundColor $Yellow
Read-Host
