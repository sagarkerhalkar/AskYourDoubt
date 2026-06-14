@echo off
cd /d "%~dp0"
set PY=C:\Users\Pc\AppData\Local\Python\pythoncore-3.14-64\python.exe
if not exist "%PY%" set PY=python
"%PY%" app.py
pause
