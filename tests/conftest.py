from pathlib import Path
import sys

import pytest
from werkzeug.security import generate_password_hash

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app import create_app
from db import get_db


@pytest.fixture()
def app(tmp_path):
    app = create_app({
        'TESTING': True,
        'SECRET_KEY': 'test-secret',
        'DATABASE': str(tmp_path / 'test.db'),
        'UPLOAD_DOUBTS': str(tmp_path / 'uploads' / 'doubts'),
        'UPLOAD_RESOURCES': str(tmp_path / 'uploads' / 'resources'),
        'QR_FOLDER': str(tmp_path / 'qr'),
        'EXPORT_FOLDER': str(tmp_path / 'exports'),
        'BASE_URL': 'http://testserver',
    })
    with app.app_context():
        db = get_db()
        db.execute(
            '''INSERT INTO teachers(name,mobile,email,dob,username,password,status)
               VALUES(?,?,?,?,?,?,?)''',
            ('Test Teacher','9876543210','teacher@example.com','1990-01-01','teacher',generate_password_hash('teacher123'),'ACTIVE'),
        )
        db.commit()
    yield app


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def teacher_client(app):
    client = app.test_client()
    response = client.post('/teacher-login', data={'username':'teacher','password':'teacher123'})
    assert response.status_code == 302
    return client


@pytest.fixture()
def admin_client(app):
    client = app.test_client()
    response = client.post('/admin-login', data={'username':'admin','password':'admin123'})
    assert response.status_code == 302
    return client
