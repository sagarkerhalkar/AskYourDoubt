param(
    [switch]$FullBrowserMatrix
)

$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $Root

function Resolve-Python {
    $known = @(
        "$env:LOCALAPPDATA\Python\pythoncore-3.14-64\python.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python314\python.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python313\python.exe"
    )
    foreach ($path in $known) {
        if ($path -and (Test-Path $path)) {
            return @{ Exe = $path; Prefix = @() }
        }
    }

    $py = Get-Command py -ErrorAction SilentlyContinue
    if ($py) { return @{ Exe = $py.Source; Prefix = @('-3.14') } }

    $python = Get-Command python -ErrorAction SilentlyContinue
    if ($python) { return @{ Exe = $python.Source; Prefix = @() } }

    throw 'Python was not found. Install Python 3.14 or add Python to PATH.'
}

$resolved = Resolve-Python
$PythonExe = $resolved.Exe
$PythonPrefix = $resolved.Prefix

function Invoke-Python {
    param([Parameter(ValueFromRemainingArguments = $true)][string[]]$PythonArgs)
    & $PythonExe @PythonPrefix @PythonArgs
    if ($LASTEXITCODE -ne 0) {
        throw "Python command failed: $($PythonArgs -join ' ')"
    }
}

$Stamp = Get-Date -Format 'yyyyMMdd_HHmmss_fff'
$RunId = "${Stamp}_$PID"
$ResultRoot = Join-Path $Root 'test_results'
$RunRoot = Join-Path $ResultRoot "qa_runs\$RunId"
$TempRoot = Join-Path $RunRoot 'temp'
$DeviceRoot = Join-Path $RunRoot 'device_results'

New-Item -ItemType Directory -Path $TempRoot -Force | Out-Null
New-Item -ItemType Directory -Path $DeviceRoot -Force | Out-Null

# Never use the locked global pytest-of-user directory.
$env:TEMP = $TempRoot
$env:TMP = $TempRoot
$env:AYD_DEVICE_RESULTS_ROOT = $DeviceRoot
$env:PYTHONDONTWRITEBYTECODE = '1'

$Log = Join-Path $RunRoot 'quality_gate.log'
$Summary = Join-Path $ResultRoot 'LATEST_QUALITY_GATE.md'
$CoreBaseTemp = Join-Path $RunRoot 'pytest_core'
$ContractBaseTemp = Join-Path $RunRoot 'pytest_contract'
$BrowserBaseTemp = Join-Path $RunRoot 'pytest_browser'

Start-Transcript -Path $Log -Force | Out-Null
try {
    Write-Host '=======================================================' -ForegroundColor Cyan
    Write-Host 'AskYourDoubt 1.3.1 Permission-Safe QA Quality Gate' -ForegroundColor Cyan
    Write-Host '=======================================================' -ForegroundColor Cyan
    Write-Host "Project: $Root"
    Write-Host "Python: $PythonExe $($PythonPrefix -join ' ')"
    Write-Host "QA run: $RunRoot"

    Write-Host '[1/7] Installing compatible dependencies' -ForegroundColor Yellow
    Invoke-Python -PythonArgs @('-m','pip','install','--upgrade','pip')
    Invoke-Python -PythonArgs @('-m','pip','install','-r','requirements-dev.txt')

    Write-Host '[2/7] Python compile check' -ForegroundColor Yellow
    Invoke-Python -PythonArgs @('-m','compileall','-q','app.py','db.py','auth.py','utils.py','routes')

    Write-Host '[3/7] Flask import and route registration' -ForegroundColor Yellow
    Invoke-Python -PythonArgs @('-c',"import app; rules=list(app.app.url_map.iter_rules()); print('Registered routes:', len(rules)); assert len(rules) >= 45")

    Write-Host '[4/7] Integration and logic tests' -ForegroundColor Yellow
    Invoke-Python -PythonArgs @(
        '-m','pytest','-q','tests',
        '--basetemp',$CoreBaseTemp,
        '-p','no:cacheprovider',
        "--junitxml=$(Join-Path $RunRoot 'core-junit.xml')"
    )

    Write-Host '[5/7] UI/animation/mobile contract checks' -ForegroundColor Yellow
    Invoke-Python -PythonArgs @(
        '-m','pytest','-q','tests/test_quality_gate_contracts.py',
        '--basetemp',$ContractBaseTemp,
        '-p','no:cacheprovider',
        "--junitxml=$(Join-Path $RunRoot 'ui-contract-junit.xml')"
    )

    Write-Host '[6/7] 12-device Chromium responsive matrix' -ForegroundColor Yellow
    Invoke-Python -PythonArgs @('run_device_matrix.py')

    $BrowserStatus = 'NOT REQUESTED'
    if ($FullBrowserMatrix) {
        Write-Host '[7/7] Chromium + Firefox + WebKit live browser matrix' -ForegroundColor Yellow
        Invoke-Python -PythonArgs @('-m','playwright','install','chromium','firefox','webkit')
        Invoke-Python -PythonArgs @(
            '-m','pytest','-q','browser_tests',
            '--browser','chromium','--browser','firefox','--browser','webkit',
            '--basetemp',$BrowserBaseTemp,
            '-p','no:cacheprovider',
            "--junitxml=$(Join-Path $RunRoot 'browser-junit.xml')"
        )
        $BrowserStatus = 'PASSED'
    }
    else {
        Write-Host '[7/7] Full browser matrix skipped in standard run' -ForegroundColor DarkYellow
    }

@"
# AskYourDoubt Latest Quality Gate

- Date: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
- Result: PASSED
- Python compile: PASSED
- Flask import/routes: PASSED
- Core integration tests: PASSED
- UI/animation/mobile contracts: PASSED
- 12-device Chromium matrix: PASSED
- Full Chromium/Firefox/WebKit matrix: $BrowserStatus
- Evidence: $RunRoot
- Log: $Log
"@ | Set-Content $Summary -Encoding UTF8

    Write-Host 'QUALITY GATE PASSED' -ForegroundColor Green
    Write-Host "Evidence: $RunRoot"
    exit 0
}
catch {
@"
# AskYourDoubt Latest Quality Gate

- Date: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
- Result: FAILED
- Error: $($_.Exception.Message)
- Evidence: $RunRoot
- Log: $Log
"@ | Set-Content $Summary -Encoding UTF8

    Write-Host 'QUALITY GATE FAILED' -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Write-Host "Evidence: $RunRoot"
    exit 1
}
finally {
    Stop-Transcript | Out-Null
}
