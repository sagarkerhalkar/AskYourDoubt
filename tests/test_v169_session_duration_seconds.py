from datetime import datetime, timezone

from db import get_db


def _create(teacher_client, seconds: str):
    response = teacher_client.post('/teacher/create-session', data={
        'session_name': f'Duration {seconds}',
        'duration_seconds': seconds,
        'question_limit': '10',
    })
    assert response.status_code == 302
    return int(response.headers['Location'].rstrip('/').split('/')[-1])


def test_teacher_can_create_manual_zero_second_session(app, teacher_client):
    session_id = _create(teacher_client, '0')
    with app.app_context():
        row = get_db().execute('SELECT duration, duration_seconds, ends_at FROM sessions WHERE id=?', (session_id,)).fetchone()
        assert row['duration'] == 0
        assert row['duration_seconds'] == 0
        assert row['ends_at'] == ''

    page = teacher_client.get(f'/teacher/session/{session_id}')
    assert page.status_code == 200
    assert b'Manual close' in page.data


def test_teacher_can_create_precise_seconds_under_one_minute(app, teacher_client):
    session_id = _create(teacher_client, '30')
    with app.app_context():
        row = get_db().execute('SELECT duration, duration_seconds, ends_at FROM sessions WHERE id=?', (session_id,)).fetchone()
        assert row['duration'] == 1  # legacy minutes column kept for old exports/UI compatibility
        assert row['duration_seconds'] == 30
        end = datetime.fromisoformat(row['ends_at'])
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        assert 0 <= (end - now).total_seconds() <= 35


def test_teacher_duration_is_clamped_to_24_hours(app, teacher_client):
    session_id = _create(teacher_client, '999999')
    with app.app_context():
        row = get_db().execute('SELECT duration, duration_seconds, ends_at FROM sessions WHERE id=?', (session_id,)).fetchone()
        assert row['duration_seconds'] == 86400
        assert row['duration'] == 1440


def test_teacher_can_update_duration_from_live_settings(app, teacher_client):
    session_id = _create(teacher_client, '3600')
    response = teacher_client.post(f'/teacher/session/{session_id}/settings', data={
        'duration_seconds': '7200',
        'question_limit': '15',
    })
    assert response.status_code == 302
    with app.app_context():
        row = get_db().execute('SELECT duration, duration_seconds, question_limit FROM sessions WHERE id=?', (session_id,)).fetchone()
        assert row['duration_seconds'] == 7200
        assert row['duration'] == 120
        assert row['question_limit'] == 15
