from extensions import app

from flask import (
    render_template,
    request,
    redirect,
    session
)

import sqlite3


# =====================================
# ADMIN LOGIN
# =====================================

@app.route("/admin-login")
def admin_login():

    return render_template(
        "admin/login.html"
    )


@app.route(
    "/admin-login",
    methods=["POST"]
)
def admin_login_post():

    username = request.form["username"]
    password = request.form["password"]

    conn = sqlite3.connect("database.db")

    row = conn.execute(
        """
        SELECT *
        FROM admins
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

    session["admin"] = True

    return redirect(
        "/admin-dashboard"
    )


# =====================================
# DASHBOARD
# =====================================

@app.route("/admin-dashboard")
def admin_dashboard():

    if not session.get("admin"):
        return redirect("/admin-login")

    conn = sqlite3.connect(
        "database.db"
    )

    total_teachers = conn.execute(
        "SELECT COUNT(*) FROM teachers"
    ).fetchone()[0]

    total_sessions = conn.execute(
        "SELECT COUNT(*) FROM sessions"
    ).fetchone()[0]

    total_students = conn.execute(
        "SELECT COUNT(*) FROM students"
    ).fetchone()[0]

    total_doubts = conn.execute(
        "SELECT COUNT(*) FROM doubts"
    ).fetchone()[0]

    conn.close()

    return render_template(
        "admin/dashboard.html",

        total_teachers=total_teachers,
        total_sessions=total_sessions,
        total_students=total_students,
        total_doubts=total_doubts
    )


# =====================================
# CREATE TEACHER
# =====================================

@app.route("/admin-create-teacher")
def admin_create_teacher():

    return render_template(
        "admin/create_teacher.html"
    )


@app.route(
    "/admin-create-teacher",
    methods=["POST"]
)
def admin_create_teacher_post():

    name = request.form["name"]
    username = request.form["username"]
    password = request.form["password"]

    conn = sqlite3.connect(
        "database.db"
    )

    conn.execute(
        """
        INSERT INTO teachers(
            name,
            username,
            password
        )
        VALUES(?,?,?)
        """,
        (
            name,
            username,
            password
        )
    )

    conn.commit()
    conn.close()

    return redirect(
        "/admin-teachers"
    )


# =====================================
# TEACHERS
# =====================================

@app.route("/admin-teachers")
def admin_teachers():

    conn = sqlite3.connect(
        "database.db"
    )

    teachers = conn.execute(
        """
        SELECT
            id,
            name,
            username,
            status
        FROM teachers
        ORDER BY id DESC
        """
    ).fetchall()

    conn.close()

    return render_template(
        "admin/teachers.html",
        teachers=teachers
    )


# =====================================
# SESSIONS
# =====================================

@app.route("/admin-sessions")
def admin_sessions():

    conn = sqlite3.connect(
        "database.db"
    )

    rows = conn.execute(
        """
        SELECT
            s.id,
            s.session_name,
            s.duration,
            t.name
        FROM sessions s
        LEFT JOIN teachers t
        ON s.teacher_id=t.id
        ORDER BY s.id DESC
        """
    ).fetchall()

    conn.close()

    return render_template(
        "admin/sessions.html",
        rows=rows
    )


# =====================================
# STUDENTS
# =====================================

@app.route("/admin-students")
def admin_students():

    conn = sqlite3.connect(
        "database.db"
    )

    students = conn.execute(
        """
        SELECT
            id,
            name,
            mobile
        FROM students
        ORDER BY id DESC
        """
    ).fetchall()

    conn.close()

    return render_template(
        "admin/students.html",
        students=students
    )


# =====================================
# SESSION STUDENTS
# =====================================

@app.route(
    "/admin-session-students/<session_id>"
)
def admin_session_students(
    session_id
):

    conn = sqlite3.connect(
        "database.db"
    )

    rows = conn.execute(
        """
        SELECT
            st.name,
            st.mobile
        FROM session_students ss
        JOIN students st
        ON ss.student_id=st.id
        WHERE ss.session_id=?
        """,
        (session_id,)
    ).fetchall()

    conn.close()

    html = f"""
    <h1>
    Session {session_id}
    Students
    </h1>

    <hr>
    """

    for row in rows:

        html += f"""
        Name :
        {row[0]}

        <br>

        Mobile :
        {row[1]}

        <hr>
        """

    return html


# =====================================
# ALL DOUBTS
# =====================================

@app.route("/admin-doubts")
def admin_doubts():

    conn = sqlite3.connect(
        "database.db"
    )

    doubts = conn.execute(
        """
        SELECT
            id,
            question,
            category,
            keyword,
            votes,
            status
        FROM doubts
        ORDER BY id DESC
        """
    ).fetchall()

    conn.close()

    return render_template(
        "admin/doubts.html",
        doubts=doubts
    )


# =====================================
# TEACHER ACTIVITY
# =====================================

@app.route(
    "/admin-teacher-activity"
)
def admin_teacher_activity():

    conn = sqlite3.connect(
        "database.db"
    )

    rows = conn.execute(
        """
        SELECT
            ta.activity,
            ta.created_at,
            t.name
        FROM teacher_activity ta
        LEFT JOIN teachers t
        ON ta.teacher_id=t.id
        ORDER BY ta.id DESC
        """
    ).fetchall()

    conn.close()

    html = """
    <h1>
    Teacher Activity
    </h1>

    <hr>
    """

    for row in rows:

        html += f"""
        Teacher :
        {row[2]}

        <br>

        Activity :
        {row[0]}

        <br>

        Date :
        {row[1]}

        <hr>
        """

    return html


# =====================================
# CATEGORY ANALYTICS
# =====================================

@app.route(
    "/admin-category-analytics"
)
def admin_category_analytics():

    conn = sqlite3.connect(
        "database.db"
    )

    rows = conn.execute(
        """
        SELECT
            category,
            COUNT(*)
        FROM doubts
        GROUP BY category
        ORDER BY COUNT(*) DESC
        """
    ).fetchall()

    conn.close()

    html = """
    <h1>
    Category Analytics
    </h1>

    <hr>
    """

    for row in rows:

        html += f"""
        {row[0]}
        :
        {row[1]}
        <br>
        """

    return html


# =====================================
# KEYWORD ANALYTICS
# =====================================

@app.route(
    "/admin-keyword-analytics"
)
def admin_keyword_analytics():

    conn = sqlite3.connect(
        "database.db"
    )

    rows = conn.execute(
        """
        SELECT
            keyword,
            COUNT(*)
        FROM doubts
        GROUP BY keyword
        ORDER BY COUNT(*) DESC
        LIMIT 50
        """
    ).fetchall()

    conn.close()

    html = """
    <h1>
    Keyword Analytics
    </h1>

    <hr>
    """

    for row in rows:

        html += f"""
        {row[0]}
        :
        {row[1]}
        <br>
        """

    return html


# =====================================
# LOGOUT
# =====================================

@app.route("/admin-logout")
def admin_logout():

    session.clear()

    return redirect(
        "/admin-login"
    )