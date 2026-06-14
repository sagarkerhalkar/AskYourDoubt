@echo off
cd /d "%~dp0"
if not exist ngrok.exe (
  echo ngrok.exe not found in this folder.
  echo Copy ngrok.exe here or run the ngrok command from its installed location.
  pause
  exit /b 1
)
ngrok.exe http --url=https://pout-outbound-reenter.ngrok-free.dev 9000
pause
