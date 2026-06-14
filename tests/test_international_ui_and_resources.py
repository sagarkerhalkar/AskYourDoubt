import io
from pathlib import Path

from db import get_db


def create_session(teacher_client, name='Global Physics'):
    response = teacher_client.post('/teacher/create-session', data={
        'session_name': name,
        'duration': '90',
        'question_limit': '25',
    })
    assert response.status_code == 302
    return int(response.headers['Location'].rstrip('/').split('/')[-1])


def join_student(app, session_id):
    client = app.test_client()
    response = client.post(
        f'/join-session/{session_id}',
        data={'name': 'International Student', 'mobile': '9111111111'},
    )
    assert response.status_code == 302
    return client


def test_copy_link_supports_copy_target_and_live_page_button(teacher_client):
    session_id = create_session(teacher_client)
    page = teacher_client.get(f'/teacher/session/{session_id}')
    assert page.status_code == 200
    assert b'data-copy-target="#joinLink"' in page.data
    assert b'Share Resources' in page.data

    js = Path(__file__).resolve().parents[1] / 'static' / 'js' / 'app.js'
    text = js.read_text(encoding='utf-8')
    assert "[data-copy], [data-copy-target]" in text
    assert 'navigator.clipboard' in text
    assert 'execCommand' in text


def test_teacher_shares_file_video_and_note_and_student_can_access(app, teacher_client):
    session_id = create_session(teacher_client, 'Resource Session')
    student = join_student(app, session_id)

    file_response = teacher_client.post(
        f'/teacher/session/{session_id}/resources',
        data={
            'title': 'Revision PDF',
            'resource_type': 'FILE',
            'file': (io.BytesIO(b'%PDF-test-content'), 'revision.pdf'),
        },
        content_type='multipart/form-data',
    )
    assert file_response.status_code == 302

    video_response = teacher_client.post(
        f'/teacher/session/{session_id}/resources',
        data={
            'title': 'Concept Video',
            'resource_type': 'VIDEO',
            'video_url': 'https://example.com/video',
        },
    )
    assert video_response.status_code == 302

    note_response = teacher_client.post(
        f'/teacher/session/{session_id}/resources',
        data={
            'title': 'Teacher Note',
            'resource_type': 'NOTE',
            'notes': 'Focus on the highlighted formula.',
        },
    )
    assert note_response.status_code == 302

    with app.app_context():
        rows = get_db().execute(
            'SELECT * FROM resources WHERE session_id=? ORDER BY id',
            (session_id,),
        ).fetchall()
        assert len(rows) == 3
        file_id = rows[0]['id']
        assert rows[0]['resource_type'] == 'PDF'
        assert rows[1]['resource_type'] == 'VIDEO'
        assert rows[2]['resource_type'] == 'NOTE'

    api_data = student.get(f'/api/student/session/{session_id}').get_json()
    titles = {item['title'] for item in api_data['resources']}
    assert {'Revision PDF', 'Concept Video', 'Teacher Note'} <= titles

    file_download = student.get(f'/student/resource/{file_id}')
    assert file_download.status_code == 200
    assert b'%PDF-test-content' in file_download.data


def test_resource_page_has_three_clear_sharing_workflows(teacher_client):
    session_id = create_session(teacher_client)
    page = teacher_client.get(f'/teacher/session/{session_id}/resources')
    assert page.status_code == 200
    assert b'Upload a file' in page.data
    assert b'Share a video' in page.data
    assert b'Publish a note' in page.data
    assert b'.pptx' in page.data


def test_international_design_tokens_and_responsive_breakpoints():
    root = Path(__file__).resolve().parents[1]
    css = (root / 'static' / 'css' / 'app.css').read_text(encoding='utf-8')
    assert '--primary:#5b5cf0' in css
    assert '--primary-2:#2f7df4' in css
    assert '@media(max-width:1024px)' in css
    assert '@media(max-width:760px)' in css
    assert '@media(max-width:520px)' in css
    assert '@media(max-width:380px)' in css
    assert 'prefers-reduced-motion' in css
    assert '.portal{min-height:100vh' in css


def test_commercial_pages_load_with_shared_design(client, teacher_client, admin_client):
    for path in ['/', '/teacher-login', '/admin-login']:
        response = client.get(path)
        assert response.status_code == 200
        assert b'/static/css/app.css' in response.data
        assert b'/static/js/app.js' in response.data

    teacher_dashboard = teacher_client.get('/teacher-dashboard')
    admin_dashboard = admin_client.get('/admin-dashboard')
    assert b'/static/css/app.css' in teacher_dashboard.data
    assert b'/static/css/app.css' in admin_dashboard.data


def test_resource_file_matrix_and_student_video_rejection(app, teacher_client):
    session_id = create_session(teacher_client, 'Resource Matrix')
    student = join_student(app, session_id)

    for title, filename, payload in [
        ('Class Image', 'diagram.png', b'png-bytes'),
        ('Presentation', 'lesson.pptx', b'pptx-bytes'),
        ('Word Notes', 'notes.docx', b'docx-bytes'),
    ]:
        response = teacher_client.post(
            f'/teacher/session/{session_id}/resources',
            data={
                'title': title,
                'resource_type': 'FILE',
                'file': (io.BytesIO(payload), filename),
            },
            content_type='multipart/form-data',
        )
        assert response.status_code == 302

    rejected = student.post(
        f'/student/session/{session_id}/submit',
        data={
            'question': 'Please inspect this video',
            'attachment': (io.BytesIO(b'video'), 'clip.mp4'),
        },
        content_type='multipart/form-data',
    )
    assert rejected.status_code == 302

    with app.app_context():
        resource_types = {
            row['resource_type']
            for row in get_db().execute(
                'SELECT resource_type FROM resources WHERE session_id=?',
                (session_id,),
            ).fetchall()
        }
        assert {'PNG', 'PPTX', 'DOCX'} <= resource_types
        assert get_db().execute(
            'SELECT COUNT(*) AS c FROM doubts WHERE session_id=?',
            (session_id,),
        ).fetchone()['c'] == 0
