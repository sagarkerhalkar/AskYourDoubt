from extensions import app

from flask import (
    render_template,
    request,
    redirect,
    session
)

import sqlite3
import qrcode
import os

BASE_URL = app.config["BASE_URL"]


# =====================================
# CATEGORY DETECTION
# =====================================

def detect_category(question):

    q = question.lower()

    if any(word in q for word in [
        "force",
        "motion",
        "newton",
        "velocity",
        "acceleration",
        "physics"
    ]):
        return "Physics"

    if any(word in q for word in [
        "math",
        "equation",
        "quadratic",
        "algebra",
        "geometry",
        "trigonometry"
    ]):
        return "Mathematics"

    if any(word in q for word in [
        "atom",
        "molecule",
        "chemistry",
        "reaction"
    ]):
        return "Chemistry"

    if any(word in q for word in [
        "cell",
        "biology",
        "human body",
        "uterus"
    ]):
        return "Biology"

    return "General"


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
            name
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
        return "Invalid Login"

    session["teacher_id"] = row[0]
    session["teacher_name"] = row[1]

    return redirect("/teacher-dashboard")


# =====================================
# DASHBOARD
# =====================================

@app.route("/teacher-dashboard")
def teacher_dashboard():

    teacher_id = session.get("teacher_id")

    if not teacher_id:
        return redirect("/teacher-login")

    conn = sqlite3.connect("database.db")

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
        FROM doubts
        WHERE session_id IN (
            SELECT id
            FROM sessions
            WHERE teacher_id=?
        )
        """,
        (teacher_id,)
    ).fetchone()[0]

    conn.close()

    return render_template(
        "teacher/dashboard.html",
        total_sessions=total_sessions,
        total_questions=total_questions,
        teacher_name=session["teacher_name"]
    )


# =====================================
# CREATE SESSION
# =====================================

@app.route("/teacher-create-session")
def teacher_create_session():

    if "teacher_id" not in session:
        return redirect("/teacher-login")

    return render_template(
        "teacher/create_session.html"
    )


@app.route(
    "/teacher-create-session",
    methods=["POST"]
)
def teacher_create_session_post():

    teacher_id = session["teacher_id"]

    session_name = request.form["session_name"]
    duration = request.form["duration"]

    conn = sqlite3.connect("database.db")

    conn.execute(
        """
        INSERT INTO sessions(
            teacher_id,
            session_name,
            duration
        )
        VALUES(?,?,?)
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
            f"Created Session {session_id}"
        )
    )

    conn.commit()
    conn.close()

    os.makedirs(
        "static/qr",
        exist_ok=True
    )

    join_url = (
        f"{BASE_URL}/join-session/{session_id}"
    )

    img = qrcode.make(join_url)

    img.save(
        f"static/qr/session_{session_id}.png"
    )

    return redirect(
        f"/teacher-session/{session_id}"
    )


# =====================================
# SESSION VIEW
# =====================================

@app.route("/teacher-session/<session_id>")
def teacher_session(session_id):

    if "teacher_id" not in session:
        return redirect("/teacher-login")

    conn = sqlite3.connect("database.db")

    doubts = conn.execute(
        """
        SELECT
            id,
            question,
            category,
            votes,
            status
        FROM doubts
        WHERE session_id=?
        ORDER BY votes DESC,id DESC
        """,
        (session_id,)
    ).fetchall()

    total_students = conn.execute(
        """
        SELECT COUNT(*)
        FROM session_students
        WHERE session_id=?
        """,
        (session_id,)
    ).fetchone()[0]

    conn.close()

    return render_template(
        "teacher/session_questions.html",
        session_id=session_id,
        doubts=doubts,
        total_students=total_students
    )


# =====================================
# COMPLETE DOUBT
# =====================================

@app.route(
    "/complete-doubt/<doubt_id>"
)
def complete_doubt(doubt_id):

    conn = sqlite3.connect("database.db")

    conn.execute(
        """
        UPDATE doubts
        SET status='COMPLETED'
        WHERE id=?
        """,
        (doubt_id,)
    )

    conn.commit()

    session_id = conn.execute(
        """
        SELECT session_id
        FROM doubts
        WHERE id=?
        """,
        (doubt_id,)
    ).fetchone()[0]

    conn.close()

    return redirect(
        f"/teacher-session/{session_id}"
    )


# =====================================
# SKIP DOUBT
# =====================================

@app.route(
    "/skip-doubt/<doubt_id>"
)
def skip_doubt(doubt_id):

    conn = sqlite3.connect("database.db")

    conn.execute(
        """
        UPDATE doubts
        SET status='SKIPPED'
        WHERE id=?
        """,
        (doubt_id,)
    )

    conn.commit()

    session_id = conn.execute(
        """
        SELECT session_id
        FROM doubts
        WHERE id=?
        """,
        (doubt_id,)
    ).fetchone()[0]

    conn.close()

    return redirect(
        f"/teacher-session/{session_id}"
    )


# =====================================
# KEYWORD ANALYSIS
# =====================================

@app.route(
    "/teacher-keywords/<session_id>"
)
def teacher_keywords(session_id):

    conn = sqlite3.connect("database.db")

    rows = conn.execute(
        """
        SELECT question
        FROM doubts
        WHERE session_id=?
        """,
        (session_id,)
    ).fetchall()

    conn.close()

    keywords = {}

    for row in rows:

        words = row[0].lower().split()

        for word in words:

            if len(word) < 4:
                continue

            keywords[word] = (
                keywords.get(word, 0) + 1
            )

    sorted_words = sorted(
        keywords.items(),
        key=lambda x: x[1],
        reverse=True
    )

    html = """
    <h1>Keyword Analysis</h1>
    <hr>
    """

    for word, count in sorted_words[:50]:

        html += (
            f"<b>{word}</b> : {count}<br>"
        )

    return html


# =====================================
# CATEGORY ANALYSIS
# =====================================

@app.route(
    "/teacher-categories/<session_id>"
)
def teacher_categories(session_id):

    conn = sqlite3.connect("database.db")

    rows = conn.execute(
        """
        SELECT
            category,
            COUNT(*)
        FROM doubts
        WHERE session_id=?
        GROUP BY category
        """,
        (session_id,)
    ).fetchall()

    conn.close()

    html = """
    <h1>Category Analysis</h1>
    <hr>
    """

    for row in rows:

        html += (
            f"{row[0]} : {row[1]}<br>"
        )

    return html


# =====================================
# LOGOUT
# =====================================

@app.route("/teacher-logout")
def teacher_logout():

    session.clear()

    return redirect(
        "/teacher-login"
    )