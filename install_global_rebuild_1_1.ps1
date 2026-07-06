$ErrorActionPreference = 'Stop'
$Source = Split-Path -Parent $MyInvocation.MyCommand.Path
$Target = 'D:\AskYourDoubtGlobal'
$Legacy = 'D:\AskYourDoubtV1'
$Python = 'C:\Users\Pc\AppData\Local\Python\pythoncore-3.14-64\python.exe'
if (-not (Test-Path $Python)) { $Python = 'python' }

Write-Host '=======================================================' -ForegroundColor Cyan
Write-Host 'AskYourDoubt Global Rebuild 1.1 - International Update' -ForegroundColor Cyan
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

if (Test-Path $Target) {
    $Stamp = Get-Date -Format 'yyyyMMdd_HHmmss'
    $Backup = "D:\AskYourDoubtGlobal_BACKUP_$Stamp"
    Write-Host "Creating full safety backup: $Backup" -ForegroundColor Yellow
    Copy-Item $Target $Backup -Recurse -Force
} else {
    New-Item -ItemType Directory -Path $Target -Force | Out-Null
}

if ((Resolve-Path $Source).Path -ne (Resolve-Path $Target).Path) {
    Write-Host 'Updating application code and UI...'
    Get-ChildItem $Source -Force | ForEach-Object {
        Copy-Item $_.FullName $Target -Recurse -Force
    }
}

# For a fresh install only, import legacy data when available.
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
Write-Host '[1/4] Installing runtime dependencies...'
& $Python -m pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) { throw 'Dependency installation failed.' }

Write-Host '[2/4] Compiling Python code...'
& $Python -m compileall -q app.py db.py auth.py utils.py routes
if ($LASTEXITCODE -ne 0) { throw 'Python compile failed.' }

Write-Host '[3/4] Importing routes and migrating database...'
& $Python -c "import app; print('Registered routes:', len(list(app.app.url_map.iter_rules())))"
if ($LASTEXITCODE -ne 0) { throw 'Application import or migration failed.' }

Write-Host '[4/4] Running automated integration tests...'
& $Python -m pytest -q
if ($LASTEXITCODE -ne 0) { throw 'Automated tests failed.' }

Write-Host ''
Write-Host 'UPDATE INSTALLED AND ALL INTEGRATION TESTS PASSED.' -ForegroundColor Green
Write-Host "Application: $Target"
Write-Host "Start locally: $Target\start_local.bat"
Write-Host "Start Waitress: $Target\start_waitress.bat"
Write-Host "Full debug: $Target\run_debug_ci_cd.bat"
