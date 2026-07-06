@echo off
setlocal EnableExtensions EnableDelayedExpansion
cd /d "%~dp0"
where py >nul 2>&1
if not errorlevel 1 (set "PY=py -3.14") else (set "PY=python")
for /f %%I in ('powershell -NoProfile -Command "Get-Date -Format yyyyMMdd_HHmmss_fff"') do set "STAMP=%%I"
set "QA_RUN=%CD%\test_results\qa_runs\full_1_4_%STAMP%_%RANDOM%"
set "TEMP=%QA_RUN%\temp"
set "TMP=%QA_RUN%\temp"
set "AYD_DEVICE_RESULTS_ROOT=%QA_RUN%\device_results"
mkdir "%TEMP%" || goto :fail
mkdir "%AYD_DEVICE_RESULTS_ROOT%" || goto :fail

echo [1/6] Dependency resolution
%PY% -m pip install --dry-run -r requirements-dev.txt || goto :fail
echo [2/6] Python compile
%PY% -m compileall -q app.py db.py auth.py utils.py routes || goto :fail
echo [3/6] Integration and UI tests
%PY% -m pytest -q tests --basetemp "%QA_RUN%\pytest_core" -p no:cacheprovider --junitxml "%QA_RUN%\core-junit.xml" || goto :fail
echo [4/6] Responsive Chromium evidence
%PY% run_device_matrix.py || goto :fail
echo [5/6] Install Chromium Firefox WebKit
%PY% -m playwright install chromium firefox webkit || goto :fail
echo [6/6] Live browser matrix
%PY% -m pytest -q browser_tests --browser chromium --browser firefox --browser webkit --basetemp "%QA_RUN%\pytest_browser" -p no:cacheprovider --junitxml "%QA_RUN%\browser-junit.xml" || goto :fail

echo.
echo FULL QA PASSED ON THIS MACHINE.
echo Evidence: %QA_RUN%
pause
exit /b 0
:fail
echo.
echo FULL QA FAILED. No success is being claimed.
echo Evidence: %QA_RUN%
pause
exit /b 1
