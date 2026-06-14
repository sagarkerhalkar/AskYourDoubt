from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_premium_palette_motion_and_font_scale():
    css = (ROOT / 'static' / 'css' / 'app.css').read_text(encoding='utf-8')
    assert '--blue:#4f6bff' in css
    assert '--violet:#8b5cf6' in css
    assert '--cyan:#00c7ff' in css
    assert '--amber:#ffb547' in css
    assert 'font-size:15px' in css
    assert '@keyframes ambientDrift' in css
    assert '@keyframes floatCard' in css
    assert '@keyframes photoShine' in css
    assert '[data-reveal]' in css
    assert '@media(max-width:520px)' in css
    assert '@media(prefers-reduced-motion:reduce)' in css


def test_realistic_teacher_student_photography_and_no_generator_credit():
    css = (ROOT / 'static' / 'css' / 'app.css').read_text(encoding='utf-8')
    home = (ROOT / 'templates' / 'public' / 'home.html').read_text(encoding='utf-8')
    teacher = (ROOT / 'templates' / 'teacher' / 'login.html').read_text(encoding='utf-8')
    student = (ROOT / 'templates' / 'student' / 'start.html').read_text(encoding='utf-8')
    assert 'pexels-photo-5212345' in css
    assert 'pexels-photo-8199159' in css
    combined = home + teacher + student
    assert 'Sagar Kerhalkar' not in combined
    assert 'ChatGPT' not in combined


def test_high_resolution_logo_is_vector():
    logo = ROOT / 'static' / 'img' / 'logo.svg'
    text = logo.read_text(encoding='utf-8')
    assert logo.exists()
    assert 'viewBox="0 0 640 160"' in text
    assert 'Ask Your Doubt' in text


def test_device_matrix_runner_and_ci_matrix_exist():
    runner = (ROOT / 'run_device_matrix.py').read_text(encoding='utf-8')
    workflow = (ROOT / '.github' / 'workflows' / 'ci-cd.yml').read_text(encoding='utf-8')
    assert 'iphone-se' in runner
    assert 'ipad-air' in runner
    assert 'desktop-qhd' in runner
    assert 'chromium, firefox, webkit' in workflow
