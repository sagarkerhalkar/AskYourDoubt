@echo off
cd /d "%~dp0"
PowerShell -NoProfile -ExecutionPolicy Bypass -File ".\INSTALL_1_5_0.ps1"
if errorlevel 1 (
  echo INSTALLATION FAILED.
  pause
  exit /b 1
)
echo INSTALLATION COMPLETED.
pause
