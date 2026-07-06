param(
    [switch]$FullBrowserMatrix,
    [switch]$DockerSmoke
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
        if ($path -and (Test-Path $path)) { return @{ Exe = $path; Prefix = @() } }
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
    & $PythonExe @PythonPrefix @args
    if ($LASTEXITCODE -ne 0) { throw "Python command failed: $($args -join ' ')" }
}

$Stamp = Get-Date -Format 'yyyyMMdd_HHmmss_fff'
$ResultDir = Join-Path $Root "test_results\quality_gate_$Stamp"
$TempDir = Join-Path $ResultDir 'temp'
$BaseTemp = Join-Path $ResultDir 'pytest'
New-Item -ItemType Directory -Path $TempDir -Force | Out-Null
$env:TEMP = $TempDir
$env:TMP = $TempDir
$Log = Join-Path $ResultDir 'quality_gate.log'
$Summary = Join-Path $Root 'test_results\LATEST_QUALITY_GATE.md'
$BrowserStatus = 'NOT RUN'
$DockerStatus = 'NOT RUN'
$env:AYD_DATABASE = Join-Path $ResultDir 'qa-runtime.db'
$env:AYD_SECRET_KEY = 'quality-gate-only-secret'
$env:AYD_BASE_URL = 'http://127.0.0.1:9000'

Start-Transcript -Path $Log -Force | Out-Null
try {
    Write-Host '=======================================================' -ForegroundColor Cyan
    Write-Host 'AskYourDoubt 1.5.2 Commercial Global QA Gate' -ForegroundColor Cyan
    Write-Host '=======================================================' -ForegroundColor Cyan
    Write-Host "Project: $Root"
    Write-Host "Python: $PythonExe $($PythonPrefix -join ' ')"

    Write-Host '[1/8] Install pinned development dependencies' -ForegroundColor Yellow
    Invoke-Python -m pip install --upgrade pip
    Invoke-Python -m pip install -r requirements-dev.txt

    Write-Host '[2/8] Compile every Python module' -ForegroundColor Yellow
    Invoke-Python -m compileall -q app.py auth.py config.py db.py utils.py routes tests browser_tests run_device_matrix.py

    Write-Host '[3/8] Import Flask and verify route registration' -ForegroundColor Yellow
    Invoke-Python -c "import app; rules=list(app.app.url_map.iter_rules()); print('Registered routes:', len(rules)); assert len(rules) >= 57"

    Write-Host '[4/8] Run the complete functional/requirement suite' -ForegroundColor Yellow
    Invoke-Python -m pytest -q tests --basetemp $BaseTemp -p no:cacheprovider --junitxml (Join-Path $ResultDir 'core-junit.xml')

    Write-Host '[5/8] Validate JavaScript syntax when Node.js is available' -ForegroundColor Yellow
    $node = Get-Command node -ErrorAction SilentlyContinue
    if ($node) {
        & $node.Source --check static/js/app.js
        if ($LASTEXITCODE -ne 0) { throw 'JavaScript syntax validation failed.' }
    } else {
        Write-Host 'Node.js not installed: JavaScript syntax check NOT RUN.' -ForegroundColor DarkYellow
    }

    Write-Host '[6/8] Run 12-device responsive rendering matrix' -ForegroundColor Yellow
    Invoke-Python run_device_matrix.py

    Write-Host '[7/8] Live browser matrix' -ForegroundColor Yellow
    if ($FullBrowserMatrix) {
        Invoke-Python -m playwright install chromium firefox webkit
        $BrowserBase = Join-Path $ResultDir 'browser-pytest'
        $BrowserJunit = Join-Path $ResultDir 'browser-junit.xml'
        Invoke-Python -m pytest -q browser_tests --browser chromium --browser firefox --browser webkit --basetemp $BrowserBase -p no:cacheprovider --junitxml $BrowserJunit
        [xml]$BrowserXml = Get-Content $BrowserJunit
        $Suites = $BrowserXml.SelectNodes('//testsuite')
        $BrowserTests = 0
        $BrowserSkipped = 0
        foreach ($Suite in $Suites) {
            $BrowserTests += [int]$Suite.tests
            $BrowserSkipped += [int]$Suite.skipped
        }
        if ($BrowserTests -gt 0 -and $BrowserSkipped -eq $BrowserTests) {
            $BrowserStatus = 'NOT RUN'
            Write-Host 'All live browser tests were skipped by an environment restriction.' -ForegroundColor DarkYellow
        } else {
            $BrowserStatus = 'PASS'
        }
    } else {
        Write-Host 'NOT RUN. Use run_browser_matrix.bat for Chromium, Firefox and WebKit.' -ForegroundColor DarkYellow
    }

    Write-Host '[8/8] Docker production smoke' -ForegroundColor Yellow
    if ($DockerSmoke) {
        $docker = Get-Command docker -ErrorAction SilentlyContinue
        if (-not $docker) {
            throw 'Docker smoke was requested, but Docker is not installed or not on PATH.'
        } else {
            & $docker.Source build -t askyourdoubt:1.5.2-qa .
            if ($LASTEXITCODE -ne 0) { throw 'Docker image build failed.' }
            & $docker.Source run -d --name askyourdoubt-qa -p 9090:9000 -e AYD_SECRET_KEY=qa-only-secret askyourdoubt:1.5.2-qa
            if ($LASTEXITCODE -ne 0) { throw 'Docker container start failed.' }
            try {
                $healthy = $false
                1..30 | ForEach-Object {
                    try {
                        $response = Invoke-WebRequest 'http://127.0.0.1:9090/healthz' -UseBasicParsing -TimeoutSec 3
                        if ($response.StatusCode -eq 200) { $healthy = $true; return }
                    } catch { Start-Sleep -Seconds 2 }
                }
                if (-not $healthy) { & $docker.Source logs askyourdoubt-qa; throw 'Docker health smoke failed.' }
                $DockerStatus = 'PASS'
            } finally {
                & $docker.Source rm -f askyourdoubt-qa | Out-Null
            }
        }
    } else {
        Write-Host 'NOT RUN. Run with -DockerSmoke to build and health-test the image.' -ForegroundColor DarkYellow
    }

    @"
# AskYourDoubt 1.5.2 Latest Quality Gate

- Date: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
- Python compilation: PASS
- Flask import and 57-route threshold: PASS
- Complete functional/requirement suite: PASS
- 12-device Chromium rendering matrix: PASS
- Chromium/Firefox/WebKit live matrix: $BrowserStatus
- Docker build and health smoke: $DockerStatus
- Evidence directory: $ResultDir
- Log: $Log
"@ | Set-Content $Summary -Encoding UTF8

    Write-Host 'QUALITY GATE PASSED' -ForegroundColor Green
    Write-Host "Evidence: $ResultDir"
    exit 0
}
catch {
    @"
# AskYourDoubt 1.5.2 Latest Quality Gate

- Date: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
- Result: FAIL
- Error: $($_.Exception.Message)
- Browser matrix: $BrowserStatus
- Docker smoke: $DockerStatus
- Evidence directory: $ResultDir
- Log: $Log
"@ | Set-Content $Summary -Encoding UTF8
    Write-Host 'QUALITY GATE FAILED' -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    exit 1
}
finally {
    Stop-Transcript | Out-Null
}
