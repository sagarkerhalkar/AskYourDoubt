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
    pytest.param({'width': 1920, 'height': 1080}, id='desktop-fhd'),
]


def prepare(page, viewport):
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


def test_home_primary_actions_and_no_generator_credit(page, live_server_url):
    prepare(page, {'width': 390, 'height': 844})
    page.goto(live_server_url + '/', wait_until='domcontentloaded')
    assert page.get_by_role('link', name='Join Student Session').is_visible()
    assert page.get_by_role('link', name='Open Teacher Portal').is_visible()
    assert page.get_by_role('link', name='Open Admin Portal').is_visible()
    html = page.content()
    assert 'Sagar Kerhalkar' not in html
    assert 'ChatGPT' not in html


@pytest.mark.parametrize('viewport', VIEWPORTS)
def test_authenticated_portals_have_no_overflow(page, live_server_url, viewport):
    prepare(page, viewport)

    page.goto(live_server_url + '/join-session/1', wait_until='domcontentloaded')
    page.get_by_label('Full name').fill('Responsive Student')
    page.get_by_label('10-digit mobile number').fill('9000000099')
    page.get_by_role('button', name='Enter live session').click()
    assert page.get_by_text('Hello, Responsive Student').is_visible()
    assert_no_overflow(page, '/student/session/1', viewport)

    page.context.clear_cookies()
    page.goto(live_server_url + '/teacher-login', wait_until='domcontentloaded')
    page.get_by_label('Username').fill('browserteacher')
    page.get_by_label('Password').fill('browserpass')
    page.get_by_role('button', name='Open Teacher Portal').click()
    page.goto(live_server_url + '/teacher/session/1', wait_until='domcontentloaded')
    assert page.get_by_text('Browser Session').first.is_visible()
    assert_no_overflow(page, '/teacher/session/1', viewport)

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
    copy_button = page.get_by_role('button', name='Copy Link')
    assert copy_button.is_visible()
    copy_button.click()
    assert page.get_by_role('button', name='Copied ✓').is_visible()
    assert page.get_by_role('link', name='Share Resources').is_visible()
    assert page.get_by_role('button', name='Share QR').is_visible()
    with page.expect_download() as download_info:
        page.get_by_role('link', name='Download QR').click()
    assert download_info.value.suggested_filename.endswith('_student_QR.png')

    page.goto(live_server_url + '/teacher/session/1/resources', wait_until='domcontentloaded')
    assert page.get_by_role('heading', name='Upload a file').is_visible()
    assert page.get_by_role('heading', name='Share a video').is_visible()
    assert page.get_by_role('heading', name='Publish a note').is_visible()
