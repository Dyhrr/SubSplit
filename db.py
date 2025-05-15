db_code = """\"\"\"
Set up SQLite connection, schema, and thread-safe writes
\"\"\"
import sqlite3
import threading
from datetime import datetime

DB_FILE = 'transcripts.db'

# singleton connection and lock
db_lock = threading.Lock()
conn = None

def init_db():
    \"\"\"
    Initialize the SQLite database. Sets PRAGMAs and creates tables.
    \"\"\"
    global conn
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    conn.execute('PRAGMA journal_mode=WAL;')
    conn.execute('PRAGMA foreign_keys = ON;')
    conn.execute(\"\"\"
        CREATE TABLE IF NOT EXISTS transcripts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            path TEXT UNIQUE,
            content TEXT,
            summary TEXT,
            timestamp TEXT
        )
    \"\"\")
    conn.commit()

def insert_transcript(path, content, timestamp, summary=None):
    \"\"\"
    Thread-safe insertion of a transcript record into the database.
    \"\"\"
    # Ensure database is initialized
    if conn is None:
        init_db()

    with db_lock:
        cursor = conn.cursor()
        cursor.execute(
            \"\"\"
            INSERT OR REPLACE INTO transcripts (path, content, summary, timestamp)
            VALUES (?, ?, ?, ?)
            \"\"\",
            (path, content, summary, timestamp)
        )
        conn.commit()