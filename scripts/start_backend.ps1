<#
.SYNOPSIS
    Démarre le backend Sentinelle AIOps (FastAPI + scheduler) sur http://localhost:8000

.DESCRIPTION
    - Crée le venv s'il n'existe pas (dossier venv_env/) et installe les dépendances.
    - Vérifie que le port 8000 est libre avant de lancer.
    - Lance uvicorn avec le working directory backend/ (la base SQLite y est résolue
      par app/core/config.py, quelle que soit la commande d'appel).

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File scripts\start_backend.ps1
#>
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

$VenvPython = Join-Path $Root "venv_env\Scripts\python.exe"
$BackendDir = Join-Path $Root "backend"
$Port = 8000

# ── 1. venv + dépendances ────────────────────────────────────────────────
if (-not (Test-Path $VenvPython)) {
    Write-Host "[start_backend] venv introuvable : création de venv_env/ ..." -ForegroundColor Yellow
    $SystemPython = if (Get-Command py -ErrorAction SilentlyContinue) { "py" } else { "python" }
    if ($SystemPython -eq "py") { & py -3 -m venv venv_env } else { & $SystemPython -m venv venv_env }
    if (-not (Test-Path $VenvPython)) { Write-Error "Echec de création du venv."; exit 1 }
    & $VenvPython -m pip install --upgrade pip --quiet
    Write-Host "[start_backend] Installation des dépendances (premier lancement, ~2 min) ..." -ForegroundColor Yellow
    & $VenvPython -m pip install -r requirements.txt --quiet
}

# ── 2. port libre ? ──────────────────────────────────────────────────────
$busy = Get-NetTCPConnection -State Listen -LocalPort $Port -ErrorAction SilentlyContinue
if ($busy) {
    Write-Error "Le port $Port est déjà occupé (PID $($busy.OwningProcess)). Arrêtez le service existant."
    exit 1
}

# ── 3. lancement ─────────────────────────────────────────────────────────
Write-Host "[start_backend] Backend sur http://localhost:$Port/docs  (Ctrl+C pour arrêter)" -ForegroundColor Green
Write-Host "[start_backend] Scheduler actif : télémétrie 10s / TTF 30s / santé 60s." -ForegroundColor DarkGray
Set-Location $BackendDir
& $VenvPython -m uvicorn main:app --host 127.0.0.1 --port $Port
