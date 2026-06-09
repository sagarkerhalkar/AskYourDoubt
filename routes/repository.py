from extensions import app

from flask import (
    request,
    redirect,
    session,
    render_template
)

import sqlite3


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


@app.route("/teacher-question-bank/<session_id>")
def teacher_question_bank(session_id):

    if not teacher_logged_in():
        return redirect("/teacher-login")

    if not teacher_owns_session(session_id):
        return "Not allowed"

    search = request.args.get("search", "")

    conn = sqlite3.connect("database.db")

    if search:

        rows = conn.execute(
            """
            SELECT
                id,
                question,
                category,
                keyword,
                total_votes
            FROM repository
            WHERE question LIKE ?
            OR category LIKE ?
            OR keyword LIKE ?
            ORDER BY total_votes DESC,id DESC
            """,
            (
                f"%{search}%",
                f"%{search}%",
                f"%{search}%"
            )
        ).fetchall()

    else:

        rows = conn.execute(
            """
            SELECT
                id,
                question,
                category,
                keyword,
                total_votes
            FROM repository
            ORDER BY total_votes DESC,id DESC
            LIMIT 100
            """
        ).fetchall()

    conn.close()

    return render_template(
        "teacher/question_bank.html",
        rows=rows,
        session_id=session_id,
        search=search
    )


@app.route("/add-bank-question-to-session/<repo_id>/<session_id>")
def add_bank_question_to_session(repo_id, session_id):

    if not teacher_logged_in():
        return redirect("/teacher-login")

    if not teacher_owns_session(session_id):
        return "Not allowed"

    conn = sqlite3.connect("database.db")

    row = conn.execute(
        """
        SELECT
            question,
            category,
            keyword,
            total_votes
        FROM repository
        WHERE id=?
        """,
        (repo_id,)
    ).fetchone()

    if not row:
        conn.close()
        return "Question not found"

    conn.execute(
        """
        INSERT INTO doubts(
            session_id,
            student_id,
            question,
            category,
            keyword,
            votes,
            status
        )
        VALUES(?,?,?,?,?,?,'OPEN')
        """,
        (
            session_id,
            None,
            row[0],
            row[1],
            row[2],
            0
        )
    )

    conn.commit()
    conn.close()

    return redirect(
        f"/teacher-session/{session_id}"
    )


@app.route("/sync-completed-to-bank/<session_id>")
def sync_completed_to_bank(session_id):

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
            votes
        FROM doubts
        WHERE session_id=?
        AND status='COMPLETED'
        """,
        (session_id,)
    ).fetchall()

    for row in rows:

        existing = conn.execute(
            """
            SELECT id,total_votes,total_sessions
            FROM repository
            WHERE question=?
            """,
            (row[0],)
        ).fetchone()

        if existing:

            conn.execute(
                """
                UPDATE repository
                SET
                    total_votes=?,
                    total_sessions=?
                WHERE id=?
                """,
                (
                    existing[1] + row[3],
                    existing[2] + 1,
                    existing[0]
                )
            )

        else:

            conn.execute(
                """
                INSERT INTO repository(
                    question,
                    category,
                    keyword,
                    total_votes,
                    total_sessions
                )
                VALUES(?,?,?,?,1)
                """,
                (
                    row[0],
                    row[1],
                    row[2],
                    row[3]
                )
            )

    conn.commit()
    conn.close()

    return redirect(
        f"/teacher-question-bank/{session_id}"
    )


@app.route("/admin-question-bank")
def admin_question_bank():

    if not admin_logged_in():
        return redirect("/admin-login")

    search = request.args.get("search", "")

    conn = sqlite3.connect("database.db")

    if search:

        rows = conn.execute(
            """
            SELECT
                id,
                question,
                category,
                keyword,
                total_votes,
                total_sessions
            FROM repository
            WHERE question LIKE ?
            OR category LIKE ?
            OR keyword LIKE ?
            ORDER BY total_votes DESC,id DESC
            """,
            (
                f"%{search}%",
                f"%{search}%",
                f"%{search}%"
            )
        ).fetchall()

    else:

        rows = conn.execute(
            """
            SELECT
                id,
                question,
                category,
                keyword,
                total_votes,
                total_sessions
            FROM repository
            ORDER BY total_votes DESC,id DESC
            """
        ).fetchall()

    conn.close()

    return render_template(
        "admin/question_bank.html",
        rows=rows,
        search=search
    )