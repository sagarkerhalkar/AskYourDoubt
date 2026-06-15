from db import get_db


def _create_session(client):
    response = client.post('/teacher/create-session', data={
        'session_name': 'Role Stability', 'duration': '90', 'question_limit': '10'
    })
    assert response.status_code == 302
    return int(response.headers['Location'].rstrip('/').split('/')[-1])


def test_teacher_and_student_can_coexist_in_same_browser_session(app):
    client = app.test_client()
    assert client.post('/teacher-login', data={'username':'teacher','password':'teacher123'}).status_code == 302
    sid = _create_session(client)
    assert client.post(f'/join-session/{sid}', data={'name':'Same Browser Student','mobile':'9111111111'}).status_code == 302

    with client.session_transaction() as browser_session:
        assert browser_session.get('teacher_id')
        assert browser_session.get('student_id')
        assert browser_session.get('student_session_id') == sid

    response = client.post(f'/student/session/{sid}/submit', data={'question':'Does posting keep both sessions active?'})
    assert response.status_code == 302
    assert 'tab=live' in response.headers['Location']
    assert client.get(f'/api/teacher/session/{sid}').status_code == 200
    assert client.get(f'/api/student/session/{sid}').status_code == 200


def test_teacher_actions_do_not_remove_student_session(app):
    client = app.test_client()
    client.post('/teacher-login', data={'username':'teacher','password':'teacher123'})
    sid = _create_session(client)
    client.post(f'/join-session/{sid}', data={'name':'Student','mobile':'9222222222'})
    client.post(f'/student/session/{sid}/submit', data={'question':'Can the teacher complete this safely?'})
    with app.app_context():
        doubt_id = get_db().execute('SELECT id FROM doubts ORDER BY id DESC LIMIT 1').fetchone()['id']
    assert client.post(f'/api/teacher/doubt/{doubt_id}/complete').status_code == 200
    assert client.get(f'/api/student/session/{sid}').status_code == 200
    with client.session_transaction() as browser_session:
        assert browser_session.get('teacher_id')
        assert browser_session.get('student_id')


def test_role_scoped_logout_keeps_other_portal_login(app):
    client = app.test_client()
    client.post('/teacher-login', data={'username':'teacher','password':'teacher123'})
    sid = _create_session(client)
    client.post(f'/join-session/{sid}', data={'name':'Student','mobile':'9333333333'})

    assert client.get('/student/logout').status_code == 302
    with client.session_transaction() as browser_session:
        assert browser_session.get('teacher_id')
        assert not browser_session.get('student_id')

    client.post(f'/join-session/{sid}', data={'name':'Student','mobile':'9333333333'})
    assert client.get('/teacher-logout').status_code == 302
    with client.session_transaction() as browser_session:
        assert browser_session.get('student_id')
        assert not browser_session.get('teacher_id')


def test_admin_login_does_not_clear_teacher_or_student(app):
    client = app.test_client()
    client.post('/teacher-login', data={'username':'teacher','password':'teacher123'})
    sid = _create_session(client)
    client.post(f'/join-session/{sid}', data={'name':'Student','mobile':'9444444444'})
    assert client.post('/admin-login', data={'username':'admin','password':'admin123'}).status_code == 302
    with client.session_transaction() as browser_session:
        assert browser_session.get('admin_id')
        assert browser_session.get('teacher_id')
        assert browser_session.get('student_id')
