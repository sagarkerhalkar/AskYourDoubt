# AskYourDoubt 1.5.2 Test Report

## Release under test

```text
Version: 1.5.2
Source folder: AskYourDoubt_Global_Rebuild_1_5_2_SKY_BLUE_SAAS
Date: 2026-06-15
```

## Results

| Test category | Result | Evidence |
|---|---:|---|
| Python compilation | PASS | `test_evidence_1_5_2/static/python_compile.txt` |
| Flask route registration | PASS — 57 routes | `test_evidence_1_5_2/static/project_checks.txt` |
| Jinja template parsing | PASS — 34 templates | `test_evidence_1_5_2/static/project_checks.txt` |
| YAML parsing | PASS — 4 files | `test_evidence_1_5_2/static/project_checks.txt` |
| JavaScript syntax | PASS | `test_evidence_1_5_2/static/javascript_check.txt` |
| CSS structural check | PASS — 1,655 balanced rule blocks | `test_evidence_1_5_2/static/project_checks.txt` |
| Functional/regression suite | PASS — 66/66 | `test_evidence_1_5_2/core/core-output.txt` |
| Responsive device matrix | PASS — 168/168 | `test_evidence_1_5_2/device/DEVICE_MATRIX_REPORT.md` |
| Native Waitress health smoke | PASS | `test_evidence_1_5_2/runtime/waitress-smoke.txt` |
| Chromium localhost browser workflows | NOT RUN — environment policy skipped 31 tests | `test_evidence_1_5_2/browser/chromium-output.txt` |
| Firefox live browser workflows | NOT RUN — browser binary unavailable locally | Install through Playwright or use GitHub Actions |
| WebKit/Safari live browser workflows | NOT RUN — browser binary unavailable locally | Install through Playwright or use GitHub Actions |
| Docker build and container health | NOT RUN — Docker is unavailable in this environment | Run `RUN_FULL_QA_1_5_2.bat` on a Docker-enabled machine |
| Physical iPhone/Android/iPad testing | NOT RUN | Requires physical devices |

## New 1.5.2 verification

The automated regression suite confirms:

- Teacher Completed Questions pagination and metadata.
- Teacher Skipped Doubts pagination and metadata.
- Student Answered Questions pagination and metadata.
- Total session export contains Open + Completed only.
- Open, Completed and Skipped exports contain only the requested status.
- Teacher ownership remains enforced for session exports and APIs.
- Teacher live page contains the four current-session download controls.
- Teacher QR/link area contains maximize/full-page controls.
- Sky-blue/cool-grey palette contract is present.
- Teacher Login uses the local classroom image asset.

## Commands used

```powershell
py -3.14 -m compileall -q app.py auth.py config.py db.py utils.py routes tests browser_tests run_device_matrix.py
py -3.14 -m pytest -q tests
py -3.14 run_device_matrix.py
node --check static/js/app.js
```

Full browser matrix on a normal Windows or CI runner:

```powershell
py -3.14 -m playwright install chromium firefox webkit
py -3.14 -m pytest -q browser_tests --browser chromium --browser firefox --browser webkit
```

Docker smoke on a Docker-enabled machine:

```powershell
docker build -t askyourdoubt:1.5.2 .
docker run -d --name askyourdoubt-smoke -p 9090:9000 -e AYD_SECRET_KEY=smoke-secret askyourdoubt:1.5.2
Invoke-WebRequest http://127.0.0.1:9090/healthz -UseBasicParsing
docker rm -f askyourdoubt-smoke
```
