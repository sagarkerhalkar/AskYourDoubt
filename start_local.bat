@echo off
setlocal
cd /d "%~dp0"
if exist ".env" (
  for /f "usebackq eol=# tokens=1,* delims==" %%A in (".env") do set "%%A=%%B"
)
set "PY=C:\Users\Pc\AppData\Local\Python\pythoncore-3.14-64\python.exe"
if exist "%PY%" (
  "%PY%" app.py
) else (
  py -3.14 app.py
)
pause
