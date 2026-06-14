@echo off
setlocal
cd /d "%~dp0"
set PY=C:\Users\Pc\AppData\Local\Python\pythoncore-3.14-64\python.exe
if not exist "%PY%" set PY=python

echo =======================================================
echo AskYourDoubt 1.2 - Device and Responsive Browser Matrix
echo =======================================================
echo Installing test dependencies...
"%PY%" -m pip install -r requirements-dev.txt
if errorlevel 1 goto :fail

echo Running 12-device Chromium rendering matrix...
"%PY%" run_device_matrix.py
if errorlevel 1 goto :fail

echo.
echo PASS. Open:
echo device_test_results\DEVICE_MATRIX_REPORT.md
echo device_test_results\screenshots
pause
exit /b 0

:fail
echo FAILED. Read the error above.
pause
exit /b 1
