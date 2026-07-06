# AskYourDoubt 1.2.1 QA Test Report

## Scope

This QA pass focuses on dependency resolution, Python compilation, Flask route registration, core application logic, UI/animation contracts, and responsive Chromium rendering.

## Dependency conflict fixed

The previous package incorrectly combined:

- `pytest==9.0.2`
- `pytest-playwright==0.7.1`

`pytest-playwright 0.7.1` requires pytest below 9, so installation failed.

The corrected development set is:

- `pytest==9.0.2`
- `pytest-playwright==0.8.0`
- `playwright==1.57.0`
- `requests==2.32.5`

Runtime dependencies no longer include pytest.

## Executed in the build environment

### Dependency resolver

Command:

```text
python -m pip install --dry-run -r requirements-dev.txt
```

Result: **PASSED — no resolution conflict**

### Python compilation

Command:

```text
python -m compileall -q app.py db.py auth.py utils.py routes
```

Result: **PASSED**

### Flask route import

Result: **52 routes registered**

### Core integration and UI contract tests

Command:

```text
python -m pytest -q tests
```

Result:

```text
26 passed
```

Coverage includes authentication, student mobile validation, teacher/student/admin flows, voting, self-vote prevention, duplicate-vote prevention, attachments, resources, session lifecycle, question bank, admin controls, copy-link contracts, 3D/premium-motion CSS contracts, live polling contracts, and mobile breakpoints.

### Responsive Chromium device matrix

Command:

```text
python run_device_matrix.py
```

Result:

```text
108 passed
0 failed
15 screenshots generated
```

Device profiles:

- iPhone SE — 320 × 568
- Android small — 360 × 800
- iPhone 14 — 390 × 844
- Android large — 412 × 915
- iPad portrait — 768 × 1024
- iPad Air — 820 × 1180
- iPad Pro — 1024 × 1366
- Small laptop — 1280 × 800
- Laptop — 1366 × 768
- MacBook — 1440 × 900
- Full HD desktop — 1920 × 1080
- QHD desktop — 2560 × 1440

Pages checked at every profile:

- Home
- Student login
- Teacher login
- Admin login
- Student portal
- Teacher dashboard
- Teacher live session
- Teacher resources
- Admin dashboard

## Full browser matrix status

The repository now has a corrected GitHub Actions matrix for:

- Chromium
- Firefox
- WebKit

The build sandbox could not run live localhost navigation in Playwright because browser navigation to `127.0.0.1` is blocked by the environment. This is an environment restriction, not a passed browser result. The full browser suite must run on the user's Windows laptop through `run_browser_matrix.bat` or in GitHub Actions.

## Honest conclusion

- Dependency resolution: **PASSED**
- Compile/import: **PASSED**
- Core tests: **26 PASSED**
- Responsive Chromium matrix: **108 PASSED**
- Live Chromium/Firefox/WebKit matrix in this sandbox: **NOT EXECUTED due environment restriction**
- CI/CD workflows: **corrected and included**
