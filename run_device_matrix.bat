@echo off
setlocal
cd /d "%~dp0"
set PY=C:\Users\Pc\AppData\Local\Python\pythoncore-3.14-64\python.exe
if not exist "%PY%" set PY=py -3.14

echo =======================================================
echo AskYourDoubt 1.5.2 - 12 Device Responsive Matrix
echo =======================================================
%PY% -m pip install -r requirements-dev.txt
if errorlevel 1 goto :fail
%PY% run_device_matrix.py
if errorlevel 1 goto :fail

echo.
echo PASS. Open device_test_results\LATEST_DEVICE_MATRIX_REPORT.md
pause
exit /b 0
:fail
echo FAILED. Read the error above.
pause
exit /b 1
