from extensions import app

from flask import (
    render_template,
    request,
    redirect,
    session
)

import sqlite3
import os
import time
from werkzeug.utils import secure_filename


# =====================================
# HELPERS
# =====================================

def teacher_logged_in():
    return "teacher_id" in session


def teacher_owns_session(session_id):

    teacher_id = session.get("teacher_id")

    conn = sqlite3.connect("database.db")

    row = conn.execute(
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

    conn.close()

    return row


# =====================================
# TEACHER RESOURCES PAGE
# =====================================

@app.route("/teacher-resources/<session_id>")
def teacher_resources(session_id):

    if not teacher_logged_in():
        return redirect("/teacher-login")

    session_row = teacher_owns_session(session_id)

    if not session_row:
        return render_template(
            "message.html",
            title="Access Denied",
            message="You are not allowed to access resources for this session.",
            box_class="warning",
            button_text="Go to Teacher Dashboard",
            button_link="/teacher-dashboard"
        )

    conn = sqlite3.connect("database.db")

    resources = conn.execute(
        """
        SELECT
            id,
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
        "teacher/resources.html",
        session_id=session_id,
        session_name=session_row[1],
        resources=resources
    )


# =====================================
# UPLOAD FILE RESOURCE
# =====================================

@app.route(
    "/upload-resource/<session_id>",
    methods=["POST"]
)
def upload_resource(session_id):

    if not teacher_logged_in():
        return redirect("/teacher-login")

    session_row = teacher_owns_session(session_id)

    if not session_row:
        return "Not allowed"

    title = request.form["title"].strip()
    resource_type = request.form["resource_type"].strip()

    uploaded_file = request.files.get("file")

    if not uploaded_file or uploaded_file.filename == "":
        return redirect(
            f"/teacher-resources/{session_id}"
        )

    original_filename = secure_filename(
        uploaded_file.filename
    )

    ext = original_filename.rsplit(".", 1)[-1].lower()

    folder = ""

    if resource_type == "PDF":
        folder = "uploads/pdf"

    elif resource_type == "PPT":
        folder = "uploads/ppt"

    elif resource_type == "IMAGE":
        folder = "uploads/images"

    else:
        return redirect(
            f"/teacher-resources/{session_id}"
        )

    os.makedirs(
        folder,
        exist_ok=True
    )

    filename = f"{int(time.time())}_{original_filename}"

    save_path = os.path.join(
        folder,
        filename
    )

    uploaded_file.save(save_path)

    file_path = save_path.replace("\\", "/")

    conn = sqlite3.connect("database.db")

    conn.execute(
        """
        INSERT INTO resources(
            session_id,
            title,
            resource_type,
            file_path,
            video_url,
            notes
        )
        VALUES(?,?,?,?,?,?)
        """,
        (
            session_id,
            title,
            resource_type,
            file_path,
            "",
            ""
        )
    )

    conn.commit()
    conn.close()

    return redirect(
        f"/teacher-resources/{session_id}"
    )


# =====================================
# ADD VIDEO RESOURCE
# =====================================

@app.route(
    "/add-video-resource/<session_id>",
    methods=["POST"]
)
def add_video_resource(session_id):

    if not teacher_logged_in():
        return redirect("/teacher-login")

    session_row = teacher_owns_session(session_id)

    if not session_row:
        return "Not allowed"

    title = request.form["title"].strip()
    video_url = request.form["video_url"].strip()

    conn = sqlite3.connect("database.db")

    conn.execute(
        """
        INSERT INTO resources(
            session_id,
            title,
            resource_type,
            file_path,
            video_url,
            notes
        )
        VALUES(?,?,?,?,?,?)
        """,
        (
            session_id,
            title,
            "VIDEO",
            "",
            video_url,
            ""
        )
    )

    conn.commit()
    conn.close()

    return redirect(
        f"/teacher-resources/{session_id}"
    )


# =====================================
# ADD TEXT NOTES RESOURCE
# =====================================

@app.route(
    "/add-notes-resource/<session_id>",
    methods=["POST"]
)
def add_notes_resource(session_id):

    if not teacher_logged_in():
        return redirect("/teacher-login")

    session_row = teacher_owns_session(session_id)

    if not session_row:
        return "Not allowed"

    title = request.form["title"].strip()
    notes = request.form["notes"].strip()

    conn = sqlite3.connect("database.db")

    conn.execute(
        """
        INSERT INTO resources(
            session_id,
            title,
            resource_type,
            file_path,
            video_url,
            notes
        )
        VALUES(?,?,?,?,?,?)
        """,
        (
            session_id,
            title,
            "NOTES",
            "",
            "",
            notes
        )
    )

    conn.commit()
    conn.close()

    return redirect(
        f"/teacher-resources/{session_id}"
    )


# =====================================
# DELETE RESOURCE
# =====================================

@app.route("/delete-resource/<resource_id>/<session_id>")
def delete_resource(resource_id, session_id):

    if not teacher_logged_in():
        return redirect("/teacher-login")

    session_row = teacher_owns_session(session_id)

    if not session_row:
        return "Not allowed"

    conn = sqlite3.connect("database.db")

    resource = conn.execute(
        """
        SELECT file_path
        FROM resources
        WHERE id=?
        AND session_id=?
        """,
        (
            resource_id,
            session_id
        )
    ).fetchone()

    if resource and resource[0]:

        try:
            if os.path.exists(resource[0]):
                os.remove(resource[0])
        except:
            pass

    conn.execute(
        """
        DELETE FROM resources
        WHERE id=?
        AND session_id=?
        """,
        (
            resource_id,
            session_id
        )
    )

    conn.commit()
    conn.close()

    return redirect(
        f"/teacher-resources/{session_id}"
    )