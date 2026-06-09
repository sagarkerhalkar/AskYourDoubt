from extensions import app

from flask import (
    render_template,
    request,
    redirect,
    session
)

import sqlite3


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
        "reaction",
        "chemistry"
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
# JOIN SESSION
# =====================================

@app.route("/join-session/<session_id>")
def join_session(session_id):

    return render_template(
        "student/join.html",
        session_id=session_id
    )


# =====================================
# STUDENT JOIN
# =====================================

@app.route(
    "/student-join/<session_id>",
    methods=["POST"]
)
def student_join(session_id):

    name = request.form["name"]
    mobile = request.form["mobile"]

    conn = sqlite3.connect("database.db")

    existing = conn.execute(
        """
        SELECT id
        FROM students
        WHERE mobile=?
        """,
        (mobile,)
    ).fetchone()

    if existing:

        student_id = existing[0]

    else:

        conn.execute(
            """
            INSERT INTO students(
                name,
                mobile
            )
            VALUES(?,?)
            """,
            (
                name,
                mobile
            )
        )

        conn.commit()

        student_id = conn.execute(
            "SELECT last_insert_rowid()"
        ).fetchone()[0]

    link_exists = conn.execute(
        """
        SELECT id
        FROM session_students
        WHERE session_id=?
        AND student_id=?
        """,
        (
            session_id,
            student_id
        )
    ).fetchone()

    if not link_exists:

        conn.execute(
            """
            INSERT INTO session_students(
                session_id,
                student_id
            )
            VALUES(?,?)
            """,
            (
                session_id,
                student_id
            )
        )

        conn.commit()

    conn.close()

    session["student_id"] = student_id
    session["mobile"] = mobile
    session["session_id"] = session_id

    return redirect(
        f"/student-doubts/{session_id}"
    )


# =====================================
# STUDENT DOUBTS PAGE
# =====================================

@app.route("/student-doubts/<session_id>")
def student_doubts(session_id):

    conn = sqlite3.connect("database.db")

    doubts = conn.execute(
        """
        SELECT
            id,
            question,
            votes,
            status
        FROM doubts
        WHERE session_id=?
        AND status='OPEN'
        ORDER BY votes DESC,id DESC
        """,
        (session_id,)
    ).fetchall()

    resources = conn.execute(
        """
        SELECT
            title,
            resource_type,
            file_path,
            video_url,
            notes
        FROM resources
        WHERE session_id=?
        """,
        (session_id,)
    ).fetchall()

    conn.close()

    return render_template(
        "student/doubts.html",
        doubts=doubts,
        resources=resources,
        session_id=session_id
    )


# =====================================
# SUBMIT DOUBT
# =====================================

@app.route(
    "/submit-doubt/<session_id>",
    methods=["POST"]
)
def submit_doubt(session_id):

    question = request.form["question"]

    student_id = session.get(
        "student_id"
    )

    category = detect_category(
        question
    )

    keyword = (
        question.split()[0]
        if question.strip()
        else "General"
    )

    conn = sqlite3.connect(
        "database.db"
    )

    duplicate = conn.execute(
        """
        SELECT id
        FROM doubts
        WHERE session_id=?
        AND question=?
        """,
        (
            session_id,
            question
        )
    ).fetchone()

    if duplicate:

        conn.close()

        return redirect(
            f"/student-doubts/{session_id}"
        )

    conn.execute(
        """
        INSERT INTO doubts(
            session_id,
            student_id,
            question,
            category,
            keyword,
            votes
        )
        VALUES(?,?,?,?,?,0)
        """,
        (
            session_id,
            student_id,
            question,
            category,
            keyword
        )
    )

    conn.commit()
    conn.close()

    return redirect(
        f"/student-doubts/{session_id}"
    )


# =====================================
# UPVOTE
# =====================================

@app.route(
    "/upvote/<doubt_id>"
)
def upvote(doubt_id):

    mobile = session.get(
        "mobile"
    )

    session_id = session.get(
        "session_id"
    )

    conn = sqlite3.connect(
        "database.db"
    )

    already = conn.execute(
        """
        SELECT id
        FROM doubt_votes
        WHERE doubt_id=?
        AND mobile=?
        """,
        (
            doubt_id,
            mobile
        )
    ).fetchone()

    if already:

        conn.close()

        return redirect(
            f"/student-doubts/{session_id}"
        )

    conn.execute(
        """
        INSERT INTO doubt_votes(
            doubt_id,
            mobile
        )
        VALUES(?,?)
        """,
        (
            doubt_id,
            mobile
        )
    )

    conn.execute(
        """
        UPDATE doubts
        SET votes=votes+1
        WHERE id=?
        """,
        (doubt_id,)
    )

    conn.commit()
    conn.close()

    return redirect(
        f"/student-doubts/{session_id}"
    )


# =====================================
# STUDENT LOGOUT
# =====================================

@app.route("/student-logout")
def student_logout():

    session.clear()

    return redirect("/")