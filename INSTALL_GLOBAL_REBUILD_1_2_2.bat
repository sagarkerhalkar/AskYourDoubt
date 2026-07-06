@echo off
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0install_global_rebuild_1_2_2.ps1"
if errorlevel 1 (
  echo.
  echo INSTALLATION OR QA FAILED. Read the error above.
) else (
  echo.
  echo INSTALLATION AND LOCAL QA COMPLETED.
)
pause
