from extensions import app

from flask import (
    render_template,
    request,
    redirect,
    session
)

from config import BASE_URL

import sqlite3
import qrcode
import os

from html import escape


# =====================================
# HELPERS
# =====================================

def require_teacher():

    return "teacher_id" in session


def log_teacher_activity(teacher_id, activity):

    conn = sqlite3.connect("database.db")

    conn.execute(
        """
        INSERT INTO teacher_activity(
            teacher_id,
            activity
        )
        VALUES(?,?)
        """,
        (
            teacher_id,
            activity
        )
    )

    conn.commit()
    conn.close()


# =====================================
# TEACHER LOGIN
# =====================================

@app.route("/teacher-login")
def teacher_login():

    return render_template(
        "teacher/login.html"
    )


@app.route(
    "/teacher-login",
    methods=["POST"]
)
def teacher_login_post():

    username = request.form["username"]
    password = request.form["password"]

    conn = sqlite3.connect("database.db")

    row = conn.execute(
        """
        SELECT
            id,
            name,
            username,
            password,
            status
        FROM teachers
        WHERE username=?
        AND password=?
        """,
        (
            username,
            password
        )
    ).fetchone()

    conn.close()

    if not row:

        return render_template(
            "message.html",
            title="Invalid Teacher Login",
            message="Username or password is incorrect. Please try again.",
            box_class="warning",
            button_text="Back to Teacher Login",
            button_link="/teacher-login"
        )

    if row[4] != "ACTIVE":

        return render_template(
            "message.html",
            title="Teacher Account Disabled",
            message="Your teacher account is disabled by admin. Please contact admin.",
            box_class="warning",
            button_text="Back to Teacher Login",
            button_link="/teacher-login"
        )

    session.clear()
    session["teacher_id"] = row[0]
    session["teacher_name"] = row[1]

    log_teacher_activity(
        row[0],
        "Teacher logged in"
    )

    return redirect(
        "/teacher-dashboard"
    )


# =====================================
# TEACHER DASHBOARD
# =====================================

@app.route("/teacher-dashboard")
def teacher_dashboard():

    if not require_teacher():
        return redirect("/teacher-login")

    teacher_id = session["teacher_id"]

    conn = sqlite3.connect("database.db")

    teacher = conn.execute(
        """
        SELECT
            name,
            status
        FROM teachers
        WHERE id=?
        """,
        (teacher_id,)
    ).fetchone()

    if not teacher:
        conn.close()
        session.clear()
        return redirect("/teacher-login")

    if teacher[1] != "ACTIVE":
        conn.close()
        session.clear()
        return redirect("/teacher-disabled")

    sessions = conn.execute(
        """
        SELECT
            id,
            session_name,
            duration,
            status,
            created_at
        FROM sessions
        WHERE teacher_id=?
        ORDER BY id DESC
        """,
        (teacher_id,)
    ).fetchall()

    total_sessions = conn.execute(
        """
        SELECT COUNT(*)
        FROM sessions
        WHERE teacher_id=?
        """,
        (teacher_id,)
    ).fetchone()[0]

    total_questions = conn.execute(
        """
        SELECT COUNT(*)
        FROM doubts d
        JOIN sessions s
        ON d.session_id=s.id
        WHERE s.teacher_id=?
        """,
        (teacher_id,)
    ).fetchone()[0]

    conn.close()

    return render_template(
        "teacher/dashboard.html",
        teacher_name=teacher[0],
        sessions=sessions,
        total_sessions=total_sessions,
        total_questions=total_questions
    )


# =====================================
# CREATE SESSION
# =====================================

@app.route("/teacher-create-session")
def teacher_create_session():

    if not require_teacher():
        return redirect("/teacher-login")

    return render_template(
        "teacher/create_session.html"
    )


@app.route(
    "/teacher-create-session",
    methods=["POST"]
)
def teacher_create_session_post():

    if not require_teacher():
        return redirect("/teacher-login")

    teacher_id = session["teacher_id"]

    session_name = request.form["session_name"]
    duration = request.form["duration"]

    conn = sqlite3.connect("database.db")

    conn.execute(
        """
        INSERT INTO sessions(
            teacher_id,
            session_name,
            duration,
            status
        )
        VALUES(?,?,?,'ACTIVE')
        """,
        (
            teacher_id,
            session_name,
            duration
        )
    )

    conn.commit()

    session_id = conn.execute(
        "SELECT last_insert_rowid()"
    ).fetchone()[0]

    conn.close()

    os.makedirs(
        "static/qr",
        exist_ok=True
    )

    join_url = f"{BASE_URL}/join-session/{session_id}"

    qr = qrcode.make(join_url)

    qr.save(
        f"static/qr/session_{session_id}.png"
    )

    log_teacher_activity(
        teacher_id,
        f"Created session {session_id}: {session_name}"
    )

    return redirect(
        f"/teacher-session/{session_id}"
    )


# =====================================
# TEACHER SESSION PAGE
# =====================================

@app.route("/teacher-session/<session_id>")
def teacher_session(session_id):

    if not require_teacher():
        return redirect("/teacher-login")

    teacher_id = session["teacher_id"]

    conn = sqlite3.connect("database.db")

    row = conn.execute(
        """
        SELECT
            id,
            session_name,
            status
        FROM sessions
        WHERE id=?
        AND teacher_id=?
        """,
        (
            session_id,
            teacher_id
        )
    ).fetchone()

    conn.close()

    if not row:

        return render_template(
            "message.html",
            title="Access Denied",
            message="You are not allowed to access this session.",
            box_class="warning",
            button_text="Go to Teacher Dashboard",
            button_link="/teacher-dashboard"
        )

    session_name = row[1]
    session_status = row[2]

    join_url = f"{BASE_URL}/join-session/{session_id}"

    return render_template(
        "teacher/session_questions.html",
        session_id=session_id,
        session_name=session_name,
        session_status=session_status,
        join_url=join_url
    )


# =====================================
# LIVE SESSION DATA
# =====================================

@app.route("/teacher-session-live/<session_id>")
def teacher_session_live(session_id):

    if not require_teacher():
        return "Login required"

    teacher_id = session["teacher_id"]

    conn = sqlite3.connect("database.db")

    owner = conn.execute(
        """
        SELECT
            id,
            status
        FROM sessions
        WHERE id=?
        AND teacher_id=?
        """,
        (
            session_id,
            teacher_id
        )
    ).fetchone()

    if not owner:
        conn.close()
        return "Not allowed"

    session_status = owner[1]

    total_students = conn.execute(
        """
        SELECT COUNT(*)
        FROM session_students
        WHERE session_id=?
        """,
        (session_id,)
    ).fetchone()[0]

    total_doubts = conn.execute(
        """
        SELECT COUNT(*)
        FROM doubts
        WHERE session_id=?
        """,
        (session_id,)
    ).fetchone()[0]

    open_count = conn.execute(
        """
        SELECT COUNT(*)
        FROM doubts
        WHERE session_id=?
        AND status='OPEN'
        """,
        (session_id,)
    ).fetchone()[0]

    completed_count = conn.execute(
        """
        SELECT COUNT(*)
        FROM doubts
        WHERE session_id=?
        AND status='COMPLETED'
        """,
        (session_id,)
    ).fetchone()[0]

    skipped_count = conn.execute(
        """
        SELECT COUNT(*)
        FROM doubts
        WHERE session_id=?
        AND status='SKIPPED'
        """,
        (session_id,)
    ).fetchone()[0]

    open_doubts = conn.execute(
        """
        SELECT
            id,
            question,
            category,
            keyword,
            votes
        FROM doubts
        WHERE session_id=?
        AND status='OPEN'
        ORDER BY votes DESC,id DESC
        """,
        (session_id,)
    ).fetchall()

    completed_doubts = conn.execute(
        """
        SELECT
            id,
            question,
            category,
            keyword,
            votes
        FROM doubts
        WHERE session_id=?
        AND status='COMPLETED'
        ORDER BY id DESC
        LIMIT 10
        """,
        (session_id,)
    ).fetchall()

    skipped_doubts = conn.execute(
        """
        SELECT
            id,
            question,
            category,
            keyword,
            votes
        FROM doubts
        WHERE session_id=?
        AND status='SKIPPED'
        ORDER BY id DESC
        LIMIT 10
        """,
        (session_id,)
    ).fetchall()

    conn.close()

    html = ""

    if session_status == "CLOSED":

        html += """
        <div class="warning">
            This session is closed. Students are automatically logged out and cannot submit new doubts.
        </div>
        """

    html += f"""
    <div class="card-row">

        <div class="card">
            <h3>Students Joined</h3>
            <p>{total_students}</p>
        </div>

        <div class="card">
            <h3>Total Doubts</h3>
            <p>{total_doubts}</p>
        </div>

        <div class="card">
            <h3>Open</h3>
            <p>{open_count}</p>
        </div>

        <div class="card">
            <h3>Completed</h3>
            <p>{completed_count}</p>
        </div>

        <div class="card">
            <h3>Skipped</h3>
            <p>{skipped_count}</p>
        </div>

    </div>
    """

    html += """
    <div class="section">
        <h2>Open Doubts</h2>
    """

    if len(open_doubts) == 0:
        html += "<p>No open doubts.</p>"

    for doubt in open_doubts:

        doubt_id = doubt[0]
        question = escape(str(doubt[1]))
        category = escape(str(doubt[2]))
        keyword = escape(str(doubt[3]))
        votes = doubt[4]

        html += f"""
        <div class="doubt-card">

            <span class="badge">Votes: {votes}</span>
            <span class="badge">{category}</span>
            <span class="badge">{keyword}</span>

            <div class="doubt-question">
                {question}
            </div>

            <a class="btn btn-green"
               href="/complete-doubt/{doubt_id}">
                Mark Completed
            </a>

            <a class="btn btn-red"
               href="/skip-doubt/{doubt_id}"
               onclick="return confirm('Skip this doubt?')">
                Skip
            </a>

        </div>
        """

    html += """
    </div>

    <div class="section">
        <h2>Recently Completed</h2>
    """

    if len(completed_doubts) == 0:
        html += "<p>No completed doubts yet.</p>"

    for doubt in completed_doubts:

        doubt_id = doubt[0]
        question = escape(str(doubt[1]))
        category = escape(str(doubt[2]))
        keyword = escape(str(doubt[3]))
        votes = doubt[4]

        html += f"""
        <div class="doubt-card completed-card">

            <span class="badge badge-green">Completed</span>
            <span class="badge">{category}</span>
            <span class="badge">{keyword}</span>
            <span class="badge">Votes: {votes}</span>

            <div class="doubt-question">
                {question}
            </div>

            <a class="btn btn-gray"
               href="/restore-doubt/{doubt_id}">
                Move Back to Open
            </a>

        </div>
        """

    html += """
    </div>

    <div class="section">
        <h2>Skipped Doubts</h2>
    """

    if len(skipped_doubts) == 0:
        html += "<p>No skipped doubts.</p>"

    for doubt in skipped_doubts:

        doubt_id = doubt[0]
        question = escape(str(doubt[1]))
        category = escape(str(doubt[2]))
        keyword = escape(str(doubt[3]))
        votes = doubt[4]

        html += f"""
        <div class="doubt-card skipped-card">

            <span class="badge badge-red">Skipped</span>
            <span class="badge">{category}</span>
            <span class="badge">{keyword}</span>
            <span class="badge">Votes: {votes}</span>

            <div class="doubt-question">
                {question}
            </div>

            <a class="btn btn-gray"
               href="/restore-doubt/{doubt_id}">
                Restore Doubt
            </a>

        </div>
        """

    html += """
    </div>
    """

    return html


# =====================================
# COMPLETE DOUBT
# =====================================

@app.route("/complete-doubt/<doubt_id>")
def complete_doubt(doubt_id):

    if not require_teacher():
        return redirect("/teacher-login")

    teacher_id = session["teacher_id"]

    conn = sqlite3.connect("database.db")

    row = conn.execute(
        """
        SELECT
            d.session_id
        FROM doubts d
        JOIN sessions s
        ON d.session_id=s.id
        WHERE d.id=?
        AND s.teacher_id=?
        """,
        (
            doubt_id,
            teacher_id
        )
    ).fetchone()

    if not row:
        conn.close()
        return "Not allowed"

    session_id = row[0]

    conn.execute(
        """
        UPDATE doubts
        SET status='COMPLETED'
        WHERE id=?
        """,
        (doubt_id,)
    )

    conn.commit()
    conn.close()

    log_teacher_activity(
        teacher_id,
        f"Completed doubt {doubt_id} in session {session_id}"
    )

    return redirect(
        f"/teacher-session/{session_id}"
    )


# =====================================
# SKIP DOUBT
# =====================================

@app.route("/skip-doubt/<doubt_id>")
def skip_doubt(doubt_id):

    if not require_teacher():
        return redirect("/teacher-login")

    teacher_id = session["teacher_id"]

    conn = sqlite3.connect("database.db")

    row = conn.execute(
        """
        SELECT
            d.session_id
        FROM doubts d
        JOIN sessions s
        ON d.session_id=s.id
        WHERE d.id=?
        AND s.teacher_id=?
        """,
        (
            doubt_id,
            teacher_id
        )
    ).fetchone()

    if not row:
        conn.close()
        return "Not allowed"

    session_id = row[0]

    conn.execute(
        """
        UPDATE doubts
        SET status='SKIPPED'
        WHERE id=?
        """,
        (doubt_id,)
    )

    conn.commit()
    conn.close()

    log_teacher_activity(
        teacher_id,
        f"Skipped doubt {doubt_id} in session {session_id}"
    )

    return redirect(
        f"/teacher-session/{session_id}"
    )


# =====================================
# RESTORE DOUBT
# =====================================

@app.route("/restore-doubt/<doubt_id>")
def restore_doubt(doubt_id):

    if not require_teacher():
        return redirect("/teacher-login")

    teacher_id = session["teacher_id"]

    conn = sqlite3.connect("database.db")

    row = conn.execute(
        """
        SELECT
            d.session_id
        FROM doubts d
        JOIN sessions s
        ON d.session_id=s.id
        WHERE d.id=?
        AND s.teacher_id=?
        """,
        (
            doubt_id,
            teacher_id
        )
    ).fetchone()

    if not row:
        conn.close()
        return "Not allowed"

    session_id = row[0]

    conn.execute(
        """
        UPDATE doubts
        SET status='OPEN'
        WHERE id=?
        """,
        (doubt_id,)
    )

    conn.commit()
    conn.close()

    log_teacher_activity(
        teacher_id,
        f"Restored doubt {doubt_id} in session {session_id}"
    )

    return redirect(
        f"/teacher-session/{session_id}"
    )


# =====================================
# CATEGORY ANALYSIS
# =====================================

@app.route("/teacher-categories/<session_id>")
def teacher_categories(session_id):

    if not require_teacher():
        return redirect("/teacher-login")

    teacher_id = session["teacher_id"]
    selected_category = request.args.get("category", "")

    conn = sqlite3.connect("database.db")

    session_row = conn.execute(
        """
        SELECT
            id,
            session_name
        FROM sessions
        WHERE id=?
        AND teacher_id=?
        """,
        (
            session_id,
            teacher_id
        )
    ).fetchone()

    if not session_row:
        conn.close()
        return "Not allowed"

    category_rows = conn.execute(
        """
        SELECT
            category,
            COUNT(*) AS total_questions,
            SUM(votes) AS total_votes,
            SUM(CASE WHEN status='OPEN' THEN 1 ELSE 0 END) AS open_count,
            SUM(CASE WHEN status='COMPLETED' THEN 1 ELSE 0 END) AS completed_count,
            SUM(CASE WHEN status='SKIPPED' THEN 1 ELSE 0 END) AS skipped_count
        FROM doubts
        WHERE session_id=?
        GROUP BY category
        ORDER BY total_questions DESC
        """,
        (session_id,)
    ).fetchall()

    questions = []

    if selected_category:

        questions = conn.execute(
            """
            SELECT
                question,
                keyword,
                votes,
                status
            FROM doubts
            WHERE session_id=?
            AND category=?
            ORDER BY votes DESC,id DESC
            """,
            (
                session_id,
                selected_category
            )
        ).fetchall()

    conn.close()

    return render_template(
        "teacher/categories.html",
        session_id=session_id,
        session_name=session_row[1],
        category_rows=category_rows,
        selected_category=selected_category,
        questions=questions,
        chart_labels=[row[0] for row in category_rows],
        chart_values=[row[1] for row in category_rows]
    )


# =====================================
# KEYWORD ANALYSIS
# =====================================

@app.route("/teacher-keywords/<session_id>")
def teacher_keywords(session_id):

    if not require_teacher():
        return redirect("/teacher-login")

    teacher_id = session["teacher_id"]
    selected_keyword = request.args.get("keyword", "")

    conn = sqlite3.connect("database.db")

    session_row = conn.execute(
        """
        SELECT
            id,
            session_name
        FROM sessions
        WHERE id=?
        AND teacher_id=?
        """,
        (
            session_id,
            teacher_id
        )
    ).fetchone()

    if not session_row:
        conn.close()
        return "Not allowed"

    keyword_rows = conn.execute(
        """
        SELECT
            keyword,
            COUNT(*) AS total_questions,
            SUM(votes) AS total_votes,
            SUM(CASE WHEN status='OPEN' THEN 1 ELSE 0 END) AS open_count,
            SUM(CASE WHEN status='COMPLETED' THEN 1 ELSE 0 END) AS completed_count,
            SUM(CASE WHEN status='SKIPPED' THEN 1 ELSE 0 END) AS skipped_count
        FROM doubts
        WHERE session_id=?
        GROUP BY keyword
        ORDER BY total_questions DESC
        LIMIT 50
        """,
        (session_id,)
    ).fetchall()

    questions = []

    if selected_keyword:

        questions = conn.execute(
            """
            SELECT
                question,
                category,
                votes,
                status
            FROM doubts
            WHERE session_id=?
            AND keyword=?
            ORDER BY votes DESC,id DESC
            """,
            (
                session_id,
                selected_keyword
            )
        ).fetchall()

    conn.close()

    return render_template(
        "teacher/keywords.html",
        session_id=session_id,
        session_name=session_row[1],
        keyword_rows=keyword_rows,
        selected_keyword=selected_keyword,
        questions=questions,
        chart_labels=[row[0] for row in keyword_rows],
        chart_values=[row[1] for row in keyword_rows]
    )


# =====================================
# CLOSE SESSION
# =====================================

@app.route("/close-session/<session_id>")
def close_session(session_id):

    if not require_teacher():
        return redirect("/teacher-login")

    teacher_id = session["teacher_id"]

    conn = sqlite3.connect("database.db")

    row = conn.execute(
        """
        SELECT id
        FROM sessions
        WHERE id=?
        AND teacher_id=?
        """,
        (
            session_id,
            teacher_id
        )
    ).fetchone()

    if not row:
        conn.close()
        return "Not allowed"

    conn.execute(
        """
        UPDATE sessions
        SET status='CLOSED'
        WHERE id=?
        """,
        (session_id,)
    )

    conn.commit()
    conn.close()

    log_teacher_activity(
        teacher_id,
        f"Closed session {session_id}"
    )

    return redirect(
        f"/teacher-session/{session_id}"
    )


# =====================================
# REOPEN SESSION
# =====================================

@app.route("/reopen-session/<session_id>")
def reopen_session(session_id):

    if not require_teacher():
        return redirect("/teacher-login")

    teacher_id = session["teacher_id"]

    conn = sqlite3.connect("database.db")

    row = conn.execute(
        """
        SELECT id
        FROM sessions
        WHERE id=?
        AND teacher_id=?
        """,
        (
            session_id,
            teacher_id
        )
    ).fetchone()

    if not row:
        conn.close()
        return "Not allowed"

    conn.execute(
        """
        UPDATE sessions
        SET status='ACTIVE'
        WHERE id=?
        """,
        (session_id,)
    )

    conn.commit()
    conn.close()

    log_teacher_activity(
        teacher_id,
        f"Reopened session {session_id}"
    )

    return redirect(
        f"/teacher-session/{session_id}"
    )


# =====================================
# LOGOUT
# =====================================

@app.route("/teacher-logout")
def teacher_logout():

    teacher_id = session.get("teacher_id")

    if teacher_id:

        log_teacher_activity(
            teacher_id,
            "Teacher logged out"
        )

    session.clear()

    return redirect(
        "/teacher-login"
    )