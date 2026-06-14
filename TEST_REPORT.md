# AskYourDoubt 1.3.1 Test Report

Test date: 2026-06-14

## Executed in the build environment

| Check | Result | Evidence |
|---|---|---|
| Development dependency installation | PASS | `requirements-dev.txt` installed in an isolated virtual environment |
| Python compilation | PASS | `app.py`, `db.py`, `auth.py`, `utils.py`, and `routes/` compiled |
| Flask import and route registration | PASS | 55 routes registered |
| Public health endpoint | PASS | `/healthz` returned HTTP 200 JSON |
| Core integration/UI tests | PASS | 33 passed |
| Responsive offline Chromium device matrix | PASS | 108/108 checks, 15 screenshots |
| Compose YAML parse | PASS | `compose.yaml` and `compose.production.yaml` parsed |
| GitHub Actions YAML parse | PASS | `.github/workflows/ci-cd.yml` parsed |
| Visible author/generator credit removal | PASS | Public templates and rendered-page contracts verify absence |
| Live Chromium localhost browser navigation in this sandbox | NOT RUN successfully | Environment returned `ERR_BLOCKED_BY_ADMINISTRATOR` for localhost navigation |
| Firefox live browser matrix in this sandbox | NOT RUN | Must run on GitHub Actions or the Windows laptop |
| WebKit live browser matrix in this sandbox | NOT RUN | Must run on GitHub Actions or the Windows laptop |
| Docker build/container smoke in this sandbox | NOT RUN | Docker was not installed in this environment |

## Windows commands required before production approval

```powershell
cd D:\AskYourDoubtGlobal
.\RUN_FULL_QA_1_3.bat
```

Docker:

```powershell
docker build -f Dockerfile.test -t askyourdoubt:test .
docker run --rm askyourdoubt:test

docker compose up -d --build
Invoke-WebRequest http://127.0.0.1:9000/healthz -UseBasicParsing
docker compose logs --tail 200
```

Only report Chromium, Firefox, WebKit, Docker image, and Docker container as PASS after those commands or the corresponding GitHub Actions jobs finish successfully.
