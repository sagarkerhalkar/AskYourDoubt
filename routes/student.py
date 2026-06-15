from __future__ import annotations

from datetime import datetime
from pathlib import Path

from flask import Blueprint, current_app, flash, redirect, render_template, request, send_file, session, url_for

from auth import clear_role_session, student_required
from db import get_db, transaction
from utils import detect_category_and_keyword, save_upload, validate_mobile

bp = Blueprint('student', __name__)


def _session_row(session_id: int):
    return get_db().execute(
        '''
        SELECT s.*, t.name AS teacher_name
        FROM sessions s
        JOIN teachers t ON t.id=s.teacher_id
        WHERE s.id=?
        ''',
        (session_id,),
    ).fetchone()


def _student_can_access(session_id: int) -> bool:
    return session.get('student_id') and int(session.get('student_session_id', 0)) == int(session_id)


@bp.route('/join-session/<int:session_id>', methods=['GET', 'POST'])
def join(session_id: int):
    row = _session_row(session_id)
    if not row:
        return render_template('student/closed.html', title='Session not found', message='This doubt session is not available.'), 404
    if row['status'] != 'ACTIVE':
        session.pop('student_id', None)
        session.pop('student_session_id', None)
        return render_template(
            'student/closed.html',
            title='Session is closed',
            message='Please wait until your teacher shares an active QR code or link.',
            session_name=row['session_name'],
        )

    error = None
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        mobile = request.form.get('mobile', '').strip()
        if len(name) < 2:
            error = 'Enter your full name.'
        elif not validate_mobile(mobile):
            error = 'Mobile number must contain exactly 10 digits.'
        else:
            db = get_db()
            student = db.execute('SELECT id FROM students WHERE mobile=? ORDER BY id DESC LIMIT 1', (mobile,)).fetchone()
            with transaction() as tx:
                if student:
                    student_id = student['id']
                    tx.execute('UPDATE students SET name=? WHERE id=?', (name, student_id))
                else:
                    cur = tx.execute('INSERT INTO students(name, mobile) VALUES(?,?)', (name, mobile))
                    student_id = cur.lastrowid
                tx.execute(
                    'INSERT OR IGNORE INTO session_students(session_id, student_id) VALUES(?,?)',
                    (session_id, student_id),
                )
            clear_role_session('student')
            session.permanent = True
            session['student_id'] = student_id
            session['student_name'] = name
            session['student_mobile'] = mobile
            session['student_session_id'] = session_id
            session['student_active_tab'] = 'ask'
            return redirect(url_for('student.portal', session_id=session_id))

    return render_template('student/join.html', class_session=row, error=error)


@bp.route('/student/session/<int:session_id>')
@student_required
def portal(session_id: int):
    if not _student_can_access(session_id):
        return redirect(url_for('student.join', session_id=session_id))
    class_session = _session_row(session_id)
    if not class_session or class_session['status'] != 'ACTIVE':
        session.pop('student_id', None)
        session.pop('student_session_id', None)
        return render_template(
            'student/closed.html',
            title='This doubt session has ended',
            message='Your teacher has closed this session. Please wait for a new QR code or link.',
            session_name=class_session['session_name'] if class_session else '',
        )

    db = get_db()
    count = db.execute(
        'SELECT COUNT(*) AS c FROM doubts WHERE session_id=? AND student_id=?',
        (session_id, session['student_id']),
    ).fetchone()['c']
    resources = db.execute(
        'SELECT * FROM resources WHERE session_id=? ORDER BY id DESC',
        (session_id,),
    ).fetchall()
    active_tab = request.args.get('tab') or session.get('student_active_tab', 'ask')
    if active_tab not in {'ask', 'live', 'answered', 'resources'}:
        active_tab = 'ask'
    session['student_active_tab'] = active_tab
    return render_template(
        'student/portal.html',
        class_session=class_session,
        used=count,
        remaining=max(int(class_session['question_limit'] or 100) - count, 0),
        resources=resources,
        active_tab=active_tab,
    )


@bp.route('/student/session/<int:session_id>/focus')
@student_required
def live_focus(session_id: int):
    if not _student_can_access(session_id):
        return redirect(url_for('student.join', session_id=session_id))
    class_session = _session_row(session_id)
    if not class_session or class_session['status'] != 'ACTIVE':
        session.pop('student_id', None)
        session.pop('student_session_id', None)
        return render_template(
            'student/closed.html',
            title='This doubt session has ended',
            message='Your teacher has closed this session. Please wait for a new QR code or link.',
            session_name=class_session['session_name'] if class_session else '',
        )
    db = get_db()
    count = db.execute(
        'SELECT COUNT(*) AS c FROM doubts WHERE session_id=? AND student_id=?',
        (session_id, session['student_id']),
    ).fetchone()['c']
    session['student_active_tab'] = 'live'
    return render_template(
        'student/portal.html',
        class_session=class_session,
        used=count,
        remaining=max(int(class_session['question_limit'] or 100) - count, 0),
        resources=[],
        active_tab='live',
        immersive_mode=True,
    )


@bp.route('/student/session/<int:session_id>/tab/<tab>')
@student_required
def set_tab(session_id: int, tab: str):
    if tab in {'ask', 'live', 'answered', 'resources'}:
        session['student_active_tab'] = tab
    return redirect(url_for('student.portal', session_id=session_id, tab=tab))


@bp.route('/student/session/<int:session_id>/submit', methods=['POST'])
@student_required
def submit_doubt(session_id: int):
    if not _student_can_access(session_id):
        return redirect(url_for('student.join', session_id=session_id))
    class_session = _session_row(session_id)
    if not class_session or class_session['status'] != 'ACTIVE':
        return redirect(url_for('student.portal', session_id=session_id))

    question = request.form.get('question', '').strip()
    if not question:
        flash('Question text is compulsory.', 'error')
        session['student_active_tab'] = 'ask'
        return redirect(url_for('student.portal', session_id=session_id, tab='ask'))
    if len(question) > 50000:
        flash('Question must be below 50,000 characters.', 'error')
        return redirect(url_for('student.portal', session_id=session_id, tab='ask'))

    db = get_db()
    used = db.execute(
        'SELECT COUNT(*) AS c FROM doubts WHERE session_id=? AND student_id=?',
        (session_id, session['student_id']),
    ).fetchone()['c']
    if used >= int(class_session['question_limit'] or 100):
        flash('You have reached the question limit for this session.', 'error')
        return redirect(url_for('student.portal', session_id=session_id, tab='live'))

    attachment_path = attachment_name = attachment_type = ''
    uploaded = request.files.get('attachment')
    if uploaded and uploaded.filename:
        try:
            attachment_path, attachment_name, attachment_type = save_upload(
                uploaded, current_app.config['UPLOAD_DOUBTS'], resource=False
            )
        except ValueError as exc:
            flash(str(exc), 'error')
            return redirect(url_for('student.portal', session_id=session_id, tab='ask'))

    category, keyword = detect_category_and_keyword(question)
    with transaction() as tx:
        cur = tx.execute(
            '''
            INSERT INTO doubts(
                session_id, student_id, question, category, keyword,
                votes, status, attachment_path, attachment_name, attachment_type
            ) VALUES(?,?,?,?,?,0,'OPEN',?,?,?)
            ''',
            (
                session_id, session['student_id'], question, category, keyword,
                attachment_path, attachment_name, attachment_type,
            ),
        )
        doubt_id = cur.lastrowid
        tx.execute(
            '''
            INSERT INTO repository(
                doubt_id, question, category, keyword, total_votes, status,
                teacher_id, session_id, session_name, session_date, updated_at
            ) VALUES(?,?,?,?,0,'OPEN',?,?,?,?,CURRENT_TIMESTAMP)
            ''',
            (
                doubt_id, question, category, keyword, class_session['teacher_id'],
                session_id, class_session['session_name'], class_session['created_at'],
            ),
        )
    session['student_active_tab'] = 'live'
    if attachment_name:
        flash(f'Doubt sent successfully with attachment: {attachment_name}', 'success')
    else:
        flash('Doubt sent successfully.', 'success')
    return redirect(url_for('student.portal', session_id=session_id, tab='live'))


@bp.route('/student/resource/<int:resource_id>')
@student_required
def resource_download(resource_id: int):
    db = get_db()
    row = db.execute('SELECT * FROM resources WHERE id=?', (resource_id,)).fetchone()
    if not row or int(row['session_id']) != int(session.get('student_session_id', 0)):
        return render_template('public/error.html', code=403, title='Access denied', message='This resource is not available.'), 403
    if row['video_url']:
        return redirect(row['video_url'])
    if row['file_path'] and Path(row['file_path']).exists():
        return send_file(row['file_path'], as_attachment=True, download_name=Path(row['file_path']).name)
    return render_template('public/error.html', code=404, title='Resource missing', message='The file is not available on the server.'), 404


@bp.route('/student/doubt-attachment/<int:doubt_id>')
@student_required
def doubt_attachment(doubt_id: int):
    db = get_db()
    row = db.execute(
        '''
        SELECT d.*, s.allow_student_attachment_download
        FROM doubts d JOIN sessions s ON s.id=d.session_id
        WHERE d.id=?
        ''',
        (doubt_id,),
    ).fetchone()
    if not row or int(row['session_id']) != int(session.get('student_session_id', 0)):
        return render_template('public/error.html', code=403, title='Access denied', message='You cannot download this file.'), 403
    if not row['allow_student_attachment_download']:
        return render_template('public/error.html', code=403, title='Download disabled', message='Your teacher has not enabled student attachment downloads.'), 403
    if row['attachment_path'] and Path(row['attachment_path']).exists():
        return send_file(row['attachment_path'], as_attachment=True, download_name=row['attachment_name'])
    return render_template('public/error.html', code=404, title='File missing', message='The attachment is not available.'), 404


@bp.route('/student/logout')
def logout():
    student_session_id = session.get('student_session_id')
    clear_role_session('student')
    if student_session_id:
        return redirect(url_for('student.join', session_id=student_session_id))
    return redirect(url_for('public.student_start'))
