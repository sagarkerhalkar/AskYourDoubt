@echo off
cd /d "%~dp0"
start "AskYourDoubt Waitress" cmd /k start_waitress.bat
timeout /t 3 /nobreak >nul
if exist ngrok.exe start "AskYourDoubt ngrok" cmd /k start_ngrok.bat
