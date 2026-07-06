from __future__ import annotations

from pathlib import Path

from flask import Blueprint, current_app, flash, redirect, render_template, request, send_file, session, url_for
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename

from auth import admin_required, clear_role_session
from db import get_db, transaction
from utils import duration_label, pagination_args, pagination_meta, rows_to_csv, session_end_time, verify_and_upgrade_password, validate_mobile

bp = Blueprint('admin', __name__)


@bp.route('/admin-login', methods=['GET', 'POST'])
def login():
    if session.get('admin_id'):
        return redirect(url_for('admin.dashboard'))
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        db = get_db()
        row = db.execute('SELECT * FROM admins WHERE username=?', (username,)).fetchone()
        if not row or row['status'] != 'ACTIVE':
            error = 'Invalid username or password.'
        else:
            valid, upgraded = verify_and_upgrade_password(row['password'], password)
            if not valid:
                error = 'Invalid username or password.'
            else:
                if upgraded:
                    with transaction() as tx:
                        tx.execute('UPDATE admins SET password=? WHERE id=?', (upgraded, row['id']))
                clear_role_session('admin')
                session.permanent = True
                session['admin_id'] = row['id']
                session['admin_name'] = row['display_name'] or row['username']
                return redirect(url_for('admin.dashboard'))
    return render_template('admin/login.html', error=error)


@bp.route('/admin-dashboard')
@admin_required
def dashboard():
    db = get_db()
    totals = db.execute(
        '''
        SELECT
          (SELECT COUNT(*) FROM teachers WHERE status!='DELETED') AS teachers,
          (SELECT COUNT(*) FROM sessions) AS sessions,
          (SELECT COUNT(*) FROM students) AS students,
          (SELECT COUNT(*) FROM doubts) AS doubts,
          (SELECT COUNT(*) FROM doubts WHERE status='OPEN') AS open_count,
          (SELECT COUNT(*) FROM doubts WHERE status='COMPLETED') AS completed_count,
          (SELECT COUNT(*) FROM doubts WHERE status='SKIPPED') AS skipped_count
        '''
    ).fetchone()
    live_sessions = db.execute(
        '''SELECT s.id, s.session_name, s.status, s.created_at, t.name AS teacher_name,
                  (SELECT COUNT(*) FROM doubts d WHERE d.session_id=s.id) AS doubts
           FROM sessions s JOIN teachers t ON t.id=s.teacher_id
           ORDER BY CASE s.status WHEN 'ACTIVE' THEN 0 ELSE 1 END, s.id DESC LIMIT 5'''
    ).fetchall()
    activity = db.execute(
        '''SELECT a.activity, a.created_at, t.name FROM teacher_activity a
           LEFT JOIN teachers t ON t.id=a.teacher_id ORDER BY a.id DESC LIMIT 5'''
    ).fetchall()
    categories = db.execute('SELECT category AS label, COUNT(*) AS value FROM doubts GROUP BY category ORDER BY value DESC LIMIT 10').fetchall()
    keywords = db.execute('SELECT keyword AS label, COUNT(*) AS value FROM doubts GROUP BY keyword ORDER BY value DESC LIMIT 10').fetchall()
    return render_template('admin/dashboard.html', totals=totals, live_sessions=live_sessions, activity=activity, categories=categories, keywords=keywords)


@bp.route('/admin/activity')
@admin_required
def activity_page():
    page, per_page = pagination_args(default=10)
    db = get_db()
    total = db.execute('SELECT COUNT(*) AS c FROM teacher_activity').fetchone()['c']
    pager = pagination_meta(total, page, per_page)
    rows = db.execute(
        '''SELECT a.activity, a.created_at, t.name
           FROM teacher_activity a LEFT JOIN teachers t ON t.id=a.teacher_id
           ORDER BY a.id DESC LIMIT ? OFFSET ?''',
        (per_page, (pager['page'] - 1) * per_page),
    ).fetchall()
    return render_template('admin/activity.html', activity=rows, pager=pager)


@bp.route('/admin/teachers', methods=['GET', 'POST'])
@admin_required
def teachers():
    error = None
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        mobile = request.form.get('mobile', '').strip()
        email = request.form.get('email', '').strip()
        dob = request.form.get('dob', '').strip()
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        if not name or not username:
            error = 'Teacher name and username are required.'
        elif not validate_mobile(mobile):
            error = 'Teacher mobile number must contain exactly 10 digits.'
        elif len(password) < 8:
            error = 'Password must contain at least 8 characters.'
        else:
            try:
                with transaction() as db:
                    db.execute(
                        '''INSERT INTO teachers(name,mobile,email,dob,username,password,status)
                           VALUES(?,?,?,?,?,?,'ACTIVE')''',
                        (name, mobile, email, dob, username, generate_password_hash(password)),
                    )
                flash('Teacher account created.', 'success')
                return redirect(url_for('admin.teachers'))
            except Exception as exc:
                error = 'Username already exists.' if 'UNIQUE' in str(exc).upper() else str(exc)
    page, per_page = pagination_args(default=10)
    db = get_db()
    total = db.execute("SELECT COUNT(*) AS c FROM teachers WHERE status!='DELETED'").fetchone()['c']
    pager = pagination_meta(total, page, per_page)
    rows = db.execute(
        '''SELECT t.*,
                  (SELECT COUNT(*) FROM sessions s WHERE s.teacher_id=t.id) AS session_count,
                  (SELECT COUNT(*) FROM doubts d JOIN sessions s ON s.id=d.session_id WHERE s.teacher_id=t.id) AS doubt_count
           FROM teachers t WHERE t.status!='DELETED' ORDER BY t.id DESC LIMIT ? OFFSET ?''',
        (per_page, (pager['page'] - 1) * per_page),
    ).fetchall()
    return render_template('admin/teachers.html', teachers=rows, error=error, pager=pager)


@bp.route('/admin/teacher/<int:teacher_id>/status', methods=['POST'])
@admin_required
def teacher_status(teacher_id: int):
    action = request.form.get('action')
    status = {'enable': 'ACTIVE', 'disable': 'DISABLED', 'delete': 'DELETED'}.get(action)
    if not status:
        return ('Invalid action', 400)
    with transaction() as db:
        db.execute('UPDATE teachers SET status=? WHERE id=?', (status, teacher_id))
    return redirect(url_for('admin.teachers'))


@bp.route('/admin/teacher/<int:teacher_id>/reset-password', methods=['GET', 'POST'])
@admin_required
def reset_teacher_password(teacher_id: int):
    row = get_db().execute('SELECT id,name,username FROM teachers WHERE id=?', (teacher_id,)).fetchone()
    if not row:
        return render_template('public/error.html', code=404, title='Teacher not found', message='The teacher account does not exist.'), 404
    error = None
    if request.method == 'POST':
        new = request.form.get('new_password', '')
        confirm = request.form.get('confirm_password', '')
        if len(new) < 8:
            error = 'Password must contain at least 8 characters.'
        elif new != confirm:
            error = 'Passwords do not match.'
        else:
            with transaction() as db:
                db.execute('UPDATE teachers SET password=? WHERE id=?', (generate_password_hash(new), teacher_id))
            flash('Teacher password reset successfully.', 'success')
            return redirect(url_for('admin.teachers'))
    return render_template('admin/reset_teacher_password.html', teacher=row, error=error)


@bp.route('/admin/admins', methods=['GET', 'POST'])
@admin_required
def admins():
    error = None
    if request.method == 'POST':
        display_name = request.form.get('display_name', '').strip()
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        if not display_name or not username:
            error = 'Name and username are required.'
        elif len(password) < 8:
            error = 'Password must contain at least 8 characters.'
        else:
            try:
                with transaction() as db:
                    db.execute(
                        'INSERT INTO admins(username,password,display_name,status) VALUES(?,?,?,\'ACTIVE\')',
                        (username, generate_password_hash(password), display_name),
                    )
                flash('Second admin created.', 'success')
                return redirect(url_for('admin.admins'))
            except Exception:
                error = 'Admin username already exists.'
    page, per_page = pagination_args(default=10)
    db = get_db()
    total = db.execute('SELECT COUNT(*) AS c FROM admins').fetchone()['c']
    pager = pagination_meta(total, page, per_page)
    rows = db.execute(
        'SELECT id,username,display_name,status,created_at FROM admins ORDER BY id LIMIT ? OFFSET ?',
        (per_page, (pager['page'] - 1) * per_page),
    ).fetchall()
    return render_template('admin/admins.html', admins=rows, error=error, pager=pager)


@bp.route('/admin/change-password', methods=['GET', 'POST'])
@admin_required
def change_password():
    error = None
    if request.method == 'POST':
        current = request.form.get('current_password', '')
        new = request.form.get('new_password', '')
        confirm = request.form.get('confirm_password', '')
        row = get_db().execute('SELECT password FROM admins WHERE id=?', (session['admin_id'],)).fetchone()
        valid, _ = verify_and_upgrade_password(row['password'], current)
        if not valid:
            error = 'Current password is incorrect.'
        elif len(new) < 8:
            error = 'New password must contain at least 8 characters.'
        elif new != confirm:
            error = 'Passwords do not match.'
        else:
            with transaction() as db:
                db.execute('UPDATE admins SET password=? WHERE id=?', (generate_password_hash(new), session['admin_id']))
            flash('Admin password changed.', 'success')
            return redirect(url_for('admin.dashboard'))
    return render_template('admin/change_password.html', error=error)


@bp.route('/admin/sessions')
@admin_required
def sessions_page():
    page, per_page = pagination_args(default=10)
    db = get_db()
    total = db.execute('SELECT COUNT(*) AS c FROM sessions').fetchone()['c']
    pager = pagination_meta(total, page, per_page)
    rows = db.execute(
        '''SELECT s.*, t.name AS teacher_name,
                  (SELECT COUNT(*) FROM doubts d WHERE d.session_id=s.id) AS doubt_count,
                  (SELECT COUNT(*) FROM doubts d WHERE d.session_id=s.id AND d.status='SKIPPED') AS skipped_count
           FROM sessions s JOIN teachers t ON t.id=s.teacher_id
           ORDER BY s.id DESC LIMIT ? OFFSET ?''',
        (per_page, (pager['page'] - 1) * per_page),
    ).fetchall()
    return render_template('admin/sessions.html', sessions=rows, pager=pager)


@bp.route('/admin/session/<int:session_id>/status', methods=['POST'])
@admin_required
def session_status(session_id: int):
    action = request.form.get('action')
    if action == 'close':
        with transaction() as db:
            db.execute("UPDATE sessions SET status='CLOSED', closed_at=CURRENT_TIMESTAMP WHERE id=?", (session_id,))
    elif action == 'reopen':
        db = get_db()
        row = db.execute('SELECT duration, duration_seconds FROM sessions WHERE id=?', (session_id,)).fetchone()
        seconds = row['duration_seconds'] if row and 'duration_seconds' in row.keys() and row['duration_seconds'] is not None else int(row['duration'] or 90) * 60
        with transaction() as tx:
            tx.execute("UPDATE sessions SET status='ACTIVE', started_at=CURRENT_TIMESTAMP, ends_at=?, closed_at=NULL WHERE id=?", (session_end_time(seconds), session_id))
    return redirect(url_for('admin.sessions_page'))


@bp.route('/admin/students')
@admin_required
def students():
    page, per_page = pagination_args(default=10)
    db = get_db()
    total = db.execute('SELECT COUNT(*) AS c FROM students').fetchone()['c']
    pager = pagination_meta(total, page, per_page)
    rows = db.execute(
        '''SELECT st.*, COUNT(DISTINCT ss.session_id) AS sessions_joined, COUNT(DISTINCT d.id) AS doubts
           FROM students st LEFT JOIN session_students ss ON ss.student_id=st.id
           LEFT JOIN doubts d ON d.student_id=st.id GROUP BY st.id
           ORDER BY st.id DESC LIMIT ? OFFSET ?''',
        (per_page, (pager['page'] - 1) * per_page),
    ).fetchall()
    return render_template('admin/students.html', students=rows, pager=pager)


@bp.route('/admin/questions')
@admin_required
def questions():
    page, per_page = pagination_args(default=10)
    db = get_db()
    total = db.execute('SELECT COUNT(*) AS c FROM doubts').fetchone()['c']
    pager = pagination_meta(total, page, per_page)
    rows = db.execute(
        '''SELECT d.*, s.session_name, t.name AS teacher_name, st.name AS student_name, st.mobile
           FROM doubts d JOIN sessions s ON s.id=d.session_id JOIN teachers t ON t.id=s.teacher_id
           JOIN students st ON st.id=d.student_id ORDER BY d.id DESC LIMIT ? OFFSET ?''',
        (per_page, (pager['page'] - 1) * per_page),
    ).fetchall()
    return render_template('admin/questions.html', questions=rows, pager=pager)


@bp.route('/admin/analytics')
@admin_required
def analytics():
    db = get_db()
    categories = db.execute('SELECT category AS label, COUNT(*) AS value FROM doubts GROUP BY category ORDER BY value DESC').fetchall()
    keywords = db.execute('SELECT keyword AS label, COUNT(*) AS value FROM doubts GROUP BY keyword ORDER BY value DESC LIMIT 30').fetchall()
    teachers = db.execute(
        '''SELECT t.name AS label, COUNT(d.id) AS value FROM teachers t LEFT JOIN sessions s ON s.teacher_id=t.id
           LEFT JOIN doubts d ON d.session_id=s.id GROUP BY t.id ORDER BY value DESC'''
    ).fetchall()
    statuses = db.execute('SELECT status AS label, COUNT(*) AS value FROM doubts GROUP BY status').fetchall()
    return render_template('admin/analytics.html', categories=categories, keywords=keywords, teachers=teachers, statuses=statuses)


@bp.route('/admin/export/<kind>.csv')
@admin_required
def export_csv(kind: str):
    db = get_db()
    if kind == 'questions':
        rows = db.execute(
            '''SELECT t.name,s.session_name,d.question,d.category,d.keyword,d.votes,d.status,d.created_at
               FROM doubts d JOIN sessions s ON s.id=d.session_id JOIN teachers t ON t.id=s.teacher_id ORDER BY d.id DESC'''
        ).fetchall()
        headers = ['Teacher','Session','Question','Category','Keyword','Votes','Status','Created At']
        iterable = ([r['name'],r['session_name'],r['question'],r['category'],r['keyword'],r['votes'],r['status'],r['created_at']] for r in rows)
    elif kind == 'students':
        rows = db.execute('SELECT name,mobile,created_at FROM students ORDER BY id DESC').fetchall()
        headers = ['Name','Mobile','Created At']
        iterable = ([r['name'],r['mobile'],r['created_at']] for r in rows)
    elif kind == 'sessions':
        rows = db.execute(
            '''SELECT t.name,s.id,s.session_name,s.status,s.duration,s.duration_seconds,s.question_limit,s.created_at
               FROM sessions s JOIN teachers t ON t.id=s.teacher_id ORDER BY s.id DESC'''
        ).fetchall()
        headers = ['Teacher','Session ID','Session','Status','Duration','Question Limit','Created At']
        iterable = ([r['name'],r['id'],r['session_name'],r['status'],duration_label(r['duration_seconds'] if 'duration_seconds' in r.keys() and r['duration_seconds'] is not None else int(r['duration'] or 90) * 60),r['question_limit'],r['created_at']] for r in rows)
    else:
        return ('Unknown export', 404)
    file = rows_to_csv(headers, iterable)
    return send_file(file, as_attachment=True, download_name=f'admin_{kind}.csv', mimetype='text/csv')


@bp.route('/brand-settings', methods=['GET', 'POST'])
@admin_required
def brand_settings():
    error = None
    if request.method == 'POST':
        upload = request.files.get('logo')
        if not upload or not upload.filename:
            error = 'Choose a logo file.'
        else:
            ext = upload.filename.rsplit('.', 1)[-1].lower() if '.' in upload.filename else ''
            if ext not in {'png','jpg','jpeg','webp','svg'}:
                error = 'Use PNG, JPG, WEBP, or SVG.'
            else:
                filename = f'logo.{ext}'
                folder = Path(current_app.root_path) / 'static' / 'brand'
                folder.mkdir(parents=True, exist_ok=True)
                upload.save(folder / filename)
                logo_path = f'/static/brand/{filename}'
                with transaction() as db:
                    db.execute(
                        '''INSERT INTO app_settings(setting_key,setting_value,updated_at)
                           VALUES('logo_path',?,CURRENT_TIMESTAMP)
                           ON CONFLICT(setting_key) DO UPDATE SET setting_value=excluded.setting_value, updated_at=CURRENT_TIMESTAMP''',
                        (logo_path,),
                    )
                flash('High-resolution logo updated.', 'success')
                return redirect(url_for('admin.brand_settings'))
    return render_template('admin/brand_settings.html', error=error)


@bp.route('/admin-logout')
def logout():
    clear_role_session('admin')
    return redirect(url_for('admin.login'))

@bp.route('/admin/teacher/<int:teacher_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_teacher(teacher_id: int):
    db = get_db()
    teacher = db.execute('SELECT * FROM teachers WHERE id=? AND status!=\'DELETED\'', (teacher_id,)).fetchone()
    if not teacher:
        return render_template('public/error.html', code=404, title='Teacher not found', message='The teacher account does not exist.'), 404
    error = None
    if request.method == 'POST':
        name = request.form.get('name','').strip()
        mobile = request.form.get('mobile','').strip()
        email = request.form.get('email','').strip()
        dob = request.form.get('dob','').strip()
        username = request.form.get('username','').strip()
        if not name or not username:
            error = 'Name and username are required.'
        elif not validate_mobile(mobile):
            error = 'Mobile number must contain exactly 10 digits.'
        else:
            try:
                with transaction() as tx:
                    tx.execute('UPDATE teachers SET name=?,mobile=?,email=?,dob=?,username=? WHERE id=?', (name,mobile,email,dob,username,teacher_id))
                flash('Teacher profile updated.', 'success')
                return redirect(url_for('admin.teachers'))
            except Exception as exc:
                error = 'Username already exists.' if 'UNIQUE' in str(exc).upper() else str(exc)
    return render_template('admin/edit_teacher.html', teacher=teacher, error=error)


@bp.route('/admin/question-bank')
@admin_required
def question_bank():
    db = get_db()
    teacher_id = request.args.get('teacher_id','')
    session_id = request.args.get('session_id','')
    status = request.args.get('status','ALL')
    page, per_page = pagination_args(default=10)
    where_sql = ' WHERE 1=1'
    params = []
    if teacher_id.isdigit():
        where_sql += ' AND r.teacher_id=?'; params.append(int(teacher_id))
    if session_id.isdigit():
        where_sql += ' AND r.session_id=?'; params.append(int(session_id))
    if status in {'OPEN','COMPLETED'}:
        where_sql += ' AND r.status=?'; params.append(status)
    total = db.execute('SELECT COUNT(*) AS c FROM repository r' + where_sql, params).fetchone()['c']
    pager = pagination_meta(total, page, per_page)
    rows = db.execute(
        '''SELECT r.*, t.name AS teacher_name FROM repository r
           LEFT JOIN teachers t ON t.id=r.teacher_id''' + where_sql +
        ' ORDER BY r.id DESC LIMIT ? OFFSET ?',
        [*params, per_page, (pager['page'] - 1) * per_page],
    ).fetchall()
    teachers = db.execute("SELECT id,name FROM teachers WHERE status!='DELETED' ORDER BY name").fetchall()
    sessions = db.execute('SELECT id,session_name FROM sessions ORDER BY id DESC').fetchall()
    return render_template(
        'admin/question_bank.html', questions=rows, teachers=teachers, sessions=sessions,
        teacher_id=teacher_id, session_id=session_id, status=status, pager=pager,
    )


@bp.route('/admin/question-bank.csv')
@admin_required
def question_bank_csv():
    db = get_db()
    teacher_id = request.args.get('teacher_id','')
    session_id = request.args.get('session_id','')
    sql = '''SELECT t.name,r.session_name,r.question,r.category,r.keyword,r.total_votes,r.status,r.session_date
             FROM repository r LEFT JOIN teachers t ON t.id=r.teacher_id WHERE 1=1'''
    params=[]
    if teacher_id.isdigit(): sql += ' AND r.teacher_id=?'; params.append(int(teacher_id))
    if session_id.isdigit(): sql += ' AND r.session_id=?'; params.append(int(session_id))
    sql += ' ORDER BY r.id DESC'
    rows=db.execute(sql,params).fetchall()
    file=rows_to_csv(['Teacher','Session','Question','Category','Keyword','Votes','Status','Session Date'], ([r['name'],r['session_name'],r['question'],r['category'],r['keyword'],r['total_votes'],r['status'],r['session_date']] for r in rows))
    return send_file(file,as_attachment=True,download_name='admin_question_bank.csv',mimetype='text/csv')
