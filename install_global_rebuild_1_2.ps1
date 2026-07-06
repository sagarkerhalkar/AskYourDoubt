$ErrorActionPreference = 'Stop'
$Source = Split-Path -Parent $MyInvocation.MyCommand.Path
$Target = 'D:\AskYourDoubtGlobal'
$Legacy = 'D:\AskYourDoubtV1'
function Resolve-Python {
    $known = @(
        "$env:LOCALAPPDATA\Python\pythoncore-3.14-64\python.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python314\python.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python313\python.exe"
    )
    foreach ($path in $known) {
        if ($path -and (Test-Path $path)) { return @{ Exe = $path; Prefix = @() } }
    }
    $py = Get-Command py -ErrorAction SilentlyContinue
    if ($py) { return @{ Exe = $py.Source; Prefix = @('-3.14') } }
    $python = Get-Command python -ErrorAction SilentlyContinue
    if ($python) { return @{ Exe = $python.Source; Prefix = @() } }
    throw 'Python was not found. Install Python 3.14 or add Python to PATH.'
}
$ResolvedPython = Resolve-Python
$Python = $ResolvedPython.Exe
$PythonPrefix = $ResolvedPython.Prefix
function Invoke-Python {
    & $Python @PythonPrefix @args
    if ($LASTEXITCODE -ne 0) { throw "Python command failed: $($args -join ' ')" }
}

Write-Host '=======================================================' -ForegroundColor Cyan
Write-Host 'AskYourDoubt Global Rebuild 1.2 - Premium International' -ForegroundColor Cyan
Write-Host '=======================================================' -ForegroundColor Cyan
Write-Host "Source: $Source"
Write-Host "Target: $Target"

$PreservedBaseUrl = $null
if (Test-Path "$Target\config.py") {
    $CurrentConfig = Get-Content "$Target\config.py" -Raw
    if ($CurrentConfig -match "BASE_URL = os.getenv\('AYD_BASE_URL', '([^']+)'\)") {
        $PreservedBaseUrl = $Matches[1]
    }
}

$PreserveRoot = Join-Path $env:TEMP ("AskYourDoubt_preserve_" + (Get-Date -Format 'yyyyMMdd_HHmmss'))
New-Item -ItemType Directory -Path $PreserveRoot -Force | Out-Null

if (Test-Path $Target) {
    $Stamp = Get-Date -Format 'yyyyMMdd_HHmmss'
    $Backup = "D:\AskYourDoubtGlobal_BACKUP_$Stamp"
    Write-Host "Creating full safety backup: $Backup" -ForegroundColor Yellow
    Copy-Item $Target $Backup -Recurse -Force

    foreach ($item in @('database.db','ngrok.exe')) {
        if (Test-Path "$Target\$item") { Copy-Item "$Target\$item" "$PreserveRoot\$item" -Force }
    }
    foreach ($folder in @('static\uploads','static\qr','exports')) {
        if (Test-Path "$Target\$folder") {
            $dest = Join-Path $PreserveRoot $folder
            New-Item -ItemType Directory -Path (Split-Path $dest -Parent) -Force | Out-Null
            Copy-Item "$Target\$folder" $dest -Recurse -Force
        }
    }
} else {
    New-Item -ItemType Directory -Path $Target -Force | Out-Null
}

Write-Host 'Installing application code and premium UI...'
Get-ChildItem $Source -Force | ForEach-Object {
    Copy-Item $_.FullName $Target -Recurse -Force
}

# Restore preserved live data after code update.
foreach ($item in @('database.db','ngrok.exe')) {
    if (Test-Path "$PreserveRoot\$item") { Copy-Item "$PreserveRoot\$item" "$Target\$item" -Force }
}
foreach ($folder in @('static\uploads','static\qr','exports')) {
    if (Test-Path "$PreserveRoot\$folder") {
        $targetFolder = Join-Path $Target $folder
        if (Test-Path $targetFolder) { Remove-Item $targetFolder -Recurse -Force }
        New-Item -ItemType Directory -Path (Split-Path $targetFolder -Parent) -Force | Out-Null
        Copy-Item "$PreserveRoot\$folder" $targetFolder -Recurse -Force
    }
}

# Fresh install: import legacy data when available.
if (-not (Test-Path "$Target\database.db") -and (Test-Path "$Legacy\database.db")) {
    Write-Host 'Importing legacy database for the first installation...'
    Copy-Item "$Legacy\database.db" "$Target\database.db" -Force
}
if (-not (Test-Path "$Target\ngrok.exe") -and (Test-Path "$Legacy\ngrok.exe")) {
    Copy-Item "$Legacy\ngrok.exe" "$Target\ngrok.exe" -Force
}

if ($PreservedBaseUrl) {
    $ConfigPath = "$Target\config.py"
    $NewConfig = Get-Content $ConfigPath -Raw
    $NewConfig = $NewConfig -replace "BASE_URL = os.getenv\('AYD_BASE_URL', '[^']*'\)", "BASE_URL = os.getenv('AYD_BASE_URL', '$PreservedBaseUrl')"
    Set-Content $ConfigPath $NewConfig -Encoding UTF8
    Write-Host "Preserved current BASE_URL: $PreservedBaseUrl" -ForegroundColor Green
} elseif (Test-Path "$Legacy\config.py") {
    $LegacyConfig = Get-Content "$Legacy\config.py" -Raw
    if ($LegacyConfig -match 'BASE_URL\s*=\s*["'']([^"'']+)["'']') {
        $Url = $Matches[1]
        $ConfigPath = "$Target\config.py"
        $NewConfig = Get-Content $ConfigPath -Raw
        $NewConfig = $NewConfig -replace "BASE_URL = os.getenv\('AYD_BASE_URL', '[^']*'\)", "BASE_URL = os.getenv('AYD_BASE_URL', '$Url')"
        Set-Content $ConfigPath $NewConfig -Encoding UTF8
        Write-Host "Imported legacy BASE_URL: $Url" -ForegroundColor Green
    }
}

Set-Location $Target
Write-Host '[1/5] Installing runtime and test dependencies...'
Invoke-Python -m pip install -r requirements-dev.txt

Write-Host '[2/5] Compiling Python code...'
Invoke-Python -m compileall -q app.py db.py auth.py utils.py routes

Write-Host '[3/5] Importing routes and migrating database...'
Invoke-Python -c "import app; print('Registered routes:', len(list(app.app.url_map.iter_rules())))"

Write-Host '[4/5] Running automated integration tests...'
Invoke-Python -m pytest -q tests

Write-Host '[5/5] Running 12-device responsive Chromium matrix...'
Invoke-Python run_device_matrix.py

Write-Host ''
Write-Host 'VERSION 1.2.1 QA INSTALLED. CORE TESTS AND DEVICE MATRIX PASSED.' -ForegroundColor Green
Write-Host "Application: $Target"
Write-Host "Test report: $Target\device_test_results\DEVICE_MATRIX_REPORT.md"
Write-Host "Screenshots: $Target\device_test_results\screenshots"
Write-Host "Start locally: $Target\start_local.bat"
Write-Host "Start Waitress: $Target\start_waitress.bat"
Write-Host "Full debug: $Target\run_debug_ci_cd.bat"

Remove-Item $PreserveRoot -Recurse -Force -ErrorAction SilentlyContinue
