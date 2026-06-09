from extensions import app

from flask import (
    render_template,
    request,
    redirect,
    session,
    jsonify
)

import sqlite3
import re


# =====================================
# CATEGORY DETECTION
# =====================================

def detect_category(question):

    q = question.lower()

    if any(word in q for word in [
        "force", "motion", "newton", "velocity", "acceleration",
        "gravity", "energy", "light", "sound", "electricity",
        "magnet", "physics"
    ]):
        return "Physics"

    if any(word in q for word in [
        "math", "equation", "quadratic", "algebra", "geometry",
        "trigonometry", "calculus", "derivative", "integration",
        "percentage", "ratio", "profit", "loss"
    ]):
        return "Mathematics"

    if any(word in q for word in [
        "atom", "molecule", "reaction", "chemistry", "acid",
        "base", "salt", "compound", "chemical", "bond"
    ]):
        return "Chemistry"

    if any(word in q for word in [
        "cell", "biology", "human body", "uterus", "heart",
        "brain", "blood", "plant", "animal", "photosynthesis",
        "respiration"
    ]):
        return "Biology"

    if any(word in q for word in [
        "history", "geography", "civics", "constitution",
        "government", "economics"
    ]):
        return "Social Science"

    if any(word in q for word in [
        "python", "java", "html", "css", "javascript",
        "coding", "program", "computer", "software", "database"
    ]):
        return "Computer"

    return "General"


# =====================================
# KEYWORD EXTRACTION
# =====================================

def extract_keyword(question):

    stop_words = {
        "what", "why", "how", "when", "where", "which",
        "is", "are", "am", "the", "a", "an", "of", "to",
        "in", "on", "for", "and", "or", "explain", "define",
        "meaning", "difference", "between", "tell", "me",
        "sir", "mam", "madam", "please", "your", "this",
        "that", "with", "from"
    }

    words = re.findall(
        r"[a-zA-Z]+",
        question.lower()
    )

    for word in words:
        if len(word) >= 4 and word not in stop_words:
            return word.capitalize()

    return "General"


# =====================================
# SIMILAR DOUBT DETECTION
# =====================================

def clean_question_text(text):

    text = text.lower()

    text = re.sub(
        r"[^a-z0-9\s]",
        "",
        text
    )

    stop_words = {
        "what", "why", "how", "when", "where", "which",
        "is", "are", "am", "the", "a", "an", "of", "to",
        "in", "on", "for", "and", "or", "explain", "define",
        "meaning", "difference", "between", "tell", "me",
        "sir", "mam", "madam", "please", "your", "this",
        "that", "with", "from"
    }

    words = text.split()

    words = [
        word
        for word in words
        if word not in stop_words
        and len(word) >= 3
    ]

    return words


def find_similar_doubts(session_id, question):

    new_words = clean_question_text(question)

    if len(new_words) == 0:
        return []

    conn = sqlite3.connect("database.db")

    rows = conn.execute(
        """
        SELECT
            id,
            question,
            votes
        FROM doubts
        WHERE session_id=?
        AND status='OPEN'
        ORDER BY votes DESC,id DESC
        """,
        (session_id,)
    ).fetchall()

    conn.close()

    similar = []

    for row in rows:

        old_words = clean_question_text(row[1])

        if len(old_words) == 0:
            continue

        match_count = 0

        for word in new_words:

            if word in old_words:
                match_count = match_count + 1

        score = match_count / max(
            len(new_words),
            1
        )

        if score >= 0.5:
            similar.append(row)

    return similar[:5]


# =====================================
# CLEAR ONLY STUDENT SESSION
# =====================================

def clear_student_session():

    session.pop("student_id", None)
    session.pop("student_name", None)
    session.pop("mobile", None)
    session.pop("session_id", None)


# =====================================
# JOIN SESSION PAGE
# =====================================

@app.route("/join-session/<session_id>")
def join_session(session_id):

    conn = sqlite3.connect("database.db")

    row = conn.execute(
        """
        SELECT
            session_name,
            status
        FROM sessions
        WHERE id=?
        """,
        (session_id,)
    ).fetchone()

    conn.close()

    if not row:
      return render_template(
    "message.html",
    title="Session Not Found",
    message="This session does not exist. Please check the session ID or ask your teacher.",
    box_class="warning",
    button_text="Back to Student Portal",
    button_link="/student"
)

    session_name = row[0]
    session_status = row[1]

    return render_template(
        "student/join.html",
        session_id=session_id,
        session_name=session_name,
        session_status=session_status
    )


# =====================================
# STUDENT JOIN
# =====================================

@app.route(
    "/student-join/<session_id>",
    methods=["POST"]
)
def student_join(session_id):

    name = request.form["name"].strip()
    mobile = request.form["mobile"].strip()

    conn = sqlite3.connect("database.db")

    session_row = conn.execute(
        """
        SELECT status
        FROM sessions
        WHERE id=?
        """,
        (session_id,)
    ).fetchone()

    if not session_row:
        conn.close()
        return "Session not found"

    if session_row[0] != "ACTIVE":
        conn.close()
        return redirect(
            f"/session-ended/{session_id}"
        )

    existing_student = conn.execute(
        """
        SELECT id
        FROM students
        WHERE mobile=?
        """,
        (mobile,)
    ).fetchone()

    if existing_student:

        student_id = existing_student[0]

        conn.execute(
            """
            UPDATE students
            SET name=?
            WHERE id=?
            """,
            (
                name,
                student_id
            )
        )

        conn.commit()

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

    already_joined = conn.execute(
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

    if not already_joined:

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
    session["student_name"] = name
    session["mobile"] = mobile
    session["session_id"] = session_id

    return redirect(
        f"/student-doubts/{session_id}"
    )


# =====================================
# STUDENT MAIN PAGE
# =====================================

@app.route("/student-doubts/<session_id>")
def student_doubts(session_id):

    if "student_id" not in session:
        return redirect(
            f"/join-session/{session_id}"
        )

    conn = sqlite3.connect("database.db")

    session_row = conn.execute(
        """
        SELECT
            session_name,
            status
        FROM sessions
        WHERE id=?
        """,
        (session_id,)
    ).fetchone()

    if not session_row:
        conn.close()
        return "Session not found"

    session_name = session_row[0]
    session_status = session_row[1]

    if session_status != "ACTIVE":
        conn.close()
        return redirect(
            f"/session-ended/{session_id}"
        )

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
        ORDER BY id DESC
        """,
        (session_id,)
    ).fetchall()

    conn.close()

    return render_template(
        "student/doubts.html",
        session_id=session_id,
        session_name=session_name,
        session_status=session_status,
        resources=resources,
        student_name=session.get("student_name", "")
    )


# =====================================
# AJAX SESSION STATUS CHECK
# =====================================

@app.route("/student-session-status/<session_id>")
def student_session_status(session_id):

    conn = sqlite3.connect("database.db")

    row = conn.execute(
        """
        SELECT
            session_name,
            status
        FROM sessions
        WHERE id=?
        """,
        (session_id,)
    ).fetchone()

    conn.close()

    if not row:
        return jsonify({
            "status": "NOT_FOUND",
            "session_name": ""
        })

    return jsonify({
        "status": row[1],
        "session_name": row[0]
    })


# =====================================
# SESSION ENDED PAGE
# =====================================

@app.route("/session-ended/<session_id>")
def session_ended(session_id):

    conn = sqlite3.connect("database.db")

    row = conn.execute(
        """
        SELECT session_name
        FROM sessions
        WHERE id=?
        """,
        (session_id,)
    ).fetchone()

    conn.close()

    session_name = "This Session"

    if row:
        session_name = row[0]

    clear_student_session()

    return render_template(
        "student/session_ended.html",
        session_id=session_id,
        session_name=session_name
    )


# =====================================
# AJAX DOUBT LIST
# =====================================

@app.route("/student-doubt-list/<session_id>")
def student_doubt_list(session_id):

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
        AND status!='SKIPPED'
        ORDER BY
            CASE
                WHEN status='OPEN' THEN 1
                WHEN status='COMPLETED' THEN 2
                ELSE 3
            END,
            votes DESC,
            id DESC
        """,
        (session_id,)
    ).fetchall()

    conn.close()

    html = ""

    if len(doubts) == 0:

        html += """
        <div class="student-empty">
            No doubts yet. Be the first student to ask a question.
        </div>
        """

    for doubt in doubts:

        doubt_id = doubt[0]
        question = doubt[1]
        votes = doubt[2]
        status = doubt[3]

        if status == "COMPLETED":

            html += f"""
            <div class="student-live-card completed">

                <span class="badge badge-green">
                    Answered in Class
                </span>

                <span class="badge">
                    Votes: {votes}
                </span>

                <div class="student-question">
                    {question}
                </div>

            </div>
            """

        else:

            html += f"""
            <div class="student-live-card">

                <span class="badge">
                    Open
                </span>

                <span class="badge">
                    Votes: {votes}
                </span>

                <div class="student-question">
                    {question}
                </div>

                <a class="btn" href="/upvote/{doubt_id}">
                    👍 I Have Same Doubt
                </a>

            </div>
            """

    return html


# =====================================
# SUBMIT DOUBT
# =====================================

@app.route(
    "/submit-doubt/<session_id>",
    methods=["POST"]
)
def submit_doubt(session_id):

    if "student_id" not in session:
        return redirect(
            f"/join-session/{session_id}"
        )

    question = request.form["question"].strip()

    if question == "":
        return redirect(
            f"/student-doubts/{session_id}"
        )

    conn = sqlite3.connect("database.db")

    session_row = conn.execute(
        """
        SELECT status
        FROM sessions
        WHERE id=?
        """,
        (session_id,)
    ).fetchone()

    conn.close()

    if not session_row:
        return "Session not found"

    if session_row[0] != "ACTIVE":
        return redirect(
            f"/session-ended/{session_id}"
        )

    similar_doubts = find_similar_doubts(
        session_id,
        question
    )

    if len(similar_doubts) > 0:

        return render_template(
            "student/similar_doubts.html",
            session_id=session_id,
            question=question,
            similar_doubts=similar_doubts
        )

    return save_student_doubt(
        session_id,
        question
    )


# =====================================
# SAVE DOUBT
# =====================================

def save_student_doubt(session_id, question):

    student_id = session.get("student_id")

    category = detect_category(question)
    keyword = extract_keyword(question)

    conn = sqlite3.connect("database.db")

    session_row = conn.execute(
        """
        SELECT status
        FROM sessions
        WHERE id=?
        """,
        (session_id,)
    ).fetchone()

    if not session_row:
        conn.close()
        return "Session not found"

    if session_row[0] != "ACTIVE":
        conn.close()
        return redirect(
            f"/session-ended/{session_id}"
        )

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
        VALUES(?,?,?,?,?,0,'OPEN')
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
# SUBMIT ANYWAY
# =====================================

@app.route(
    "/submit-doubt-anyway/<session_id>",
    methods=["POST"]
)
def submit_doubt_anyway(session_id):

    if "student_id" not in session:
        return redirect(
            f"/join-session/{session_id}"
        )

    question = request.form["question"].strip()

    if question == "":
        return redirect(
            f"/student-doubts/{session_id}"
        )

    return save_student_doubt(
        session_id,
        question
    )


# =====================================
# UPVOTE
# =====================================

@app.route("/upvote/<doubt_id>")
def upvote(doubt_id):

    mobile = session.get("mobile")
    session_id = session.get("session_id")

    if not mobile or not session_id:
        return redirect("/")

    conn = sqlite3.connect("database.db")

    session_row = conn.execute(
        """
        SELECT status
        FROM sessions
        WHERE id=?
        """,
        (session_id,)
    ).fetchone()

    if not session_row:
        conn.close()
        return redirect("/")

    if session_row[0] != "ACTIVE":
        conn.close()
        return redirect(
            f"/session-ended/{session_id}"
        )

    doubt = conn.execute(
        """
        SELECT
            session_id,
            status
        FROM doubts
        WHERE id=?
        """,
        (doubt_id,)
    ).fetchone()

    if not doubt:
        conn.close()
        return redirect(
            f"/student-doubts/{session_id}"
        )

    doubt_session_id = str(doubt[0])
    doubt_status = doubt[1]

    if doubt_session_id != str(session_id):
        conn.close()
        return redirect(
            f"/student-doubts/{session_id}"
        )

    if doubt_status != "OPEN":
        conn.close()
        return redirect(
            f"/student-doubts/{session_id}"
        )

    already_voted = conn.execute(
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

    if already_voted:
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
        SET votes = votes + 1
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
# LOGOUT
# =====================================

@app.route("/student-logout")
def student_logout():

    clear_student_session()

    return redirect("/")