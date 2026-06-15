# AskYourDoubt 1.5.2 — Commercial Global UI & QA Release

AskYourDoubt is a responsive Flask platform for live classroom doubt collection, same-doubt voting, teacher moderation, QR joining, resource sharing, question-bank management, analytics, exports, and administrator control.

Version **1.5.2** keeps the session and data logic from the 1.4.1 stability build while replacing oversized headings and oversized hero areas with a compact, professional international SaaS design. Teacher and student live-doubt panels can be minimized, maximized, opened in a dedicated window, or placed in browser full screen. Live data refreshes silently every second without reloading the page or clearing text being typed.

## Release identity

```text
Version: 1.5.2
Default port: 9000
Recommended Windows folder: D:\AskYourDoubtGlobal
Repository: https://github.com/sagarkerhalkar/AskYourDoubt
Health endpoint: /healthz
```

## 1.5.2 commercial UI changes

### Defect corrections requested after 1.5.0

- Teacher Completed and Skipped sections now have independent 10/20/30 pagination with Previous/Next controls.
- Student Answered section now has independent 10/20/30 pagination.
- Current-session CSV downloads are split into Total (Open + Completed), Open, Completed, and Skipped.
- Teacher QR/link panel can open in browser full screen or a dedicated full-page QR view with Back to Session.
- Teacher login uses a local realistic Indian classroom image; it does not depend on a remote image URL.
- Coloured emoji navigation icons were replaced with neutral symbols so the final branding remains blue/grey.
- Teacher Question Bank now filters and displays questions **session by session**, not only during CSV export.
- The selected session remains visible while switching between All, Open, and Completed filters.
- Current-view and full-session exports are separate and preserve the selected session/status.
- Student attachment picker now changes to a clear selected-file state showing filename, size, ready-to-upload text, and a Remove action.
- Successful doubt submission confirms the exact attachment filename.
- Completed question text is explicitly rendered in both Teacher and Student completed/answered views.
- Teacher and Student resource areas use clean file/video/note workflows and consistent commercial resource cards.
- Teacher pages no longer use the dark violet promotional banner shown in the previous build; role pages use restrained navy, sky-blue, white, and cool-grey surfaces.
- Responsive evidence now includes Teacher Question Bank, Teacher Resources, Student Answered, and Student Resources at every device profile.

- Compact global heading scale across public, student, teacher, and admin pages.
- Student welcome panel reduced to approximately 150 px minimum height.
- Teacher dashboard hero reduced to approximately 168 px minimum height.
- Teacher live launcher reduced to approximately 164 px minimum height.
- Professional navy, sky-blue, white, and cool-grey palette with controlled accents; green-led branding is removed.
- Restrained 3D depth, soft glass surfaces, hover lift, animated live indicators, and responsive motion.
- Touch-specific styling and reduced-motion accessibility support.
- No external Google Font request; the UI works offline and avoids font-loading delays.
- Content visibility and responsive layout optimizations for long dashboards.
- Teacher and student live-doubt minimize/maximize controls.
- Full-screen and dedicated-new-window live focus modes.
- One-second silent polling with in-flight request protection and change signatures to avoid unnecessary rerendering.
- Copy-link feedback, QR download/share/print, and resources remain available.

## Product roles

### Student

- Join from QR code, direct link, or teacher-provided session.
- Full name and exactly 10 numeric mobile digits are required.
- Submit a compulsory text doubt with emoji support.
- Add an optional PDF, Word, TXT, or image attachment up to 10 MB.
- Video-file doubt uploads are rejected.
- See `My Question` on own questions.
- Cannot vote on own question.
- Can select `I have the same doubt` once on another student's question.
- Highest-voted open doubts remain first.
- Skipped doubts stay hidden.
- Completed doubts move to Answered.
- Teacher resources are available in Resources.
- Other students' attachments remain hidden unless the teacher allows downloading.
- Live queue updates silently every second.
- Typed text remains in the composer while background polling runs.
- Live panel can be minimized, maximized, opened in a new window, or shown full screen.

### Teacher

- Separate teacher login and role-safe session.
- Create 90, 120, or 180 minute sessions.
- Set per-student question limits from 1 to 10,000,000.
- Close and reopen sessions.
- Anonymous live queue: teacher API does not expose student name or mobile.
- Complete, skip, and reopen doubts.
- Download an attachment only when one exists.
- Download all session attachments as ZIP.
- Export current-session questions and question-bank CSV files.
- Share notes, PDFs, Word files, PowerPoint files, TXT, images, and HTTP/HTTPS video links.
- Copy join link, download QR PNG, share QR, print QR, and open full QR view.
- Category, keyword/topic, and session analytics.
- Change own password.
- Live queue updates silently every second and supports 100, 250, or 500 items per page.
- Live panel can be minimized, maximized, opened in a new window, or shown full screen.

### Administrator

- Separate admin login and role-safe session.
- Create and manage administrators.
- Create, edit, enable, disable, soft-delete, and reset teacher accounts.
- View students, sessions, questions, skipped doubts, question bank, analytics, and paginated activity.
- Close or reopen any session.
- Export students, sessions, questions, and filtered question-bank data.
- Upload a replacement high-resolution logo.
- Change own password.

## Responsive targets

```text
320×568      compact phone / iPhone SE class
360×800      small Android
390×844      modern iPhone
412×915      large Android
768×1024     iPad portrait
820×1180     iPad Air
1024×1366    iPad Pro
1280×800     small laptop
1366×768     standard laptop
1440×900     MacBook-sized viewport
1920×1080    Full HD desktop
2560×1440    QHD desktop
```

The local device runner renders 14 application pages at every profile: **168 responsive checks**.

## Browser strategy

- Chromium is used locally for deterministic offline responsive rendering. Live localhost navigation may be blocked by restricted environments and is then reported as NOT RUN.
- Chromium, Firefox, and WebKit are configured as independent GitHub Actions jobs.
- Chrome and Edge follow the Chromium code path.
- Safari and Mobile Safari follow the WebKit code path.
- A configured CI job is not proof of a pass; always verify the actual GitHub Actions result.

## Technology

```text
Python 3.14 target runtime
Flask 3.1.2
Werkzeug 3.1.3
SQLite with WAL for laptop/single-container use
Waitress 3.0.2
Jinja2
Vanilla JavaScript
Responsive CSS with restrained motion and 3D depth
Pytest 9.0.2
Playwright 1.57.0
Docker / Docker Compose
Caddy HTTPS reverse proxy
GitHub Actions CI/CD
```

## Project structure

```text
app.py                         Flask application factory and security headers
config.py                      environment-based settings
db.py                          schema, migrations, indexes, WAL setup
auth.py                        role authentication and protection
utils.py                       upload, QR, URL, and export helpers
routes/                        public, student, teacher, admin, API routes
templates/                     34 Jinja templates
static/css/app.css             global responsive UI, animation, and 3D layer
static/js/app.js               live controls, copy/share, minimize/fullscreen
static/uploads/                student and teacher resource storage
static/qr/                     generated session QR files
tests/                         62 integration and requirement tests
browser_tests/                 31 Chromium/Firefox/WebKit interaction tests
run_device_matrix.py           12-profile × 14-page responsive renderer
Dockerfile                     non-root Waitress production image
Dockerfile.test                isolated test image
compose.yaml                   local persistent Docker deployment
compose.production.yaml        Caddy HTTPS deployment
.github/workflows/ci.yml       Python 3.11–3.14 core matrix
.github/workflows/browser-matrix.yml  browser, Docker smoke, GHCR publish
REQUIREMENTS_TRACEABILITY_1.5.2.md    requirement-by-requirement evidence
TEST_REPORT_1.5.2.md                 actual PASS/NOT RUN report
```

## Security before real use

1. Change the default administrator password immediately.
2. Replace `AYD_SECRET_KEY` with a long random value.
3. Enable HTTPS and set `AYD_COOKIE_SECURE=1` in production.
4. Never commit `.env`, databases, uploads, exports, backups, or generated QR files.
5. Keep server-side file-type and 10 MB enforcement enabled.
6. Back up the database, uploads, resources, QR files, exports, and logo.
7. Define student mobile-number privacy, retention, consent, and deletion rules before commercial deployment.
8. Run only one application instance with SQLite. Migrate to PostgreSQL before horizontal scaling.

Generate a strong secret on Windows:

```powershell
py -3.14 -c "import secrets; print(secrets.token_urlsafe(48))"
```

## Windows installation

### Automated installation

Extract the release ZIP, open PowerShell as a normal user, and run:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\INSTALL_1_5_2.ps1 -InstallPath "D:\AskYourDoubtGlobal"
```

Or double-click:

```text
INSTALL_1_5_2.bat
```

The installer copies `.env.windows.example` to `.env` when `.env` does not exist. Edit the secret before starting the server.

### Manual installation

```powershell
cd D:\AskYourDoubtGlobal
py -3.14 -m pip install --upgrade pip
py -3.14 -m pip install -r requirements.txt
Copy-Item .env.windows.example .env
notepad .env
```

Start the production-like Windows server:

```powershell
.\start_waitress.bat
```

Or directly:

```powershell
$env:AYD_SECRET_KEY="replace-with-a-long-random-secret"
$env:AYD_BASE_URL="http://127.0.0.1:9000"
$env:AYD_PORT="9000"
py -3.14 -m waitress --listen=0.0.0.0:9000 --threads=8 app:app
```

Open:

```text
http://127.0.0.1:9000
http://127.0.0.1:9000/healthz
```

## Environment variables

### Windows `.env`

Use `.env.windows.example`:

```env
AYD_SECRET_KEY=replace-with-a-long-random-secret
AYD_BASE_URL=http://127.0.0.1:9000
AYD_PORT=9000
AYD_THREADS=8
AYD_DEBUG=0
AYD_COOKIE_SECURE=0
```

### Docker `.env`

Use `.env.example`:

```env
AYD_SECRET_KEY=replace-with-a-long-random-secret
AYD_DATABASE=/app/data/database.db
AYD_BASE_URL=http://127.0.0.1:9000
AYD_PORT=9000
AYD_THREADS=8
AYD_DEBUG=0
AYD_COOKIE_SECURE=0
AYD_UPLOAD_DOUBTS=/app/static/uploads/doubts
AYD_UPLOAD_RESOURCES=/app/static/uploads/resources
AYD_QR_FOLDER=/app/static/qr
AYD_EXPORT_FOLDER=/app/exports
```

For HTTPS production, set:

```env
AYD_BASE_URL=https://ask.sagarkerhalkar.com
AYD_COOKIE_SECURE=1
AYD_DEBUG=0
```

`AYD_BASE_URL` must match the public URL before creating sessions; otherwise generated join links and QR codes can contain the wrong host.

## Complete debug and QA commands

Install development dependencies:

```powershell
cd D:\AskYourDoubtGlobal
py -3.14 -m pip install -r requirements-dev.txt
```

Validate dependency resolution:

```powershell
py -3.14 -m pip install --dry-run -r requirements-dev.txt
```

Compile all Python source and tests:

```powershell
py -3.14 -m compileall -q app.py auth.py config.py db.py utils.py routes tests browser_tests run_device_matrix.py
```

List all Flask routes:

```powershell
$env:AYD_DATABASE="$env:TEMP\ayd-route-check.db"
py -3.14 -c "import app; rules=sorted(str(r) for r in app.app.url_map.iter_rules()); print('Registered routes:',len(rules)); print('\n'.join(rules)); assert len(rules) >= 57"
Remove-Item "$env:TEMP\ayd-route-check.db" -ErrorAction SilentlyContinue
```

Run the permission-safe complete functional suite:

```powershell
$stamp = Get-Date -Format "yyyyMMdd_HHmmss_fff"
$run = Join-Path $PWD "test_results\manual_$stamp"
$tmp = Join-Path $run "temp"
$base = Join-Path $run "pytest"
New-Item -ItemType Directory -Force $tmp | Out-Null
$env:TEMP = $tmp
$env:TMP = $tmp
py -3.14 -m pytest -q tests --basetemp "$base" -p no:cacheprovider --junitxml "$run\core-junit.xml"
```

Run the 12-device responsive matrix:

```powershell
py -3.14 run_device_matrix.py
```

Run Chromium only:

```powershell
py -3.14 -m playwright install chromium
py -3.14 -m pytest -q browser_tests --browser chromium --basetemp ".\test_results\browser-chromium" -p no:cacheprovider --junitxml ".\test_results\browser-chromium.xml"
```

Run Chromium, Firefox, and WebKit:

```powershell
py -3.14 -m playwright install chromium firefox webkit
py -3.14 -m pytest -q browser_tests --browser chromium --browser firefox --browser webkit --basetemp ".\test_results\browser-all" -p no:cacheprovider --junitxml ".\test_results\browser-all.xml"
```

Run the standard quality gate:

```powershell
.\run_debug_ci_cd.bat
```

Run the browser matrix:

```powershell
.\run_browser_matrix.bat
```

Run full browser + Docker QA:

```powershell
.\RUN_FULL_QA_1_5_2.bat
```

Every QA result must be reported as `PASS`, `FAIL`, or `NOT RUN`; do not call a configured workflow a pass until it actually executes.

## Docker local deployment

Docker Desktop must be installed and running.

```powershell
cd D:\AskYourDoubtGlobal
Copy-Item .env.example .env
notepad .env
docker compose config
docker compose up -d --build
docker compose ps
docker compose logs -f --tail 200
```

Open `http://127.0.0.1:9000`.

Stop without deleting persistent data:

```powershell
docker compose down
```

Do not run `docker compose down -v` unless you deliberately want to delete the database and persistent volumes.

### Manual Docker image

```powershell
docker build -t askyourdoubt:1.5.2 .
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
  askyourdoubt:1.5.2
```

Health smoke:

```powershell
Start-Sleep -Seconds 8
Invoke-WebRequest http://127.0.0.1:9000/healthz -UseBasicParsing
docker logs askyourdoubt
```

### Docker test image

```powershell
docker build -f Dockerfile.test -t askyourdoubt:test .
docker run --rm askyourdoubt:test
```

## Public HTTPS deployment with Caddy

1. Obtain an Ubuntu server.
2. Point `ask.sagarkerhalkar.com` to the server public IP.
3. Allow TCP 80 and 443 and UDP 443.
4. Install Docker Engine and Docker Compose.
5. Clone the repository.
6. Create production `.env`.
7. Copy and review the Caddyfile.
8. Start the production stack.

```bash
git clone https://github.com/sagarkerhalkar/AskYourDoubt.git
cd AskYourDoubt
cp .env.example .env
cp deploy/Caddyfile.example deploy/Caddyfile
nano .env
nano deploy/Caddyfile
docker compose -f compose.production.yaml config
docker compose -f compose.production.yaml up -d --build
docker compose -f compose.production.yaml ps
docker compose -f compose.production.yaml logs -f --tail 200
```

Caddy obtains and renews HTTPS certificates only when DNS and public ports are correct.

## CI/CD

`.github/workflows/ci.yml` runs the core suite on Python 3.11, 3.12, 3.13, and 3.14.

`.github/workflows/browser-matrix.yml` runs:

1. Python compilation and 57-route threshold.
2. All 57 functional/requirement tests.
3. Independent Chromium, Firefox, and WebKit jobs.
4. Docker production build and `/healthz` smoke test.
5. GHCR image publishing after a successful main-branch or release-tag push.

Push and inspect GitHub Actions:

```powershell
git add .
git commit -m "Release AskYourDoubt 1.5.2 commercial global UI and QA"
git tag v1.5.2
git push origin main
git push origin v1.5.2
```

Do not publish or deploy when any required job is red or missing.

## Backup

### Native SQLite backup

Stop writes or use SQLite's online backup API:

```powershell
py -3.14 -c "import sqlite3; s=sqlite3.connect('database.db'); d=sqlite3.connect('backups/database.backup.db'); s.backup(d); d.close(); s.close()"
```

### Docker database backup

```powershell
New-Item -ItemType Directory -Force .\backups | Out-Null
docker exec askyourdoubt python -c "import sqlite3; s=sqlite3.connect('/app/data/database.db'); d=sqlite3.connect('/app/data/database.backup.db'); s.backup(d); d.close(); s.close()"
docker cp askyourdoubt:/app/data/database.backup.db .\backups\database.backup.db
```

Also back up uploads, resources, generated QR files, exports, and the replacement logo.

## Troubleshooting

### Port 9000 is busy

```powershell
netstat -ano | findstr :9000
tasklist /FI "PID eq <PID>"
```

Change `AYD_PORT` and `AYD_BASE_URL` together.

### QR opens the wrong address

Correct `AYD_BASE_URL`, restart the application, and create a new session or regenerate its QR.

### Browser shows old CSS or JavaScript

```powershell
ipconfig /flushdns
```

Then hard refresh with `Ctrl+F5`, close old tabs, and confirm that the server is running the new extracted folder.

### Device-test screenshot folder is locked on Windows

Close File Explorer previews and image viewers. The runner automatically falls back to a new folder under the Windows temporary directory when the project evidence directory is locked.

### Database is locked

Confirm that only one application instance is using the SQLite file. SQLite is not for multiple horizontally scaled application containers.

## Actual release evidence

See:

- `TEST_REPORT_1.5.2.md`
- `REQUIREMENTS_TRACEABILITY_1.5.2.md`
- `test_evidence_1_5_2/`

The local environment did not have Docker installed, Firefox/WebKit binaries, or permission for Chromium localhost navigation, so those executions are correctly recorded as `NOT RUN` locally. The deterministic Chromium rendering matrix passed 168/168 checks. The CI jobs are configured, but their result must be checked after pushing to GitHub. The packaged ZIP is verified after generation and the extracted copy is rerun through the core suite.

## Scale limitation

This SQLite release is suitable for local development, demonstrations, pilots, and one application instance. It is not a 50,000,000-concurrent-student production architecture. Large deployment requires PostgreSQL, Redis, object storage, CDN, realtime gateways, queues, rate limiting, load balancing, observability, backups, multi-region planning, privacy controls, and security testing. See `PRODUCTION_SCALE_PLAN.md`.

## Default administrator

```text
Username: admin
Password: admin123
```

Change it immediately after first login.

## License

All rights reserved. No open-source license is granted unless the repository owner deliberately adds one.
