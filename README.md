# AskYourDoubt

AskYourDoubt is a responsive Flask application for live classroom doubt collection, same-doubt voting, teacher moderation, resource sharing, question-bank management, analytics, exports, and administrator control.

## Current release

```text
Version: 1.3.1
Default port: 9000
Local development path used on Windows: D:\AskYourDoubtGlobal
Repository: https://github.com/sagarkerhalkar/AskYourDoubt
```

## GitHub versus public application

A public GitHub repository makes the **source code** public. GitHub does not run this Flask server. To make the application available to students and teachers, deploy it to a continuously running server or cloud platform. Docker and an HTTPS Caddy configuration are included.

## Features

### Student

- Join using a teacher QR code, link, or numeric session code.
- Name and exactly 10 numeric mobile digits are required.
- Chat-style text doubt composer with emoji support.
- Text is required; PDF, Word, TXT, or image attachment is optional up to 10 MB.
- Video-file doubt uploads are rejected.
- Silent background live updates without a visible page refresh.
- `My Question` marker.
- Own-question voting is blocked.
- Another student can select `I have the same doubt` once.
- Skipped questions stay hidden.
- Completed questions appear in a collapsed Answered section.
- Attachments from other students stay hidden unless the teacher enables downloads.
- Teacher-shared files, notes, images, presentations, and video links are available.
- Top 100 live doubts by default, with larger views supported.

### Teacher

- Login and password change.
- Create, close, and reopen sessions.
- Anonymous live question queue ranked by vote count.
- Silent one-second polling.
- Complete, Skip, Reopen, and conditional Download actions.
- Copy join link, full-screen QR, download QR PNG, print QR, and share QR.
- Per-student question limit and student download permission.
- Download all student attachments as ZIP.
- Share PDF, Word, PowerPoint, TXT, image, note, and video-link resources.
- Question bank, category/keyword/session analytics, and CSV exports.

### Administrator

- Manage administrators and teachers.
- Create, edit, enable, disable, soft-delete, and reset teacher passwords.
- View students, sessions, questions, skipped doubts, question bank, and analytics.
- Close/reopen sessions and export teacher-wise/session-wise data.
- Upload a high-resolution logo.
- Compact dashboard showing the latest activity, with a separate paginated activity page.
- Long tables use search, filters, pagination, and 10/20/30 rows per page.

## Responsive targets

```text
320×568      compact phone
360×800      small Android
390×844      modern iPhone
412×915      large Android
768×1024     iPad portrait
820×1180     iPad Air
1024×1366    iPad Pro
1280×800     small laptop
1366×768     laptop
1440×900     MacBook-sized viewport
1920×1080    Full HD
2560×1440    QHD
```

Browser automation supports Chromium, Firefox, and WebKit. A configured workflow is not proof that a browser passed; verify the actual GitHub Actions job or local test output.

## Technology

```text
Python 3.14
Flask 3.1.2
SQLite for laptop/single-container use
Waitress 3.0.2
Jinja2
Vanilla JavaScript
Responsive CSS with animation and 3D effects
Pytest 9.0.2
Playwright 1.57.0
Docker / Docker Compose
GitHub Actions
```

## Project structure

```text
app.py                         Flask application factory
config.py                      environment-based settings
db.py                          schema and database helpers
auth.py                        authentication helpers
utils.py                       upload, export, and QR helpers
routes/                        public, student, teacher, admin, API routes
templates/                     Jinja templates
static/css/app.css             responsive UI and animation
static/js/app.js               polling, voting, tabs, copy/share controls
tests/                         integration and UI contract tests
browser_tests/                 Chromium/Firefox/WebKit tests
Dockerfile                     runtime container
Dockerfile.test                test container
compose.yaml                   local Docker deployment
compose.production.yaml        Caddy HTTPS deployment
.github/workflows/ci-cd.yml    CI, browser tests, Docker smoke and GHCR publish
```

## Security before public deployment

1. Change the default administrator password.
2. Set a long random `AYD_SECRET_KEY`.
3. Use HTTPS.
4. Never commit `.env`, `database.db`, uploads, exports, backups, or generated QR files.
5. Keep server-side file-type and 10 MB size validation.
6. Back up the database and resources.
7. Define privacy and retention rules before collecting real student mobile numbers.
8. SQLite supports only one application instance. Migrate to PostgreSQL before horizontal scaling.

## Environment variables

```powershell
Copy-Item .env.example .env
notepad .env
```

```env
AYD_SECRET_KEY=replace-with-a-long-random-value
AYD_DATABASE=/app/data/database.db
AYD_BASE_URL=http://127.0.0.1:9000
AYD_PORT=9000
AYD_DOMAIN=ask.sagarkerhalkar.com
AYD_DEBUG=0
```

Generate a secure secret:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

## Windows local installation

```powershell
cd D:\AskYourDoubtGlobal
py -3.14 -m pip install --upgrade pip
py -3.14 -m pip install -r requirements.txt
py -3.14 app.py
```

Open `http://127.0.0.1:9000`.

Use Waitress for a stable server process:

```powershell
py -3.14 -m waitress --listen=0.0.0.0:9000 --threads=8 app:app
```

## Temporary public test URL

```powershell
cd D:\AskYourDoubtGlobal
.\ngrok.exe http --url=https://pout-outbound-reenter.ngrok-free.dev 9000
```

Set `AYD_BASE_URL` to the exact HTTPS public URL before creating new sessions, otherwise QR codes can contain an old address.

## Docker quick start

Install Docker Desktop, then:

```powershell
cd D:\AskYourDoubtGlobal
Copy-Item .env.example .env
notepad .env
docker compose up -d --build
```

Check:

```powershell
docker compose ps
docker compose logs -f --tail 200
```

Open `http://127.0.0.1:9000`.

Stop without deleting persistent data:

```powershell
docker compose down
```

Do not run `docker compose down -v` unless you deliberately want to delete the database/uploads volumes.

## Build and run a Docker image manually

```powershell
docker build -t askyourdoubt:1.3.1 .

docker run -d `
  --name askyourdoubt `
  --restart unless-stopped `
  -p 9000:9000 `
  -e AYD_SECRET_KEY="replace-this" `
  -e AYD_BASE_URL="http://127.0.0.1:9000" `
  -v ayd_database:/app/data `
  -v ayd_uploads:/app/static/uploads `
  -v ayd_qr:/app/static/qr `
  -v ayd_exports:/app/exports `
  -v ayd_brand:/app/static/brand `
  askyourdoubt:1.3.1
```

## Go public with a domain

Recommended server flow:

1. Obtain an Ubuntu VPS.
2. Point `ask.sagarkerhalkar.com` to the VPS public IP.
3. Open TCP ports 80 and 443.
4. Install Docker Engine and Docker Compose.
5. Clone this repository.
6. Create `.env` with a secure secret and HTTPS base URL.
7. Copy the Caddy example.
8. Start the production stack.

```bash
git clone https://github.com/sagarkerhalkar/AskYourDoubt.git
cd AskYourDoubt
cp .env.example .env
cp deploy/Caddyfile.example deploy/Caddyfile
nano .env
nano deploy/Caddyfile
docker compose -f compose.production.yaml up -d --build
docker compose -f compose.production.yaml ps
docker compose -f compose.production.yaml logs -f --tail 200
```

Production `.env`:

```env
AYD_SECRET_KEY=long-random-production-secret
AYD_BASE_URL=https://ask.sagarkerhalkar.com
AYD_DOMAIN=ask.sagarkerhalkar.com
AYD_PORT=9000
AYD_DEBUG=0
```

Caddy obtains and renews HTTPS certificates when DNS and public ports are correct.

## Debug and test

### Install test dependencies

```powershell
py -3.14 -m pip install -r requirements-dev.txt
```

### Dependency resolution

```powershell
py -3.14 -m pip install --dry-run -r requirements-dev.txt
```

### Compile

```powershell
py -3.14 -m compileall -q app.py db.py auth.py utils.py routes
```

### List routes

```powershell
py -3.14 -c "import app; print('\n'.join(sorted(str(r) for r in app.app.url_map.iter_rules())))"
```

### Permission-safe Windows core tests

```powershell
$stamp = Get-Date -Format "yyyyMMdd_HHmmss_fff"
$run = Join-Path $PWD "test_results\manual_$stamp"
$tmp = Join-Path $run "temp"
$base = Join-Path $run "pytest"
New-Item -ItemType Directory -Force $tmp | Out-Null
$env:TEMP = $tmp
$env:TMP = $tmp
py -3.14 -m pytest -q tests --basetemp "$base" -p no:cacheprovider --junitxml "$run\junit.xml"
```

### Device matrix

```powershell
py -3.14 run_device_matrix.py
```

### Browser matrix

```powershell
py -3.14 -m playwright install chromium firefox webkit
py -3.14 -m pytest -q browser_tests --browser chromium --browser firefox --browser webkit --basetemp ".\test_results\browser" -p no:cacheprovider
```

### Full Windows QA

```powershell
.\RUN_FULL_QA_1_3.bat
```

Report each test category as `PASS`, `FAIL`, or `NOT RUN`.

## Docker tests

```powershell
docker build -f Dockerfile.test -t askyourdoubt:test .
docker run --rm askyourdoubt:test

docker build -t askyourdoubt:smoke .
docker run -d --name askyourdoubt-smoke -p 9090:9000 -e AYD_SECRET_KEY="smoke-secret" askyourdoubt:smoke
Start-Sleep -Seconds 8
Invoke-WebRequest http://127.0.0.1:9090/healthz -UseBasicParsing
docker logs askyourdoubt-smoke
docker rm -f askyourdoubt-smoke
```

## CI/CD

`.github/workflows/ci-cd.yml` runs:

- Python compilation and route checks.
- Integration/UI tests.
- Chromium, Firefox, and WebKit jobs.
- Docker build and container smoke test.
- GHCR publishing after successful main-branch or release-tag execution.

Check the GitHub Actions result and JUnit artifacts before reporting success.

## Backup

```powershell
docker exec askyourdoubt python -c "import sqlite3; s=sqlite3.connect('/app/data/database.db'); d=sqlite3.connect('/app/data/database.backup.db'); s.backup(d); d.close(); s.close()"
docker cp askyourdoubt:/app/data/database.backup.db .\backups\database.backup.db
```

Back up uploads, resources, QR files, exports, and logo data too.

## Scaling limitation

The SQLite build is for local testing, demos, pilots, and one application instance. It does not support 50,000,000 concurrent students. Large deployment needs PostgreSQL, Redis, object storage, CDN, realtime gateways, queues, load balancing, monitoring, backups, rate limits, and security hardening.

## Default administrator

```text
Username: admin
Password: admin123
```

Change it immediately after first login.

## License

All rights reserved. No open-source license is granted unless the repository owner deliberately selects one.
