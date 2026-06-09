from extensions import app

from flask import (
    redirect,
    session,
    request,
    render_template
)

import sqlite3


# =====================================
# HELPERS
# =====================================

def admin_logged_in():
    return session.get("admin") == True


def clear_teacher_session():
    session.pop("teacher_id", None)
    session.pop("teacher_name", None)


def is_teacher_protected_path(path):

    protected_paths = [
        "/teacher-dashboard",
        "/teacher-create-session",
        "/teacher-session",
        "/teacher-session-live",
        "/teacher-resources",
        "/teacher-question-bank",
        "/teacher-keywords",
        "/teacher-categories",
        "/export-session-questions",
        "/complete-doubt",
        "/skip-doubt",
        "/close-session",
        "/reopen-session",
        "/upload-resource",
        "/add-video-resource",
        "/add-notes-resource",
        "/delete-resource",
        "/sync-completed-to-bank",
        "/add-bank-question-to-session"
    ]

    for protected_path in protected_paths:
        if path.startswith(protected_path):
            return True

    return False


# =====================================
# BLOCK DISABLED TEACHER
# =====================================

@app.before_request
def block_disabled_teacher():

    path = request.path

    if "teacher_id" not in session:
        return None

    if not is_teacher_protected_path(path):
        return None

    teacher_id = session.get("teacher_id")

    conn = sqlite3.connect("database.db")

    row = conn.execute(
        """
        SELECT status
        FROM teachers
        WHERE id=?
        """,
        (teacher_id,)
    ).fetchone()

    conn.close()

    if not row:
        clear_teacher_session()
        return redirect("/teacher-disabled")

    if row[0] != "ACTIVE":
        clear_teacher_session()
        return redirect("/teacher-disabled")

    return None


# =====================================
# TEACHER DISABLED PAGE
# =====================================

@app.route("/teacher-disabled")
def teacher_disabled():

    return render_template(
        "teacher/disabled.html"
    )


# =====================================
# ADMIN DISABLE TEACHER
# =====================================

@app.route("/admin-disable-teacher/<teacher_id>")
def admin_disable_teacher(teacher_id):

    if not admin_logged_in():
        return redirect("/admin-login")

    conn = sqlite3.connect("database.db")

    conn.execute(
        """
        UPDATE teachers
        SET status='INACTIVE'
        WHERE id=?
        """,
        (teacher_id,)
    )

    conn.execute(
        """
        UPDATE sessions
        SET status='CLOSED'
        WHERE teacher_id=?
        AND status='ACTIVE'
        """,
        (teacher_id,)
    )

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
            "Teacher disabled by admin. Active sessions were closed."
        )
    )

    conn.commit()
    conn.close()

    return redirect("/admin-teachers")


# =====================================
# ADMIN ENABLE TEACHER
# =====================================

@app.route("/admin-enable-teacher/<teacher_id>")
def admin_enable_teacher(teacher_id):

    if not admin_logged_in():
        return redirect("/admin-login")

    conn = sqlite3.connect("database.db")

    conn.execute(
        """
        UPDATE teachers
        SET status='ACTIVE'
        WHERE id=?
        """,
        (teacher_id,)
    )

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
            "Teacher enabled by admin."
        )
    )

    conn.commit()
    conn.close()

    return redirect("/admin-teachers")