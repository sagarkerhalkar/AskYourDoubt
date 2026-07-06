from werkzeug.security import generate_password_hash

from db import get_db


def _create_session(client, name):
    response = client.post('/teacher/create-session', data={
        'session_name': name,
        'duration': '90',
        'question_limit': '10',
    })
    assert response.status_code == 302
    return int(response.headers['Location'].rstrip('/').split('/')[-1])


def _join_and_ask(app, session_id, name, mobile, question):
    student = app.test_client()
    joined = student.post(f'/join-session/{session_id}', data={'name': name, 'mobile': mobile})
    assert joined.status_code == 302
    submitted = student.post(f'/student/session/{session_id}/submit', data={'question': question})
    assert submitted.status_code == 302


def test_teacher_question_bank_filters_visible_questions_by_owned_session(app, teacher_client):
    session_a = _create_session(teacher_client, 'Session Alpha')
    session_b = _create_session(teacher_client, 'Session Beta')
    _join_and_ask(app, session_a, 'Alpha Student', '9111111111', 'Alpha-only question')
    _join_and_ask(app, session_b, 'Beta Student', '9222222222', 'Beta-only question')

    all_page = teacher_client.get('/teacher/question-bank')
    assert all_page.status_code == 200
    assert b'Alpha-only question' in all_page.data
    assert b'Beta-only question' in all_page.data

    alpha_page = teacher_client.get(f'/teacher/question-bank?session_id={session_a}')
    assert alpha_page.status_code == 200
    assert b'Session Alpha' in alpha_page.data
    assert b'Alpha-only question' in alpha_page.data
    assert b'Beta-only question' not in alpha_page.data
    assert f'value="{session_a}" selected'.encode() in alpha_page.data

    beta_open_page = teacher_client.get(f'/teacher/question-bank?session_id={session_b}&status=OPEN')
    assert beta_open_page.status_code == 200
    assert b'Beta-only question' in beta_open_page.data
    assert b'Alpha-only question' not in beta_open_page.data
    assert b'Export current view' in beta_open_page.data


def test_question_bank_rejects_another_teachers_session_filter(app, teacher_client):
    own_session = _create_session(teacher_client, 'Owned Session')
    _join_and_ask(app, own_session, 'Owner Student', '9333333333', 'Owned visible question')

    with app.app_context():
        db = get_db()
        cursor = db.execute(
            '''INSERT INTO teachers(name,mobile,email,dob,username,password,status)
               VALUES(?,?,?,?,?,?,?)''',
            ('Other Teacher', '9444444444', 'other@example.com', '1991-01-01', 'other', generate_password_hash('other1234'), 'ACTIVE'),
        )
        other_teacher_id = cursor.lastrowid
        cursor = db.execute(
            '''INSERT INTO sessions(teacher_id,session_name,duration,status,created_at,started_at,ends_at,question_limit)
               VALUES(?,?,'90','ACTIVE',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP,CURRENT_TIMESTAMP,10)''',
            (other_teacher_id, 'Foreign Session'),
        )
        foreign_session_id = cursor.lastrowid
        db.execute(
            '''INSERT INTO repository(question,category,keyword,total_votes,status,teacher_id,session_id,session_name,session_date,updated_at)
               VALUES(?,?,?,?,?,?,?,?,CURRENT_TIMESTAMP,CURRENT_TIMESTAMP)''',
            ('Foreign hidden question', 'General', 'Foreign', 0, 'OPEN', other_teacher_id, foreign_session_id, 'Foreign Session'),
        )
        db.commit()

    page = teacher_client.get(f'/teacher/question-bank?session_id={foreign_session_id}')
    assert page.status_code == 200
    assert b'Foreign hidden question' not in page.data
    assert b'Owned visible question' in page.data
    assert b'All teacher sessions' in page.data

    export = teacher_client.get(f'/teacher/question-bank.csv?session_id={foreign_session_id}')
    assert export.status_code == 200
    assert b'Foreign hidden question' not in export.data
    assert b'Owned visible question' in export.data
