from extensions import app

from flask import (
    render_template,
    request,
    redirect,
    session
)

import sqlite3


# =====================================
# HELPERS
# =====================================

def admin_logged_in():
    return session.get("admin") == True


def teacher_logged_in():
    return "teacher_id" in session


# =====================================
# ADMIN CHANGE OWN PASSWORD
# =====================================

@app.route(
    "/admin-change-password",
    methods=["GET", "POST"]
)
def admin_change_password():

    if not admin_logged_in():
        return redirect("/admin-login")

    if request.method == "GET":

        return render_template(
            "admin/change_password.html"
        )

    current_password = request.form["current_password"].strip()
    new_password = request.form["new_password"].strip()
    confirm_password = request.form["confirm_password"].strip()

    if new_password != confirm_password:

        return render_template(
            "message.html",
            title="Password Not Matched",
            message="New password and confirm password are not same.",
            box_class="warning",
            button_text="Try Again",
            button_link="/admin-change-password"
        )

    if len(new_password) < 4:

        return render_template(
            "message.html",
            title="Weak Password",
            message="Password must be at least 4 characters.",
            box_class="warning",
            button_text="Try Again",
            button_link="/admin-change-password"
        )

    conn = sqlite3.connect("database.db")

    row = conn.execute(
        """
        SELECT id
        FROM admins
        WHERE id=1
        AND password=?
        """,
        (current_password,)
    ).fetchone()

    if not row:

        conn.close()

        return render_template(
            "message.html",
            title="Wrong Current Password",
            message="Your current admin password is incorrect.",
            box_class="warning",
            button_text="Try Again",
            button_link="/admin-change-password"
        )

    conn.execute(
        """
        UPDATE admins
        SET password=?
        WHERE id=1
        """,
        (new_password,)
    )

    conn.commit()
    conn.close()

    return render_template(
        "message.html",
        title="Password Changed",
        message="Admin password changed successfully.",
        box_class="notice",
        button_text="Go to Admin Dashboard",
        button_link="/admin-dashboard"
    )


# =====================================
# TEACHER CHANGE OWN PASSWORD
# =====================================

@app.route(
    "/teacher-change-password",
    methods=["GET", "POST"]
)
def teacher_change_password():

    if not teacher_logged_in():
        return redirect("/teacher-login")

    teacher_id = session["teacher_id"]

    if request.method == "GET":

        return render_template(
            "teacher/change_password.html"
        )

    current_password = request.form["current_password"].strip()
    new_password = request.form["new_password"].strip()
    confirm_password = request.form["confirm_password"].strip()

    if new_password != confirm_password:

        return render_template(
            "message.html",
            title="Password Not Matched",
            message="New password and confirm password are not same.",
            box_class="warning",
            button_text="Try Again",
            button_link="/teacher-change-password"
        )

    if len(new_password) < 4:

        return render_template(
            "message.html",
            title="Weak Password",
            message="Password must be at least 4 characters.",
            box_class="warning",
            button_text="Try Again",
            button_link="/teacher-change-password"
        )

    conn = sqlite3.connect("database.db")

    row = conn.execute(
        """
        SELECT id
        FROM teachers
        WHERE id=?
        AND password=?
        """,
        (
            teacher_id,
            current_password
        )
    ).fetchone()

    if not row:

        conn.close()

        return render_template(
            "message.html",
            title="Wrong Current Password",
            message="Your current teacher password is incorrect.",
            box_class="warning",
            button_text="Try Again",
            button_link="/teacher-change-password"
        )

    conn.execute(
        """
        UPDATE teachers
        SET password=?
        WHERE id=?
        """,
        (
            new_password,
            teacher_id
        )
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
            "Teacher changed own password."
        )
    )

    conn.commit()
    conn.close()

    return render_template(
        "message.html",
        title="Password Changed",
        message="Your teacher password changed successfully.",
        box_class="notice",
        button_text="Go to Teacher Dashboard",
        button_link="/teacher-dashboard"
    )


# =====================================
# ADMIN RESET TEACHER PASSWORD
# =====================================

@app.route(
    "/admin-reset-teacher-password/<teacher_id>",
    methods=["GET", "POST"]
)
def admin_reset_teacher_password(teacher_id):

    if not admin_logged_in():
        return redirect("/admin-login")

    conn = sqlite3.connect("database.db")

    teacher = conn.execute(
        """
        SELECT
            id,
            name,
            username
        FROM teachers
        WHERE id=?
        """,
        (teacher_id,)
    ).fetchone()

    if not teacher:

        conn.close()

        return render_template(
            "message.html",
            title="Teacher Not Found",
            message="This teacher account does not exist.",
            box_class="warning",
            button_text="Back to Teachers",
            button_link="/admin-teachers"
        )

    if request.method == "GET":

        conn.close()

        return render_template(
            "admin/reset_teacher_password.html",
            teacher=teacher
        )

    new_password = request.form["new_password"].strip()
    confirm_password = request.form["confirm_password"].strip()

    if new_password != confirm_password:

        conn.close()

        return render_template(
            "message.html",
            title="Password Not Matched",
            message="New password and confirm password are not same.",
            box_class="warning",
            button_text="Try Again",
            button_link=f"/admin-reset-teacher-password/{teacher_id}"
        )

    if len(new_password) < 4:

        conn.close()

        return render_template(
            "message.html",
            title="Weak Password",
            message="Password must be at least 4 characters.",
            box_class="warning",
            button_text="Try Again",
            button_link=f"/admin-reset-teacher-password/{teacher_id}"
        )

    conn.execute(
        """
        UPDATE teachers
        SET password=?
        WHERE id=?
        """,
        (
            new_password,
            teacher_id
        )
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
            "Teacher password reset by admin."
        )
    )

    conn.commit()
    conn.close()

    return render_template(
        "message.html",
        title="Teacher Password Reset",
        message=f"Password reset successfully for teacher: {teacher[1]}",
        box_class="notice",
        button_text="Back to Teachers",
        button_link="/admin-teachers"
    )


# =====================================
# TEACHER FORGOT PASSWORD PAGE
# =====================================

@app.route("/teacher-forgot-password")
def teacher_forgot_password():

    return render_template(
        "message.html",
        title="Forgot Teacher Password",
        message="Please contact admin. Admin can reset your teacher password from the teacher list.",
        box_class="warning",
        button_text="Back to Teacher Login",
        button_link="/teacher-login"
    )


# =====================================
# ADMIN FORGOT PASSWORD PAGE
# =====================================

@app.route("/admin-forgot-password")
def admin_forgot_password():

    return render_template(
        "message.html",
        title="Forgot Admin Password",
        message="For V1, admin password can be changed only after admin login. If forgotten, reset it directly from the database.",
        box_class="warning",
        button_text="Back to Admin Login",
        button_link="/admin-login"
    )