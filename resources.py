from extensions import app

from flask import (
    render_template,
    request,
    redirect,
    session
)

from werkzeug.utils import secure_filename

import sqlite3
import os
import time


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


def save_uploaded_file(file, resource_type):

    original_name = secure_filename(file.filename)

    timestamp = str(int(time.time()))

    filename = timestamp + "_" + original_name

    if resource_type == "PDF":

        folder = "uploads/pdf"

    elif resource_type == "PPT":

        folder = "uploads/ppt"

    elif resource_type == "IMAGE":

        folder = "uploads/images"

    else:

        folder = "uploads"

    os.makedirs(folder, exist_ok=True)

    full_path = os.path.join(
        folder,
        filename
    )

    file.save(full_path)

    return full_path.replace("\\", "/")


# =====================================
# RESOURCE PAGE
# =====================================

@app.route("/teacher-resources/<session_id>")
def teacher_resources(session_id):

    if not teacher_logged_in():
        return redirect("/teacher-login")

    if not teacher_owns_session(session_id):
        return "Not allowed"

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

    if not teacher_owns_session(session_id):
        return "Not allowed"

    title = request.form["title"]
    resource_type = request.form["resource_type"]

    file = request.files.get("file")

    if not file or file.filename == "":
        return "No file selected"

    file_path = save_uploaded_file(
        file,
        resource_type
    )

    conn = sqlite3.connect("database.db")

    conn.execute(
        """
        INSERT INTO resources(
            session_id,
            title,
            resource_type,
            file_path
        )
        VALUES(?,?,?,?)
        """,
        (
            session_id,
            title,
            resource_type,
            file_path
        )
    )

    conn.commit()
    conn.close()

    return redirect(
        f"/teacher-resources/{session_id}"
    )


# =====================================
# ADD VIDEO LINK
# =====================================

@app.route(
    "/add-video-resource/<session_id>",
    methods=["POST"]
)
def add_video_resource(session_id):

    if not teacher_logged_in():
        return redirect("/teacher-login")

    if not teacher_owns_session(session_id):
        return "Not allowed"

    title = request.form["title"]
    video_url = request.form["video_url"]

    conn = sqlite3.connect("database.db")

    conn.execute(
        """
        INSERT INTO resources(
            session_id,
            title,
            resource_type,
            video_url
        )
        VALUES(?,?,?,?)
        """,
        (
            session_id,
            title,
            "VIDEO",
            video_url
        )
    )

    conn.commit()
    conn.close()

    return redirect(
        f"/teacher-resources/{session_id}"
    )


# =====================================
# ADD NOTES
# =====================================

@app.route(
    "/add-notes-resource/<session_id>",
    methods=["POST"]
)
def add_notes_resource(session_id):

    if not teacher_logged_in():
        return redirect("/teacher-login")

    if not teacher_owns_session(session_id):
        return "Not allowed"

    title = request.form["title"]
    notes = request.form["notes"]

    conn = sqlite3.connect("database.db")

    conn.execute(
        """
        INSERT INTO resources(
            session_id,
            title,
            resource_type,
            notes
        )
        VALUES(?,?,?,?)
        """,
        (
            session_id,
            title,
            "NOTES",
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

@app.route(
    "/delete-resource/<resource_id>/<session_id>"
)
def delete_resource(resource_id, session_id):

    if not teacher_logged_in():
        return redirect("/teacher-login")

    if not teacher_owns_session(session_id):
        return "Not allowed"

    conn = sqlite3.connect("database.db")

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