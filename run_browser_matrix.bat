@echo off
setlocal
cd /d "%~dp0"
PowerShell -NoProfile -ExecutionPolicy Bypass -File ".\tools\run_quality_gate.ps1" -FullBrowserMatrix
set EXITCODE=%ERRORLEVEL%
echo.
if not "%EXITCODE%"=="0" (
  echo FULL BROWSER MATRIX FAILED. Read the newest log in test_results.
) else (
  echo FULL BROWSER MATRIX PASSED FOR CHROMIUM, FIREFOX AND WEBKIT.
)
pause
exit /b %EXITCODE%
