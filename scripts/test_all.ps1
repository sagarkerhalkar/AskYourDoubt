param(
    [switch]$FullBrowserMatrix
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $Root

$Stamp = Get-Date -Format "yyyyMMdd_HHmmss_fff"
$Run = Join-Path $Root "test_results\qa_runs\$Stamp"
$Temp = Join-Path $Run "temp"

New-Item -ItemType Directory -Force $Temp | Out-Null
$env:TEMP = $Temp
$env:TMP = $Temp
$env:AYD_DEVICE_RESULTS_ROOT = Join-Path $Run "device_results"

$Python = "py"
$PythonPrefix = @("-3.14")

function Invoke-Python {
    param([Parameter(ValueFromRemainingArguments=$true)][string[]]$Arguments)
    & $Python @PythonPrefix @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Python command failed: $($Arguments -join ' ')"
    }
}

Write-Host "QA evidence: $Run" -ForegroundColor Cyan

Invoke-Python -m pip install --dry-run -r requirements-dev.txt
Invoke-Python -m compileall -q app.py db.py auth.py utils.py routes
Invoke-Python -c "import app; rules=list(app.app.url_map.iter_rules()); print('Registered routes:',len(rules)); assert len(rules)>=45"
Invoke-Python -m pytest -q tests --basetemp (Join-Path $Run "pytest_core") -p no:cacheprovider --junitxml (Join-Path $Run "core-junit.xml")
Invoke-Python run_device_matrix.py

if ($FullBrowserMatrix) {
    Invoke-Python -m playwright install chromium firefox webkit
    Invoke-Python -m pytest -q browser_tests --browser chromium --browser firefox --browser webkit --basetemp (Join-Path $Run "pytest_browser") -p no:cacheprovider --junitxml (Join-Path $Run "browser-junit.xml")
}

Write-Host "QA PASSED. Evidence: $Run" -ForegroundColor Green
