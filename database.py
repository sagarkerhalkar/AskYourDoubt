import sqlite3

DB_NAME = "database.db"


def init_db():

    conn = sqlite3.connect(DB_NAME)

    conn.execute("""
    CREATE TABLE IF NOT EXISTS admins(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
    """)

    conn.execute("""
    CREATE TABLE IF NOT EXISTS teachers(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        username TEXT UNIQUE,
        password TEXT,
        status TEXT DEFAULT 'ACTIVE'
    )
    """)

    conn.execute("""
    CREATE TABLE IF NOT EXISTS sessions(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        teacher_id INTEGER,
        session_name TEXT,
        duration INTEGER,
        status TEXT DEFAULT 'ACTIVE',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.execute("""
    CREATE TABLE IF NOT EXISTS students(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        mobile TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.execute("""
    CREATE TABLE IF NOT EXISTS session_students(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id INTEGER,
        student_id INTEGER,
        joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.execute("""
    CREATE TABLE IF NOT EXISTS doubts(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id INTEGER,
        student_id INTEGER,
        question TEXT,
        category TEXT,
        keyword TEXT,
        votes INTEGER DEFAULT 0,
        status TEXT DEFAULT 'OPEN',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.execute("""
    CREATE TABLE IF NOT EXISTS doubt_votes(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        doubt_id INTEGER,
        mobile TEXT
    )
    """)

    conn.execute("""
    CREATE TABLE IF NOT EXISTS resources(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id INTEGER,
        title TEXT,
        resource_type TEXT,
        file_path TEXT,
        video_url TEXT,
        notes TEXT
    )
    """)

    conn.execute("""
    CREATE TABLE IF NOT EXISTS teacher_activity(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        teacher_id INTEGER,
        activity TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.execute("""
    CREATE TABLE IF NOT EXISTS repository(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question TEXT,
        category TEXT,
        keyword TEXT,
        total_votes INTEGER DEFAULT 0
    )
    """)

    conn.execute("""
    INSERT OR IGNORE INTO admins(
        id,
        username,
        password
    )
    VALUES(
        1,
        'admin',
        'admin123'
    )
    """)

    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_db()