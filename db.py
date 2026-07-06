from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Iterator

from flask import current_app, g
from werkzeug.security import generate_password_hash


def get_db() -> sqlite3.Connection:
    if 'db' not in g:
        db_path = current_app.config['DATABASE']
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        g.db = sqlite3.connect(db_path, timeout=30, check_same_thread=False)
        g.db.row_factory = sqlite3.Row
        g.db.execute('PRAGMA foreign_keys = ON')
        g.db.execute('PRAGMA journal_mode = WAL')
        g.db.execute('PRAGMA busy_timeout = 5000')
    return g.db


def close_db(_: object | None = None) -> None:
    db = g.pop('db', None)
    if db is not None:
        db.close()


@contextmanager
def transaction() -> Iterator[sqlite3.Connection]:
    db = get_db()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise


def _columns(db: sqlite3.Connection, table: str) -> set[str]:
    return {row['name'] for row in db.execute(f'PRAGMA table_info({table})')}


def _add_column(db: sqlite3.Connection, table: str, name: str, sql_type: str) -> None:
    if name not in _columns(db, table):
        db.execute(f'ALTER TABLE {table} ADD COLUMN {name} {sql_type}')


def migrate_database() -> None:
    db = get_db()
    db.executescript(
        '''
        CREATE TABLE IF NOT EXISTS admins(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            display_name TEXT DEFAULT 'Administrator',
            status TEXT DEFAULT 'ACTIVE',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS teachers(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            mobile TEXT,
            email TEXT,
            dob TEXT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            status TEXT DEFAULT 'ACTIVE',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS sessions(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            teacher_id INTEGER NOT NULL,
            session_name TEXT NOT NULL,
            duration INTEGER DEFAULT 90,
            duration_seconds INTEGER DEFAULT 5400,
            status TEXT DEFAULT 'ACTIVE',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            started_at TIMESTAMP,
            ends_at TIMESTAMP,
            closed_at TIMESTAMP,
            question_limit INTEGER DEFAULT 100,
            allow_student_attachment_download INTEGER DEFAULT 0,
            FOREIGN KEY(teacher_id) REFERENCES teachers(id)
        );

        CREATE TABLE IF NOT EXISTS students(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            mobile TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS session_students(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER NOT NULL,
            student_id INTEGER NOT NULL,
            joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(session_id, student_id)
        );

        CREATE TABLE IF NOT EXISTS doubts(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER NOT NULL,
            student_id INTEGER NOT NULL,
            question TEXT NOT NULL,
            category TEXT DEFAULT 'General',
            keyword TEXT DEFAULT 'General',
            votes INTEGER DEFAULT 0,
            status TEXT DEFAULT 'OPEN',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP,
            attachment_path TEXT DEFAULT '',
            attachment_name TEXT DEFAULT '',
            attachment_type TEXT DEFAULT ''
        );

        CREATE TABLE IF NOT EXISTS doubt_votes(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            doubt_id INTEGER NOT NULL,
            student_id INTEGER,
            mobile TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(doubt_id, student_id)
        );

        CREATE TABLE IF NOT EXISTS resources(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            resource_type TEXT NOT NULL,
            file_path TEXT DEFAULT '',
            video_url TEXT DEFAULT '',
            notes TEXT DEFAULT '',
            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS teacher_activity(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            teacher_id INTEGER,
            activity TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS repository(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT NOT NULL,
            category TEXT,
            keyword TEXT,
            total_votes INTEGER DEFAULT 0,
            total_sessions INTEGER DEFAULT 1,
            status TEXT DEFAULT 'OPEN',
            teacher_id INTEGER,
            session_id INTEGER,
            doubt_id INTEGER UNIQUE,
            session_name TEXT,
            session_date TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS app_settings(
            setting_key TEXT PRIMARY KEY,
            setting_value TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE INDEX IF NOT EXISTS idx_doubts_session_status_votes
            ON doubts(session_id, status, votes DESC, id DESC);
        CREATE INDEX IF NOT EXISTS idx_doubts_student_session
            ON doubts(student_id, session_id);
        CREATE INDEX IF NOT EXISTS idx_sessions_teacher
            ON sessions(teacher_id, created_at DESC);
        CREATE INDEX IF NOT EXISTS idx_resources_session
            ON resources(session_id, uploaded_at DESC);
        '''
    )

    # Upgrade older databases without deleting data.
    table_columns = {
        'admins': {
            'display_name': "TEXT DEFAULT 'Administrator'",
            'status': "TEXT DEFAULT 'ACTIVE'",
            'created_at': 'TIMESTAMP',
        },
        'teachers': {
            'mobile': "TEXT DEFAULT ''",
            'email': "TEXT DEFAULT ''",
            'dob': "TEXT DEFAULT ''",
            'created_at': 'TIMESTAMP',
        },
        'sessions': {
            'duration_seconds': 'INTEGER DEFAULT 5400',
            'started_at': 'TIMESTAMP',
            'ends_at': 'TIMESTAMP',
            'closed_at': 'TIMESTAMP',
            'question_limit': 'INTEGER DEFAULT 100',
            'allow_student_attachment_download': 'INTEGER DEFAULT 0',
        },
        'doubts': {
            'completed_at': 'TIMESTAMP',
            'attachment_path': "TEXT DEFAULT ''",
            'attachment_name': "TEXT DEFAULT ''",
            'attachment_type': "TEXT DEFAULT ''",
        },
        'doubt_votes': {
            'student_id': 'INTEGER',
            'created_at': 'TIMESTAMP',
        },
        'resources': {
            'uploaded_at': 'TIMESTAMP',
        },
        'repository': {
            'total_sessions': 'INTEGER DEFAULT 1',
            'status': "TEXT DEFAULT 'OPEN'",
            'teacher_id': 'INTEGER',
            'session_id': 'INTEGER',
            'doubt_id': 'INTEGER',
            'session_name': 'TEXT',
            'session_date': 'TEXT',
            'updated_at': 'TIMESTAMP',
        },
    }
    for table, columns in table_columns.items():
        for name, type_sql in columns.items():
            _add_column(db, table, name, type_sql)

    # De-duplicate migrated rows before adding partial unique indexes.
    db.execute("DELETE FROM doubt_votes WHERE student_id IS NOT NULL AND id NOT IN (SELECT MIN(id) FROM doubt_votes WHERE student_id IS NOT NULL GROUP BY doubt_id, student_id)")
    db.execute("DELETE FROM repository WHERE doubt_id IS NOT NULL AND id NOT IN (SELECT MAX(id) FROM repository WHERE doubt_id IS NOT NULL GROUP BY doubt_id)")
    db.execute("CREATE UNIQUE INDEX IF NOT EXISTS uq_doubt_votes_student ON doubt_votes(doubt_id, student_id) WHERE student_id IS NOT NULL")
    db.execute("CREATE UNIQUE INDEX IF NOT EXISTS uq_repository_doubt ON repository(doubt_id) WHERE doubt_id IS NOT NULL")

    # Default admin. Existing plaintext passwords remain supported and are rehashed on login.
    existing = db.execute('SELECT id FROM admins LIMIT 1').fetchone()
    if not existing:
        db.execute(
            'INSERT INTO admins(username, password, display_name) VALUES(?,?,?)',
            ('admin', generate_password_hash('admin123'), 'Super Admin'),
        )

    # Normalize session time fields for old rows.
    db.execute(
        "UPDATE sessions SET started_at=COALESCE(started_at, created_at) WHERE started_at IS NULL"
    )
    # duration is the legacy minutes field; duration_seconds is the precise 0s to 24h control.
    db.execute(
        "UPDATE sessions SET duration_seconds=COALESCE(duration_seconds, MIN(MAX(COALESCE(duration,90) * 60, 0), 86400))"
    )
    db.execute("UPDATE admins SET created_at=COALESCE(created_at, CURRENT_TIMESTAMP)")
    db.execute("UPDATE teachers SET created_at=COALESCE(created_at, CURRENT_TIMESTAMP)")
    db.execute("UPDATE resources SET uploaded_at=COALESCE(uploaded_at, CURRENT_TIMESTAMP)")
    db.execute("UPDATE repository SET updated_at=COALESCE(updated_at, created_at, CURRENT_TIMESTAMP)")
    db.commit()


def init_app(app) -> None:
    app.teardown_appcontext(close_db)
    with app.app_context():
        migrate_database()
