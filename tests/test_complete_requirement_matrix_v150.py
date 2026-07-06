from __future__ import annotations

import io
import zipfile
from pathlib import Path

from werkzeug.security import check_password_hash

from db import get_db


def create_session(client, name='Commercial Class', duration='90', limit='100') -> int:
    response = client.post('/teacher/create-session', data={
        'session_name': name,
        'duration': duration,
        'question_limit': limit,
    })
    assert response.status_code == 302
    return int(response.headers['Location'].rstrip('/').split('/')[-1])


def join_student(app, session_id: int, name='Global Student', mobile='9000000001'):
    client = app.test_client()
    response = client.post(f'/join-session/{session_id}', data={'name': name, 'mobile': mobile})
    assert response.status_code == 302
    return client


def submit(client, session_id: int, question: str, attachment=None):
    data = {'question': question}
    if attachment is not None:
        data['attachment'] = attachment
    return client.post(
        f'/student/session/{session_id}/submit',
        data=data,
        content_type='multipart/form-data' if attachment is not None else None,
    )


def test_student_join_validation_closed_flow_and_role_privacy(app, teacher_client):
    session_id = create_session(teacher_client)
    public = app.test_client()

    assert public.get(f'/join-session/{session_id}').status_code == 200
    missing_name = public.post(f'/join-session/{session_id}', data={'name': '', 'mobile': '9000000001'})
    assert b'Enter your full name' in missing_name.data
    for invalid in ('123', 'abcdefghij', '12345678901', '12345 6789'):
        response = public.post(f'/join-session/{session_id}', data={'name': 'Valid Student', 'mobile': invalid})
        assert b'exactly 10 digits' in response.data

    student = join_student(app, session_id)
    portal = student.get(f'/student/session/{session_id}')
    assert portal.status_code == 200
    assert b'Teacher Portal' not in portal.data
    assert b'Admin Portal' not in portal.data

    teacher_client.post(f'/teacher/session/{session_id}/close')
    closed = student.get(f'/student/session/{session_id}', follow_redirects=True)
    assert closed.status_code == 200
    assert b'This doubt session has ended' in closed.data
    assert b'Open Teacher Portal' not in closed.data

    join_closed = public.get(f'/join-session/{session_id}')
    assert b'Session is closed' in join_closed.data


def test_student_upload_matrix_emoji_exact_limit_and_video_rejection(app, teacher_client):
    session_id = create_session(teacher_client, limit='20')
    student = join_student(app, session_id)

    allowed = [
        ('Question with emoji 🙂', 'notes.pdf', b'%PDF-small'),
        ('Word question', 'notes.doc', b'doc-small'),
        ('DOCX question', 'notes.docx', b'docx-small'),
        ('Text question', 'notes.txt', b'txt-small'),
        ('JPG question', 'image.jpg', b'jpg-small'),
        ('JPEG question', 'image.jpeg', b'jpeg-small'),
        ('PNG question', 'image.png', b'png-small'),
        ('WEBP question', 'image.webp', b'webp-small'),
    ]
    for question, filename, payload in allowed:
        response = submit(student, session_id, question, (io.BytesIO(payload), filename))
        assert response.status_code == 302
        assert 'tab=live' in response.headers['Location']

    # The actual file may be exactly 10 MB; multipart request overhead has separate headroom.
    exact_ten_mb = submit(
        student,
        session_id,
        'Exactly ten megabytes',
        (io.BytesIO(b'x' * (10 * 1024 * 1024)), 'exact.txt'),
    )
    assert exact_ten_mb.status_code == 302
    assert 'tab=live' in exact_ten_mb.headers['Location']

    rejected_video = submit(student, session_id, 'Video must be rejected', (io.BytesIO(b'video'), 'clip.mp4'))
    assert rejected_video.status_code == 302
    assert 'tab=ask' in rejected_video.headers['Location']

    over_limit = submit(
        student,
        session_id,
        'Oversized file must be rejected',
        (io.BytesIO(b'x' * (10 * 1024 * 1024 + 1)), 'too-large.txt'),
    )
    assert over_limit.status_code == 302
    assert 'tab=ask' in over_limit.headers['Location']

    with app.app_context():
        rows = get_db().execute(
            'SELECT question, attachment_type FROM doubts WHERE session_id=? ORDER BY id',
            (session_id,),
        ).fetchall()
        assert len(rows) == 9
        assert rows[0]['question'] == 'Question with emoji 🙂'
        assert {row['attachment_type'] for row in rows} == {'PDF', 'DOC', 'DOCX', 'TXT', 'JPG', 'JPEG', 'PNG', 'WEBP'}


def test_student_live_ranking_markers_votes_visibility_and_pagination(app, teacher_client):
    session_id = create_session(teacher_client, limit='500')
    owner = join_student(app, session_id, 'Owner Student', '9000000011')
    voter = join_student(app, session_id, 'Voting Student', '9000000012')

    submit(owner, session_id, 'Lower ranked own question')
    submit(voter, session_id, 'Question that will become highest ranked')
    with app.app_context():
        db = get_db()
        rows = db.execute('SELECT id, question FROM doubts WHERE session_id=? ORDER BY id', (session_id,)).fetchall()
        first_id, second_id = rows[0]['id'], rows[1]['id']

    assert owner.post(f'/api/student/doubt/{first_id}/vote').status_code == 400
    assert owner.post(f'/api/student/doubt/{second_id}/vote').status_code == 200
    assert owner.post(f'/api/student/doubt/{second_id}/vote').status_code == 409

    data = owner.get(f'/api/student/session/{session_id}?page=1&per_page=100').get_json()
    assert data['pagination']['per_page'] == 100
    assert data['pagination']['allowed_sizes'] == [100, 250, 500]
    assert data['open'][0]['id'] == second_id
    own = next(item for item in data['open'] if item['id'] == first_id)
    voted = next(item for item in data['open'] if item['id'] == second_id)
    assert own['is_mine'] is True and own['can_vote'] is False
    assert voted['voted'] is True and voted['can_vote'] is False

    assert teacher_client.post(f'/api/teacher/doubt/{first_id}/complete').status_code == 200
    assert teacher_client.post(f'/api/teacher/doubt/{second_id}/skip').status_code == 200
    data = owner.get(f'/api/student/session/{session_id}?per_page=500').get_json()
    assert data['pagination']['per_page'] == 500
    assert not data['open']
    assert [item['id'] for item in data['completed']] == [first_id]
    assert all(item['id'] != second_id for item in data['open'] + data['completed'])

    page = owner.get(f'/student/session/{session_id}?tab=live')
    assert b'My Question' in page.data  # Render contract lives in the JS card template.
    assert b'I have the same doubt' in page.data
    assert b'Answered' in page.data
    assert b'POLL_INTERVAL_MS = 1000' in page.data
    assert b'window.location.reload' not in page.data


def test_student_attachment_permission_resources_tabs_and_focus(app, teacher_client):
    session_id = create_session(teacher_client, limit='10')
    owner = join_student(app, session_id, 'Attachment Owner', '9000000021')
    viewer = join_student(app, session_id, 'Attachment Viewer', '9000000022')
    submit(owner, session_id, 'Please inspect this diagram', (io.BytesIO(b'png-content'), 'diagram.png'))

    with app.app_context():
        doubt_id = get_db().execute('SELECT id FROM doubts WHERE session_id=?', (session_id,)).fetchone()['id']

    hidden = viewer.get(f'/api/student/session/{session_id}').get_json()['open'][0]
    assert hidden['download_url'] is None
    assert viewer.get(f'/student/doubt-attachment/{doubt_id}').status_code == 403

    teacher_client.post(
        f'/teacher/session/{session_id}/settings',
        data={'question_limit': '10', 'allow_student_attachment_download': 'on'},
    )
    visible = viewer.get(f'/api/student/session/{session_id}').get_json()['open'][0]
    assert visible['download_url']
    assert viewer.get(visible['download_url']).status_code == 200

    teacher_client.post(f'/teacher/session/{session_id}/resources', data={
        'title': 'Teacher note', 'resource_type': 'NOTE', 'notes': 'Read chapter four.'
    })
    teacher_client.post(f'/teacher/session/{session_id}/resources', data={
        'title': 'Safe video', 'resource_type': 'VIDEO', 'video_url': 'https://example.com/video'
    })
    unsafe = teacher_client.post(f'/teacher/session/{session_id}/resources', data={
        'title': 'Unsafe video', 'resource_type': 'VIDEO', 'video_url': 'javascript:alert(1)'
    }, follow_redirects=True)
    assert b'must start with http:// or https://' in unsafe.data

    resources = viewer.get(f'/api/student/session/{session_id}?resource_page=1&resource_per_page=10').get_json()
    assert {item['title'] for item in resources['resources']} == {'Teacher note', 'Safe video'}
    assert resources['resource_pagination']['allowed_sizes'] == [10, 20, 30]

    viewer.get(f'/student/session/{session_id}/tab/resources')
    refreshed = viewer.get(f'/student/session/{session_id}')
    assert b'tab active' in refreshed.data and b'Resources' in refreshed.data

    focus = viewer.get(f'/student/session/{session_id}/focus')
    assert focus.status_code == 200
    for token in (b'Return to Original Size', b'data-minimize-target="#studentFocusStage"', b'POLL_INTERVAL_MS = 1000', b'id="studentPerPage"'):
        assert token in focus.data


def test_teacher_session_controls_live_privacy_focus_qr_and_actions(app, teacher_client):
    session_id = create_session(teacher_client, 'International Session', duration='120', limit='99999999')
    with app.app_context():
        row = get_db().execute('SELECT duration, question_limit FROM sessions WHERE id=?', (session_id,)).fetchone()
        assert row['duration'] == 120
        assert row['question_limit'] == 10_000_000

    student = join_student(app, session_id, 'Private Student', '9000000031')
    submit(student, session_id, 'Why is the sky blue?', (io.BytesIO(b'pdf'), 'question.pdf'))
    with app.app_context():
        doubt_id = get_db().execute('SELECT id FROM doubts WHERE session_id=?', (session_id,)).fetchone()['id']

    api = teacher_client.get(f'/api/teacher/session/{session_id}?per_page=100')
    assert api.status_code == 200
    payload_text = api.get_data(as_text=True).lower()
    for private_key in ('student_name', 'student_mobile', 'student_count', 'category', 'keyword'):
        assert private_key not in payload_text
    doubt = api.get_json()['open'][0]
    assert doubt['download_url'] and doubt['has_attachment'] is True

    page = teacher_client.get(f'/teacher/session/{session_id}')
    assert page.status_code == 200
    for token in (b'Copy Link', b'Download QR', b'Share QR', b'Print QR', b'Focus Full Screen', b'Open New Window'):
        assert token in page.data
    assert b'POLL_INTERVAL_MS = 1000' in page.data

    focus = teacher_client.get(f'/teacher/session/{session_id}/focus')
    for token in (
        b'Return to Original Size', b'data-minimize-target="#teacherFocusStage"', b'id="teacherPerPage"',
        b'Copy Link', b'Download QR', b'Share QR', b'Print QR', b'id="teacherQrImage"',
    ):
        assert token in focus.data

    qr = teacher_client.get(f'/teacher/session/{session_id}/qr')
    qr_download = teacher_client.get(f'/teacher/session/{session_id}/qr/download')
    assert qr.status_code == 200 and b'Full Screen QR' in qr.data
    assert qr_download.status_code == 200 and qr_download.mimetype == 'image/png'

    assert teacher_client.post(f'/api/teacher/doubt/{doubt_id}/complete').get_json()['status'] == 'COMPLETED'
    assert teacher_client.post(f'/api/teacher/doubt/{doubt_id}/reopen').get_json()['status'] == 'OPEN'
    assert teacher_client.post(f'/api/teacher/doubt/{doubt_id}/skip').get_json()['status'] == 'SKIPPED'
    assert teacher_client.post(f'/api/teacher/doubt/{doubt_id}/reopen').get_json()['status'] == 'OPEN'

    teacher_client.post(f'/teacher/session/{session_id}/close')
    assert teacher_client.get(f'/api/teacher/session/{session_id}').get_json()['session']['status'] == 'CLOSED'
    teacher_client.post(f'/teacher/session/{session_id}/reopen')
    assert teacher_client.get(f'/api/teacher/session/{session_id}').get_json()['session']['status'] == 'ACTIVE'


def test_teacher_limits_zip_resources_exports_bank_analytics_and_password(app, teacher_client):
    session_id = create_session(teacher_client, 'Operations Session', limit='1')
    student = join_student(app, session_id, 'Limited Student', '9000000041')
    submit(student, session_id, 'First allowed question', (io.BytesIO(b'attachment'), 'evidence.txt'))
    second = submit(student, session_id, 'Second blocked question')
    assert 'tab=live' in second.headers['Location']
    with app.app_context():
        assert get_db().execute('SELECT COUNT(*) AS c FROM doubts WHERE session_id=?', (session_id,)).fetchone()['c'] == 1

    archive = teacher_client.get(f'/teacher/session/{session_id}/attachments.zip')
    assert archive.status_code == 200 and archive.mimetype == 'application/zip'
    with zipfile.ZipFile(io.BytesIO(archive.data)) as zf:
        assert len(zf.namelist()) == 1

    for data in (
        {'title': 'Class note', 'resource_type': 'NOTE', 'notes': 'Revision note'},
        {'title': 'Video lesson', 'resource_type': 'VIDEO', 'video_url': 'https://example.com/lesson'},
    ):
        assert teacher_client.post(f'/teacher/session/{session_id}/resources', data=data).status_code == 302
    file_resource = teacher_client.post(
        f'/teacher/session/{session_id}/resources',
        data={'title': 'Slides', 'resource_type': 'FILE', 'file': (io.BytesIO(b'pptx'), 'lesson.pptx')},
        content_type='multipart/form-data',
    )
    assert file_resource.status_code == 302

    for path in (
        f'/teacher/session/{session_id}/questions.csv', '/teacher/questions.csv',
        '/teacher/question-bank.csv', f'/teacher/question-bank.csv?session_id={session_id}',
    ):
        response = teacher_client.get(path)
        assert response.status_code == 200
        assert response.headers['Content-Type'].startswith('text/csv')

    bank = teacher_client.get('/teacher/question-bank?per_page=10')
    analytics = teacher_client.get('/teacher/analytics')
    resources = teacher_client.get(f'/teacher/session/{session_id}/resources?per_page=30')
    assert bank.status_code == analytics.status_code == resources.status_code == 200
    assert b'10' in bank.data and b'20' in bank.data and b'30' in bank.data

    changed = teacher_client.post('/teacher/change-password', data={
        'current_password': 'teacher123', 'new_password': 'NewTeacher123', 'confirm_password': 'NewTeacher123'
    })
    assert changed.status_code == 302
    relogin = app.test_client().post('/teacher-login', data={'username': 'teacher', 'password': 'NewTeacher123'})
    assert relogin.status_code == 302


def test_teacher_live_100_250_500_order_and_internal_pagination(app, teacher_client):
    session_id = create_session(teacher_client, 'Large Queue', limit='500')
    student = join_student(app, session_id, 'Bulk Student', '9000000051')
    with app.app_context():
        db = get_db()
        student_id = db.execute("SELECT id FROM students WHERE mobile='9000000051'").fetchone()['id']
        rows = [
            (session_id, student_id, f'Bulk question {index}', 'General', 'Bulk', index % 7, 'OPEN')
            for index in range(130)
        ]
        db.executemany(
            'INSERT INTO doubts(session_id,student_id,question,category,keyword,votes,status) VALUES(?,?,?,?,?,?,?)',
            rows,
        )
        db.commit()

    first = teacher_client.get(f'/api/teacher/session/{session_id}?page=1&per_page=100').get_json()
    second = teacher_client.get(f'/api/teacher/session/{session_id}?page=2&per_page=100').get_json()
    all_250 = teacher_client.get(f'/api/teacher/session/{session_id}?page=1&per_page=250').get_json()
    all_500 = student.get(f'/api/student/session/{session_id}?page=1&per_page=500').get_json()
    assert len(first['open']) == 100 and len(second['open']) == 30
    assert len(all_250['open']) == 130 and len(all_500['open']) == 130
    assert first['pagination']['allowed_sizes'] == [100, 250, 500]
    votes = [item['votes'] for item in first['open']]
    assert votes == sorted(votes, reverse=True)


def test_admin_complete_management_exports_activity_pagination_and_brand(app, admin_client, teacher_client):
    session_id = create_session(teacher_client, 'Admin Session')
    student = join_student(app, session_id, 'Admin Visible Student', '9000000061')
    submit(student, session_id, 'Admin visible question')

    create_admin = admin_client.post('/admin/admins', data={
        'display_name': 'Second Administrator', 'username': 'secondadmin', 'password': 'SecondAdmin123'
    })
    assert create_admin.status_code == 302

    create_teacher_response = admin_client.post('/admin/teachers', data={
        'name': 'Managed Teacher', 'mobile': '9111111111', 'email': 'managed@example.com',
        'dob': '1991-02-03', 'username': 'managedteacher', 'password': 'Managed123'
    })
    assert create_teacher_response.status_code == 302
    with app.app_context():
        managed_id = get_db().execute("SELECT id FROM teachers WHERE username='managedteacher'").fetchone()['id']

    edit = admin_client.post(f'/admin/teacher/{managed_id}/edit', data={
        'name': 'Managed Teacher Updated', 'mobile': '9222222222', 'email': '', 'dob': '', 'username': 'managedteacher'
    })
    assert edit.status_code == 302
    reset = admin_client.post(f'/admin/teacher/{managed_id}/reset-password', data={
        'new_password': 'ResetTeacher123', 'confirm_password': 'ResetTeacher123'
    })
    assert reset.status_code == 302

    for action, expected in [('disable', 'DISABLED'), ('enable', 'ACTIVE'), ('delete', 'DELETED')]:
        assert admin_client.post(f'/admin/teacher/{managed_id}/status', data={'action': action}).status_code == 302
        with app.app_context():
            assert get_db().execute('SELECT status FROM teachers WHERE id=?', (managed_id,)).fetchone()['status'] == expected

    for path in ('/admin/students', '/admin/sessions', '/admin/questions', '/admin/analytics', '/admin/question-bank'):
        response = admin_client.get(path)
        assert response.status_code == 200
    students = admin_client.get('/admin/students')
    assert b'Admin Visible Student' in students.data and b'9000000061' in students.data

    admin_client.post(f'/admin/session/{session_id}/status', data={'action': 'close'})
    with app.app_context():
        assert get_db().execute('SELECT status FROM sessions WHERE id=?', (session_id,)).fetchone()['status'] == 'CLOSED'
    admin_client.post(f'/admin/session/{session_id}/status', data={'action': 'reopen'})
    with app.app_context():
        assert get_db().execute('SELECT status FROM sessions WHERE id=?', (session_id,)).fetchone()['status'] == 'ACTIVE'

    for kind in ('questions', 'students', 'sessions'):
        response = admin_client.get(f'/admin/export/{kind}.csv')
        assert response.status_code == 200 and response.headers['Content-Type'].startswith('text/csv')
    assert admin_client.get('/admin/question-bank.csv').status_code == 200

    with app.app_context():
        db = get_db()
        for index in range(8):
            db.execute('INSERT INTO teacher_activity(teacher_id,activity) VALUES(?,?)', (1, f'Unique activity {index}'))
        db.commit()
    dashboard = admin_client.get('/admin-dashboard').get_data(as_text=True)
    assert dashboard.count('Unique activity') == 5
    activity = admin_client.get('/admin/activity?per_page=10')
    assert activity.status_code == 200 and b'Unique activity' in activity.data
    for size in (10, 20, 30):
        assert admin_client.get(f'/admin/activity?per_page={size}').status_code == 200

    logo_path = Path(app.root_path) / 'static' / 'brand' / 'logo.png'
    try:
        logo = admin_client.post(
            '/brand-settings',
            data={'logo': (io.BytesIO(b'png-logo'), 'logo.png')},
            content_type='multipart/form-data',
        )
        assert logo.status_code == 302 and logo_path.exists()
    finally:
        logo_path.unlink(missing_ok=True)

    changed = admin_client.post('/admin/change-password', data={
        'current_password': 'admin123', 'new_password': 'NewAdmin123', 'confirm_password': 'NewAdmin123'
    })
    assert changed.status_code == 302
    relogin = app.test_client().post('/admin-login', data={'username': 'admin', 'password': 'NewAdmin123'})
    assert relogin.status_code == 302

    with app.app_context():
        admin_row = get_db().execute("SELECT password FROM admins WHERE username='admin'").fetchone()
        teacher_row = get_db().execute("SELECT password FROM teachers WHERE username='managedteacher'").fetchone()
        assert check_password_hash(admin_row['password'], 'NewAdmin123')
        assert check_password_hash(teacher_row['password'], 'ResetTeacher123')


def test_security_headers_health_config_migration_and_route_protection(app, client):
    health = client.get('/healthz')
    assert health.status_code == 200 and health.get_json()['status'] == 'ok'
    assert health.headers['X-Content-Type-Options'] == 'nosniff'
    assert health.headers['X-Frame-Options'] == 'SAMEORIGIN'
    api = client.get('/api/teacher/session/1')
    assert api.status_code == 403 and 'no-store' in api.headers['Cache-Control']

    protected = [
        '/teacher-dashboard', '/teacher/create-session', '/teacher/question-bank', '/teacher/analytics',
        '/admin-dashboard', '/admin/teachers', '/admin/activity', '/brand-settings',
    ]
    for path in protected:
        response = client.get(path)
        assert response.status_code == 302

    with app.app_context():
        db = get_db()
        assert db.execute('PRAGMA journal_mode').fetchone()[0].lower() == 'wal'
        indexes = {row['name'] for row in db.execute("SELECT name FROM sqlite_master WHERE type='index'")}
        assert 'uq_doubt_votes_student' in indexes
        assert 'uq_repository_doubt' in indexes


def test_global_ui_contract_has_compact_typography_3d_reduced_motion_and_no_public_credit():
    root = Path(__file__).resolve().parents[1]
    css = (root / 'static/css/app.css').read_text(encoding='utf-8')
    js = (root / 'static/js/app.js').read_text(encoding='utf-8')
    templates = '\n'.join(path.read_text(encoding='utf-8') for path in (root / 'templates').rglob('*.html'))

    for token in (
        'AskYourDoubt 1.5.0', 'h1{font-size:clamp(1.45rem,1.9vw,1.85rem)}',
        '.teacher-dashboard-hero{', 'min-height:168px', '.student-welcome-v14{', 'min-height:150px',
        'transform-style:preserve-3d', '@media(hover:hover) and (pointer:fine)',
        '@media(hover:none)', '@media(prefers-reduced-motion:reduce)', 'content-visibility:auto',
        '.teacher-focus-stage.is-minimized', '.student-focus-stage.is-minimized',
    ):
        assert token in css
    for token in ('data-minimize-target', 'is-minimized', 'requestFullscreen', 'simulated-fullscreen'):
        assert token in js
    assert 'Built by Sagar Kerhalkar' not in templates
    assert 'ChatGPT' not in templates
