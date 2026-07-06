from db import get_db
from utils import duration_hours_input, parse_session_duration_hours


def test_duration_hours_parser_uses_hours_minutes_format():
    assert parse_session_duration_hours('0') == 0
    assert parse_session_duration_hours('.30') == 30 * 60
    assert parse_session_duration_hours('1') == 60 * 60
    assert parse_session_duration_hours('1.30') == 90 * 60
    assert parse_session_duration_hours('24') == 24 * 60 * 60
    assert parse_session_duration_hours('99') == 24 * 60 * 60


def test_duration_hours_input_formats_existing_seconds():
    assert duration_hours_input(0) == '0'
    assert duration_hours_input(1800) == '.30'
    assert duration_hours_input(3600) == '1'
    assert duration_hours_input(5400) == '1.30'
    assert duration_hours_input(86400) == '24'


def test_teacher_create_session_accepts_hours_format(app, teacher_client):
    response = teacher_client.post('/teacher/create-session', data={
        'session_name': 'Hours Format Session',
        'duration_hours': '1.30',
        'question_limit': '100',
    })
    assert response.status_code == 302
    session_id = int(response.headers['Location'].rstrip('/').split('/')[-1])
    with app.app_context():
        row = get_db().execute('SELECT duration, duration_seconds FROM sessions WHERE id=?', (session_id,)).fetchone()
        assert row['duration_seconds'] == 5400
        assert row['duration'] == 90


def test_teacher_live_settings_accept_hours_format(app, teacher_client):
    create = teacher_client.post('/teacher/create-session', data={
        'session_name': 'Live Hours Settings',
        'duration_hours': '.30',
        'question_limit': '100',
    })
    session_id = int(create.headers['Location'].rstrip('/').split('/')[-1])
    response = teacher_client.post(f'/teacher/session/{session_id}/settings', data={
        'duration_hours': '12',
        'question_limit': '100000',
    })
    assert response.status_code == 302
    with app.app_context():
        row = get_db().execute('SELECT duration, duration_seconds, question_limit FROM sessions WHERE id=?', (session_id,)).fetchone()
        assert row['duration_seconds'] == 43200
        assert row['duration'] == 720
        assert row['question_limit'] == 100000


def test_teacher_control_ui_shows_professional_hours_copy(teacher_client):
    create = teacher_client.post('/teacher/create-session', data={
        'session_name': 'UI Hours Session',
        'duration_hours': '1.30',
        'question_limit': '100',
    })
    session_id = int(create.headers['Location'].rstrip('/').split('/')[-1])
    page = teacher_client.get(f'/teacher/session/{session_id}')
    assert page.status_code == 200
    assert b'name="duration_hours"' in page.data
    assert b'value="1.30"' in page.data
    assert b'0 manual' in page.data
    assert b'1 crore' in page.data
    assert b'teacher-control-card-pro' in page.data
