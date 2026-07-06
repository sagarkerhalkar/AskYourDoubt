from __future__ import annotations

import io
import os
import zipfile
from datetime import datetime, timezone
from pathlib import Path

from flask import (
    Blueprint, current_app, flash, redirect, render_template, request,
    send_file, session, url_for,
)
from werkzeug.security import generate_password_hash

from auth import clear_role_session, teacher_required
from db import get_db, transaction
from utils import (clamp_session_duration_seconds, create_qr, duration_label, parse_session_duration_hours, pagination_args, pagination_meta, rows_to_csv, save_upload, session_end_time, valid_http_url, verify_and_upgrade_password)

bp = Blueprint('teacher', __name__)


def _anonymous_attachment_name(doubt_id: int, original_name: str | None = None) -> str:
    """Return a teacher-safe download name that never exposes student-provided filenames.

    A student may upload a file named with their own name or mobile number. Teachers are allowed
    to download the resource content, but not any student identity or original filename.
    """
    suffix = Path(str(original_name or '')).suffix.lower()
    if not suffix or len(suffix) > 12 or not suffix.startswith('.'):
        suffix = '.bin'
    safe_id = int(doubt_id)
    return f"student_resource_doubt_{safe_id}{suffix}"



def _teacher_session(session_id: int):
    return get_db().execute(
        'SELECT * FROM sessions WHERE id=? AND teacher_id=?',
        (session_id, session.get('teacher_id')),
    ).fetchone()


def _log(activity: str) -> None:
    with transaction() as db:
        db.execute(
            'INSERT INTO teacher_activity(teacher_id, activity) VALUES(?,?)',
            (session.get('teacher_id'), activity),
        )


@bp.route('/teacher-login', methods=['GET', 'POST'])
def login():
    if session.get('teacher_id'):
        return redirect(url_for('teacher.dashboard'))
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        db = get_db()
        row = db.execute('SELECT * FROM teachers WHERE username=?', (username,)).fetchone()
        if not row:
            error = 'Invalid username or password.'
        elif row['status'] != 'ACTIVE':
            error = 'This teacher account is disabled. Contact the administrator.'
        else:
            valid, upgraded = verify_and_upgrade_password(row['password'], password)
            if not valid:
                error = 'Invalid username or password.'
            else:
                if upgraded:
                    with transaction() as tx:
                        tx.execute('UPDATE teachers SET password=? WHERE id=?', (upgraded, row['id']))
                clear_role_session('teacher')
                session.permanent = True
                session['teacher_id'] = row['id']
                session['teacher_name'] = row['name']
                _log('Teacher logged in')
                return redirect(url_for('teacher.dashboard'))
    return render_template('teacher/login.html', error=error)


@bp.route('/teacher-dashboard')
@teacher_required
def dashboard():
    db = get_db()
    page, per_page = pagination_args(default=10)
    total_sessions = db.execute(
        'SELECT COUNT(*) AS c FROM sessions WHERE teacher_id=?',
        (session['teacher_id'],),
    ).fetchone()['c']
    pager = pagination_meta(total_sessions, page, per_page)
    rows = db.execute(
        '''
        SELECT s.*,
               (SELECT COUNT(*) FROM doubts d WHERE d.session_id=s.id) AS doubt_count,
               (SELECT COUNT(*) FROM doubts d WHERE d.session_id=s.id AND d.status='OPEN') AS open_count
        FROM sessions s
        WHERE s.teacher_id=?
        ORDER BY s.id DESC
        LIMIT ? OFFSET ?
        ''',
        (session['teacher_id'], per_page, (pager['page'] - 1) * per_page),
    ).fetchall()
    totals = db.execute(
        '''
        SELECT COUNT(DISTINCT s.id) AS sessions,
               COUNT(d.id) AS doubts,
               SUM(CASE WHEN d.status='OPEN' THEN 1 ELSE 0 END) AS open_count,
               SUM(CASE WHEN d.status='COMPLETED' THEN 1 ELSE 0 END) AS completed_count,
               COUNT(DISTINCT CASE WHEN s.status='ACTIVE' THEN s.id END) AS active_sessions,
               COALESCE(SUM(d.votes),0) AS total_votes
        FROM sessions s LEFT JOIN doubts d ON d.session_id=s.id
        WHERE s.teacher_id=?
        ''',
        (session['teacher_id'],),
    ).fetchone()
    return render_template('teacher/dashboard.html', sessions=rows, totals=totals, pager=pager)


@bp.route('/teacher/create-session', methods=['GET', 'POST'])
@teacher_required
def create_session():
    if request.method == 'POST':
        name = request.form.get('session_name', '').strip()
        try:
            question_limit = int(request.form.get('question_limit', 100))
        except ValueError:
            question_limit = 100
        # New precise duration control: teacher can set any value from 0 seconds to 24 hours.
        # Backward compatibility: older tests/forms may post legacy duration in minutes.
        if 'duration_hours' in request.form:
            duration_seconds = parse_session_duration_hours(request.form.get('duration_hours'), default_seconds=90 * 60)
        elif 'duration_seconds' in request.form:
            duration_seconds = clamp_session_duration_seconds(request.form.get('duration_seconds'), default=90 * 60)
            duration = (duration_seconds + 59) // 60 if duration_seconds else 0
        else:
            try:
                legacy_minutes = int(request.form.get('duration', 90))
            except ValueError:
                legacy_minutes = 90
            duration = max(legacy_minutes, 0)
            duration_seconds = clamp_session_duration_seconds(duration * 60, default=90 * 60)
        duration = (duration_seconds + 59) // 60 if duration_seconds else 0
        question_limit = min(max(question_limit, 1), 10_000_000)
        if not name:
            flash('Session name is required.', 'error')
            return render_template('teacher/create_session.html')
        now = datetime.now(timezone.utc).replace(tzinfo=None).isoformat(timespec='seconds')
        ends_at = session_end_time(duration_seconds)
        with transaction() as db:
            cur = db.execute(
                '''
                INSERT INTO sessions(
                    teacher_id, session_name, duration, duration_seconds, status, created_at,
                    started_at, ends_at, question_limit
                ) VALUES(?,?,?,?,'ACTIVE',?,?,?,?)
                ''',
                (
                    session['teacher_id'], name, duration, duration_seconds, now, now, ends_at,
                    question_limit,
                ),
            )
            session_id = cur.lastrowid
        create_qr(session_id)
        _log(f"Created session '{name}' for {duration_label(duration_seconds)}")
        return redirect(url_for('teacher.live_session', session_id=session_id))
    return render_template('teacher/create_session.html')


@bp.route('/teacher/session/<int:session_id>')
@teacher_required
def live_session(session_id: int):
    class_session = _teacher_session(session_id)
    if not class_session:
        return render_template('public/error.html', code=403, title='Access denied', message='This session does not belong to you.'), 403
    join_url = f"{current_app.config['BASE_URL'].rstrip('/')}/join-session/{session_id}"
    qr_path = Path(current_app.config['QR_FOLDER']) / f'session_{session_id}.png'
    if not qr_path.exists():
        create_qr(session_id)
    return render_template('teacher/live_session.html', class_session=class_session, join_url=join_url)


@bp.route('/teacher/session/<int:session_id>/focus')
@teacher_required
def live_focus(session_id: int):
    class_session = _teacher_session(session_id)
    if not class_session:
        return render_template('public/error.html', code=403, title='Access denied', message='This session does not belong to you.'), 403
    join_url = f"{current_app.config['BASE_URL'].rstrip('/')}/join-session/{session_id}"
    qr_path = Path(current_app.config['QR_FOLDER']) / f'session_{session_id}.png'
    if not qr_path.exists():
        create_qr(session_id)
    return render_template(
        'teacher/live_session.html',
        class_session=class_session,
        join_url=join_url,
        immersive_mode=True,
    )


@bp.route('/teacher/session/<int:session_id>/qr')
@teacher_required
def full_qr(session_id: int):
    class_session = _teacher_session(session_id)
    if not class_session:
        return render_template('public/error.html', code=403, title='Access denied', message='This session does not belong to you.'), 403
    join_url = f"{current_app.config['BASE_URL'].rstrip('/')}/join-session/{session_id}"
    qr_path = Path(current_app.config['QR_FOLDER']) / f'session_{session_id}.png'
    if not qr_path.exists():
        create_qr(session_id)
    return render_template('teacher/full_qr.html', class_session=class_session, join_url=join_url)


@bp.route('/teacher/session/<int:session_id>/qr/download')
@teacher_required
def download_qr(session_id: int):
    class_session = _teacher_session(session_id)
    if not class_session:
        return render_template('public/error.html', code=403, title='Access denied', message='This session does not belong to you.'), 403
    qr_path = Path(current_app.config['QR_FOLDER']) / f'session_{session_id}.png'
    if not qr_path.exists():
        create_qr(session_id)
    safe_name = ''.join(ch if ch.isalnum() or ch in ('-', '_') else '_' for ch in class_session['session_name']).strip('_')
    download_name = f"{safe_name or f'session_{session_id}'}_student_QR.png"
    return send_file(qr_path, as_attachment=True, download_name=download_name, mimetype='image/png')


@bp.route('/teacher/session/<int:session_id>/close', methods=['POST'])
@teacher_required
def close_session(session_id: int):
    class_session = _teacher_session(session_id)
    if not class_session:
        return ('Access denied', 403)
    with transaction() as db:
        db.execute("UPDATE sessions SET status='CLOSED', closed_at=CURRENT_TIMESTAMP WHERE id=?", (session_id,))
    _log(f"Closed session '{class_session['session_name']}'")
    return redirect(url_for('teacher.live_session', session_id=session_id))


@bp.route('/teacher/session/<int:session_id>/reopen', methods=['POST'])
@teacher_required
def reopen_session(session_id: int):
    class_session = _teacher_session(session_id)
    if not class_session:
        return ('Access denied', 403)
    ends_at = session_end_time(class_session['duration_seconds'] if 'duration_seconds' in class_session.keys() else int(class_session['duration'] or 90) * 60)
    with transaction() as db:
        db.execute(
            "UPDATE sessions SET status='ACTIVE', started_at=CURRENT_TIMESTAMP, ends_at=?, closed_at=NULL WHERE id=?",
            (ends_at, session_id),
        )
    create_qr(session_id)
    _log(f"Reopened session '{class_session['session_name']}'")
    return redirect(url_for('teacher.live_session', session_id=session_id))


@bp.route('/teacher/session/<int:session_id>/settings', methods=['POST'])
@teacher_required
def session_settings(session_id: int):
    class_session = _teacher_session(session_id)
    if not class_session:
        return ('Access denied', 403)
    try:
        limit = min(max(int(request.form.get('question_limit', 100)), 1), 10_000_000)
    except ValueError:
        limit = 100
    duration_seconds = None
    if 'duration_hours' in request.form:
        duration_seconds = parse_session_duration_hours(request.form.get('duration_hours'), default_seconds=(class_session['duration_seconds'] if 'duration_seconds' in class_session.keys() and class_session['duration_seconds'] is not None else int(class_session['duration'] or 90) * 60))
    elif 'duration_seconds' in request.form:
        duration_seconds = clamp_session_duration_seconds(request.form.get('duration_seconds'), default=(class_session['duration_seconds'] if 'duration_seconds' in class_session.keys() and class_session['duration_seconds'] is not None else int(class_session['duration'] or 90) * 60))
    allow = 1 if request.form.get('allow_student_attachment_download') == 'on' else 0
    with transaction() as db:
        if duration_seconds is None:
            db.execute(
                'UPDATE sessions SET question_limit=?, allow_student_attachment_download=? WHERE id=?',
                (limit, allow, session_id),
            )
        else:
            duration_minutes_legacy = (duration_seconds + 59) // 60 if duration_seconds else 0
            db.execute(
                'UPDATE sessions SET question_limit=?, duration=?, duration_seconds=?, ends_at=?, allow_student_attachment_download=? WHERE id=?',
                (limit, duration_minutes_legacy, duration_seconds, session_end_time(duration_seconds), allow, session_id),
            )
    flash('Doubt control settings updated.', 'success')
    return redirect(url_for('teacher.live_session', session_id=session_id))


@bp.route('/teacher/session/<int:session_id>/resources', methods=['GET', 'POST'])
@teacher_required
def resources(session_id: int):
    class_session = _teacher_session(session_id)
    if not class_session:
        return render_template('public/error.html', code=403, title='Access denied', message='This session does not belong to you.'), 403
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        resource_type = request.form.get('resource_type', '').upper()
        notes = request.form.get('notes', '').strip()
        video_url = request.form.get('video_url', '').strip()
        file_path = ''
        uploaded = request.files.get('file')
        if uploaded and uploaded.filename:
            try:
                file_path, _, file_type = save_upload(uploaded, current_app.config['UPLOAD_RESOURCES'], resource=True)
                resource_type = file_type
            except ValueError as exc:
                flash(str(exc), 'error')
                return redirect(url_for('teacher.resources', session_id=session_id))
        if not title:
            flash('Resource title is required.', 'error')
        elif not any([file_path, video_url, notes]):
            flash('Add a file, video link, or note.', 'error')
        elif video_url and not valid_http_url(video_url):
            flash('Video link must start with http:// or https://.', 'error')
        else:
            if video_url:
                resource_type = 'VIDEO'
            elif notes and not file_path:
                resource_type = 'NOTE'
            with transaction() as db:
                db.execute(
                    '''INSERT INTO resources(session_id,title,resource_type,file_path,video_url,notes)
                       VALUES(?,?,?,?,?,?)''',
                    (session_id, title, resource_type, file_path, video_url, notes),
                )
            flash('Resource shared with students.', 'success')
            _log(f"Shared a resource in '{class_session['session_name']}'")
        return redirect(url_for('teacher.resources', session_id=session_id))
    page, per_page = pagination_args(default=10)
    db = get_db()
    total = db.execute('SELECT COUNT(*) AS c FROM resources WHERE session_id=?', (session_id,)).fetchone()['c']
    pager = pagination_meta(total, page, per_page)
    rows = db.execute(
        'SELECT * FROM resources WHERE session_id=? ORDER BY id DESC LIMIT ? OFFSET ?',
        (session_id, per_page, (pager['page'] - 1) * per_page),
    ).fetchall()
    return render_template('teacher/resources.html', class_session=class_session, resources=rows, pager=pager)


@bp.route('/teacher/resource/<int:resource_id>/open')
@teacher_required
def open_resource(resource_id: int):
    row = get_db().execute(
        '''SELECT r.*, s.teacher_id FROM resources r JOIN sessions s ON s.id=r.session_id WHERE r.id=?''',
        (resource_id,),
    ).fetchone()
    if not row or row['teacher_id'] != session['teacher_id']:
        return ('Access denied', 403)
    if row['video_url']:
        return redirect(row['video_url'])
    if row['file_path'] and Path(row['file_path']).exists():
        return send_file(row['file_path'], as_attachment=False)
    return render_template('public/error.html', code=404, title='Resource missing', message='The resource is not available.'), 404


@bp.route('/teacher/questions.csv')
@teacher_required
def all_questions_csv():
    rows = get_db().execute(
        '''SELECT s.session_name, d.question, d.category, d.keyword, d.votes, d.status, d.created_at
           FROM doubts d JOIN sessions s ON s.id=d.session_id
           WHERE s.teacher_id=? ORDER BY s.id DESC, d.votes DESC, d.id DESC''',
        (session['teacher_id'],),
    ).fetchall()
    csv_file = rows_to_csv(
        ['Session','Question','Category','Keyword','Votes','Status','Created At'],
        ([r['session_name'],r['question'],r['category'],r['keyword'],r['votes'],r['status'],r['created_at']] for r in rows),
    )
    return send_file(csv_file, as_attachment=True, download_name='teacher_all_session_questions.csv', mimetype='text/csv')


@bp.route('/teacher/resource/<int:resource_id>/delete', methods=['POST'])
@teacher_required
def delete_resource(resource_id: int):
    db = get_db()
    row = db.execute(
        '''SELECT r.*, s.teacher_id FROM resources r JOIN sessions s ON s.id=r.session_id WHERE r.id=?''',
        (resource_id,),
    ).fetchone()
    if not row or row['teacher_id'] != session['teacher_id']:
        return ('Access denied', 403)
    if row['file_path']:
        try:
            Path(row['file_path']).unlink(missing_ok=True)
        except OSError:
            pass
    with transaction() as tx:
        tx.execute('DELETE FROM resources WHERE id=?', (resource_id,))
    return redirect(url_for('teacher.resources', session_id=row['session_id']))


@bp.route('/teacher/doubt/<int:doubt_id>/attachment')
@teacher_required
def doubt_attachment(doubt_id: int):
    row = get_db().execute(
        '''
        SELECT d.attachment_path, d.attachment_name, s.teacher_id
        FROM doubts d JOIN sessions s ON s.id=d.session_id WHERE d.id=?
        ''',
        (doubt_id,),
    ).fetchone()
    if not row or row['teacher_id'] != session['teacher_id']:
        return ('Access denied', 403)
    if row['attachment_path'] and Path(row['attachment_path']).exists():
        return send_file(row['attachment_path'], as_attachment=True, download_name=_anonymous_attachment_name(doubt_id, row['attachment_name']))
    return render_template('public/error.html', code=404, title='Attachment missing', message='The attachment is not available.'), 404


@bp.route('/teacher/session/<int:session_id>/attachments.zip')
@teacher_required
def attachment_zip(session_id: int):
    class_session = _teacher_session(session_id)
    if not class_session:
        return ('Access denied', 403)
    rows = get_db().execute(
        "SELECT id, attachment_path, attachment_name FROM doubts WHERE session_id=? AND attachment_path!=''",
        (session_id,),
    ).fetchall()
    memory = io.BytesIO()
    added = 0
    with zipfile.ZipFile(memory, 'w', zipfile.ZIP_DEFLATED) as archive:
        for row in rows:
            if row['attachment_path'] and Path(row['attachment_path']).exists():
                archive.write(row['attachment_path'], arcname=_anonymous_attachment_name(row['id'], row['attachment_name']))
                added += 1
    if not added:
        flash('No student attachments are available.', 'error')
        return redirect(url_for('teacher.live_session', session_id=session_id))
    memory.seek(0)
    return send_file(memory, as_attachment=True, download_name=f"session_{session_id}_attachments.zip", mimetype='application/zip')


@bp.route('/teacher/session/<int:session_id>/questions.csv')
@teacher_required
def session_questions_csv(session_id: int):
    class_session = _teacher_session(session_id)
    if not class_session:
        return ('Access denied', 403)

    export_filter = request.args.get('filter', 'ALL').upper().strip()
    if export_filter not in {'ALL', 'OPEN', 'COMPLETED', 'SKIPPED'}:
        export_filter = 'ALL'

    sql = '''SELECT question, category, keyword, votes, status, created_at FROM doubts
             WHERE session_id=?'''
    params: list[object] = [session_id]
    if export_filter == 'ALL':
        sql += " AND status IN ('OPEN','COMPLETED')"
    else:
        sql += ' AND status=?'
        params.append(export_filter)
    sql += ' ORDER BY votes DESC, id DESC'
    rows = get_db().execute(sql, tuple(params)).fetchall()

    csv_file = rows_to_csv(
        ['Question', 'Category', 'Keyword', 'Votes', 'Status', 'Created At'],
        ([r['question'], r['category'], r['keyword'], r['votes'], r['status'], r['created_at']] for r in rows),
    )
    label = {'ALL': 'total_open_completed', 'OPEN': 'open', 'COMPLETED': 'completed', 'SKIPPED': 'skipped'}[export_filter]
    safe_session = ''.join(ch if ch.isalnum() or ch in {'-', '_'} else '_' for ch in class_session['session_name']).strip('_') or f'session_{session_id}'
    return send_file(
        csv_file,
        as_attachment=True,
        download_name=f"{safe_session}_{label}_questions.csv",
        mimetype='text/csv',
    )


@bp.route('/teacher/question-bank')
@teacher_required
def question_bank():
    db = get_db()
    status = request.args.get('status', 'ALL').upper().strip()
    if status not in {'ALL', 'OPEN', 'COMPLETED'}:
        status = 'ALL'

    requested_session_id = request.args.get('session_id', '').strip()
    selected_session_id = int(requested_session_id) if requested_session_id.isdigit() else None
    selected_session = None
    if selected_session_id is not None:
        selected_session = db.execute(
            'SELECT id, session_name, created_at, status FROM sessions WHERE id=? AND teacher_id=?',
            (selected_session_id, session['teacher_id']),
        ).fetchone()
        if selected_session is None:
            selected_session_id = None

    page, per_page = pagination_args(default=10)
    params = [session['teacher_id']]
    where_sql = ' WHERE teacher_id=?'
    if selected_session_id is not None:
        where_sql += ' AND session_id=?'
        params.append(selected_session_id)
    if status in {'OPEN', 'COMPLETED'}:
        where_sql += ' AND status=?'
        params.append(status)

    total = db.execute('SELECT COUNT(*) AS c FROM repository' + where_sql, params).fetchone()['c']
    pager = pagination_meta(total, page, per_page)
    rows = db.execute(
        'SELECT * FROM repository' + where_sql + ' ORDER BY updated_at DESC, id DESC LIMIT ? OFFSET ?',
        [*params, per_page, (pager['page'] - 1) * per_page],
    ).fetchall()
    sessions = db.execute(
        '''SELECT s.id, s.session_name, s.created_at, s.status,
                  COUNT(r.id) AS question_count
           FROM sessions s
           LEFT JOIN repository r ON r.session_id=s.id AND r.teacher_id=s.teacher_id
           WHERE s.teacher_id=?
           GROUP BY s.id
           ORDER BY s.id DESC''',
        (session['teacher_id'],),
    ).fetchall()
    return render_template(
        'teacher/question_bank.html',
        questions=rows,
        sessions=sessions,
        selected_status=status,
        selected_session_id=selected_session_id,
        selected_session=selected_session,
        pager=pager,
    )


@bp.route('/teacher/question-bank.csv')
@teacher_required
def question_bank_csv():
    session_id = request.args.get('session_id', '').strip()
    status = request.args.get('status', '').upper().strip()
    db = get_db()
    params = [session['teacher_id']]
    sql = 'SELECT question, category, keyword, total_votes, status, session_name, session_date FROM repository WHERE teacher_id=?'
    if session_id.isdigit():
        owned = db.execute(
            'SELECT 1 FROM sessions WHERE id=? AND teacher_id=?',
            (int(session_id), session['teacher_id']),
        ).fetchone()
        if owned:
            sql += ' AND session_id=?'
            params.append(int(session_id))
    if status in {'OPEN', 'COMPLETED'}:
        sql += ' AND status=?'
        params.append(status)
    sql += ' ORDER BY id DESC'
    rows = db.execute(sql, params).fetchall()
    csv_file = rows_to_csv(
        ['Question', 'Category', 'Keyword', 'Votes', 'Status', 'Session', 'Session Date'],
        ([r['question'], r['category'], r['keyword'], r['total_votes'], r['status'], r['session_name'], r['session_date']] for r in rows),
    )
    return send_file(csv_file, as_attachment=True, download_name='teacher_question_bank.csv', mimetype='text/csv')


@bp.route('/teacher/analytics')
@teacher_required
def analytics():
    db = get_db()
    categories = db.execute(
        '''SELECT d.category AS label, COUNT(*) AS value FROM doubts d
           JOIN sessions s ON s.id=d.session_id WHERE s.teacher_id=?
           GROUP BY d.category ORDER BY value DESC LIMIT 12''',
        (session['teacher_id'],),
    ).fetchall()
    keywords = db.execute(
        '''SELECT d.keyword AS label, COUNT(*) AS value FROM doubts d
           JOIN sessions s ON s.id=d.session_id WHERE s.teacher_id=?
           GROUP BY d.keyword ORDER BY value DESC LIMIT 12''',
        (session['teacher_id'],),
    ).fetchall()
    session_rows = db.execute(
        '''SELECT s.session_name AS label, COUNT(d.id) AS value FROM sessions s
           LEFT JOIN doubts d ON d.session_id=s.id WHERE s.teacher_id=?
           GROUP BY s.id ORDER BY s.id DESC LIMIT 12''',
        (session['teacher_id'],),
    ).fetchall()
    return render_template('teacher/analytics.html', categories=categories, keywords=keywords, session_rows=session_rows)


@bp.route('/teacher/change-password', methods=['GET', 'POST'])
@teacher_required
def change_password():
    error = None
    if request.method == 'POST':
        current = request.form.get('current_password', '')
        new = request.form.get('new_password', '')
        confirm = request.form.get('confirm_password', '')
        row = get_db().execute('SELECT password FROM teachers WHERE id=?', (session['teacher_id'],)).fetchone()
        valid, _ = verify_and_upgrade_password(row['password'], current)
        if not valid:
            error = 'Current password is incorrect.'
        elif len(new) < 8:
            error = 'New password must contain at least 8 characters.'
        elif new != confirm:
            error = 'New passwords do not match.'
        else:
            with transaction() as db:
                db.execute('UPDATE teachers SET password=? WHERE id=?', (generate_password_hash(new), session['teacher_id']))
            flash('Password changed successfully.', 'success')
            return redirect(url_for('teacher.dashboard'))
    return render_template('teacher/change_password.html', error=error)


@bp.route('/teacher-logout')
def logout():
    clear_role_session('teacher')
    return redirect(url_for('teacher.login'))
