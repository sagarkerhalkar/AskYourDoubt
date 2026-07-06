@echo off
setlocal
cd /d "%~dp0"
PowerShell -NoProfile -ExecutionPolicy Bypass -File ".\install_global_rebuild_1_2.ps1"
set EXITCODE=%ERRORLEVEL%
echo.
if not "%EXITCODE%"=="0" (
  echo INSTALLATION OR QA FAILED. Read the error above.
) else (
  echo ASK YOUR DOUBT 1.2.1 QA INSTALLED AND VERIFIED.
)
pause
exit /b %EXITCODE%
