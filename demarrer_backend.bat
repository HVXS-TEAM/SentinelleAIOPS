@echo off
rem Sentinelle AIOps - demarre le backend (FastAPI) sur http://localhost:8000
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\start_backend.ps1"
pause
