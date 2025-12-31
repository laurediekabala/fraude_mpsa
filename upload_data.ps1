# Script pour uploader un fichier CSV volumineux via curl/PowerShell
# Utilisation: .\upload_data.ps1 -CsvFile "C:\path\to\MPSA.csv"

param(
    [Parameter(Mandatory=$true)]
    [string]$CsvFile,
    
    [string]$ApiUrl = "http://localhost:5000",
    [int]$MaxRows = 50000,
    [float]$SampleRatio = 1.0
)

# Vérifier que le fichier existe
if (-not (Test-Path $CsvFile)) {
    Write-Host "❌ Fichier non trouvé: $CsvFile" -ForegroundColor Red
    exit 1
}

$FilePath = (Get-Item $CsvFile).FullName
$FileName = (Get-Item $CsvFile).Name
$FileSizeMB = [math]::Round((Get-Item $CsvFile).Length / 1MB, 2)

Write-Host "📤 Upload en cours..." -ForegroundColor Cyan
Write-Host "  📄 Fichier: $FileName"
Write-Host "  📊 Taille: $FileSizeMB MB"
Write-Host "  📈 Lignes max: $MaxRows"
Write-Host "  🎯 Sampling: $([math]::Round($SampleRatio * 100, 1))%"
Write-Host ""

try {
    $Endpoint = "$ApiUrl/drift/upload/training-data"
    
    # Utiliser curl pour l'upload (évite les limites de Streamlit)
    $Form = @{
        file = Get-Item -Path $FilePath
        max_rows = $MaxRows
        sample_ratio = $SampleRatio
    }
    
    $Response = Invoke-WebRequest `
        -Uri $Endpoint `
        -Method Post `
        -Form $Form `
        -ErrorAction Stop
    
    if ($Response.StatusCode -eq 200) {
        $Result = $Response.Content | ConvertFrom-Json
        Write-Host "✅ Upload réussi!" -ForegroundColor Green
        Write-Host "  ✓ Baseline créée avec $($Result.baseline_summary.total_samples) échantillons"
        Write-Host "  ✓ Créée le: $($Result.baseline_summary.created_at)"
    }
    else {
        Write-Host "❌ Erreur API ($($Response.StatusCode)): $($Response.Content)" -ForegroundColor Red
        exit 1
    }
}
catch {
    if ($_.Exception.Message -like "*Connection refused*") {
        Write-Host "❌ Erreur de connexion: Impossible de contacter $ApiUrl" -ForegroundColor Red
        Write-Host "   Vérifiez que le serveur Flask est en cours d'exécution" -ForegroundColor Yellow
    }
    else {
        Write-Host "❌ Erreur: $($_.Exception.Message)" -ForegroundColor Red
    }
    exit 1
}
