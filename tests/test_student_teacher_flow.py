import io
import zipfile

from db import get_db


def create_session(teacher_client):
    response = teacher_client.post('/teacher/create-session', data={
        'session_name':'Physics Live','duration':'90','question_limit':'2'
    })
    assert response.status_code == 302
    return int(response.headers['Location'].rstrip('/').split('/')[-1])


def join(client, session_id, name, mobile):
    response = client.post(f'/join-session/{session_id}', data={'name':name,'mobile':mobile})
    assert response.status_code == 302


def test_live_doubt_vote_complete_reopen_skip(app, teacher_client):
    session_id = create_session(teacher_client)
    student1 = app.test_client(); join(student1, session_id, 'Student One', '9000000001')
    student2 = app.test_client(); join(student2, session_id, 'Student Two', '9000000002')

    response = student1.post(f'/student/session/{session_id}/submit', data={'question':'Why does light bend?'})
    assert response.status_code == 302
    assert 'tab=live' in response.headers['Location']

    with app.app_context():
        doubt_id = get_db().execute('SELECT id FROM doubts ORDER BY id DESC LIMIT 1').fetchone()['id']

    own_vote = student1.post(f'/api/student/doubt/{doubt_id}/vote')
    assert own_vote.status_code == 400

    other_vote = student2.post(f'/api/student/doubt/{doubt_id}/vote')
    assert other_vote.status_code == 200
    assert other_vote.get_json()['votes'] == 1
    duplicate = student2.post(f'/api/student/doubt/{doubt_id}/vote')
    assert duplicate.status_code == 409

    teacher_data = teacher_client.get(f'/api/teacher/session/{session_id}').get_json()
    assert teacher_data['open'][0]['id'] == doubt_id
    assert teacher_data['open'][0]['votes'] == 1
    assert 'student_name' not in teacher_data['open'][0]

    assert teacher_client.post(f'/api/teacher/doubt/{doubt_id}/complete').status_code == 200
    student_data = student1.get(f'/api/student/session/{session_id}').get_json()
    assert not student_data['open']
    assert student_data['completed'][0]['id'] == doubt_id

    assert teacher_client.post(f'/api/teacher/doubt/{doubt_id}/reopen').status_code == 200
    assert teacher_client.post(f'/api/teacher/doubt/{doubt_id}/skip').status_code == 200
    student_data = student1.get(f'/api/student/session/{session_id}').get_json()
    assert all(item['id'] != doubt_id for item in student_data['open'] + student_data['completed'])
    with app.app_context():
        assert get_db().execute('SELECT id FROM repository WHERE doubt_id=?', (doubt_id,)).fetchone() is None


def test_text_required_optional_file_and_limit(app, teacher_client):
    session_id = create_session(teacher_client)
    student = app.test_client(); join(student, session_id, 'Student', '9000000010')
    response = student.post(f'/student/session/{session_id}/submit', data={
        'question':'',
        'attachment':(io.BytesIO(b'hello'), 'note.txt'),
    }, content_type='multipart/form-data')
    assert response.status_code == 302
    with app.app_context():
        assert get_db().execute('SELECT COUNT(*) c FROM doubts').fetchone()['c'] == 0

    for q in ['First question','Second question']:
        student.post(f'/student/session/{session_id}/submit', data={'question':q})
    student.post(f'/student/session/{session_id}/submit', data={'question':'Third question'})
    with app.app_context():
        count = get_db().execute('SELECT COUNT(*) c FROM doubts WHERE session_id=?', (session_id,)).fetchone()['c']
        assert count == 2

def test_attachment_visibility_resources_qr_and_close(app, teacher_client):
    session_id = create_session(teacher_client)
    student = app.test_client(); join(student, session_id, 'Resource Student', '9000000020')

    response = student.post(
        f'/student/session/{session_id}/submit',
        data={'question':'Please check my diagram', 'attachment':(io.BytesIO(b'fake-png'), 'diagram.png')},
        content_type='multipart/form-data',
    )
    assert response.status_code == 302
    data = student.get(f'/api/student/session/{session_id}').get_json()
    assert data['open'][0]['download_url'] is None

    settings = teacher_client.post(
        f'/teacher/session/{session_id}/settings',
        data={'question_limit':'2','allow_student_attachment_download':'on'},
    )
    assert settings.status_code == 302
    data = student.get(f'/api/student/session/{session_id}').get_json()
    assert data['open'][0]['download_url']

    shared = teacher_client.post(
        f'/teacher/session/{session_id}/resources',
        data={'title':'Class Notes','resource_type':'NOTE','notes':'Important revision points'},
    )
    assert shared.status_code == 302
    data = student.get(f'/api/student/session/{session_id}').get_json()
    assert data['resources'][0]['title'] == 'Class Notes'

    qr_page = teacher_client.get(f'/teacher/session/{session_id}/qr')
    assert qr_page.status_code == 200
    assert b'Full Screen QR' in qr_page.data

    teacher_client.post(f'/teacher/session/{session_id}/close')
    data = student.get(f'/api/student/session/{session_id}').get_json()
    assert data['closed'] is True
    teacher_client.post(f'/teacher/session/{session_id}/reopen')
    data = student.get(f'/api/student/session/{session_id}').get_json()
    assert data['closed'] is False


def test_teacher_never_receives_student_identity_or_original_attachment_filename(app, teacher_client):
    session_id = create_session(teacher_client)
    student = app.test_client()
    join(student, session_id, 'Sagar Kerhalkar', '9000000099')

    response = student.post(
        f'/student/session/{session_id}/submit',
        data={
            'question': 'Please check my private file',
            'attachment': (io.BytesIO(b'private-pdf'), 'Sagar-Kerhalkar-9000000099-result.pdf'),
        },
        content_type='multipart/form-data',
    )
    assert response.status_code == 302

    with app.app_context():
        doubt_id = get_db().execute('SELECT id FROM doubts ORDER BY id DESC LIMIT 1').fetchone()['id']

    teacher_data = teacher_client.get(f'/api/teacher/session/{session_id}').get_json()
    sensitive_blob = str(teacher_data).lower()
    assert 'sagar' not in sensitive_blob
    assert 'kerhalkar' not in sensitive_blob
    assert '9000000099' not in sensitive_blob
    assert 'student_name' not in sensitive_blob
    assert 'mobile' not in sensitive_blob
    assert 'joined' not in sensitive_blob
    assert 'student_count' not in sensitive_blob

    one_file = teacher_client.get(f'/teacher/doubt/{doubt_id}/attachment')
    assert one_file.status_code == 200
    disposition = one_file.headers.get('Content-Disposition', '').lower()
    assert 'student_resource_doubt_' in disposition
    assert 'sagar' not in disposition
    assert 'kerhalkar' not in disposition
    assert '9000000099' not in disposition

    zip_response = teacher_client.get(f'/teacher/session/{session_id}/attachments.zip')
    assert zip_response.status_code == 200
    with zipfile.ZipFile(io.BytesIO(zip_response.data)) as archive:
        names = archive.namelist()
    assert names
    joined_names = ' '.join(names).lower()
    assert 'student_resource_doubt_' in joined_names
    assert 'sagar' not in joined_names
    assert 'kerhalkar' not in joined_names
    assert '9000000099' not in joined_names
