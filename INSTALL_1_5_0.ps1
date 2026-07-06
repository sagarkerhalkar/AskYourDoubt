param([string]$InstallPath = 'D:\AskYourDoubtGlobal')
$ErrorActionPreference = 'Stop'
$Source = Split-Path -Parent $MyInvocation.MyCommand.Path
$sourceResolved = (Resolve-Path $Source).Path
$targetResolved = if (Test-Path $InstallPath) { (Resolve-Path $InstallPath).Path } else { $null }
if ($sourceResolved -ne $targetResolved) {
    New-Item -ItemType Directory -Force $InstallPath | Out-Null
    robocopy $Source $InstallPath /E /XD .git __pycache__ .pytest_cache test_results device_test_results /XF database.db *.zip | Out-Null
    if ($LASTEXITCODE -gt 7) { throw "Robocopy failed with code $LASTEXITCODE" }
}
Set-Location $InstallPath
$python = "$env:LOCALAPPDATA\Python\pythoncore-3.14-64\python.exe"
if (-not (Test-Path $python)) { $python = (Get-Command python -ErrorAction Stop).Source }
& $python -m pip install --upgrade pip
& $python -m pip install -r requirements.txt
if (-not (Test-Path '.env')) { Copy-Item '.env.windows.example' '.env' }
& $python -m compileall -q app.py auth.py config.py db.py utils.py routes
if ($LASTEXITCODE -ne 0) { throw 'Compile validation failed.' }
Write-Host 'AskYourDoubt 1.5.0 installed.' -ForegroundColor Green
Write-Host "Edit $InstallPath\.env, change AYD_SECRET_KEY, then run start_waitress.bat."
