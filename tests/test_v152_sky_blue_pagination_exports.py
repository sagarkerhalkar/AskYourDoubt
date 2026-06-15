import csv
import io
from pathlib import Path

from db import get_db


def create_session(teacher_client):
    response = teacher_client.post('/teacher/create-session', data={
        'session_name': 'Commercial Physics',
        'duration': '90',
        'question_limit': '100',
    })
    assert response.status_code == 302
    return int(response.headers['Location'].rstrip('/').split('/')[-1])


def join_student(client, session_id):
    response = client.post(
        f'/join-session/{session_id}',
        data={'name': 'Pagination Student', 'mobile': '9000000999'},
    )
    assert response.status_code == 302


def seed_questions(app, session_id, student_id):
    with app.app_context():
        db = get_db()
        rows = []
        rows += [(session_id, student_id, f'Open question {i}', 'OPEN', None) for i in range(1, 6)]
        rows += [(session_id, student_id, f'Completed question {i}', 'COMPLETED', '2026-06-14 12:00:00') for i in range(1, 26)]
        rows += [(session_id, student_id, f'Skipped question {i}', 'SKIPPED', None) for i in range(1, 24)]
        db.executemany(
            '''INSERT INTO doubts(session_id, student_id, question, status, completed_at)
               VALUES(?,?,?,?,?)''',
            rows,
        )
        db.commit()


def test_teacher_completed_and_skipped_pagination(app, teacher_client):
    session_id = create_session(teacher_client)
    student = app.test_client()
    join_student(student, session_id)
    with student.session_transaction() as sess:
        student_id = sess['student_id']
    seed_questions(app, session_id, student_id)

    response = teacher_client.get(
        f'/api/teacher/session/{session_id}'
        '?completed_page=2&completed_per_page=10&skipped_page=3&skipped_per_page=10'
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data['stats']['total'] == 30  # open + completed only
    assert data['stats']['skipped'] == 23
    assert len(data['completed']) == 10
    assert data['completed_pagination']['page'] == 2
    assert data['completed_pagination']['pages'] == 3
    assert len(data['skipped']) == 3
    assert data['skipped_pagination']['page'] == 3
    assert data['skipped_pagination']['pages'] == 3

    page = teacher_client.get(f'/teacher/session/{session_id}')
    assert b'completedPerPage' in page.data
    assert b'skippedPerPage' in page.data
    assert b'Current session export' in page.data
    assert b'Full Page' in page.data


def test_student_answered_pagination(app, teacher_client):
    session_id = create_session(teacher_client)
    student = app.test_client()
    join_student(student, session_id)
    with student.session_transaction() as sess:
        student_id = sess['student_id']
    seed_questions(app, session_id, student_id)

    response = student.get(
        f'/api/student/session/{session_id}?answered_page=3&answered_per_page=10'
    )
    assert response.status_code == 200
    data = response.get_json()
    assert len(data['completed']) == 5
    assert data['answered_pagination']['page'] == 3
    assert data['answered_pagination']['pages'] == 3
    assert data['answered_pagination']['total'] == 25

    page = student.get(f'/student/session/{session_id}?tab=answered')
    assert b'answeredPerPage' in page.data
    assert b'answeredPageInfo' in page.data


def _csv_rows(response):
    text = response.data.decode('utf-8-sig')
    return list(csv.DictReader(io.StringIO(text)))


def test_current_session_filtered_downloads(app, teacher_client):
    session_id = create_session(teacher_client)
    student = app.test_client()
    join_student(student, session_id)
    with student.session_transaction() as sess:
        student_id = sess['student_id']
    seed_questions(app, session_id, student_id)

    total = _csv_rows(teacher_client.get(f'/teacher/session/{session_id}/questions.csv?filter=ALL'))
    opened = _csv_rows(teacher_client.get(f'/teacher/session/{session_id}/questions.csv?filter=OPEN'))
    completed = _csv_rows(teacher_client.get(f'/teacher/session/{session_id}/questions.csv?filter=COMPLETED'))
    skipped = _csv_rows(teacher_client.get(f'/teacher/session/{session_id}/questions.csv?filter=SKIPPED'))

    assert len(total) == 30
    assert {row['Status'] for row in total} == {'OPEN', 'COMPLETED'}
    assert len(opened) == 5 and {row['Status'] for row in opened} == {'OPEN'}
    assert len(completed) == 25 and {row['Status'] for row in completed} == {'COMPLETED'}
    assert len(skipped) == 23 and {row['Status'] for row in skipped} == {'SKIPPED'}


def test_sky_blue_palette_and_realistic_login_asset(client):
    root = Path(__file__).resolve().parents[1]
    css = (root / 'static' / 'css' / 'app.css').read_text(encoding='utf-8')
    assert 'AskYourDoubt 1.5.2 — sky-grey / blue commercial SaaS release' in css
    assert '--saas-teal:#4296e8' in css
    assert '--green:#3f8edc' in css
    assert 'teacher-login-classroom.jpg' in (root / 'templates' / 'teacher' / 'login.html').read_text(encoding='utf-8')
    assert (root / 'static' / 'img' / 'teacher-login-classroom.jpg').stat().st_size > 10_000

    login = client.get('/teacher-login')
    assert login.status_code == 200
    assert b'teacher-login-classroom.jpg' in login.data
    assert b'Indian teacher discussing a classroom question with a student' in login.data
