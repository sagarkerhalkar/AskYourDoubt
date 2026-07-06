@echo off
setlocal
cd /d "%~dp0"
PowerShell -NoProfile -ExecutionPolicy Bypass -File ".\tools\run_quality_gate.ps1" -FullBrowserMatrix -DockerSmoke
set EXITCODE=%ERRORLEVEL%
echo.
if not "%EXITCODE%"=="0" (
  echo AskYourDoubt 1.5.0 FULL QA FAILED. Read test_results\LATEST_QUALITY_GATE.md.
) else (
  echo AskYourDoubt 1.5.0 FULL QA PASSED. Read test_results\LATEST_QUALITY_GATE.md.
)
pause
exit /b %EXITCODE%
