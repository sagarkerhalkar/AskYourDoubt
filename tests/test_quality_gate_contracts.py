from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding='utf-8')


def test_runtime_and_dev_dependencies_are_compatible():
    runtime = read('requirements.txt')
    dev = read('requirements-dev.txt')
    assert 'pytest' not in runtime.lower()
    assert 'pytest==9.0.2' in dev
    assert 'pytest-playwright==0.8.0' in dev
    assert 'playwright==1.57.0' in dev


def test_premium_motion_and_3d_css_contracts_exist():
    css = read('static/css/app.css')
    required = [
        'perspective(',
        'transform-style:preserve-3d',
        '@keyframes heroAura',
        '@keyframes floatCard',
        '@keyframes photoShine',
        '@keyframes cardIn',
        '@media(prefers-reduced-motion:reduce)',
    ]
    for token in required:
        assert token in css, token


def test_motion_javascript_contracts_exist():
    js = read('static/js/app.js')
    required = [
        'IntersectionObserver',
        'data-tilt',
        'perspective(900px)',
        'requestAnimationFrame',
        'navigator.clipboard',
        'fallbackCopy',
    ]
    for token in required:
        assert token in js, token


def test_teacher_and_student_live_updates_are_background_polling():
    teacher = read('templates/teacher/live_session.html')
    student = read('templates/student/portal.html')
    assert 'setInterval(load, 1000)' in teacher
    assert 'setInterval(load,1000)' in student
    assert "no-store" in teacher
    assert "no-store" in student
    assert 'Connecting to live doubts' in teacher
    assert 'Connecting to live doubts' in student


def test_mobile_tablet_and_desktop_breakpoints_exist():
    css = read('static/css/app.css')
    for width in ('1024px', '760px', '480px'):
        assert width in css
    assert 'overflow-x:hidden' in css


def test_teacher_resource_and_copy_link_controls_exist():
    template = read('templates/teacher/live_session.html')
    assert 'Share Resources' in template
    assert 'Copy Link' in template
    assert 'data-copy-target' in template
