@echo off
setlocal
cd /d "%~dp0"
PowerShell -NoProfile -ExecutionPolicy Bypass -File ".\tools\run_quality_gate.ps1"
set EXITCODE=%ERRORLEVEL%
echo.
if not "%EXITCODE%"=="0" (
  echo FAILED. Open test_results\LATEST_QUALITY_GATE.md and the newest quality_gate log.
) else (
  echo PASSED. See test_results\LATEST_QUALITY_GATE.md.
)
pause
exit /b %EXITCODE%
