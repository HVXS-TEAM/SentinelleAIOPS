<#
.SYNOPSIS
    Préflight de l'environnement Sentinelle AIOps (ne lance rien).

.DESCRIPTION
    Vérifie : version Python, présence du venv + dépendances clés,
    base SQLite présente, disponibilité des ports 8000/8501.

    Code de sortie : 0 = tout OK, 1 = au moins un problème bloquant.

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File scripts\check_env.ps1
#>
# Préférence explicite : les tracebacks des tests d'import (stderr) ne doivent
# JAMAIS interrompre le préflight, même si ce script est appelé par un parent
# avec $ErrorActionPreference = "Stop" (cas de start_all.ps1).
$ErrorActionPreference = "Continue"
$Root = Split-Path -Parent $PSScriptRoot
$fail = $false

function Check([string]$Label, [bool]$Ok, [string]$Hint = "") {
    if ($Ok) {
        Write-Host "  [OK]   $Label" -ForegroundColor Green
    } else {
        Write-Host "  [ECHEC] $Label" -ForegroundColor Red
        if ($Hint) { Write-Host "          -> $Hint" -ForegroundColor DarkYellow }
        $script:fail = $true
    }
}

Write-Host "── Sentinelle AIOps — préflight ─────────────────────"

# ── 1. Python du venv ────────────────────────────────────────────────────
$VenvPython = Join-Path $Root "venv_env\Scripts\python.exe"
$pyOk = Test-Path $VenvPython
Check "venv venv_env/ présent" $pyOk "Le venv est créé automatiquement au premier lancement (start_*.ps1)."
$pyVersion = ""
if ($pyOk) {
    $pyVersion = (& $VenvPython --version 2>&1) -replace "Python ", ""
    $major = [int]($pyVersion.Split(".")[0]); $minor = [int]($pyVersion.Split(".")[1])
    Check "Python >= 3.11 (détecté : $pyVersion)" (($major -gt 3) -or ($major -eq 3 -and $minor -ge 11)) "Reinstallez le venv avec Python 3.11+."
}

# ── 2. dépendances clés ──────────────────────────────────────────────────
if ($pyOk) {
    # Dépendances critiques : sans elles, l'app ne démarre pas.
    $critical = @("fastapi", "uvicorn", "sqlalchemy", "streamlit", "pandas", "plotly")
    $missing = @()
    foreach ($m in $critical) {
        # 2>&1 : avale le traceback en cas d'import manquant (évite tout NativeCommandError)
        $null = & $VenvPython -c "import $m" 2>&1
        if ($LASTEXITCODE -ne 0) { $missing += $m }
    }
    Check "dépendances critiques installées (fastapi, uvicorn, sqlalchemy, streamlit, pandas, plotly)" ($missing.Count -eq 0) ("Manquantes : " + ($missing -join ", ") + " -> pip install -r requirements.txt")

    # scikit-learn : OPTIONNEL (security_service a un repli statistique sans sklearn).
    # Un avertissement seul ne bloque pas le démarrage — cas typique : réseau coupé
    # pendant pip install scikit-learn.
    $null = & $VenvPython -c "import sklearn" 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  [ATTN]  scikit-learn absent : détection d'anomalies en mode repli statistique" -ForegroundColor Yellow
        Write-Host "          -> pip install scikit-learn (recommandé avant une soutenance)" -ForegroundColor DarkYellow
    } else {
        Write-Host "  [OK]   scikit-learn présent (Isolation Forest actif)" -ForegroundColor Green
    }
}

# ── 2b. version Streamlit (D1 : modernisation 1.65.0, refresh natif) ──────────
$stVersion = (& $VenvPython -c "import streamlit; print(streamlit.__version__)" 2>$null | Select-Object -Last 1)
if ($stVersion) {
    $stVersion = "$stVersion".Trim()
    $parts = $stVersion.Split(".")
    $stOk = ([int]$parts[0] -gt 1) -or (([int]$parts[0] -eq 1) -and ([int]$parts[1] -ge 65))
    Check "streamlit >= 1.65 (détecté : $stVersion)" $stOk "Installez le wheel offline : pip install --no-index streamlit-1.65.0-py3-none-any.whl"
} else {
    Check "streamlit détectable" $false "Réinstallez les dépendances du frontend."
}

# ── 3. base SQLite ───────────────────────────────────────────────────────
$db = Join-Path $Root "backend\sentinelle_aiops.db"
Check "base backend/sentinelle_aiops.db présente" (Test-Path $db) "Lancez 'py scripts\init_db.py' (ATTENTION : recrée la base et écrase les données) ou démarrez le backend (création auto)."

# ── 4. ports ─────────────────────────────────────────────────────────────
foreach ($p in 8000, 8501) {
    $busy = Get-NetTCPConnection -State Listen -LocalPort $p -ErrorAction SilentlyContinue
    Check "port $p disponible" (-not $busy) "Occupé par le PID $($busy.OwningProcess) — arrêtez ce processus."
}

Write-Host "──────────────────────────────────────────────────────"
if ($fail) {
    Write-Host " RÉSULTAT : PROBLÈMES DÉTECTÉS" -ForegroundColor Red
    exit 1
} else {
    Write-Host " RÉSULTAT : ENVIRONNEMENT PRÊT" -ForegroundColor Green
    exit 0
}
