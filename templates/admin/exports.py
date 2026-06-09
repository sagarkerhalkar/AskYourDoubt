from extensions import app

from flask import (
    redirect,
    session
)

import sqlite3
import csv
import os
import time


# =====================================
# HELPERS
# =====================================

def teacher_logged_in():

    return "teacher_id" in session


def admin_logged_in():

    return session.get("admin") == True


def teacher_owns_session(session_id):

    teacher_id = session.get("teacher_id")

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

    conn.close()

    return row is not None


def create_export_folder():

    os.makedirs("exports", exist_ok=True)


# =====================================
# TEACHER EXPORT SESSION QUESTIONS
# =====================================

@app.route("/export-session-questions/<session_id>")
def export_session_questions(session_id):

    if not teacher_logged_in():
        return redirect("/teacher-login")

    if not teacher_owns_session(session_id):
        return "Not allowed"

    create_export_folder()

    filename = f"session_{session_id}_questions_{int(time.time())}.csv"

    filepath = os.path.join(
        "exports",
        filename
    )

    conn = sqlite3.connect("database.db")

    rows = conn.execute(
        """
        SELECT
            d.id,
            d.question,
            d.category,
            d.keyword,
            d.votes,
            d.status,
            s.name,
            s.mobile,
            d.created_at
        FROM doubts d
        LEFT JOIN students s
        ON d.student_id=s.id
        WHERE d.session_id=?
        ORDER BY d.votes DESC,d.id DESC
        """,
        (session_id,)
    ).fetchall()

    conn.close()

    with open(
        filepath,
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as file:

        writer = csv.writer(file)

        writer.writerow([
            "Doubt ID",
            "Question",
            "Category",
            "Keyword",
            "Votes",
            "Status",
            "Student Name",
            "Mobile",
            "Created At"
        ])

        for row in rows:
            writer.writerow(row)

    return redirect(
        f"/exports/{filename}"
    )


# =====================================
# ADMIN EXPORT ALL QUESTIONS
# =====================================

@app.route("/admin-export-all-questions")
def admin_export_all_questions():

    if not admin_logged_in():
        return redirect("/admin-login")

    create_export_folder()

    filename = f"all_questions_{int(time.time())}.csv"

    filepath = os.path.join(
        "exports",
        filename
    )

    conn = sqlite3.connect("database.db")

    rows = conn.execute(
        """
        SELECT
            d.id,
            d.session_id,
            d.question,
            d.category,
            d.keyword,
            d.votes,
            d.status,
            st.name,
            st.mobile,
            t.name,
            d.created_at
        FROM doubts d
        LEFT JOIN students st
        ON d.student_id=st.id
        LEFT JOIN sessions se
        ON d.session_id=se.id
        LEFT JOIN teachers t
        ON se.teacher_id=t.id
        ORDER BY d.id DESC
        """
    ).fetchall()

    conn.close()

    with open(
        filepath,
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as file:

        writer = csv.writer(file)

        writer.writerow([
            "Doubt ID",
            "Session ID",
            "Question",
            "Category",
            "Keyword",
            "Votes",
            "Status",
            "Student Name",
            "Student Mobile",
            "Teacher Name",
            "Created At"
        ])

        for row in rows:
            writer.writerow(row)

    return redirect(
        f"/exports/{filename}"
    )


# =====================================
# ADMIN EXPORT STUDENTS
# =====================================

@app.route("/admin-export-students")
def admin_export_students():

    if not admin_logged_in():
        return redirect("/admin-login")

    create_export_folder()

    filename = f"students_{int(time.time())}.csv"

    filepath = os.path.join(
        "exports",
        filename
    )

    conn = sqlite3.connect("database.db")

    rows = conn.execute(
        """
        SELECT
            st.id,
            st.name,
            st.mobile,
            st.created_at
        FROM students st
        ORDER BY st.id DESC
        """
    ).fetchall()

    conn.close()

    with open(
        filepath,
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as file:

        writer = csv.writer(file)

        writer.writerow([
            "Student ID",
            "Name",
            "Mobile",
            "Joined At"
        ])

        for row in rows:
            writer.writerow(row)

    return redirect(
        f"/exports/{filename}"
    )


# =====================================
# ADMIN EXPORT SESSIONS
# =====================================

@app.route("/admin-export-sessions")
def admin_export_sessions():

    if not admin_logged_in():
        return redirect("/admin-login")

    create_export_folder()

    filename = f"sessions_{int(time.time())}.csv"

    filepath = os.path.join(
        "exports",
        filename
    )

    conn = sqlite3.connect("database.db")

    rows = conn.execute(
        """
        SELECT
            se.id,
            se.session_name,
            se.duration,
            se.status,
            t.name,
            se.created_at,
            (
                SELECT COUNT(*)
                FROM session_students ss
                WHERE ss.session_id=se.id
            ) AS students_joined,
            (
                SELECT COUNT(*)
                FROM doubts d
                WHERE d.session_id=se.id
            ) AS doubts_count
        FROM sessions se
        LEFT JOIN teachers t
        ON se.teacher_id=t.id
        ORDER BY se.id DESC
        """
    ).fetchall()

    conn.close()

    with open(
        filepath,
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as file:

        writer = csv.writer(file)

        writer.writerow([
            "Session ID",
            "Session Name",
            "Duration",
            "Status",
            "Teacher",
            "Created At",
            "Students Joined",
            "Doubts Count"
        ])

        for row in rows:
            writer.writerow(row)

    return redirect(
        f"/exports/{filename}"
    )