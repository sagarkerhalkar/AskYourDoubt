from db import get_db, transaction


def create_session(teacher_client):
    response = teacher_client.post('/teacher/create-session', data={
        'session_name': 'QR Share Session', 'duration': '90', 'question_limit': '100'
    })
    assert response.status_code == 302
    return int(response.headers['Location'].rstrip('/').split('/')[-1])


def test_teacher_qr_can_download_and_share(app, teacher_client):
    session_id = create_session(teacher_client)

    live = teacher_client.get(f'/teacher/session/{session_id}')
    assert live.status_code == 200
    assert b'Download QR' in live.data
    assert b'Share QR' in live.data
    assert b'data-share-qr' in live.data

    full = teacher_client.get(f'/teacher/session/{session_id}/qr')
    assert full.status_code == 200
    assert b'Download QR' in full.data
    assert b'Share QR' in full.data

    download = teacher_client.get(f'/teacher/session/{session_id}/qr/download')
    assert download.status_code == 200
    assert download.mimetype == 'image/png'
    assert 'attachment' in download.headers.get('Content-Disposition', '').lower()
    assert download.data.startswith(b'\x89PNG')


def test_qr_download_requires_teacher_ownership(app, teacher_client):
    session_id = create_session(teacher_client)
    other = app.test_client()
    response = other.get(f'/teacher/session/{session_id}/qr/download')
    assert response.status_code in (302, 403)


def test_admin_dashboard_is_compact_and_activity_is_paginated(app, admin_client):
    with app.app_context():
        teacher_id = get_db().execute('SELECT id FROM teachers ORDER BY id LIMIT 1').fetchone()['id']
        with transaction() as db:
            for index in range(18):
                db.execute(
                    'INSERT INTO teacher_activity(teacher_id, activity) VALUES(?,?)',
                    (teacher_id, f'Activity {index + 1}'),
                )

    dashboard = admin_client.get('/admin-dashboard')
    assert dashboard.status_code == 200
    html = dashboard.get_data(as_text=True)
    assert 'Latest five' in html
    assert html.count('admin-activity-item') == 5
    assert '/admin/activity' in html

    activity = admin_client.get('/admin/activity?per_page=10&page=1')
    assert activity.status_code == 200
    activity_html = activity.get_data(as_text=True)
    assert 'Teacher Activity' in activity_html
    assert 'Show' in activity_html
    assert '10' in activity_html and '20' in activity_html and '30' in activity_html


def test_v13_teacher_design_contracts_exist():
    from pathlib import Path
    root = Path(__file__).resolve().parents[1]
    template = (root / 'templates/teacher/live_session.html').read_text(encoding='utf-8')
    css = (root / 'static/css/app.css').read_text(encoding='utf-8')
    js = (root / 'static/js/app.js').read_text(encoding='utf-8')

    for token in ('teacher-3d-stage', 'Doubt Control Center', 'Open Doubts Focus', 'data-share-qr', 'Download QR'):
        assert token in template
    for token in ('teacherAvatarFloat', 'teacherOrbit', 'teacher-doubt-card', 'teacher-qr-frame', 'prefers-reduced-motion'):
        assert token in css
    for token in ('navigator.share', 'navigator.canShare', 'QR downloaded and join link copied'):
        assert token in js
