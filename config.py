import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

class Config:
    SECRET_KEY = os.getenv('AYD_SECRET_KEY', 'change-this-before-production-ask-your-doubt')
    DATABASE = os.getenv('AYD_DATABASE', str(BASE_DIR / 'database.db'))
    BASE_URL = os.getenv('AYD_BASE_URL', 'http://127.0.0.1:9000')
    PORT = int(os.getenv('AYD_PORT', '9000'))
    DEBUG = os.getenv('AYD_DEBUG', '0').strip().lower() in {'1', 'true', 'yes', 'on'}
    # Allow multipart overhead while save_upload() enforces the actual 10 MB file limit.
    MAX_CONTENT_LENGTH = int(os.getenv('AYD_MAX_REQUEST_MB', '11')) * 1024 * 1024
    UPLOAD_DOUBTS = os.getenv('AYD_UPLOAD_DOUBTS', str(BASE_DIR / 'static' / 'uploads' / 'doubts'))
    UPLOAD_RESOURCES = os.getenv('AYD_UPLOAD_RESOURCES', str(BASE_DIR / 'static' / 'uploads' / 'resources'))
    QR_FOLDER = os.getenv('AYD_QR_FOLDER', str(BASE_DIR / 'static' / 'qr'))
    EXPORT_FOLDER = os.getenv('AYD_EXPORT_FOLDER', str(BASE_DIR / 'exports'))
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_SECURE = os.getenv('AYD_COOKIE_SECURE', '0').strip().lower() in {'1', 'true', 'yes', 'on'}
    PERMANENT_SESSION_LIFETIME = 60 * 60 * 12
