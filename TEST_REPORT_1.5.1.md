# AskYourDoubt 1.5.1 Test Report

## Reporting rule

Every category is reported as **PASS**, **FAIL**, or **NOT RUN**. A configured workflow is not treated as an executed pass.

## Release under test

```text
Version: 1.5.1
Source folder: AskYourDoubt_Global_Rebuild_1_5_1_COMMERCIAL_SAAS_FIX
Local Python used: 3.13
Target runtime: Python 3.14
Default port: 9000
```

## Executive result

| Category | Result | Actual evidence |
|---|---:|---|
| Complete functional and requirement pytest suite | **PASS** | 62 passed, 0 failed |
| Session-wise Teacher Question Bank regression suite | **PASS** | Owned-session filter, status filter, export filter and cross-teacher isolation |
| Student attachment-selection feedback | **PASS** | Filename, file size, ready state, Remove control and successful-upload filename confirmation |
| Completed-question visibility | **PASS** | Teacher and Student APIs and render contracts preserve question text |
| Teacher and Student resource workflows | **PASS** | File, video, note and commercial card contracts |
| Python compilation | **PASS** | App, routes, tests, browser tests and device runner |
| Flask route registration | **PASS** | 57 routes |
| Jinja template parsing | **PASS** | 34 templates |
| JavaScript syntax | **PASS** | `node --check static/js/app.js` |
| CSS parsing | **PASS** | 1,218 top-level rules, 0 parse errors |
| Compose and GitHub Actions YAML parsing | **PASS** | 4 YAML files |
| Dependency dry-run | **PASS** | All pinned dependencies resolved in the QA environment |
| Native Waitress `/healthz` and home smoke | **PASS** | HTTP 200 and expected product content |
| Offline responsive Chromium rendering matrix | **PASS** | 168/168 checks, 12 profiles × 14 pages, 24 screenshots |
| Live Chromium localhost navigation | **NOT RUN** | 31 tests skipped because this execution environment returned `ERR_BLOCKED_BY_ADMINISTRATOR` for localhost |
| Firefox live execution | **NOT RUN** | Browser binary/environment unavailable locally |
| WebKit/Safari live execution | **NOT RUN** | Browser binary/environment unavailable locally |
| Docker build and container smoke | **NOT RUN** | Docker CLI unavailable in this execution environment |
| GitHub Actions hosted CI/CD | **NOT RUN** | Requires pushing this release to the repository |
| Physical iPhone/iPad/Android testing | **NOT RUN** | Requires a physical device lab |
| External penetration test | **NOT RUN** | Requires an independent security assessment |

No failure remains in the locally executable application, integration, static, Waitress, or responsive-rendering gates.

## 1. Functional suite — PASS

Command:

```bash
python -m pytest -q tests -p no:cacheprovider --junitxml=test_evidence_1_5_1/core/core-junit.xml
```

Result:

```text
62 passed
```

The suite includes the complete existing role, session, voting, attachment, resources, QR, analytics, export, admin and security coverage plus new 1.5.1 regressions for:

- Teacher Question Bank displaying only the selected session's questions.
- All/Open/Completed status filters preserving the selected session.
- Current-view and full-session export behavior.
- Another teacher's session being rejected as a filter/export scope.
- Student file-selection feedback before upload.
- Exact attachment filename confirmation after successful submission.
- Completed question text remaining visible to teacher and student.
- Clean Teacher and Student resource workflows.

Evidence:

```text
test_evidence_1_5_1/core/core-output.txt
test_evidence_1_5_1/core/core-junit.xml
```

## 2. Static debug checks — PASS

### Python

```text
compileall: PASS
```

### Flask routes

```text
Registered routes: 57
```

### Jinja

```text
Parsed templates: 34
```

### JavaScript

```text
node --check static/js/app.js: PASS
```

### CSS

```text
Top-level rules: 1218
Parse errors: 0
```

### YAML

Successfully parsed:

```text
compose.yaml
compose.production.yaml
.github/workflows/ci.yml
.github/workflows/browser-matrix.yml
```

### Dependencies

```text
python -m pip install --dry-run -r requirements-dev.txt: PASS
```

Evidence directory:

```text
test_evidence_1_5_1/static/
```

## 3. Native Waitress smoke — PASS

A real Waitress process was started against a temporary SQLite database.

```text
Health: {"service":"askyourdoubt","status":"ok"}
Home HTTP: 200
Home product text: PASS
```

Evidence:

```text
test_evidence_1_5_1/static/native_waitress_smoke.txt
```

## 4. Responsive matrix — PASS

The deterministic Playwright `set_content` renderer tested 14 pages at every viewport without horizontal overflow.

```text
Profiles: 12
Pages per profile: 14
Total checks: 168
Passed: 168
Failed: 0
Screenshots: 24
```

Profiles:

```text
320×568, 360×800, 390×844, 412×915,
768×1024, 820×1180, 1024×1366,
1280×800, 1366×768, 1440×900,
1920×1080, 2560×1440
```

Pages:

```text
Home
Student login
Teacher login
Admin login
Teacher dashboard
Teacher live
Teacher live focus
Teacher resources
Teacher session-filtered question bank
Student live portal
Student live focus
Student answered questions
Student resources
Admin dashboard
```

Evidence:

```text
test_evidence_1_5_1/device/LATEST_DEVICE_MATRIX_REPORT.md
test_evidence_1_5_1/device/LATEST_DEVICE_MATRIX.json
test_evidence_1_5_1/device/runs/.../screenshots/
```

## 5. Live browser matrix — NOT RUN locally

The 31 Chromium tests were invoked. Chromium blocked every localhost navigation with:

```text
net::ERR_BLOCKED_BY_ADMINISTRATOR
```

The browser harness converts only this explicit host-policy failure into an honest skip. Product failures still fail normally. GitHub Actions remains configured to run Chromium, Firefox and WebKit on a normal hosted runner.

Local result:

```text
31 skipped because localhost navigation was administratively blocked
```

Evidence:

```text
test_evidence_1_5_1/browser/chromium-output.txt
test_evidence_1_5_1/browser/chromium-junit.xml
```

## 6. Docker and CI/CD

Source contracts, YAML and Docker-related application tests passed inside the core suite. Actual Docker image build/container health and hosted GitHub Actions execution were not available locally and therefore remain **NOT RUN**.

Run on the target Windows machine:

```powershell
.\RUN_FULL_QA_1_5_1.bat
```

Or run categories separately:

```powershell
.\run_debug_ci_cd.bat
.\run_device_matrix.bat
.\run_browser_matrix.bat

docker build -f Dockerfile.test -t askyourdoubt:test .
docker run --rm askyourdoubt:test

docker build -t askyourdoubt:1.5.1 .
docker run -d --name askyourdoubt-smoke -p 9090:9000 -e AYD_SECRET_KEY=smoke-secret askyourdoubt:1.5.1
Invoke-WebRequest http://127.0.0.1:9090/healthz -UseBasicParsing
docker rm -f askyourdoubt-smoke
```

## Final local verdict

```text
Application logic and regression suite: PASS
Static debug checks: PASS
Native runtime smoke: PASS
Responsive rendering: PASS
Live branded browser matrix: NOT RUN locally due environment policy
Docker runtime: NOT RUN locally
Hosted CI/CD: NOT RUN until repository push
```
