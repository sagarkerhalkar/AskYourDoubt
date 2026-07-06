@echo off
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0install_global_rebuild_1_4_1.ps1"
if errorlevel 1 (
  echo.
  echo INSTALLATION OR CORE QA FAILED. Read the error above.
) else (
  echo.
  echo VERSION 1.4.1 INSTALLATION AND CORE QA COMPLETED.
)
pause
