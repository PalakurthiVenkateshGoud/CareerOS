import sqlite3
import json
import uuid
from contextlib import contextmanager

DB_PATH = "careeros.db"

def init_db():
    with get_conn() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS sessions (
            id TEXT PRIMARY KEY,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT REFERENCES sessions(id),
            raw_resume_text TEXT,
            parsed_profile TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS career_configs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT REFERENCES sessions(id),
            target_role TEXT,
            hours_per_week INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS dashboard_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT REFERENCES sessions(id),
            final_payload TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

@contextmanager
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()

def create_session() -> str:
    session_id = str(uuid.uuid4())
    with get_conn() as conn:
        conn.execute("INSERT INTO sessions (id) VALUES (?)", (session_id,))
    return session_id

def save_profile(session_id: str, raw_text: str, parsed_profile: dict):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO profiles (session_id, raw_resume_text, parsed_profile) VALUES (?, ?, ?)",
            (session_id, raw_text, json.dumps(parsed_profile)),
        )

def save_config(session_id: str, target_role: str, hours_per_week: int):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO career_configs (session_id, target_role, hours_per_week) VALUES (?, ?, ?)",
            (session_id, target_role, hours_per_week),
        )

def save_dashboard(session_id: str, payload: dict):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO dashboard_results (session_id, final_payload) VALUES (?, ?)",
            (session_id, json.dumps(payload)),
        )

def get_session_data(session_id: str) -> dict:
    with get_conn() as conn:
        cur = conn.cursor()

        cur.execute(
            "SELECT parsed_profile FROM profiles WHERE session_id=? ORDER BY id DESC LIMIT 1",
            (session_id,),
        )
        profile_row = cur.fetchone()
        parsed_profile = json.loads(profile_row[0]) if profile_row else None

        cur.execute(
            "SELECT target_role, hours_per_week FROM career_configs WHERE session_id=? ORDER BY id DESC LIMIT 1",
            (session_id,),
        )
        config_row = cur.fetchone()
        config = {"target_role": config_row[0], "hours_per_week": config_row[1]} if config_row else None

        cur.execute(
            "SELECT final_payload FROM dashboard_results WHERE session_id=? ORDER BY id DESC LIMIT 1",
            (session_id,),
        )
        dash_row = cur.fetchone()
        dashboard = json.loads(dash_row[0]) if dash_row else None

        return {
            "session_id": session_id,
            "parsed_profile": parsed_profile,
            "config": config,
            "dashboard": dashboard,
        }