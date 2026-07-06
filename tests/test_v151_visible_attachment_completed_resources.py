import io
from pathlib import Path

from db import get_db

ROOT = Path(__file__).resolve().parents[1]


def _create_session(teacher_client, name='Visual QA Session'):
    response = teacher_client.post('/teacher/create-session', data={
        'session_name': name,
        'duration': '90',
        'question_limit': '10',
    })
    assert response.status_code == 302
    return int(response.headers['Location'].rstrip('/').split('/')[-1])


def _join(app, session_id, name='Visual Student', mobile='9555555001'):
    student = app.test_client()
    response = student.post(f'/join-session/{session_id}', data={'name': name, 'mobile': mobile})
    assert response.status_code == 302
    return student


def test_student_attachment_selection_and_success_feedback_are_explicit(app, teacher_client):
    session_id = _create_session(teacher_client)
    student = _join(app, session_id)

    ask_page = student.get(f'/student/session/{session_id}?tab=ask')
    assert ask_page.status_code == 200
    html = ask_page.get_data(as_text=True)
    assert 'data-file-picker' in html
    assert 'data-file-selection' in html
    assert 'data-file-name' in html
    assert 'data-file-size' in html
    assert 'data-file-remove' in html
    assert 'Add attachment' in html

    javascript = (ROOT / 'static/js/app.js').read_text(encoding='utf-8')
    assert 'ready to upload' in javascript
    assert "picker.classList.add('has-file')" in javascript
    assert "input.addEventListener('change', render)" in javascript

    submitted = student.post(
        f'/student/session/{session_id}/submit',
        data={
            'question': 'Please review this attached diagram.',
            'attachment': (io.BytesIO(b'png-like-test-data'), 'diagram.png'),
        },
        content_type='multipart/form-data',
        follow_redirects=True,
    )
    assert submitted.status_code == 200
    assert b'Doubt sent successfully with attachment: diagram.png' in submitted.data
    with app.app_context():
        row = get_db().execute(
            'SELECT attachment_name, attachment_path FROM doubts WHERE session_id=? ORDER BY id DESC LIMIT 1',
            (session_id,),
        ).fetchone()
        assert row['attachment_name'] == 'diagram.png'
        assert row['attachment_path']


def test_completed_question_text_remains_visible_to_teacher_and_student(app, teacher_client):
    session_id = _create_session(teacher_client, 'Completed Visibility')
    student = _join(app, session_id, mobile='9555555002')
    question = 'Why is the completed question still important for revision?'
    assert student.post(f'/student/session/{session_id}/submit', data={'question': question}).status_code == 302

    with app.app_context():
        doubt_id = get_db().execute(
            'SELECT id FROM doubts WHERE session_id=? ORDER BY id DESC LIMIT 1',
            (session_id,),
        ).fetchone()['id']

    completed = teacher_client.post(f'/api/teacher/doubt/{doubt_id}/complete')
    assert completed.status_code == 200

    teacher_data = teacher_client.get(f'/api/teacher/session/{session_id}').get_json()
    student_data = student.get(f'/api/student/session/{session_id}').get_json()
    assert any(item['question'] == question for item in teacher_data['completed'])
    assert any(item['question'] == question for item in student_data['completed'])

    teacher_page = teacher_client.get(f'/teacher/session/{session_id}').get_data(as_text=True)
    student_page = student.get(f'/student/session/{session_id}?tab=answered').get_data(as_text=True)
    assert 'teacherCompletedDoubts' in teacher_page
    assert '${esc(doubt.question)}' in teacher_page
    assert 'studentAnsweredDoubts' in student_page
    assert '${esc(doubt.question)}' in student_page
    assert 'Every completed question stays clearly visible for review.' in student_page


def test_teacher_and_student_resource_pages_use_clean_card_workflows(app, teacher_client):
    session_id = _create_session(teacher_client, 'Resource Visual QA')
    student = _join(app, session_id, mobile='9555555003')

    teacher_page = teacher_client.get(f'/teacher/session/{session_id}/resources').get_data(as_text=True)
    for text in ('Upload a file', 'Share a video', 'Publish a note', 'Shared resources'):
        assert text in teacher_page
    for token in ('resource-create-grid', 'resource-create-card', 'commercial-resource-grid'):
        assert token in teacher_page

    response = teacher_client.post(
        f'/teacher/session/{session_id}/resources',
        data={'title': 'Revision summary', 'resource_type': 'NOTE', 'notes': 'Use this after class.'},
    )
    assert response.status_code == 302

    student_page = student.get(f'/student/session/{session_id}?tab=resources').get_data(as_text=True)
    assert 'Shared resources' in student_page
    assert 'studentResources' in student_page
    assert 'commercial-resource-grid' in student_page
    api = student.get(f'/api/student/session/{session_id}').get_json()
    assert api['resources'][0]['title'] == 'Revision summary'
