from __future__ import annotations

from functools import wraps
from typing import Callable, TypeVar

from flask import redirect, session, url_for

F = TypeVar('F', bound=Callable)


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
