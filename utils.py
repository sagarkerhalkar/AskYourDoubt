from __future__ import annotations

import csv
import io
import os
import re
import secrets
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Iterable
from urllib.parse import urlparse

import qrcode
from flask import current_app
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

ALLOWED_DOUBT_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt', 'jpg', 'jpeg', 'png', 'webp'}
ALLOWED_RESOURCE_EXTENSIONS = ALLOWED_DOUBT_EXTENSIONS | {'ppt', 'pptx'}
MAX_UPLOAD_BYTES = 10 * 1024 * 1024

SUBJECT_RULES = {
    'Physics': {'force','motion','light','newton','velocity','acceleration','electricity','current','voltage','wave','energy','gravity','thermodynamics','heat','temperature'},
    'Mathematics': {'equation','algebra','geometry','trigonometry','calculus','matrix','probability','statistics','number','derivative','integral'},
    'Chemistry': {'atom','molecule','reaction','acid','base','bond','organic','inorganic','periodic','compound','chemical'},
    'Biology': {'cell','dna','gene','heart','body','plant','animal','human','respiration','photosynthesis','biology'},
    'Computer Science': {'python','java','code','program','algorithm','database','computer','network','software','error'},
    'English': {'grammar','essay','poem','literature','english','sentence','verb','noun'},
}
STOPWORDS = {'what','why','when','where','which','who','whom','whose','how','is','are','was','were','the','a','an','of','to','in','on','for','and','or','with','this','that','please','explain','tell','me','my','doubt','does','do','did','can','could','would','should'}


def verify_and_upgrade_password(stored: str, supplied: str) -> tuple[bool, str | None]:
    if not stored:
        return False, None
    if stored.startswith(('scrypt:', 'pbkdf2:', 'argon2:')):
        return check_password_hash(stored, supplied), None
    if secrets.compare_digest(stored, supplied):
        return True, generate_password_hash(supplied)
    return False, None



def valid_http_url(value: str) -> bool:
    """Allow only absolute HTTP(S) links for shared external resources."""
    try:
        parsed = urlparse((value or '').strip())
    except ValueError:
        return False
    return parsed.scheme in {'http', 'https'} and bool(parsed.netloc)


def validate_mobile(mobile: str) -> bool:
    return bool(re.fullmatch(r'\d{10}', mobile or ''))


def detect_category_and_keyword(question: str) -> tuple[str, str]:
    words = re.findall(r"[A-Za-z][A-Za-z0-9'-]*", question.lower())
    category = 'General'
    best_score = 0
    for subject, terms in SUBJECT_RULES.items():
        score = sum(1 for word in words if word in terms)
        if score > best_score:
            best_score = score
            category = subject
    keyword = next((w.title() for w in words if len(w) > 2 and w not in STOPWORDS), 'General')
    return category, keyword


def allowed_extension(filename: str, *, resource: bool = False) -> bool:
    if '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    return ext in (ALLOWED_RESOURCE_EXTENSIONS if resource else ALLOWED_DOUBT_EXTENSIONS)


def save_upload(file_storage, target_dir: str, *, resource: bool = False) -> tuple[str, str, str]:
    if not file_storage or not file_storage.filename:
        return '', '', ''
    original = secure_filename(file_storage.filename)
    if not allowed_extension(original, resource=resource):
        raise ValueError('Unsupported file type.')
    file_storage.stream.seek(0, os.SEEK_END)
    size = file_storage.stream.tell()
    file_storage.stream.seek(0)
    if size > MAX_UPLOAD_BYTES:
        raise ValueError('File size must be 10 MB or less.')
    ext = original.rsplit('.', 1)[1].lower()
    Path(target_dir).mkdir(parents=True, exist_ok=True)
    name = f"{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}_{secrets.token_hex(4)}_{original}"
    full_path = Path(target_dir) / name
    file_storage.save(full_path)
    return str(full_path), original, ext.upper()


def create_qr(session_id: int) -> str:
    public_url = current_app.config['BASE_URL'].rstrip('/')
    join_url = f'{public_url}/join-session/{session_id}'
    folder = Path(current_app.config['QR_FOLDER'])
    folder.mkdir(parents=True, exist_ok=True)
    filename = f'session_{session_id}.png'
    qrcode.make(join_url).save(folder / filename)
    return filename


MAX_SESSION_DURATION_SECONDS = 24 * 60 * 60


def clamp_session_duration_seconds(value: int | str | None, *, default: int = 90 * 60) -> int:
    """Clamp teacher/admin controlled session duration to 0 seconds through 24 hours.

    0 means manual close/no automatic expiry. This keeps demo sessions usable while still
    allowing very short timed sessions when teachers enter 1 second or more.
    """
    try:
        seconds = int(value if value not in (None, '') else default)
    except (TypeError, ValueError):
        seconds = default
    return min(max(seconds, 0), MAX_SESSION_DURATION_SECONDS)




def parse_session_duration_hours(value: int | float | str | None, *, default_seconds: int = 90 * 60) -> int:
    """Parse teacher-facing HH.MM session duration into seconds.

    The UI now accepts an easy hours format requested by the product owner:
    - 0 = manual close/no auto-expiry
    - .30 = 30 minutes
    - 1 = 1 hour
    - 1.30 = 1 hour 30 minutes
    - 24 = 24 hours maximum

    The decimal part is treated as minutes, not a mathematical decimal fraction.
    Invalid or out-of-range minute values are handled safely and final output is
    clamped to 0 through 24 hours.
    """
    if value in (None, ''):
        return clamp_session_duration_seconds(default_seconds, default=default_seconds)
    raw = str(value).strip().lower().replace('hrs', '').replace('hr', '').replace('hours', '').replace('hour', '').replace(' ', '')
    raw = raw.replace(',', '.')
    if raw in {'manual', 'none'}:
        return 0
    if raw.startswith('.'):
        hours_part = '0'
        minutes_part = raw[1:]
    elif '.' in raw:
        hours_part, minutes_part = raw.split('.', 1)
    else:
        hours_part, minutes_part = raw, '0'
    try:
        hours = int(hours_part or 0)
    except ValueError:
        return clamp_session_duration_seconds(default_seconds, default=default_seconds)
    minutes_digits = ''.join(ch for ch in minutes_part if ch.isdigit())
    if not minutes_digits:
        minutes = 0
    else:
        # HH.MM format: keep first two minute digits. .5 means 5 minutes, .30 means 30 minutes.
        try:
            minutes = int(minutes_digits[:2])
        except ValueError:
            minutes = 0
    minutes = min(max(minutes, 0), 59)
    return clamp_session_duration_seconds(hours * 3600 + minutes * 60, default=default_seconds)


def duration_hours_input(seconds: int | str | None) -> str:
    """Return compact HH.MM text for teacher duration inputs."""
    seconds = clamp_session_duration_seconds(seconds, default=0)
    if seconds == 0:
        return '0'
    hours, remainder = divmod(seconds, 3600)
    minutes = remainder // 60
    if minutes == 0:
        return str(hours)
    if hours == 0:
        return f'.{minutes:02d}'
    return f'{hours}.{minutes:02d}'


def duration_label(seconds: int | str | None) -> str:
    seconds = clamp_session_duration_seconds(seconds, default=0)
    if seconds == 0:
        return 'Manual close'
    hours, remainder = divmod(seconds, 3600)
    minutes, secs = divmod(remainder, 60)
    parts: list[str] = []
    if hours:
        parts.append(f'{hours} hr' + ('s' if hours != 1 else ''))
    if minutes:
        parts.append(f'{minutes} min' + ('s' if minutes != 1 else ''))
    if secs or not parts:
        parts.append(f'{secs} sec' + ('s' if secs != 1 else ''))
    return ' '.join(parts)


def session_end_time(duration_seconds: int | str | None) -> str:
    seconds = clamp_session_duration_seconds(duration_seconds, default=90 * 60)
    if seconds == 0:
        return ''
    value = datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(seconds=seconds)
    return value.isoformat(timespec='seconds')


def rows_to_csv(headers: list[str], rows: Iterable[Iterable]) -> io.BytesIO:
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(headers)
    writer.writerows(rows)
    data = io.BytesIO(output.getvalue().encode('utf-8-sig'))
    data.seek(0)
    return data

STANDARD_PAGE_SIZES = (10, 20, 30)
LIVE_PAGE_SIZES = (100, 250, 500)


def pagination_args(*, default: int = 20, allowed: tuple[int, ...] = STANDARD_PAGE_SIZES) -> tuple[int, int]:
    """Return validated 1-based page and page size from the current request."""
    from flask import request

    try:
        page = max(int(request.args.get('page', 1)), 1)
    except (TypeError, ValueError):
        page = 1
    try:
        per_page = int(request.args.get('per_page', default))
    except (TypeError, ValueError):
        per_page = default
    if per_page not in allowed:
        per_page = default
    return page, per_page


def pagination_meta(
    total: int,
    page: int,
    per_page: int,
    *,
    allowed: tuple[int, ...] = STANDARD_PAGE_SIZES,
) -> dict:
    """Build pagination metadata and URLs while preserving current filters."""
    from flask import request
    from urllib.parse import urlencode

    total = max(int(total or 0), 0)
    pages = max((total + per_page - 1) // per_page, 1)
    page = min(max(page, 1), pages)

    def page_url(target_page: int, target_size: int | None = None) -> str:
        args = request.args.to_dict(flat=True)
        args['page'] = str(min(max(target_page, 1), pages))
        args['per_page'] = str(target_size or per_page)
        return f"{request.path}?{urlencode(args)}"

    return {
        'page': page,
        'per_page': per_page,
        'pages': pages,
        'total': total,
        'start': 0 if total == 0 else (page - 1) * per_page + 1,
        'end': min(page * per_page, total),
        'has_prev': page > 1,
        'has_next': page < pages,
        'prev_url': page_url(page - 1),
        'next_url': page_url(page + 1),
        'first_url': page_url(1),
        'last_url': page_url(pages),
        'size_urls': {size: page_url(1, size) for size in allowed},
        'allowed_sizes': allowed,
    }
