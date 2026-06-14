import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

class Config:
    SECRET_KEY = os.getenv('AYD_SECRET_KEY', 'change-this-before-production-ask-your-doubt')
    DATABASE = os.getenv('AYD_DATABASE', str(BASE_DIR / 'database.db'))
    BASE_URL = os.getenv('AYD_BASE_URL', 'http://127.0.0.1:9000')
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024
    UPLOAD_DOUBTS = str(BASE_DIR / 'static' / 'uploads' / 'doubts')
    UPLOAD_RESOURCES = str(BASE_DIR / 'static' / 'uploads' / 'resources')
    QR_FOLDER = str(BASE_DIR / 'static' / 'qr')
    EXPORT_FOLDER = str(BASE_DIR / 'exports')
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = 60 * 60 * 12
