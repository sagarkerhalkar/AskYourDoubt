from pathlib import Path

from werkzeug.security import generate_password_hash

from db import get_db

ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding='utf-8')


def create_session(client, name: str) -> int:
    response = client.post('/teacher/create-session', data={
        'session_name': name,
        'duration': '90',
        'question_limit': '100',
    })
    assert response.status_code == 302
    return int(response.headers['Location'].rstrip('/').split('/')[-1])


def join_student(app, session_id: int, name: str, mobile: str):
    client = app.test_client()
    response = client.post(
        f'/join-session/{session_id}',
        data={'name': name, 'mobile': mobile},
    )
    assert response.status_code == 302
    return client


def test_release_version_health_and_production_defaults(client):
    assert read('VERSION').strip() == '1.5.2'
    response = client.get('/healthz')
    assert response.status_code == 200
    assert response.get_json() == {'service': 'askyourdoubt', 'status': 'ok'}

    config = read('config.py')
    app_source = read('app.py')
    assert "AYD_PORT" in config
    assert "AYD_DEBUG" in config
    assert "AYD_COOKIE_SECURE" in config
    assert "debug=app.config['DEBUG']" in app_source


def test_global_commercial_typography_and_compact_headers_contract():
    css = read('static/css/app.css')
    required = [
        'AskYourDoubt 1.5.0',
        '--global-navy:#0f1f3d',
        'h1{font-size:clamp(1.45rem,1.9vw,1.85rem)}',
        '.hero h1{font-size:clamp(2rem,3.8vw,2.8rem)',
        '.teacher-dashboard-hero{',
        'min-height:168px',
        '.teacher-live-launcher{',
        'min-height:164px',
        '.student-welcome-v14{',
        'min-height:150px',
        '.teacher-command-copy-v141 h1{font-size:clamp(1.35rem,2vw,1.7rem)',
        '@media(hover:hover) and (pointer:fine)',
        '@media(hover:none)',
        '@media(prefers-reduced-motion:reduce)',
    ]
    for token in required:
        assert token in css, token


def test_live_panels_support_minimize_maximize_and_silent_polling(app, teacher_client):
    sid = create_session(teacher_client, 'Commercial Live Controls')
    student_client = join_student(app, sid, 'Commercial Student', '9555555555')

    teacher_html = teacher_client.get(f'/teacher/session/{sid}').get_data(as_text=True)
    student_html = student_client.get(f'/student/session/{sid}?tab=live').get_data(as_text=True)

    for html, target in (
        (teacher_html, '#teacherFocusStage'),
        (student_html, '#studentFocusStage'),
    ):
        assert f'data-minimize-target="{target}"' in html
        assert 'aria-expanded="true"' in html
        assert 'const POLL_INTERVAL_MS = 1000' in html
        assert 'window.setInterval(load, POLL_INTERVAL_MS)' in html
        assert 'if (loading) return' in html
        assert "cache: 'no-store'" in html or "cache:'no-store'" in html
        assert 'visibilitychange' in html

    js = read('static/js/app.js')
    css = read('static/css/app.css')
    assert "document.querySelectorAll('[data-minimize-target]')" in js
    assert "target.classList.toggle('is-minimized'" in js
    assert "button.textContent = minimized ? 'Maximize' : 'Minimize'" in js
    assert '.teacher-focus-stage.is-minimized' in css
    assert '.student-focus-stage.is-minimized' in css


def test_teacher_session_and_student_data_are_isolated_between_two_teachers(app, teacher_client):
    first_sid = create_session(teacher_client, 'Teacher One Session')

    with app.app_context():
        db = get_db()
        db.execute(
            '''INSERT INTO teachers(name,mobile,email,dob,username,password,status)
               VALUES(?,?,?,?,?,?,?)''',
            (
                'Second Teacher',
                '9666666666',
                'second@example.com',
                '1991-01-01',
                'teacher2',
                generate_password_hash('teacher234'),
                'ACTIVE',
            ),
        )
        db.commit()

    second_teacher = app.test_client()
    assert second_teacher.post(
        '/teacher-login',
        data={'username': 'teacher2', 'password': 'teacher234'},
    ).status_code == 302
    second_sid = create_session(second_teacher, 'Teacher Two Session')

    student_one = join_student(app, first_sid, 'First Session Student', '9777777771')
    student_two = join_student(app, second_sid, 'Second Session Student', '9777777772')
    assert student_one.post(
        f'/student/session/{first_sid}/submit',
        data={'question': 'Question only for teacher one'},
    ).status_code == 302
    assert student_two.post(
        f'/student/session/{second_sid}/submit',
        data={'question': 'Question only for teacher two'},
    ).status_code == 302

    first_data = teacher_client.get(f'/api/teacher/session/{first_sid}').get_json()
    second_data = second_teacher.get(f'/api/teacher/session/{second_sid}').get_json()
    assert [item['question'] for item in first_data['open']] == ['Question only for teacher one']
    assert [item['question'] for item in second_data['open']] == ['Question only for teacher two']

    assert teacher_client.get(f'/api/teacher/session/{second_sid}').status_code in (302, 403, 404)
    assert second_teacher.get(f'/api/teacher/session/{first_sid}').status_code in (302, 403, 404)


def test_docker_compose_and_full_ci_cd_contracts_exist():
    dockerfile = read('Dockerfile')
    docker_test = read('Dockerfile.test')
    compose = read('compose.yaml')
    production = read('compose.production.yaml')
    workflow = read('.github/workflows/browser-matrix.yml')

    assert 'FROM python:3.14-slim' in dockerfile
    assert 'USER ayd' in dockerfile
    assert 'HEALTHCHECK' in dockerfile
    assert 'waitress-serve' in dockerfile
    assert 'pytest' in docker_test
    assert 'ayd_database:/app/data' in compose
    assert 'restart: unless-stopped' in compose
    assert 'caddy:2.10-alpine' in production
    assert 'matrix:' in workflow
    for browser in ('chromium', 'firefox', 'webkit'):
        assert browser in workflow
    assert 'docker-smoke:' in workflow
    assert 'publish-ghcr:' in workflow
    assert 'docker/build-push-action@v6' in workflow


def test_live_teacher_response_never_exposes_student_identity(app, teacher_client):
    sid = create_session(teacher_client, 'Anonymous Teacher View')
    student = join_student(app, sid, 'Private Student Name', '9888888888')
    student.post(
        f'/student/session/{sid}/submit',
        data={'question': 'Identity must stay hidden'},
    )

    payload = teacher_client.get(f'/api/teacher/session/{sid}').get_json()
    serialized = str(payload['open'])
    assert 'Private Student Name' not in serialized
    assert '9888888888' not in serialized
    assert 'student_name' not in payload['open'][0]
    assert 'student_mobile' not in payload['open'][0]
