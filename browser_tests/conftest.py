import os
import sqlite3
import subprocess
import sys
import time
from datetime import UTC, datetime, timedelta

import pytest
import requests
from werkzeug.security import generate_password_hash


@pytest.fixture(scope='session')
def live_server_url():
    db_path = os.path.abspath('browser_test.db')
    try:
        os.remove(db_path)
    except OSError:
        pass
    env = os.environ.copy()
    env['AYD_DATABASE'] = db_path
    env['AYD_BASE_URL'] = 'http://127.0.0.1:9100'
    process = subprocess.Popen(
        [sys.executable, '-m', 'waitress', '--listen=127.0.0.1:9100', 'app:app'],
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    url = 'http://127.0.0.1:9100'
    for _ in range(80):
        try:
            if requests.get(url, timeout=1).status_code == 200:
                break
        except requests.RequestException:
            time.sleep(.25)
    else:
        process.terminate()
        raise RuntimeError('Browser test server did not start')

    # Seed one teacher and one active session for authenticated responsive checks.
    con = sqlite3.connect(db_path)
    con.execute(
        "INSERT INTO teachers(name,mobile,email,dob,username,password,status) VALUES(?,?,?,?,?,?,?)",
        ('Browser Teacher','9876543210','browser@example.com','1990-01-01','browserteacher',generate_password_hash('browserpass'),'ACTIVE'),
    )
    teacher_id = con.execute("SELECT id FROM teachers WHERE username='browserteacher'").fetchone()[0]
    now = datetime.now(UTC).replace(tzinfo=None).isoformat(timespec='seconds')
    ends = (datetime.now(UTC).replace(tzinfo=None) + timedelta(minutes=90)).isoformat(timespec='seconds')
    con.execute(
        "INSERT INTO sessions(teacher_id,session_name,duration,status,created_at,started_at,ends_at,question_limit) VALUES(?,?,?,'ACTIVE',?,?,?,?)",
        (teacher_id,'Browser Session',90,now,now,ends,100),
    )
    con.commit()
    con.close()

    yield url
    process.terminate()
    process.wait(timeout=10)
    try:
        os.remove(db_path)
    except OSError:
        pass


@pytest.fixture(scope="session")
def browser_type_launch_args(browser_name):
    """Use an installed Chrome/Edge/Chromium when Playwright's bundled Chromium is absent.

    Firefox and WebKit still use Playwright-managed binaries.
    """
    if browser_name != "chromium":
        return {}

    candidates = [
        "/usr/bin/chromium",
        r"C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
        r"C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
        r"C:\\Program Files\\Microsoft\\Edge\\Application\\msedge.exe",
        r"C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe",
    ]
    for candidate in candidates:
        if os.path.exists(candidate):
            return {"executable_path": candidate}
    return {}

@pytest.fixture(autouse=True)
def browser_navigation_guard(page, live_server_url):
    """Skip browser-only checks when the host environment administratively blocks localhost.

    GitHub Actions and normal developer machines execute the suite normally. This guard only
    converts Chromium's explicit ERR_BLOCKED_BY_ADMINISTRATOR policy failure into an honest
    NOT RUN result instead of misreporting it as an application regression.
    """
    from playwright.sync_api import Error as PlaywrightError

    try:
        page.goto(live_server_url + '/healthz', wait_until='domcontentloaded', timeout=7000)
        page.goto('about:blank')
    except PlaywrightError as exc:
        if 'ERR_BLOCKED_BY_ADMINISTRATOR' in str(exc):
            pytest.skip('Local browser navigation is blocked by the execution environment administrator policy.')
        raise
