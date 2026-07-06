# AskYourDoubt 1.5.0 Test Report

## Reporting rule

Every category is recorded as **PASS**, **FAIL**, or **NOT RUN**. A file or CI configuration existing is not treated as an executed pass.

## Release under test

```text
Version: 1.5.0
Source folder: AskYourDoubt_Global_Rebuild_1_5_0_COMMERCIAL_GLOBAL_UI_QA
Local Python used: 3.13.5
Target runtime: Python 3.14
Local browser engine executed: system Chromium through Playwright
```

## Executive result

| Category | Result | Evidence |
|---|---:|---|
| Complete functional/requirement pytest suite | **PASS** | 57 passed, 0 failed, 0 skipped |
| Python compilation | **PASS** | Application, routes, tests, browser tests, device runner |
| Flask import and route registration | **PASS** | 57 routes registered |
| Native Waitress startup and `/healthz` smoke | **PASS** | Real localhost server and home response |
| Packaged ZIP manifest and extracted core suite | **PASS** | 144 manifest entries; extracted ZIP 57/57 tests |
| Jinja template parsing | **PASS** | 34 templates parsed |
| JavaScript syntax | **PASS** | `node --check static/js/app.js` |
| CSS parsing | **PASS** | 978 top-level rules, 0 parse errors |
| Compose and GitHub Actions YAML parsing | **PASS** | 4 YAML files parsed |
| Pinned dependency dry-run | **PASS** | `requirements-dev.txt` resolved |
| Chromium live browser suite | **PASS** | 31 tests across responsive and interaction groups |
| 12-device × 11-page responsive matrix | **PASS** | 132/132 checks, 12 screenshots |
| Dockerfile/Compose/CI contract tests | **PASS** | Automated source contracts in core suite |
| Docker image build and container health smoke locally | **NOT RUN** | Docker CLI not installed in this environment |
| Firefox Playwright execution locally | **NOT RUN** | Firefox browser binary unavailable locally |
| WebKit/Safari Playwright execution locally | **NOT RUN** | WebKit browser binary unavailable locally |
| GitHub Actions execution | **NOT RUN** | Requires push to GitHub repository |
| Manual physical iPhone/iPad/Android testing | **NOT RUN** | Requires physical device lab |
| External penetration test | **NOT RUN** | Requires independent security assessment |

No product-code failure remained in the locally executed release gates.

## 1. Complete functional and requirement suite — PASS

Command:

```bash
python -m pytest -q tests --basetemp test_results/core_v150_release/base -p no:cacheprovider --junitxml test_results/core_v150_release/junit.xml
```

Result:

```text
57 passed in 25.09s
```

Coverage includes:

- Student join validation, closed-session behavior, and role privacy.
- Text-required doubts, emoji text, all allowed file types, exact 10 MB upload, over-limit rejection, and video rejection.
- `My Question`, self-vote prevention, duplicate-vote prevention, vote ranking, completed, skipped, and reopened states.
- Student attachment permissions, resources, selected tabs, and live focus.
- Teacher session durations, limits, privacy, QR operations, complete/skip/reopen, ZIP, exports, resources, analytics, question bank, and password change.
- 100/250/500 live queue sizes and ordering.
- Administrator accounts, teachers, sessions, students, questions, exports, activity pagination, analytics, logo, and password.
- Role coexistence and teacher/student/admin session stability.
- Two-teacher session and student-data isolation.
- Health endpoint, security headers, configuration, migration, indexes, WAL, and route protection.
- Compact typography, responsive breakpoints, 3D/motion contracts, reduced motion, and no public author/AI credit.
- Docker, Compose, browser matrix, Docker smoke, and GHCR workflow source contracts.

## 2. Static debug checks — PASS

### Python compilation

```text
PASS
```

Compiled:

```text
app.py auth.py config.py db.py utils.py routes tests browser_tests run_device_matrix.py
```

### Flask routes

```text
Registered routes: 57
PASS
```

### Jinja templates

```text
Parsed templates: 34
PASS
```

### JavaScript

```text
node --check static/js/app.js
PASS
```

### CSS

```text
CSS top-level rules: 978
Parse errors: 0
PASS
```

### YAML

Parsed successfully:

```text
compose.yaml
compose.production.yaml
.github/workflows/ci.yml
.github/workflows/browser-matrix.yml
```

### Dependencies

`python -m pip install --dry-run -r requirements-dev.txt` completed successfully with all pinned application/test dependencies satisfied.

A global `pip check` warning existed for an unrelated preinstalled `moviepy` package requiring an older Pillow. `moviepy` is not an AskYourDoubt dependency and is not listed in either requirements file. The AskYourDoubt pinned dependency dry-run itself passed.

## 3. Native Waitress runtime smoke — PASS

A real Waitress process was started on localhost with a temporary SQLite database. The release returned:

```text
/healthz: {"service":"askyourdoubt","status":"ok"}
Home page: HTTP 200, expected product text present
```

Evidence: `test_evidence_1_5_0/static/NATIVE_WAITRESS_SMOKE.txt`.

## 4. Chromium live browser suite — PASS

The live browser suite uses a running Waitress server and real page navigation, authentication, form submission, polling, downloads, and DOM assertions.

### Public responsive pages

```text
12 passed
```

Verified `/`, `/student`, `/teacher-login`, and `/admin-login` at all 12 viewports with no horizontal overflow.

### Authenticated responsive portals

```text
12 passed
```

Verified student portal/focus, teacher portal/focus, and admin dashboard at all 12 viewports with no horizontal overflow.

### Interaction and live behavior

```text
7 passed
```

Verified:

- Public primary actions and no public author/AI credit.
- Copy Link feedback and QR PNG download.
- Resource studio file/video/note areas.
- Teacher and student minimize/maximize controls.
- Teacher/student sessions coexisting in one browser context.
- Professional computed heading sizes and touch targets.
- One-second silent polling preserving typed student text.
- Live-focus core actions and polling contracts.

Total Chromium browser tests represented by these groups:

```text
31 passed
```

The browser suite was split into smaller executions because the restricted container occasionally terminated long-lived Chromium sessions. Each reported group has a zero-failure JUnit file.

## 5. Device and responsive rendering matrix — PASS

Command:

```bash
python run_device_matrix.py
```

Result:

```json
{
  "total_checks": 132,
  "passed": 132,
  "failed": 0,
  "screenshots": 12
}
```

Profiles:

```text
320×568, 360×800, 390×844, 412×915,
768×1024, 820×1180, 1024×1366,
1280×800, 1366×768, 1440×900,
1920×1080, 2560×1440
```

Pages rendered at every profile:

```text
Home, Student Login, Teacher Login, Admin Login,
Teacher Dashboard, Teacher Live, Teacher Live Focus,
Teacher Resources, Student Portal, Student Live Focus,
Admin Dashboard
```

Representative phone, tablet, and laptop screenshots were visually inspected. The headings and live command panels were compact; teacher/student controls were visible; no horizontal clipping was observed.

## 6. Supplemental coverage instrumentation

A coverage XML report was produced after running the complete test suite under branch instrumentation:

```text
Valid lines: 1230
Covered lines: 1062
Line coverage: 86.34%
Valid branches: 308
Covered branches: 191
Branch coverage: 62.01%
Combined terminal coverage: 81%
```

The standalone coverage wrapper timed out during post-processing after all 57 test progress markers and after writing the coverage database/XML. The ordinary non-instrumented core execution completed normally with 57 passes; therefore coverage is supplemental evidence, not the primary pass result.

## 7. Silent one-second update verification — PASS

Student and teacher templates were checked for:

```text
const POLL_INTERVAL_MS = 1000
window.setInterval(load, POLL_INTERVAL_MS)
if (loading) return
cache: 'no-store'
visibilitychange recovery
```

Live browser verification confirmed that student typing remains unchanged while background polling executes. Change signatures prevent unnecessary list rerendering, reducing flicker.

## 8. Minimize, maximize, full-screen, and new-window verification — PASS

Verified for both student and teacher live-doubt stages:

- Minimize control sets `is-minimized`.
- Button changes to Maximize.
- Maximize removes `is-minimized`.
- Full-screen control uses the Fullscreen API with a responsive fallback.
- Dedicated focus route opens in a new window.
- Focus route includes Return to Original Size.
- Teacher focus retains QR/link controls.
- Student focus retains live queue and voting flow.

## 9. Typography and global commercial UI verification — PASS

Verified source and computed browser behavior:

- Global H1 scale is capped near 29.6 px (`1.85rem`) before role-specific reductions.
- Teacher live page title is capped near 27.2 px (`1.7rem`).
- Mobile headings reduce further.
- Student and teacher hero panels are substantially smaller than the prior design.
- Cards use restrained shadows, controlled gradients, and fine-pointer-only hover depth.
- Touch devices do not depend on hover.
- `prefers-reduced-motion` disables nonessential motion.
- External Google Font loading was removed.

## 10. Security and data-isolation verification — PASS for automated scope

Verified:

- Teacher ownership checks on protected session resources and APIs.
- Role-based route redirects/protection.
- Teacher live API omits student name and mobile.
- Unique same-doubt vote index and duplicate-vote rejection.
- Password hashing and legacy upgrade paths.
- SQLite WAL and required indexes.
- Server-side extension and actual 10 MB file validation.
- HTTP/HTTPS validation for video links.
- `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`, and `Permissions-Policy` headers.
- API `Cache-Control: no-store`.
- Two teachers cannot read or change each other's session data.

An independent penetration test, threat model review, privacy/legal review, and high-load abuse test were not run.

## 11. Docker — source PASS, local execution NOT RUN

Automated source tests confirmed:

- Python 3.14 slim base image.
- Non-root `ayd` user.
- Waitress runtime.
- Healthcheck.
- Persistent database/upload/QR/export/brand volumes.
- Local and production Compose files.
- Caddy HTTPS service.
- Docker CI smoke job.

The local environment returned `docker: command not found`, so the image build and container health smoke are **NOT RUN locally**.

Required acceptance command on a Docker-enabled machine:

```powershell
docker build -t askyourdoubt:1.5.0 .
docker run -d --name askyourdoubt-smoke -p 9090:9000 -e AYD_SECRET_KEY=smoke-secret askyourdoubt:1.5.0
Start-Sleep -Seconds 8
Invoke-WebRequest http://127.0.0.1:9090/healthz -UseBasicParsing
docker logs askyourdoubt-smoke
docker rm -f askyourdoubt-smoke
```

## 12. Firefox, WebKit/Safari, and branded browsers — NOT RUN locally

Local Playwright Firefox and WebKit binaries were unavailable and could not be downloaded in the restricted environment. The CI matrix is configured for:

```text
chromium
firefox
webkit
```

Chrome/Edge/Safari/Mobile Safari physical or branded-browser acceptance remains **NOT RUN** until performed in GitHub Actions and/or a real device/browser lab.

## 13. CI/CD — configuration PASS, hosted execution NOT RUN

YAML parsing and automated workflow-contract tests passed. The workflows include:

- Python 3.11–3.14 core matrix.
- Compile and route threshold.
- 57-test functional suite.
- Chromium/Firefox/WebKit browser jobs.
- Docker build and `/healthz` smoke.
- GHCR publish after successful main/tag push.

GitHub-hosted execution is **NOT RUN** until the release is pushed. Check every Actions job and artifact before deployment.

## 14. Packaged release integrity — PASS

The candidate ZIP was extracted into a clean temporary directory. Verification results:

```text
SHA-256 manifest entries checked: 144
Manifest mismatches: 0
Extracted-package core tests: 57 passed in 24.77s
Extracted-package Python compile: PASS
```

Evidence:

- `test_evidence_1_5_0/static/package-manifest-check.txt`
- `test_evidence_1_5_0/core/package-extracted-test.txt`
- `test_evidence_1_5_0/core/package-extracted-junit.xml`

## Final release judgment

**PASS for the locally executable functional, static, Chromium, and responsive scope.**

**NOT RUN locally:** Docker runtime, Firefox, WebKit/Safari, hosted GitHub Actions, physical mobile devices, penetration testing, and production load testing.
