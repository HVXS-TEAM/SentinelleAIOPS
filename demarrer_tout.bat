@echo off
rem Sentinelle AIOps - demarre backend + frontend en une commande
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\start_all.ps1"
pause
