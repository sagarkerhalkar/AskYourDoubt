
def _create_session(teacher_client) -> int:
    response = teacher_client.post('/teacher/create-session', data={
        'session_name': 'Immersive Test Session',
        'duration': '90',
        'question_limit': '100',
    })
    assert response.status_code == 302
    return int(response.headers['Location'].rstrip('/').split('/')[-1])


def _student_client(app, sid: int):
    client = app.test_client()
    response = client.post(
        f'/join-session/{sid}',
        data={'name': 'Focus Student', 'mobile': '9123456789'},
    )
    assert response.status_code == 302
    return client


def test_teacher_live_focus_route_is_protected_and_contains_qr_controls(app, teacher_client):
    sid = _create_session(teacher_client)
    response = teacher_client.get(f'/teacher/session/{sid}/focus')
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert 'is-immersive-route' in html
    assert 'teacherFocusStage' in html
    assert 'Return to Original Size' in html
    assert 'Copy Link' in html
    assert 'Download QR' in html
    assert 'Share QR' in html
    assert 'Print QR' in html
    assert f'/teacher/session/{sid}/qr/download' in html

    anonymous = app.test_client().get(f'/teacher/session/{sid}/focus')
    assert anonymous.status_code in (302, 403)


def test_student_live_focus_route_preserves_live_logic(app, teacher_client):
    sid = _create_session(teacher_client)
    student_client = _student_client(app, sid)
    response = student_client.get(f'/student/session/{sid}/focus')
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert 'studentFocusStage' in html
    assert 'student-focus-route' in html
    assert 'Return to Original Size' in html
    assert f'/api/student/session/${{sessionId}}' in html or '/api/student/session/' in html
    assert '/api/student/doubt/' in html
    assert 'I have the same doubt' in html


def test_teacher_dashboard_has_focus_window_action(app, teacher_client):
    sid = _create_session(teacher_client)
    response = teacher_client.get('/teacher-dashboard')
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert 'teacher-dashboard-v14' in html
    assert 'Live Focus' in html
    assert f'/teacher/session/{sid}/focus' in html


def test_live_focus_page_sizes_remain_100_250_500(app, teacher_client):
    sid = _create_session(teacher_client)
    student_client = _student_client(app, sid)
    teacher_html = teacher_client.get(f'/teacher/session/{sid}/focus').get_data(as_text=True)
    student_html = student_client.get(f'/student/session/{sid}/focus').get_data(as_text=True)
    for value in ('100', '250', '500'):
        assert f'value="{value}"' in teacher_html
        assert f'value="{value}"' in student_html
