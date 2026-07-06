@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>&1
if not errorlevel 1 (
  set PY=py -3.14
) else (
  set PY=python
)

echo [1/5] Dependency resolution
%PY% -m pip install --dry-run -r requirements-dev.txt || goto :fail

echo [2/5] Python compile
%PY% -m compileall -q app.py db.py auth.py utils.py routes || goto :fail

echo [3/5] Integration and UI contract tests
%PY% -m pytest -q tests || goto :fail

echo [4/5] Responsive Chromium evidence
%PY% run_device_matrix.py || goto :fail

echo [5/5] Full Playwright browser matrix
call run_browser_matrix.bat || goto :fail

echo.
echo FULL QA PASSED ON THIS MACHINE.
pause
exit /b 0

:fail
echo.
echo QA FAILED. No success is being claimed.
pause
exit /b 1
