<#
.SYNOPSIS
    Démarre le frontend Sentinelle AIOps (Streamlit) sur http://localhost:8501

.DESCRIPTION
    - Crée le venv s'il n'existe pas (dossier venv_env/) et installe les dépendances.
    - Vérifie que le port 8501 est libre avant de lancer.
    - Le backend doit tourner sur le port 8000 (sinon l'app affiche le bandeau
      « mode hors-ligne » au lieu de planter).

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File scripts\start_frontend.ps1
#>
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

$VenvPython = Join-Path $Root "venv_env\Scripts\python.exe"
$App = Join-Path $Root "frontend\app.py"
$Port = 8501

# ── 1. venv + dépendances ────────────────────────────────────────────────
if (-not (Test-Path $VenvPython)) {
    Write-Host "[start_frontend] venv introuvable : création de venv_env/ ..." -ForegroundColor Yellow
    $SystemPython = if (Get-Command py -ErrorAction SilentlyContinue) { "py" } else { "python" }
    if ($SystemPython -eq "py") { & py -3 -m venv venv_env } else { & $SystemPython -m venv venv_env }
    if (-not (Test-Path $VenvPython)) { Write-Error "Echec de création du venv."; exit 1 }
    & $VenvPython -m pip install --upgrade pip --quiet
    Write-Host "[start_frontend] Installation des dépendances (premier lancement, ~2 min) ..." -ForegroundColor Yellow
    & $VenvPython -m pip install -r requirements.txt --quiet
}

# ── 2. port libre ? ──────────────────────────────────────────────────────
$busy = Get-NetTCPConnection -State Listen -LocalPort $Port -ErrorAction SilentlyContinue
if ($busy) {
    Write-Error "Le port $Port est déjà occupé (PID $($busy.OwningProcess)). Arrêtez le service existant."
    exit 1
}

# ── 3. lancement ─────────────────────────────────────────────────────────
$backendUp = $false
try {
    $r = Invoke-WebRequest -Uri "http://localhost:8000/docs" -UseBasicParsing -TimeoutSec 2
    $backendUp = ($r.StatusCode -eq 200)
} catch { }
if ($backendUp) {
    Write-Host "[start_frontend] Frontend sur http://localhost:$Port  (Ctrl+C pour arrêter)" -ForegroundColor Green
} else {
    Write-Host "[start_frontend] Frontend sur http://localhost:$Port  (Ctrl+C pour arrêter)" -ForegroundColor Green
    Write-Host "[start_frontend] ATTENTION : backend introuvable sur le port 8000 — mode hors-ligne." -ForegroundColor Yellow
}
& $VenvPython -m streamlit run $App --server.port $Port
