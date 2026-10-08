<#
.SYNOPSIS
    Démarre Sentinelle AIOps en entier : backend (8000) + frontend (8501).

.DESCRIPTION
    - Vérifie l'environnement (check_env.ps1), puis lance le backend dans une
      fenêtre PowerShell dédiée et le frontend dans une autre.
    - Affiche les URLs de démarrage.

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File scripts\start_all.ps1
#>
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot

# ── 1. préflight ─────────────────────────────────────────────────────────
& (Join-Path $PSScriptRoot "check_env.ps1")
if ($LASTEXITCODE -ne 0) {
    Write-Error "Préflight échoué : corrigez les points ci-dessus avant de lancer."
    exit 1
}

# ── 2. backend (fenêtre dédiée) ──────────────────────────────────────────
Write-Host "[start_all] Lancement du backend (fenêtre PowerShell dédiée) ..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-ExecutionPolicy", "Bypass",
    "-File", "`"" + (Join-Path $PSScriptRoot "start_backend.ps1") + "`""
)

# ── 3. attente que le backend réponde ────────────────────────────────────
$ready = $false
foreach ($i in 1..30) {
    Start-Sleep -Seconds 2
    try {
        $r = Invoke-WebRequest -Uri "http://localhost:8000/docs" -UseBasicParsing -TimeoutSec 2
        if ($r.StatusCode -eq 200) { $ready = $true; break }
    } catch { }
}
if (-not $ready) {
    Write-Warning "Le backend ne répond pas encore sur le port 8000 (voir la fenêtre backend)."
}

# ── 4. frontend (fenêtre dédiée) ─────────────────────────────────────────
Write-Host "[start_all] Lancement du frontend (fenêtre PowerShell dédiée) ..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-ExecutionPolicy", "Bypass",
    "-File", "`"" + (Join-Path $PSScriptRoot "start_frontend.ps1") + "`""
)

Write-Host ""
Write-Host "════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host " Sentinelle AIOps démarré"                            -ForegroundColor Cyan
Write-Host "   API  (docs)   : http://localhost:8000/docs"         -ForegroundColor Cyan
Write-Host "   Front (app)   : http://localhost:8501"              -ForegroundColor Cyan
Write-Host " Arrêt : fermez les deux fenêtres PowerShell ouvertes." -ForegroundColor DarkGray
Write-Host "════════════════════════════════════════════════════" -ForegroundColor Cyan
