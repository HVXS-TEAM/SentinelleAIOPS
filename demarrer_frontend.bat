@echo off
rem Sentinelle AIOps - demarre le frontend (Streamlit) sur http://localhost:8501
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\start_frontend.ps1"
pause
