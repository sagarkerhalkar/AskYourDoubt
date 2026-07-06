import pytest

VIEWPORTS = [
    pytest.param({'width': 320, 'height': 568}, id='iphone-se'),
    pytest.param({'width': 360, 'height': 800}, id='android-small'),
    pytest.param({'width': 390, 'height': 844}, id='iphone-14'),
    pytest.param({'width': 412, 'height': 915}, id='android-large'),
    pytest.param({'width': 768, 'height': 1024}, id='ipad-portrait'),
    pytest.param({'width': 820, 'height': 1180}, id='ipad-air'),
    pytest.param({'width': 1024, 'height': 1366}, id='ipad-pro'),
    pytest.param({'width': 1280, 'height': 800}, id='small-laptop'),
    pytest.param({'width': 1366, 'height': 768}, id='laptop'),
    pytest.param({'width': 1440, 'height': 900}, id='macbook'),
    pytest.param({'width': 1920, 'height': 1080}, id='desktop-fhd'),
    pytest.param({'width': 2560, 'height': 1440}, id='desktop-qhd'),
]


def prepare(page, viewport):
    page.set_default_timeout(7000)
    page.set_default_navigation_timeout(15000)
    page.set_viewport_size(viewport)
    page.route('https://**', lambda route: route.abort())


def assert_no_overflow(page, path, viewport):
    overflow = page.evaluate('document.documentElement.scrollWidth > document.documentElement.clientWidth + 2')
    assert not overflow, f'Horizontal overflow on {path} at {viewport}'
    assert page.locator('body').is_visible()


@pytest.mark.parametrize('viewport', VIEWPORTS)
def test_public_pages_have_no_horizontal_overflow(page, live_server_url, viewport):
    prepare(page, viewport)
    for path in ['/', '/student', '/teacher-login', '/admin-login']:
        page.goto(live_server_url + path, wait_until='domcontentloaded')
        assert_no_overflow(page, path, viewport)


def test_home_primary_actions_and_public_credit_removed(page, live_server_url):
    prepare(page, {'width': 390, 'height': 844})
    page.goto(live_server_url + '/', wait_until='domcontentloaded')
    assert page.get_by_role('link', name='Join Student Session').is_visible()
    assert page.get_by_role('link', name='Open Teacher Portal').is_visible()
    assert page.get_by_role('link', name='Open Admin Portal').is_visible()
    assert page.get_by_text('Built by Sagar Kerhalkar').count() == 0
    assert page.get_by_text('ChatGPT').count() == 0


@pytest.mark.parametrize('viewport', VIEWPORTS)
def test_authenticated_portals_have_no_overflow(page, live_server_url, viewport):
    prepare(page, viewport)

    page.goto(live_server_url + '/join-session/1', wait_until='domcontentloaded')
    page.get_by_label('Full name').fill('Responsive Student')
    page.get_by_label('10-digit mobile number').fill('9000000099')
    page.get_by_role('button', name='Enter live session').click()
    assert page.get_by_text('Hello, Responsive Student').is_visible()
    assert_no_overflow(page, '/student/session/1', viewport)
    page.goto(live_server_url + '/student/session/1/focus', wait_until='domcontentloaded')
    assert page.get_by_text('Live doubts').is_visible()
    assert page.get_by_role('link', name='Return to Original Size').is_visible()
    assert_no_overflow(page, '/student/session/1/focus', viewport)

    page.context.clear_cookies()
    page.goto(live_server_url + '/teacher-login', wait_until='domcontentloaded')
    page.get_by_label('Username').fill('browserteacher')
    page.get_by_label('Password').fill('browserpass')
    page.get_by_role('button', name='Open Teacher Portal').click()
    page.goto(live_server_url + '/teacher/session/1', wait_until='domcontentloaded')
    assert page.get_by_text('Browser Session').first.is_visible()
    assert_no_overflow(page, '/teacher/session/1', viewport)
    page.goto(live_server_url + '/teacher/session/1/focus', wait_until='domcontentloaded')
    assert page.get_by_role('heading', name='Open Doubts').is_visible()
    assert page.get_by_role('link', name='Return to Original Size').is_visible()
    assert page.get_by_role('button', name='Copy Link').is_visible()
    assert_no_overflow(page, '/teacher/session/1/focus', viewport)

    page.context.clear_cookies()
    page.goto(live_server_url + '/admin-login', wait_until='domcontentloaded')
    page.get_by_label('Username').fill('admin')
    page.get_by_label('Password').fill('admin123')
    page.get_by_role('button', name='Open Admin Portal').click()
    assert page.get_by_text('Welcome back').first.is_visible()
    assert_no_overflow(page, '/admin-dashboard', viewport)


def test_teacher_copy_link_and_resource_studio(page, live_server_url):
    prepare(page, {'width': 390, 'height': 844})
    page.goto(live_server_url + '/teacher-login', wait_until='domcontentloaded')
    page.get_by_label('Username').fill('browserteacher')
    page.get_by_label('Password').fill('browserpass')
    page.get_by_role('button', name='Open Teacher Portal').click()

    page.goto(live_server_url + '/teacher/session/1', wait_until='domcontentloaded')
    copy_button = page.locator('[data-copy-target="#joinLink"]')
    assert copy_button.is_visible()
    manual_copy_values = []
    def accept_copy_dialog(dialog):
        manual_copy_values.append(dialog.default_value)
        dialog.accept()
    page.on('dialog', accept_copy_dialog)
    copy_button.click()
    page.wait_for_timeout(850)
    feedback = copy_button.inner_text()
    assert feedback in {'Copied ✓', 'Copy ready ✓'}
    if feedback == 'Copy ready ✓':
        assert manual_copy_values and manual_copy_values[-1].endswith('/join-session/1')
    assert page.get_by_role('link', name='Share Resources').is_visible()
    assert page.get_by_role('button', name='Share QR').is_visible()
    with page.expect_download() as download_info:
        page.get_by_role('link', name='Download QR').click()
    assert download_info.value.suggested_filename.endswith('_student_QR.png')

    page.goto(live_server_url + '/teacher/session/1/resources', wait_until='domcontentloaded')
    assert page.get_by_role('heading', name='Upload a file').is_visible()
    assert page.get_by_role('heading', name='Share a video').is_visible()
    assert page.get_by_role('heading', name='Publish a note').is_visible()


def test_teacher_and_student_focus_controls(page, live_server_url):
    prepare(page, {'width': 390, 'height': 844})

    page.goto(live_server_url + '/teacher-login', wait_until='domcontentloaded')
    page.get_by_label('Username').fill('browserteacher')
    page.get_by_label('Password').fill('browserpass')
    page.get_by_role('button', name='Open Teacher Portal').click()
    page.goto(live_server_url + '/teacher/session/1', wait_until='domcontentloaded')
    assert page.get_by_role('button', name='Focus Full Screen').is_visible()
    assert page.get_by_role('link', name='Open New Window').is_visible()
    page.goto(live_server_url + '/teacher/session/1/focus', wait_until='domcontentloaded')
    teacher_stage = page.locator('#teacherFocusStage')
    teacher_minimize = page.get_by_role('button', name='Minimize live doubt panel')
    assert teacher_minimize.is_visible()
    teacher_minimize.click()
    assert 'is-minimized' in (teacher_stage.get_attribute('class') or '')
    assert page.get_by_role('button', name='Maximize live doubt panel').is_visible()
    page.get_by_role('button', name='Maximize live doubt panel').click()
    assert 'is-minimized' not in (teacher_stage.get_attribute('class') or '')
    assert page.get_by_role('button', name='Copy Link').is_visible()
    assert page.get_by_role('link', name='Download QR').is_visible()
    assert page.get_by_role('button', name='Share QR').is_visible()
    assert page.get_by_role('button', name='Print QR').is_visible()

    page.context.clear_cookies()
    page.goto(live_server_url + '/join-session/1', wait_until='domcontentloaded')
    page.get_by_label('Full name').fill('Focus Browser Student')
    page.get_by_label('10-digit mobile number').fill('9000000088')
    page.get_by_role('button', name='Enter live session').click()
    page.goto(live_server_url + '/student/session/1?tab=live', wait_until='domcontentloaded')
    assert page.get_by_role('button', name='Maximize').is_visible()
    assert page.get_by_role('link', name='New Window').is_visible()
    page.goto(live_server_url + '/student/session/1/focus', wait_until='domcontentloaded')
    student_stage = page.locator('#studentFocusStage')
    student_minimize = page.get_by_role('button', name='Minimize live doubt panel')
    assert student_minimize.is_visible()
    student_minimize.click()
    assert 'is-minimized' in (student_stage.get_attribute('class') or '')
    page.get_by_role('button', name='Maximize live doubt panel').click()
    assert 'is-minimized' not in (student_stage.get_attribute('class') or '')
    assert page.get_by_role('link', name='Return to Original Size').is_visible()


def test_teacher_and_student_sessions_coexist_in_same_browser_context(page, live_server_url):
    prepare(page, {'width': 390, 'height': 844})
    page.goto(live_server_url + '/teacher-login', wait_until='domcontentloaded')
    page.get_by_label('Username').fill('browserteacher')
    page.get_by_label('Password').fill('browserpass')
    page.get_by_role('button', name='Open Teacher Portal').click()
    assert '/teacher-dashboard' in page.url

    page.goto(live_server_url + '/join-session/1', wait_until='domcontentloaded')
    page.get_by_label('Full name').fill('Same Browser Student')
    page.get_by_label('10-digit mobile number').fill('9000000077')
    page.get_by_role('button', name='Enter live session').click()
    assert '/student/session/1' in page.url

    # Student login must no longer remove teacher_id from the shared Flask cookie.
    page.goto(live_server_url + '/teacher/session/1', wait_until='domcontentloaded')
    assert page.get_by_text('Browser Session').first.is_visible()
    assert '/teacher-login' not in page.url

    # Teacher access must not remove the student identity either.
    page.goto(live_server_url + '/student/session/1?tab=live', wait_until='domcontentloaded')
    assert page.get_by_text('Same Browser Student').first.is_visible()
    assert '/join-session/1' not in page.url



def _font_size(page, selector):
    return float(page.locator(selector).first.evaluate("element => parseFloat(getComputedStyle(element).fontSize)"))


def test_professional_heading_scale_and_touch_targets(page, live_server_url):
    """No role-page heading may regress to a giant marketing-sized heading."""
    prepare(page, {'width': 1366, 'height': 768})
    page.goto(live_server_url + '/', wait_until='domcontentloaded')
    assert _font_size(page, '.hero h1') <= 46

    page.goto(live_server_url + '/teacher-login', wait_until='domcontentloaded')
    page.get_by_label('Username').fill('browserteacher')
    page.get_by_label('Password').fill('browserpass')
    page.get_by_role('button', name='Open Teacher Portal').click()
    assert _font_size(page, '.teacher-dashboard-copy h1') <= 30
    dashboard_box = page.locator('.teacher-dashboard-hero').first.bounding_box()
    assert dashboard_box and dashboard_box['height'] <= 230

    page.goto(live_server_url + '/teacher/session/1', wait_until='domcontentloaded')
    assert _font_size(page, '.teacher-command-copy-v141 h1') <= 30
    live_box = page.locator('.teacher-command-hero-v141').first.bounding_box()
    assert live_box and live_box['height'] <= 235

    page.context.clear_cookies()
    page.goto(live_server_url + '/join-session/1', wait_until='domcontentloaded')
    page.get_by_label('Full name').fill('Typography Student')
    page.get_by_label('10-digit mobile number').fill('9000000066')
    page.get_by_role('button', name='Enter live session').click()
    assert _font_size(page, '.student-welcome-copy h1') <= 30
    student_box = page.locator('.student-welcome-v14').first.bounding_box()
    assert student_box and student_box['height'] <= 220

    page.set_viewport_size({'width': 390, 'height': 844})
    page.reload(wait_until='domcontentloaded')
    for button in page.locator('button, a.btn').all():
        if not button.is_visible():
            continue
        box = button.bounding_box()
        if box:
            assert box['height'] >= 32, f"Touch target too short: {button.inner_text()}"


def test_student_polling_preserves_typed_text_and_updates_without_reload(page, live_server_url):
    prepare(page, {'width': 390, 'height': 844})
    page.goto(live_server_url + '/join-session/1', wait_until='domcontentloaded')
    page.get_by_label('Full name').fill('Silent Poll Student')
    page.get_by_label('10-digit mobile number').fill('9000000055')
    page.get_by_role('button', name='Enter live session').click()
    page.goto(live_server_url + '/student/session/1/tab/ask', wait_until='domcontentloaded')
    composer = page.locator('textarea[name="question"]')
    composer.fill('This draft must stay while one-second polling runs 🙂')
    original_url = page.url
    page.wait_for_timeout(2300)
    assert composer.input_value() == 'This draft must stay while one-second polling runs 🙂'
    assert page.url == original_url
    assert page.evaluate("performance.getEntriesByType('navigation').length") == 1


def test_live_focus_keeps_core_actions_and_polling_contract(page, live_server_url):
    prepare(page, {'width': 390, 'height': 844})
    page.goto(live_server_url + '/teacher-login', wait_until='domcontentloaded')
    page.get_by_label('Username').fill('browserteacher')
    page.get_by_label('Password').fill('browserpass')
    page.get_by_role('button', name='Open Teacher Portal').click()
    page.goto(live_server_url + '/teacher/session/1/focus', wait_until='domcontentloaded')
    assert page.get_by_role('link', name='Return to Original Size').is_visible()
    assert page.get_by_role('button', name='Copy Link').is_visible()
    assert page.get_by_role('link', name='Download QR').is_visible()
    assert page.get_by_role('button', name='Share QR').is_visible()
    assert page.get_by_role('button', name='Print QR').is_visible()
    assert page.locator('#teacherPerPage').is_visible()
    assert page.locator('#teacherOpenDoubts').get_attribute('aria-live') == 'polite'

    page.context.clear_cookies()
    page.goto(live_server_url + '/join-session/1', wait_until='domcontentloaded')
    page.get_by_label('Full name').fill('Focus Contract Student')
    page.get_by_label('10-digit mobile number').fill('9000000044')
    page.get_by_role('button', name='Enter live session').click()
    page.goto(live_server_url + '/student/session/1/focus', wait_until='domcontentloaded')
    assert page.get_by_role('link', name='Return to Original Size').is_visible()
    assert page.locator('#studentPerPage').is_visible()
    assert page.locator('#studentLiveDoubts').get_attribute('aria-live') == 'polite'
