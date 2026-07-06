from __future__ import annotations

from datetime import datetime, timezone

from flask import Blueprint, jsonify, request, session

from db import get_db, transaction

bp = Blueprint('api', __name__, url_prefix='/api')

LIVE_PAGE_SIZES = (100, 250, 500)
STANDARD_PAGE_SIZES = (10, 20, 30)


def _iso(value):
    return value or ''


def _teacher_owns(session_id: int) -> bool:
    row = get_db().execute('SELECT teacher_id FROM sessions WHERE id=?', (session_id,)).fetchone()
    return bool(row and row['teacher_id'] == session.get('teacher_id'))


def _student_in(session_id: int) -> bool:
    return bool(session.get('student_id') and int(session.get('student_session_id', 0)) == int(session_id))


def _auto_close_if_expired(session_row) -> bool:
    if not session_row or session_row['status'] != 'ACTIVE' or not session_row['ends_at']:
        return False
    try:
        expired = datetime.now(timezone.utc).replace(tzinfo=None) >= datetime.fromisoformat(str(session_row['ends_at']))
    except ValueError:
        expired = False
    if expired:
        with transaction() as db:
            db.execute("UPDATE sessions SET status='CLOSED', closed_at=CURRENT_TIMESTAMP WHERE id=?", (session_row['id'],))
        return True
    return False


def _page_args(allowed: tuple[int, ...], default: int, prefix: str = '') -> tuple[int, int]:
    page_key = f'{prefix}page' if prefix else 'page'
    size_key = f'{prefix}per_page' if prefix else 'per_page'
    try:
        page = max(int(request.args.get(page_key, 1)), 1)
    except (TypeError, ValueError):
        page = 1
    try:
        per_page = int(request.args.get(size_key, default))
    except (TypeError, ValueError):
        per_page = default
    if per_page not in allowed:
        per_page = default
    return page, per_page


def _pagination(total: int, page: int, per_page: int, allowed: tuple[int, ...]) -> dict:
    pages = max((int(total or 0) + per_page - 1) // per_page, 1)
    page = min(max(page, 1), pages)
    return {
        'page': page,
        'per_page': per_page,
        'pages': pages,
        'total': int(total or 0),
        'has_prev': page > 1,
        'has_next': page < pages,
        'allowed_sizes': list(allowed),
    }


def _teacher_doubt(row) -> dict:
    has_attachment = bool(row['has_attachment'])
    return {
        'id': row['id'],
        'question': row['question'],
        'votes': row['votes'] or 0,
        'status': row['status'],
        'created_at': _iso(row['created_at']),
        'has_attachment': has_attachment,
        'download_url': f'/teacher/doubt/{row["id"]}/attachment' if has_attachment else None,
    }


@bp.get('/teacher/session/<int:session_id>')
def teacher_session_data(session_id: int):
    if not session.get('teacher_id') or not _teacher_owns(session_id):
        return jsonify({'error': 'unauthorized'}), 403

    page, per_page = _page_args(LIVE_PAGE_SIZES, 100)
    completed_page, completed_per_page = _page_args(STANDARD_PAGE_SIZES, 10, 'completed_')
    skipped_page, skipped_per_page = _page_args(STANDARD_PAGE_SIZES, 10, 'skipped_')
    db = get_db()
    class_session = db.execute('SELECT * FROM sessions WHERE id=?', (session_id,)).fetchone()
    if not class_session:
        return jsonify({'error': 'not found'}), 404
    if _auto_close_if_expired(class_session):
        class_session = db.execute('SELECT * FROM sessions WHERE id=?', (session_id,)).fetchone()

    stats = db.execute(
        '''
        SELECT COUNT(*) AS total,
               SUM(CASE WHEN status='OPEN' THEN 1 ELSE 0 END) AS open_count,
               SUM(CASE WHEN status='COMPLETED' THEN 1 ELSE 0 END) AS completed_count,
               SUM(CASE WHEN status='SKIPPED' THEN 1 ELSE 0 END) AS skipped_count,
               COALESCE(SUM(votes),0) AS total_votes
        FROM doubts WHERE session_id=?
        ''',
        (session_id,),
    ).fetchone()
    open_total = int(stats['open_count'] or 0)
    completed_total = int(stats['completed_count'] or 0)
    skipped_total = int(stats['skipped_count'] or 0)
    pager = _pagination(open_total, page, per_page, LIVE_PAGE_SIZES)
    completed_pager = _pagination(completed_total, completed_page, completed_per_page, STANDARD_PAGE_SIZES)
    skipped_pager = _pagination(skipped_total, skipped_page, skipped_per_page, STANDARD_PAGE_SIZES)
    offset = (pager['page'] - 1) * per_page
    completed_offset = (completed_pager['page'] - 1) * completed_per_page
    skipped_offset = (skipped_pager['page'] - 1) * skipped_per_page

    open_rows = db.execute(
        '''
        SELECT id, question, votes, status, created_at,
               CASE WHEN attachment_path IS NOT NULL AND attachment_path!='' THEN 1 ELSE 0 END AS has_attachment
        FROM doubts
        WHERE session_id=? AND status='OPEN'
        ORDER BY votes DESC, id DESC
        LIMIT ? OFFSET ?
        ''',
        (session_id, per_page, offset),
    ).fetchall()
    completed_rows = db.execute(
        '''
        SELECT id, question, votes, status, created_at,
               CASE WHEN attachment_path IS NOT NULL AND attachment_path!='' THEN 1 ELSE 0 END AS has_attachment
        FROM doubts WHERE session_id=? AND status='COMPLETED'
        ORDER BY completed_at DESC, id DESC LIMIT ? OFFSET ?
        ''',
        (session_id, completed_per_page, completed_offset),
    ).fetchall()
    skipped_rows = db.execute(
        '''
        SELECT id, question, votes, status, created_at,
               CASE WHEN attachment_path IS NOT NULL AND attachment_path!='' THEN 1 ELSE 0 END AS has_attachment
        FROM doubts WHERE session_id=? AND status='SKIPPED'
        ORDER BY id DESC LIMIT ? OFFSET ?
        ''',
        (session_id, skipped_per_page, skipped_offset),
    ).fetchall()

    return jsonify({
        'session': {
            'id': class_session['id'],
            'name': class_session['session_name'],
            'status': class_session['status'],
            'ends_at': _iso(class_session['ends_at']),
            'duration_seconds': class_session['duration_seconds'] if 'duration_seconds' in class_session.keys() else int(class_session['duration'] or 0) * 60,
            'question_limit': class_session['question_limit'],
            'allow_student_attachment_download': bool(class_session['allow_student_attachment_download']),
        },
        'stats': {
            'total': open_total + completed_total,
            'all_records': stats['total'] or 0,
            'open': open_total,
            'completed': completed_total,
            'skipped': skipped_total,
            'votes': stats['total_votes'] or 0,
        },
        'open': [_teacher_doubt(row) for row in open_rows],
        'completed': [_teacher_doubt(row) for row in completed_rows],
        'skipped': [_teacher_doubt(row) for row in skipped_rows],
        'pagination': pager,
        'completed_pagination': completed_pager,
        'skipped_pagination': skipped_pager,
    })


@bp.post('/teacher/doubt/<int:doubt_id>/<action>')
def teacher_doubt_action(doubt_id: int, action: str):
    if not session.get('teacher_id'):
        return jsonify({'error': 'unauthorized'}), 403
    db = get_db()
    row = db.execute(
        '''SELECT d.*, s.teacher_id, s.session_name, s.created_at AS session_date
           FROM doubts d JOIN sessions s ON s.id=d.session_id WHERE d.id=?''',
        (doubt_id,),
    ).fetchone()
    if not row or row['teacher_id'] != session['teacher_id']:
        return jsonify({'error': 'unauthorized'}), 403
    if action not in {'complete', 'skip', 'reopen'}:
        return jsonify({'error': 'invalid action'}), 400
    new_status = {'complete': 'COMPLETED', 'skip': 'SKIPPED', 'reopen': 'OPEN'}[action]
    with transaction() as tx:
        tx.execute(
            "UPDATE doubts SET status=?, completed_at=CASE WHEN ?='COMPLETED' THEN CURRENT_TIMESTAMP ELSE NULL END WHERE id=?",
            (new_status, new_status, doubt_id),
        )
        if new_status == 'SKIPPED':
            tx.execute('DELETE FROM repository WHERE doubt_id=?', (doubt_id,))
        else:
            existing = tx.execute('SELECT id FROM repository WHERE doubt_id=?', (doubt_id,)).fetchone()
            if existing:
                tx.execute(
                    '''UPDATE repository SET question=?, category=?, keyword=?, total_votes=?, status=?,
                       teacher_id=?, session_id=?, session_name=?, session_date=?, updated_at=CURRENT_TIMESTAMP
                       WHERE doubt_id=?''',
                    (row['question'], row['category'], row['keyword'], row['votes'], new_status,
                     row['teacher_id'], row['session_id'], row['session_name'], row['session_date'], doubt_id),
                )
            else:
                tx.execute(
                    '''INSERT INTO repository(
                       doubt_id, question, category, keyword, total_votes, status, teacher_id,
                       session_id, session_name, session_date, updated_at
                       ) VALUES(?,?,?,?,?,?,?,?,?,?,CURRENT_TIMESTAMP)''',
                    (doubt_id, row['question'], row['category'], row['keyword'], row['votes'], new_status,
                     row['teacher_id'], row['session_id'], row['session_name'], row['session_date']),
                )
    return jsonify({'ok': True, 'status': new_status})


def _student_doubt(row, *, allow_download: bool) -> dict:
    own = row['student_id'] == session['student_id']
    has_attachment = bool(row['has_attachment'])
    return {
        'id': row['id'],
        'question': row['question'],
        'votes': row['votes'] or 0,
        'status': row['status'],
        'created_at': _iso(row['created_at']),
        'is_mine': own,
        'can_vote': not own and row['status'] == 'OPEN' and not bool(row['voted']),
        'voted': bool(row['voted']),
        'download_url': f'/student/doubt-attachment/{row["id"]}' if allow_download and has_attachment else None,
    }


@bp.get('/student/session/<int:session_id>')
def student_session_data(session_id: int):
    if not _student_in(session_id):
        return jsonify({'error': 'unauthorized'}), 403

    page, per_page = _page_args(LIVE_PAGE_SIZES, 100)
    answered_page, answered_per_page = _page_args(STANDARD_PAGE_SIZES, 10, 'answered_')
    resource_page, resource_per_page = _page_args(STANDARD_PAGE_SIZES, 10, 'resource_')
    db = get_db()
    class_session = db.execute('SELECT * FROM sessions WHERE id=?', (session_id,)).fetchone()
    if not class_session:
        return jsonify({'error': 'not found'}), 404
    if _auto_close_if_expired(class_session):
        class_session = db.execute('SELECT * FROM sessions WHERE id=?', (session_id,)).fetchone()
    if class_session['status'] != 'ACTIVE':
        return jsonify({'closed': True, 'message': 'This doubt session has ended.'})

    open_total = db.execute(
        "SELECT COUNT(*) AS c FROM doubts WHERE session_id=? AND status='OPEN'",
        (session_id,),
    ).fetchone()['c']
    pager = _pagination(open_total, page, per_page, LIVE_PAGE_SIZES)
    offset = (pager['page'] - 1) * per_page

    open_rows = db.execute(
        '''
        SELECT d.id, d.student_id, d.question, d.votes, d.status, d.created_at,
               CASE WHEN d.attachment_path IS NOT NULL AND d.attachment_path!='' THEN 1 ELSE 0 END AS has_attachment,
               EXISTS(SELECT 1 FROM doubt_votes v WHERE v.doubt_id=d.id AND (v.student_id=? OR (v.student_id IS NULL AND v.mobile=?))) AS voted
        FROM doubts d
        WHERE d.session_id=? AND d.status='OPEN'
        ORDER BY d.votes DESC, d.id DESC
        LIMIT ? OFFSET ?
        ''',
        (session['student_id'], session.get('student_mobile'), session_id, per_page, offset),
    ).fetchall()
    completed_total = db.execute(
        "SELECT COUNT(*) AS c FROM doubts WHERE session_id=? AND status='COMPLETED'",
        (session_id,),
    ).fetchone()['c']
    answered_pager = _pagination(completed_total, answered_page, answered_per_page, STANDARD_PAGE_SIZES)
    answered_offset = (answered_pager['page'] - 1) * answered_per_page
    completed_rows = db.execute(
        '''
        SELECT d.id, d.student_id, d.question, d.votes, d.status, d.created_at,
               CASE WHEN d.attachment_path IS NOT NULL AND d.attachment_path!='' THEN 1 ELSE 0 END AS has_attachment,
               EXISTS(SELECT 1 FROM doubt_votes v WHERE v.doubt_id=d.id AND (v.student_id=? OR (v.student_id IS NULL AND v.mobile=?))) AS voted
        FROM doubts d
        WHERE d.session_id=? AND d.status='COMPLETED'
        ORDER BY d.completed_at DESC, d.id DESC LIMIT ? OFFSET ?
        ''',
        (session['student_id'], session.get('student_mobile'), session_id, answered_per_page, answered_offset),
    ).fetchall()

    allow_download = bool(class_session['allow_student_attachment_download'])
    used = db.execute(
        'SELECT COUNT(*) AS c FROM doubts WHERE session_id=? AND student_id=?',
        (session_id, session['student_id']),
    ).fetchone()['c']

    resource_total = db.execute('SELECT COUNT(*) AS c FROM resources WHERE session_id=?', (session_id,)).fetchone()['c']
    resource_pager = _pagination(resource_total, resource_page, resource_per_page, STANDARD_PAGE_SIZES)
    resource_offset = (resource_pager['page'] - 1) * resource_per_page
    resources = db.execute(
        'SELECT * FROM resources WHERE session_id=? ORDER BY id DESC LIMIT ? OFFSET ?',
        (session_id, resource_per_page, resource_offset),
    ).fetchall()
    resource_data = [
        {
            'id': row['id'],
            'title': row['title'],
            'type': row['resource_type'],
            'notes': row['notes'],
            'video_url': row['video_url'],
            'download_url': f'/student/resource/{row["id"]}' if row['file_path'] or row['video_url'] else None,
        }
        for row in resources
    ]

    return jsonify({
        'closed': False,
        'session': {
            'name': class_session['session_name'],
            'ends_at': _iso(class_session['ends_at']),
            'limit': class_session['question_limit'],
            'used': used,
            'remaining': max(int(class_session['question_limit'] or 100) - used, 0),
        },
        'open': [_student_doubt(row, allow_download=allow_download) for row in open_rows],
        'completed': [_student_doubt(row, allow_download=allow_download) for row in completed_rows],
        'resources': resource_data,
        'pagination': pager,
        'answered_pagination': answered_pager,
        'resource_pagination': resource_pager,
    })


@bp.post('/student/doubt/<int:doubt_id>/vote')
def student_vote(doubt_id: int):
    if not session.get('student_id'):
        return jsonify({'error': 'unauthorized'}), 403
    db = get_db()
    row = db.execute('SELECT * FROM doubts WHERE id=?', (doubt_id,)).fetchone()
    if not row or int(row['session_id']) != int(session.get('student_session_id', 0)):
        return jsonify({'error': 'not found'}), 404
    if row['student_id'] == session['student_id']:
        return jsonify({'error': 'You cannot vote on your own question.'}), 400
    if row['status'] != 'OPEN':
        return jsonify({'error': 'Only open doubts can be voted.'}), 400
    try:
        with transaction() as tx:
            tx.execute(
                'INSERT INTO doubt_votes(doubt_id, student_id, mobile) VALUES(?,?,?)',
                (doubt_id, session['student_id'], session.get('student_mobile')),
            )
            count = tx.execute('SELECT COUNT(*) AS c FROM doubt_votes WHERE doubt_id=?', (doubt_id,)).fetchone()['c']
            tx.execute('UPDATE doubts SET votes=? WHERE id=?', (count, doubt_id))
            tx.execute('UPDATE repository SET total_votes=?, updated_at=CURRENT_TIMESTAMP WHERE doubt_id=?', (count, doubt_id))
    except Exception as exc:
        if 'UNIQUE' in str(exc).upper():
            return jsonify({'error': 'You already selected “I have the same doubt”.'}), 409
        raise
    return jsonify({'ok': True, 'votes': count})
