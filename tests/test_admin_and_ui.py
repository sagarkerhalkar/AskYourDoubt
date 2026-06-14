from pathlib import Path


def test_admin_management_pages(admin_client):
    for path in ['/admin-dashboard','/admin/teachers','/admin/admins','/admin/sessions','/admin/students','/admin/questions','/admin/analytics','/brand-settings','/admin/change-password']:
        response = admin_client.get(path)
        assert response.status_code == 200


def test_admin_creates_teacher_with_required_mobile(admin_client):
    bad = admin_client.post('/admin/teachers', data={
        'name':'New Teacher','mobile':'123','username':'newteacher','password':'password123'
    })
    assert b'exactly 10 digits' in bad.data
    good = admin_client.post('/admin/teachers', data={
        'name':'New Teacher','mobile':'9123456789','email':'','dob':'','username':'newteacher','password':'password123'
    })
    assert good.status_code == 302


def test_css_has_mobile_breakpoints_and_reduced_motion():
    css = Path(__file__).resolve().parents[1] / 'static' / 'css' / 'app.css'
    text = css.read_text(encoding='utf-8')
    assert '@media(max-width:780px)' in text
    assert '@media(max-width:480px)' in text
    assert 'prefers-reduced-motion' in text
    assert '--green:' in text

def test_admin_question_bank_and_teacher_edit(app, admin_client, teacher_client):
    teacher_client.post('/teacher/create-session', data={'session_name':'Bank Session','duration':'90','question_limit':'5'})
    student = app.test_client()
    student.post('/join-session/1', data={'name':'Bank Student','mobile':'9000000030'})
    student.post('/student/session/1/submit', data={'question':'Explain photosynthesis'})

    page = admin_client.get('/admin/question-bank')
    assert page.status_code == 200
    assert b'Explain photosynthesis' in page.data
    export = admin_client.get('/admin/question-bank.csv')
    assert export.status_code == 200
    assert export.headers['Content-Type'].startswith('text/csv')

    edit = admin_client.post('/admin/teacher/1/edit', data={
        'name':'Updated Teacher','mobile':'9876543210','email':'updated@example.com','dob':'1990-01-01','username':'teacher'
    })
    assert edit.status_code == 302
