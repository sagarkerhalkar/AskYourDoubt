@echo off
setlocal
cd /d "%~dp0"
if exist ".env" (
  for /f "usebackq eol=# tokens=1,* delims==" %%A in (".env") do set "%%A=%%B"
)
if not defined AYD_PORT set "AYD_PORT=9000"
if not defined AYD_THREADS set "AYD_THREADS=8"
set "PY=C:\Users\Pc\AppData\Local\Python\pythoncore-3.14-64\python.exe"
if exist "%PY%" (
  "%PY%" -m waitress --listen=0.0.0.0:%AYD_PORT% --threads=%AYD_THREADS% app:app
) else (
  py -3.14 -m waitress --listen=0.0.0.0:%AYD_PORT% --threads=%AYD_THREADS% app:app
)
pause
