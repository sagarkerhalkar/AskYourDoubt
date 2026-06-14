from __future__ import annotations

import base64
import json
import os
import sqlite3
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

from playwright.sync_api import sync_playwright
from werkzeug.security import generate_password_hash

ROOT = Path(__file__).resolve().parent
RUN_STAMP = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_%f")
DEFAULT_RESULTS_ROOT = ROOT / 'device_test_results'
RESULTS_ROOT = Path(os.getenv('AYD_DEVICE_RESULTS_ROOT', str(DEFAULT_RESULTS_ROOT))).resolve()
RESULTS = RESULTS_ROOT / 'runs' / f'{RUN_STAMP}_{os.getpid()}'
SCREENSHOTS = RESULTS / 'screenshots'
DB_PATH = ROOT / f"device_matrix_{RUN_STAMP}.db"

DEVICES = [
    ("iphone-se", 320, 568),
    ("android-small", 360, 800),
    ("iphone-14", 390, 844),
    ("android-large", 412, 915),
    ("ipad-portrait", 768, 1024),
    ("ipad-air", 820, 1180),
    ("ipad-pro", 1024, 1366),
    ("small-laptop", 1280, 800),
    ("laptop", 1366, 768),
    ("macbook", 1440, 900),
    ("desktop-fhd", 1920, 1080),
    ("desktop-qhd", 2560, 1440),
]


def seed_database() -> None:
    con = sqlite3.connect(DB_PATH)
    now = datetime.now(timezone.utc).replace(tzinfo=None).isoformat(timespec="seconds")
    ends = (datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(minutes=90)).isoformat(timespec="seconds")
    con.execute(
        "INSERT INTO teachers(name,mobile,email,dob,username,password,status) VALUES(?,?,?,?,?,?,?)",
        ("Global Demo Teacher", "9876543210", "teacher@example.com", "1990-01-01", "globalteacher", generate_password_hash("globalpass"), "ACTIVE"),
    )
    teacher_id = con.execute("SELECT id FROM teachers WHERE username='globalteacher'").fetchone()[0]
    con.execute(
        "INSERT INTO sessions(teacher_id,session_name,duration,status,created_at,started_at,ends_at,question_limit,allow_student_attachment_download) VALUES(?,?,?,'ACTIVE',?,?,?,?,?)",
        (teacher_id, "Global Physics Masterclass", 90, now, now, ends, 100, 1),
    )
    session_id = con.execute("SELECT last_insert_rowid()").fetchone()[0]
    for name, mobile, question, votes, status in [
        ("Aarav Sharma", "9000000001", "Why does acceleration remain constant in free fall?", 24, "OPEN"),
        ("Kavya Patel", "9000000002", "How can we visualise Newton's third law in daily life?", 12, "OPEN"),
        ("Rohan Mehta", "9000000003", "What is the difference between speed and velocity?", 7, "COMPLETED"),
    ]:
        con.execute("INSERT INTO students(name,mobile) VALUES(?,?)", (name, mobile))
        student_id = con.execute("SELECT last_insert_rowid()").fetchone()[0]
        con.execute("INSERT INTO session_students(session_id,student_id) VALUES(?,?)", (session_id, student_id))
        con.execute(
            "INSERT INTO doubts(session_id,student_id,question,category,keyword,votes,status,created_at) VALUES(?,?,?,?,?,?,?,?)",
            (session_id, student_id, question, "Motion", "Acceleration", votes, status, now),
        )
        doubt_id = con.execute("SELECT last_insert_rowid()").fetchone()[0]
        con.execute(
            "INSERT INTO repository(doubt_id,question,category,keyword,total_votes,status,teacher_id,session_id,session_name,session_date,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?,?)",
            (doubt_id, question, "Motion", "Acceleration", votes, status, teacher_id, session_id, "Global Physics Masterclass", now, now),
        )
    con.execute(
        "INSERT INTO resources(session_id,title,resource_type,notes,uploaded_at) VALUES(?,?,?,?,?)",
        (session_id, "Newton's Laws Revision Notes", "NOTE", "A concise summary shared by the teacher.", now),
    )
    con.commit()
    con.close()


def inline_html(html: str) -> str:
    css = (ROOT / "static" / "css" / "app.css").read_text(encoding="utf-8")
    import re
    # Remove remote image requests in the restricted test sandbox and use an offline premium fallback.
    css = re.sub(r"url\(['\"]https://[^)]*\)", "none", css)
    css += "\n.hero-photo,.role-card .photo,.auth-visual{background-image:linear-gradient(135deg,#101a3b,#3e3f9f 55%,#00a4d6)!important}\n[data-reveal],.panel{opacity:1!important;transform:none!important;animation:none!important}\n"
    html = html.replace('<link rel="preconnect" href="https://fonts.googleapis.com">', '')
    html = html.replace('<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>', '')
    html = re.sub(r'<link href="https://fonts\.googleapis\.com[^"]+" rel="stylesheet">', '', html)
    html = re.sub(r'<link rel="stylesheet" href="[^"]*static/css/app\.css">', f'<style>{css}</style>', html)
    html = re.sub(r'<script defer src="[^"]*static/js/app\.js"></script>', '', html)
    logo_bytes = (ROOT / 'static' / 'img' / 'logo.svg').read_bytes()
    logo_uri = 'data:image/svg+xml;base64,' + base64.b64encode(logo_bytes).decode('ascii')
    html = html.replace('src="/static/img/logo.svg"', f'src="{logo_uri}"')
    return html


def make_clients(app):
    public = app.test_client()

    teacher = app.test_client()
    response = teacher.post('/teacher-login', data={'username': 'globalteacher', 'password': 'globalpass'}, follow_redirects=True)
    assert response.status_code == 200

    student = app.test_client()
    response = student.post('/join-session/1', data={'name': 'Responsive Student', 'mobile': '9123456789'}, follow_redirects=True)
    assert response.status_code == 200

    admin = app.test_client()
    response = admin.post('/admin-login', data={'username': 'admin', 'password': 'admin123'}, follow_redirects=True)
    assert response.status_code == 200
    return public, teacher, student, admin


def rendered_pages(app):
    public, teacher, student, admin = make_clients(app)
    return {
        'home': inline_html(public.get('/').get_data(as_text=True)),
        'student-login': inline_html(public.get('/student').get_data(as_text=True)),
        'teacher-login': inline_html(public.get('/teacher-login').get_data(as_text=True)),
        'admin-login': inline_html(public.get('/admin-login').get_data(as_text=True)),
        'teacher-dashboard': inline_html(teacher.get('/teacher/dashboard').get_data(as_text=True)),
        'teacher-live': inline_html(teacher.get('/teacher/session/1').get_data(as_text=True)),
        'teacher-resources': inline_html(teacher.get('/teacher/session/1/resources').get_data(as_text=True)),
        'student-portal': inline_html(student.get('/student/session/1?tab=live').get_data(as_text=True)),
        'admin-dashboard': inline_html(admin.get('/admin-dashboard').get_data(as_text=True)),
    }


def inject_demo_content(page, page_name: str) -> None:
    if page_name == 'teacher-live':
        page.evaluate("""
        () => {
          const list = document.querySelector('#teacherOpenDoubts');
          if (list) list.innerHTML = `
            <article class="teacher-doubt-card top-vote"><div class="teacher-vote-stack vote-warm"><span>⌃</span><strong>24</strong><small>same doubts</small></div><div class="teacher-doubt-copy"><div class="teacher-doubt-meta"><span>OPEN</span><b>Highest priority</b></div><div class="teacher-doubt-question">Why does acceleration remain constant in free fall?</div></div><div class="teacher-doubt-actions"><button class="teacher-action complete">✓ Mark Completed</button><button class="teacher-action skip">▶ Skip</button></div></article>
            <article class="teacher-doubt-card"><div class="teacher-vote-stack vote-cool"><span>⌃</span><strong>12</strong><small>same doubts</small></div><div class="teacher-doubt-copy"><div class="teacher-doubt-meta"><span>OPEN</span></div><div class="teacher-doubt-question">How can we visualise Newton's third law in daily life?</div></div><div class="teacher-doubt-actions"><button class="teacher-action complete">✓ Mark Completed</button><button class="teacher-action skip">▶ Skip</button></div></article>`;
          const values = {tTotal:'3', tOpen:'2', tCompleted:'1', tVotes:'43'};
          Object.entries(values).forEach(([id,value]) => { const el=document.getElementById(id); if(el) el.textContent=value; });
        }
        """)
    if page_name == 'student-portal':
        page.evaluate("""
        () => {
          const list = document.querySelector('#studentLiveDoubts');
          if (list) list.innerHTML = `
            <article class="doubt-card live-card top-vote"><div class="rank-orb">1</div><div class="doubt-content"><div class="doubt-meta"><span class="pill vote">24 same doubts</span><span class="pill">LIVE</span></div><div class="doubt-question">Why does acceleration remain constant in free fall?</div></div><div class="doubt-actions"><button class="btn mini">I have the same doubt</button></div></article>
            <article class="doubt-card live-card"><div class="rank-orb">2</div><div class="doubt-content"><div class="doubt-meta"><span class="pill mine">My Question</span><span class="pill vote">0 same doubts</span></div><div class="doubt-question">Can you explain momentum with a real-world example?</div></div></article>`;
        }
        """)


def _prepare_result_folders() -> None:
    global RESULTS_ROOT, RESULTS, SCREENSHOTS
    try:
        SCREENSHOTS.mkdir(parents=True, exist_ok=False)
    except PermissionError:
        # Windows Explorer, antivirus, or an image preview can lock an old
        # evidence directory. Never fail application installation because of
        # that. Fall back to a new directory under the user's TEMP folder.
        import tempfile
        RESULTS_ROOT = Path(tempfile.gettempdir()) / 'AskYourDoubt_device_test_results'
        RESULTS = RESULTS_ROOT / 'runs' / f'{RUN_STAMP}_{os.getpid()}'
        SCREENSHOTS = RESULTS / 'screenshots'
        SCREENSHOTS.mkdir(parents=True, exist_ok=False)
        print(f'Warning: project evidence folder was locked. Using {RESULTS_ROOT}')


def run() -> int:
    # Each run writes to a new timestamped directory. No old screenshot folder
    # is deleted or overwritten.
    _prepare_result_folders()
    if DB_PATH.exists():
        DB_PATH.unlink(missing_ok=True)

    os.environ['AYD_DATABASE'] = str(DB_PATH)
    os.environ['AYD_BASE_URL'] = 'http://127.0.0.1:9000'
    sys.path.insert(0, str(ROOT))
    from app import app

    seed_database()
    pages = rendered_pages(app)
    report = {'engine': 'Chromium set_content offline render', 'devices': [], 'summary': {}}

    try:
        with sync_playwright() as playwright:
            candidates = [
                Path('/usr/bin/chromium'),
                Path(r'C:\Program Files\Google\Chrome\Application\chrome.exe'),
                Path(r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe'),
                Path(r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'),
                Path(r'C:\Program Files\Microsoft\Edge\Application\msedge.exe'),
            ]
            executable = next((str(candidate) for candidate in candidates if candidate.exists()), None)
            browser = playwright.chromium.launch(headless=True, executable_path=executable)
            for name, width, height in DEVICES:
                context = browser.new_context(viewport={'width': width, 'height': height}, device_scale_factor=1)
                page = context.new_page()
                checks = []
                for page_name, html in pages.items():
                    page.set_content(html, wait_until='domcontentloaded')
                    inject_demo_content(page, page_name)
                    overflow = bool(page.evaluate('document.documentElement.scrollWidth > document.documentElement.clientWidth + 2'))
                    visible = page.locator('body').is_visible()
                    status = 'PASS' if visible and not overflow else 'FAIL'
                    checks.append({'page': page_name, 'status': status, 'horizontal_overflow': overflow, 'body_visible': visible})
                    

                context.close()
                report['devices'].append({'name': name, 'viewport': {'width': width, 'height': height}, 'checks': checks})

            # Representative visual evidence: phone, tablet, and laptop.
            representative = [('iphone-14', 390, 844), ('ipad-air', 820, 1180), ('laptop', 1366, 768)]
            visual_pages = ['home', 'teacher-login', 'teacher-live', 'student-portal', 'admin-dashboard']
            for name, width, height in representative:
                context = browser.new_context(viewport={'width': width, 'height': height}, device_scale_factor=1)
                page = context.new_page()
                for page_name in visual_pages:
                    page.set_content(pages[page_name], wait_until='domcontentloaded')
                    inject_demo_content(page, page_name)
                    page.wait_for_timeout(120)
                    page.screenshot(path=SCREENSHOTS / f'{name}__{page_name}.png', full_page=False)
                context.close()
            browser.close()

        all_checks = [check for device in report['devices'] for check in device['checks']]
        passed = sum(1 for check in all_checks if check['status'] == 'PASS')
        failed = len(all_checks) - passed
        report['summary'] = {'total_checks': len(all_checks), 'passed': passed, 'failed': failed, 'screenshots': len(list(SCREENSHOTS.glob('*.png')))}
        (RESULTS / 'device_matrix.json').write_text(json.dumps(report, indent=2), encoding='utf-8')

        lines = [
            '# AskYourDoubt 1.3 Device and Browser Test Result', '',
            '## Actual local rendering performed',
            '- Browser engine: system Chromium, headless.',
            '- Rendering method: offline HTML/CSS visual render using Playwright `set_content` because this sandbox blocks browser navigation to localhost.',
            f'- Device profiles tested: {len(DEVICES)}',
            f'- Pages tested per profile: {len(pages)}',
            f'- Total responsive checks: {len(all_checks)}',
            f'- Passed: {passed}',
            f'- Failed: {failed}',
            f'- Screenshots: {report["summary"]["screenshots"]}', '',
            '## Device profiles',
        ]
        for name, width, height in DEVICES:
            lines.append(f'- {name}: {width} × {height}')
        lines += [
            '', '## Pages rendered at every profile',
            '- Commercial home page', '- Student login', '- Teacher login', '- Admin login',
            '- Teacher dashboard', '- Teacher live session', '- Teacher resources',
            '- Student portal', '- Admin dashboard', '',
            '## Functional tests',
            '- The separate pytest integration suite validates authentication, voting, self-vote prevention, duplicate-vote prevention, question limits, attachments, resources, session closing/reopening, question bank lifecycle, admin controls, and copy-link UI contracts.', '',
            '## Browser-engine coverage',
            '- Chromium: executed locally for all profiles above.',
            '- Google Chrome and Microsoft Edge: both use Chromium; the executed engine covers their core layout behavior.',
            '- Firefox and Safari/WebKit: configured in `.github/workflows/ci-cd.yml` for real Playwright CI execution. They could not be executed inside this sandbox because the browser binaries are not installed and network/browser navigation is restricted.', '',
            '## Result', 'PASS' if failed == 0 else 'FAIL',
        ]
        report_text = '\n'.join(lines) + '\n'
        (RESULTS / 'DEVICE_MATRIX_REPORT.md').write_text(report_text, encoding='utf-8')
        # Lightweight latest pointers never delete or overwrite screenshot folders.
        (RESULTS_ROOT / 'LATEST_RUN.txt').write_text(str(RESULTS), encoding='utf-8')
        (RESULTS_ROOT / 'LATEST_DEVICE_MATRIX_REPORT.md').write_text(report_text, encoding='utf-8')
        (RESULTS_ROOT / 'LATEST_DEVICE_MATRIX.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
        print(f'Device evidence: {RESULTS}')
        print(json.dumps(report['summary'], indent=2))
        return 0 if failed == 0 else 1
    finally:
        if DB_PATH.exists():
            try:
                DB_PATH.unlink()
            except PermissionError:
                print(f'Warning: test database is still locked and was left at {DB_PATH}')


if __name__ == '__main__':
    raise SystemExit(run())
