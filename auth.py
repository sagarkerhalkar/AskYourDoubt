from __future__ import annotations

from functools import wraps
from typing import Callable, TypeVar

from flask import redirect, session, url_for

F = TypeVar('F', bound=Callable)


ROLE_SESSION_KEYS = {
    "admin": ("admin_id", "admin_name"),
    "teacher": ("teacher_id", "teacher_name"),
    "student": (
        "student_id",
        "student_name",
        "student_mobile",
        "student_session_id",
        "student_active_tab",
    ),
}


def clear_role_session(role: str) -> None:
    """Remove only one portal identity without logging out other portal roles.

    Teacher, student, and admin pages are often tested in separate tabs/windows of
    the same browser. Flask uses one cookie for that browser, so session.clear()
    would sign every role out. Scoped cleanup keeps those portals independent.
    """
    for key in ROLE_SESSION_KEYS.get(role, ()):
        session.pop(key, None)


def admin_required(view: F) -> F:
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get('admin_id'):
            return redirect(url_for('admin.login'))
        return view(*args, **kwargs)
    return wrapped  # type: ignore[return-value]


def teacher_required(view: F) -> F:
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get('teacher_id'):
            return redirect(url_for('teacher.login'))
        return view(*args, **kwargs)
    return wrapped  # type: ignore[return-value]


def student_required(view: F) -> F:
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get('student_id') or not session.get('student_session_id'):
            session_id = kwargs.get('session_id')
            if session_id:
                return redirect(url_for('student.join', session_id=session_id))
            return redirect(url_for('public.student_start'))
        return view(*args, **kwargs)
    return wrapped  # type: ignore[return-value]
