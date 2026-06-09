from extensions import app

from flask import (
    send_from_directory,
    render_template,
    request,
    redirect
)

import os


# =====================================
# CREATE REQUIRED FOLDERS
# =====================================

os.makedirs("uploads", exist_ok=True)
os.makedirs("uploads/pdf", exist_ok=True)
os.makedirs("uploads/ppt", exist_ok=True)
os.makedirs("uploads/images", exist_ok=True)
os.makedirs("static", exist_ok=True)
os.makedirs("static/css", exist_ok=True)
os.makedirs("static/qr", exist_ok=True)
os.makedirs("exports", exist_ok=True)


# =====================================
# PUBLIC HOME PAGE
# =====================================

@app.route("/")
def home():

    return render_template(
        "index.html"
    )


# =====================================
# STUDENT ENTRY PAGE
# =====================================

@app.route(
    "/student",
    methods=["GET", "POST"]
)
def student_start():

    if request.method == "POST":

        session_id = request.form["session_id"].strip()

        if session_id:
            return redirect(
                f"/join-session/{session_id}"
            )

    return render_template(
        "student/start.html"
    )


# =====================================
# UPLOAD FILE SERVING
# =====================================

@app.route("/uploads/<folder>/<filename>")
def uploaded_file(folder, filename):

    return send_from_directory(
        os.path.join("uploads", folder),
        filename
    )


# =====================================
# EXPORT FILE SERVING
# =====================================

@app.route("/exports/<filename>")
def export_file(filename):

    return send_from_directory(
        "exports",
        filename,
        as_attachment=True
    )


# =====================================
# ROUTE IMPORTS
# =====================================

import routes.admin
import routes.teacher
import routes.student
import routes.resources
import routes.exports
import routes.repository
import routes.admin_controls


# =====================================
# RUN APP
# =====================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=9000,
        debug=True
    )