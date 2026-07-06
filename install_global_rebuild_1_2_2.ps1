$ErrorActionPreference = 'Stop'
$Source = Split-Path -Parent $MyInvocation.MyCommand.Path
$Target = 'D:\AskYourDoubtGlobal'
$Legacy = 'D:\AskYourDoubtV1'

function Resolve-Python {
    $known = @(
        "$env:LOCALAPPDATA\Python\pythoncore-3.14-64\python.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python314\python.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python313\python.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe"
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
Write-Host 'AskYourDoubt Global Rebuild 1.2.2 - Visual QA Fixed' -ForegroundColor Cyan
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
    Write-Host "Creating safety backup: $Backup" -ForegroundColor Yellow
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
$ExcludedTopLevel = @('device_test_results','.pytest_cache','test_results')
Get-ChildItem $Source -Force | Where-Object { $ExcludedTopLevel -notcontains $_.Name } | ForEach-Object {
    Copy-Item $_.FullName $Target -Recurse -Force
}

# Remove copied Python caches; they are never part of a release.
Get-ChildItem $Target -Directory -Recurse -Force -ErrorAction SilentlyContinue |
    Where-Object { $_.Name -eq '__pycache__' } |
    Remove-Item -Recurse -Force -ErrorAction SilentlyContinue

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

if (-not (Test-Path "$Target\database.db") -and (Test-Path "$Legacy\database.db")) {
    Write-Host 'Importing legacy database...'
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
    Write-Host "Preserved BASE_URL: $PreservedBaseUrl" -ForegroundColor Green
}

Set-Location $Target
Write-Host '[1/6] Verifying dependency resolution...'
Invoke-Python -m pip install --dry-run -r requirements-dev.txt

Write-Host '[2/6] Installing runtime and test dependencies...'
Invoke-Python -m pip install -r requirements-dev.txt

Write-Host '[3/6] Compiling Python code...'
Invoke-Python -m compileall -q app.py db.py auth.py utils.py routes

Write-Host '[4/6] Importing routes and migrating database...'
Invoke-Python -c "import app; print('Registered routes:', len(list(app.app.url_map.iter_rules())))"

Write-Host '[5/6] Running automated integration and UI contract tests...'
Invoke-Python -m pytest -q tests

Write-Host '[6/6] Running the 12-device Chromium responsive matrix...'
Invoke-Python run_device_matrix.py

Write-Host ''
Write-Host 'VERSION 1.2.2 INSTALLED. TESTS COMPLETED.' -ForegroundColor Green
Write-Host "Application: $Target"
Write-Host "Latest device result pointer: $Target\device_test_results\LATEST_RUN.txt"
Write-Host "Start locally: $Target\start_local.bat"
Write-Host "Run full Chromium/Firefox/WebKit matrix: $Target\run_browser_matrix.bat"
Write-Host ''
Write-Host 'NOTE: Full Firefox/WebKit PASS is only valid after run_browser_matrix.bat succeeds on this Windows machine.' -ForegroundColor Yellow

Remove-Item $PreserveRoot -Recurse -Force -ErrorAction SilentlyContinue
