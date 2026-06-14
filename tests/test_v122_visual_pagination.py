from datetime import datetime, timezone
from pathlib import Path

from db import get_db

ROOT = Path(__file__).resolve().parents[1]


def create_session(teacher_client, name='Pagination Session'):
    response = teacher_client.post('/teacher/create-session', data={
        'session_name': name,
        'duration': '90',
        'question_limit': '1000',
    })
    assert response.status_code == 302
    return int(response.headers['Location'].rstrip('/').split('/')[-1])


def test_live_doubts_default_100_and_optional_500(app, teacher_client):
    session_id = create_session(teacher_client)
    student = app.test_client()
    response = student.post(
        f'/join-session/{session_id}',
        data={'name': 'Pagination Student', 'mobile': '9888888888'},
    )
    assert response.status_code == 302

    with app.app_context():
        db = get_db()
        student_id = db.execute("SELECT id FROM students WHERE mobile='9888888888'").fetchone()['id']
        db.executemany(
            '''INSERT INTO doubts(session_id,student_id,question,category,keyword,votes,status,created_at)
               VALUES(?,?,?,?,?,?,?,?)''',
            [
                (session_id, student_id, f'Question {index}', 'General', 'Question', index % 7, 'OPEN', datetime.now(timezone.utc).isoformat())
                for index in range(120)
            ],
        )
        db.commit()

    teacher_default = teacher_client.get(f'/api/teacher/session/{session_id}').get_json()
    assert len(teacher_default['open']) == 100
    assert teacher_default['pagination']['per_page'] == 100
    assert teacher_default['pagination']['pages'] == 2

    teacher_500 = teacher_client.get(f'/api/teacher/session/{session_id}?per_page=500').get_json()
    assert len(teacher_500['open']) == 120
    assert teacher_500['pagination']['per_page'] == 500

    student_default = student.get(f'/api/student/session/{session_id}').get_json()
    assert len(student_default['open']) == 100
    assert student_default['pagination']['pages'] == 2

    student_500 = student.get(f'/api/student/session/{session_id}?per_page=500').get_json()
    assert len(student_500['open']) == 120


def test_standard_pages_offer_10_20_30_pagination(app, teacher_client, admin_client):
    with app.app_context():
        db = get_db()
        teacher_id = db.execute("SELECT id FROM teachers WHERE username='teacher'").fetchone()['id']
        db.executemany(
            "INSERT INTO sessions(teacher_id,session_name,duration,status,question_limit) VALUES(?, ?, 90, 'CLOSED', 100)",
            [(teacher_id, f'Session {index}') for index in range(35)],
        )
        db.commit()

    teacher_page = teacher_client.get('/teacher-dashboard?per_page=10&page=2')
    assert teacher_page.status_code == 200
    assert b'Page 2 / 4' in teacher_page.data
    assert b'>10<' in teacher_page.data and b'>20<' in teacher_page.data and b'>30<' in teacher_page.data

    admin_page = admin_client.get('/admin/sessions?per_page=20&page=2')
    assert admin_page.status_code == 200
    assert b'Page 2 / 2' in admin_page.data


def test_v122_visual_animation_and_compact_home_contracts():
    css = (ROOT / 'static' / 'css' / 'app.css').read_text(encoding='utf-8')
    teacher = (ROOT / 'templates' / 'teacher' / 'live_session.html').read_text(encoding='utf-8')
    student = (ROOT / 'templates' / 'student' / 'portal.html').read_text(encoding='utf-8')
    device_runner = (ROOT / 'run_device_matrix.py').read_text(encoding='utf-8')

    for token in (
        '.kinetic-scene', 'transform-style:preserve-3d', '@keyframes coreFloat',
        '@keyframes orbitSpin', '@keyframes newDoubtArrival', '.hero h1{font-size:clamp(2rem,3.2vw,2.85rem)',
    ):
        assert token in css
    assert 'option value="500"' in teacher
    assert 'option value="500"' in student
    assert 'LIVE_PAGE_SIZES = (100, 250, 500)' in (ROOT / 'routes' / 'api.py').read_text(encoding='utf-8')
    assert 'RUN_STAMP' in device_runner
    assert 'shutil.rmtree(RESULTS)' not in device_runner
