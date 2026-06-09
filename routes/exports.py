from extensions import app

from flask import (
    redirect,
    session
)

import sqlite3
import csv
import os
import time
import zipfile


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


def write_csv(filename, headers, rows):

    create_export_folder()

    filepath = os.path.join(
        "exports",
        filename
    )

    with open(
        filepath,
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as file:

        writer = csv.writer(file)

        writer.writerow(headers)

        for row in rows:
            writer.writerow(row)

    return filepath


# =====================================
# TEACHER EXPORT
# Teacher only gets limited data
# =====================================

@app.route("/export-session-questions/<session_id>")
def export_session_questions(session_id):

    if not teacher_logged_in():
        return redirect("/teacher-login")

    if not teacher_owns_session(session_id):
        return "Not allowed"

    conn = sqlite3.connect("database.db")

    rows = conn.execute(
        """
        SELECT
            question,
            category,
            keyword,
            votes,
            status
        FROM doubts
        WHERE session_id=?
        ORDER BY votes DESC,id DESC
        """,
        (session_id,)
    ).fetchall()

    conn.close()

    filename = f"teacher_session_{session_id}_questions_{int(time.time())}.csv"

    write_csv(
        filename,
        [
            "Question",
            "Category",
            "Keyword",
            "Votes",
            "Status"
        ],
        rows
    )

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

    conn = sqlite3.connect("database.db")

    rows = conn.execute(
        """
        SELECT
            d.id,
            d.session_id,
            se.session_name,
            t.name,
            d.question,
            d.category,
            d.keyword,
            d.votes,
            d.status,
            st.name,
            st.mobile,
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

    filename = f"admin_all_questions_{int(time.time())}.csv"

    write_csv(
        filename,
        [
            "Doubt ID",
            "Session ID",
            "Session Name",
            "Teacher Name",
            "Question",
            "Category",
            "Keyword",
            "Votes",
            "Status",
            "Student Name",
            "Student Mobile",
            "Created At"
        ],
        rows
    )

    return redirect(
        f"/exports/{filename}"
    )


# =====================================
# ADMIN EXPORT SESSION-WISE QUESTIONS
# =====================================

@app.route("/admin-export-session-questions/<session_id>")
def admin_export_session_questions(session_id):

    if not admin_logged_in():
        return redirect("/admin-login")

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
            st.name,
            st.mobile,
            t.name,
            se.session_name,
            d.created_at
        FROM doubts d
        LEFT JOIN students st
        ON d.student_id=st.id
        LEFT JOIN sessions se
        ON d.session_id=se.id
        LEFT JOIN teachers t
        ON se.teacher_id=t.id
        WHERE d.session_id=?
        ORDER BY d.votes DESC,d.id DESC
        """,
        (session_id,)
    ).fetchall()

    session_name = conn.execute(
        """
        SELECT session_name
        FROM sessions
        WHERE id=?
        """,
        (session_id,)
    ).fetchone()

    conn.close()

    clean_name = "session"

    if session_name:
        clean_name = str(session_name[0]).replace(" ", "_")

    filename = f"admin_session_{session_id}_{clean_name}_questions_{int(time.time())}.csv"

    write_csv(
        filename,
        [
            "Doubt ID",
            "Question",
            "Category",
            "Keyword",
            "Votes",
            "Status",
            "Student Name",
            "Student Mobile",
            "Teacher Name",
            "Session Name",
            "Created At"
        ],
        rows
    )

    return redirect(
        f"/exports/{filename}"
    )


# =====================================
# ADMIN EXPORT TEACHER-WISE QUESTIONS
# =====================================

@app.route("/admin-export-teacher-questions/<teacher_id>")
def admin_export_teacher_questions(teacher_id):

    if not admin_logged_in():
        return redirect("/admin-login")

    conn = sqlite3.connect("database.db")

    rows = conn.execute(
        """
        SELECT
            d.id,
            d.session_id,
            se.session_name,
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
        WHERE se.teacher_id=?
        ORDER BY d.id DESC
        """,
        (teacher_id,)
    ).fetchall()

    teacher_name = conn.execute(
        """
        SELECT name
        FROM teachers
        WHERE id=?
        """,
        (teacher_id,)
    ).fetchone()

    conn.close()

    clean_name = "teacher"

    if teacher_name:
        clean_name = str(teacher_name[0]).replace(" ", "_")

    filename = f"admin_teacher_{teacher_id}_{clean_name}_questions_{int(time.time())}.csv"

    write_csv(
        filename,
        [
            "Doubt ID",
            "Session ID",
            "Session Name",
            "Question",
            "Category",
            "Keyword",
            "Votes",
            "Status",
            "Student Name",
            "Student Mobile",
            "Teacher Name",
            "Created At"
        ],
        rows
    )

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

    conn = sqlite3.connect("database.db")

    rows = conn.execute(
        """
        SELECT
            st.id,
            st.name,
            st.mobile,
            st.created_at,
            (
                SELECT COUNT(*)
                FROM session_students ss
                WHERE ss.student_id=st.id
            ) AS sessions_joined,
            (
                SELECT COUNT(*)
                FROM doubts d
                WHERE d.student_id=st.id
            ) AS questions_asked
        FROM students st
        ORDER BY st.id DESC
        """
    ).fetchall()

    conn.close()

    filename = f"admin_students_{int(time.time())}.csv"

    write_csv(
        filename,
        [
            "Student ID",
            "Student Name",
            "Mobile",
            "Created At",
            "Sessions Joined",
            "Questions Asked"
        ],
        rows
    )

    return redirect(
        f"/exports/{filename}"
    )


# =====================================
# ADMIN EXPORT SESSIONS SUMMARY
# =====================================

@app.route("/admin-export-sessions")
def admin_export_sessions():

    if not admin_logged_in():
        return redirect("/admin-login")

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
            ) AS total_doubts,
            (
                SELECT COUNT(*)
                FROM doubts d
                WHERE d.session_id=se.id
                AND d.status='OPEN'
            ) AS open_doubts,
            (
                SELECT COUNT(*)
                FROM doubts d
                WHERE d.session_id=se.id
                AND d.status='COMPLETED'
            ) AS completed_doubts,
            (
                SELECT COUNT(*)
                FROM doubts d
                WHERE d.session_id=se.id
                AND d.status='SKIPPED'
            ) AS skipped_doubts
        FROM sessions se
        LEFT JOIN teachers t
        ON se.teacher_id=t.id
        ORDER BY se.id DESC
        """
    ).fetchall()

    conn.close()

    filename = f"admin_sessions_summary_{int(time.time())}.csv"

    write_csv(
        filename,
        [
            "Session ID",
            "Session Name",
            "Duration",
            "Status",
            "Teacher Name",
            "Created At",
            "Students Joined",
            "Total Doubts",
            "Open Doubts",
            "Completed Doubts",
            "Skipped Doubts"
        ],
        rows
    )

    return redirect(
        f"/exports/{filename}"
    )


# =====================================
# ADMIN EXPORT TEACHERS SUMMARY
# =====================================

@app.route("/admin-export-teachers")
def admin_export_teachers():

    if not admin_logged_in():
        return redirect("/admin-login")

    conn = sqlite3.connect("database.db")

    rows = conn.execute(
        """
        SELECT
            t.id,
            t.name,
            t.username,
            t.status,
            (
                SELECT COUNT(*)
                FROM sessions se
                WHERE se.teacher_id=t.id
            ) AS total_sessions,
            (
                SELECT COUNT(*)
                FROM session_students ss
                JOIN sessions se
                ON ss.session_id=se.id
                WHERE se.teacher_id=t.id
            ) AS total_students,
            (
                SELECT COUNT(*)
                FROM doubts d
                JOIN sessions se
                ON d.session_id=se.id
                WHERE se.teacher_id=t.id
            ) AS total_doubts,
            (
                SELECT COUNT(*)
                FROM doubts d
                JOIN sessions se
                ON d.session_id=se.id
                WHERE se.teacher_id=t.id
                AND d.status='COMPLETED'
            ) AS completed_doubts,
            (
                SELECT COUNT(*)
                FROM doubts d
                JOIN sessions se
                ON d.session_id=se.id
                WHERE se.teacher_id=t.id
                AND d.status='SKIPPED'
            ) AS skipped_doubts
        FROM teachers t
        ORDER BY t.id DESC
        """
    ).fetchall()

    conn.close()

    filename = f"admin_teachers_summary_{int(time.time())}.csv"

    write_csv(
        filename,
        [
            "Teacher ID",
            "Teacher Name",
            "Username",
            "Status",
            "Total Sessions",
            "Total Students",
            "Total Doubts",
            "Completed Doubts",
            "Skipped Doubts"
        ],
        rows
    )

    return redirect(
        f"/exports/{filename}"
    )


# =====================================
# ADMIN EXPORT ANALYTICS SUMMARY
# =====================================

@app.route("/admin-export-analytics")
def admin_export_analytics():

    if not admin_logged_in():
        return redirect("/admin-login")

    conn = sqlite3.connect("database.db")

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

    open_doubts = conn.execute(
        """
        SELECT COUNT(*)
        FROM doubts
        WHERE status='OPEN'
        """
    ).fetchone()[0]

    completed_doubts = conn.execute(
        """
        SELECT COUNT(*)
        FROM doubts
        WHERE status='COMPLETED'
        """
    ).fetchone()[0]

    skipped_doubts = conn.execute(
        """
        SELECT COUNT(*)
        FROM doubts
        WHERE status='SKIPPED'
        """
    ).fetchone()[0]

    category_rows = conn.execute(
        """
        SELECT category, COUNT(*)
        FROM doubts
        GROUP BY category
        ORDER BY COUNT(*) DESC
        """
    ).fetchall()

    keyword_rows = conn.execute(
        """
        SELECT keyword, COUNT(*)
        FROM doubts
        GROUP BY keyword
        ORDER BY COUNT(*) DESC
        LIMIT 50
        """
    ).fetchall()

    teacher_rows = conn.execute(
        """
        SELECT
            t.name,
            COUNT(d.id)
        FROM teachers t
        LEFT JOIN sessions se
        ON se.teacher_id=t.id
        LEFT JOIN doubts d
        ON d.session_id=se.id
        GROUP BY t.id
        ORDER BY COUNT(d.id) DESC
        """
    ).fetchall()

    conn.close()

    rows = []

    rows.append(["TOTAL TEACHERS", total_teachers])
    rows.append(["TOTAL SESSIONS", total_sessions])
    rows.append(["TOTAL STUDENTS", total_students])
    rows.append(["TOTAL DOUBTS", total_doubts])
    rows.append(["OPEN DOUBTS", open_doubts])
    rows.append(["COMPLETED DOUBTS", completed_doubts])
    rows.append(["SKIPPED DOUBTS", skipped_doubts])

    rows.append([])
    rows.append(["CATEGORY ANALYTICS"])
    rows.append(["Category", "Count"])

    for row in category_rows:
        rows.append([row[0], row[1]])

    rows.append([])
    rows.append(["KEYWORD ANALYTICS"])
    rows.append(["Keyword", "Count"])

    for row in keyword_rows:
        rows.append([row[0], row[1]])

    rows.append([])
    rows.append(["TEACHER-WISE DOUBTS"])
    rows.append(["Teacher", "Total Doubts"])

    for row in teacher_rows:
        rows.append([row[0], row[1]])

    filename = f"admin_analytics_summary_{int(time.time())}.csv"

    write_csv(
        filename,
        [
            "Metric",
            "Value"
        ],
        rows
    )

    return redirect(
        f"/exports/{filename}"
    )


# =====================================
# ADMIN EXPORT FULL DATA ZIP
# =====================================

@app.route("/admin-export-full-data")
def admin_export_full_data():

    if not admin_logged_in():
        return redirect("/admin-login")

    create_export_folder()

    timestamp = int(time.time())

    zip_filename = f"admin_full_data_{timestamp}.zip"

    zip_path = os.path.join(
        "exports",
        zip_filename
    )

    conn = sqlite3.connect("database.db")

    export_files = []

    datasets = [
        (
            f"all_questions_{timestamp}.csv",
            [
                "Doubt ID",
                "Session ID",
                "Session Name",
                "Teacher Name",
                "Question",
                "Category",
                "Keyword",
                "Votes",
                "Status",
                "Student Name",
                "Student Mobile",
                "Created At"
            ],
            conn.execute(
                """
                SELECT
                    d.id,
                    d.session_id,
                    se.session_name,
                    t.name,
                    d.question,
                    d.category,
                    d.keyword,
                    d.votes,
                    d.status,
                    st.name,
                    st.mobile,
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
        ),
        (
            f"sessions_summary_{timestamp}.csv",
            [
                "Session ID",
                "Session Name",
                "Duration",
                "Status",
                "Teacher Name",
                "Created At"
            ],
            conn.execute(
                """
                SELECT
                    se.id,
                    se.session_name,
                    se.duration,
                    se.status,
                    t.name,
                    se.created_at
                FROM sessions se
                LEFT JOIN teachers t
                ON se.teacher_id=t.id
                ORDER BY se.id DESC
                """
            ).fetchall()
        ),
        (
            f"students_{timestamp}.csv",
            [
                "Student ID",
                "Student Name",
                "Mobile",
                "Created At"
            ],
            conn.execute(
                """
                SELECT
                    id,
                    name,
                    mobile,
                    created_at
                FROM students
                ORDER BY id DESC
                """
            ).fetchall()
        ),
        (
            f"teachers_{timestamp}.csv",
            [
                "Teacher ID",
                "Teacher Name",
                "Username",
                "Status"
            ],
            conn.execute(
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
        ),
        (
            f"teacher_activity_{timestamp}.csv",
            [
                "Activity ID",
                "Teacher Name",
                "Activity",
                "Created At"
            ],
            conn.execute(
                """
                SELECT
                    ta.id,
                    t.name,
                    ta.activity,
                    ta.created_at
                FROM teacher_activity ta
                LEFT JOIN teachers t
                ON ta.teacher_id=t.id
                ORDER BY ta.id DESC
                """
            ).fetchall()
        ),
        (
            f"resources_{timestamp}.csv",
            [
                "Resource ID",
                "Session ID",
                "Title",
                "Type",
                "File Path",
                "Video URL",
                "Notes"
            ],
            conn.execute(
                """
                SELECT
                    id,
                    session_id,
                    title,
                    resource_type,
                    file_path,
                    video_url,
                    notes
                FROM resources
                ORDER BY id DESC
                """
            ).fetchall()
        )
    ]

    conn.close()

    for dataset in datasets:

        file_name = dataset[0]
        headers = dataset[1]
        rows = dataset[2]

        write_csv(
            file_name,
            headers,
            rows
        )

        export_files.append(
            os.path.join("exports", file_name)
        )

    with zipfile.ZipFile(
        zip_path,
        "w",
        zipfile.ZIP_DEFLATED
    ) as zip_file:

        for file_path in export_files:

            zip_file.write(
                file_path,
                os.path.basename(file_path)
            )

    return redirect(
        f"/exports/{zip_filename}"
    )