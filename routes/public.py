from __future__ import annotations

from flask import Blueprint, redirect, render_template, request, url_for

from db import get_db

bp = Blueprint('public', __name__)


@bp.route('/')
def home():
    return render_template('public/home.html')


@bp.route('/healthz')
def healthz():
    return {'status': 'ok'}, 200


@bp.route('/student', methods=['GET', 'POST'])
def student_start():
    error = None
    if request.method == 'POST':
        code = request.form.get('session_id', '').strip()
        if not code.isdigit():
            error = 'Enter a valid numeric session code.'
        else:
            row = get_db().execute('SELECT id, status FROM sessions WHERE id=?', (int(code),)).fetchone()
            if not row:
                error = 'Session not found. Please check the code shared by your teacher.'
            else:
                return redirect(url_for('student.join', session_id=row['id']))
    return render_template('student/start.html', error=error)
