def test_public_pages_and_responsive_assets(client):
    for path in ['/', '/student', '/teacher-login', '/admin-login']:
        response = client.get(path)
        assert response.status_code == 200
        assert b'viewport' in response.data
        assert b'/static/css/app.css' in response.data


def test_student_mobile_validation(client, teacher_client):
    teacher_client.post('/teacher/create-session', data={
        'session_name':'Validation Session','duration':'90','question_limit':'2'
    })
    response = client.post('/join-session/1', data={'name':'Student','mobile':'12345'})
    assert response.status_code == 200
    assert b'exactly 10 digits' in response.data
    response = client.post('/join-session/1', data={'name':'Student','mobile':'9876543210'})
    assert response.status_code == 302


def test_role_portals_are_separate(client):
    response = client.get('/teacher-dashboard')
    assert response.status_code == 302
    assert '/teacher-login' in response.headers['Location']
    response = client.get('/admin-dashboard')
    assert response.status_code == 302
    assert '/admin-login' in response.headers['Location']
