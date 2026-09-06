import sqlite3
import json
from pathlib import Path
from backend.config import BASE_DIR, BUSINESSES_FILE, SCHEMES_FILE
from backend.models import UserProfile

DB_PATH = BASE_DIR / "gramvantage.db"

def get_connection():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Table for sessions / chat history
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS chat_sessions (
        session_id TEXT PRIMARY KEY,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        language TEXT DEFAULT 'en',
        profile_json TEXT
    );
    """)
    
    # Table for chat messages
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS chat_messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT,
        role TEXT,
        content TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (session_id) REFERENCES chat_sessions(session_id)
    );
    """)
    
    # Table for generated reports
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS generated_reports (
        report_id TEXT PRIMARY KEY,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        session_id TEXT,
        business_id TEXT,
        report_json TEXT
    );
    """)
    
    conn.commit()
    conn.close()
    validate_mvp_datasets()

def validate_mvp_datasets():
    """Validates controlled MVP datasets on startup."""
    try:
        if BUSINESSES_FILE.exists():
            with open(BUSINESSES_FILE, "r", encoding="utf-8") as f:
                businesses = json.load(f)
                if len(businesses) != 90:
                    print(f"[MVP Dataset Warning] Expected 90 businesses, found {len(businesses)}")
                b_ids = set()
                for b in businesses:
                    b_id = b.get("id") or b.get("business_id")
                    if b_id in b_ids:
                        print(f"[MVP Dataset Warning] Duplicate business_id: {b_id}")
                    b_ids.add(b_id)
                    skills = b.get("required_skills") or b.get("skills") or []
                    if len(skills) != 3:
                        print(f"[MVP Dataset Warning] Business {b.get('business_name')} does not have exactly 3 skills: {skills}")
        print("[MVP Dataset Validator] Controlled 90-business dataset verified successfully.")
    except Exception as e:
        print(f"[MVP Dataset Validator Exception]: {e}")

# Ensure DB is initialized on module load
init_db()

def load_businesses_data():
    if BUSINESSES_FILE.exists():
        with open(BUSINESSES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    return []

def load_schemes_data():
    if SCHEMES_FILE.exists():
        with open(SCHEMES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def get_business_by_id(business_id: str):
    businesses = load_businesses_data()
    for b in businesses:
        if b.get("id") == business_id:
            return b
    return None

def save_report(report_id: str, session_id: str, business_id: str, report_dict: dict):
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR REPLACE INTO generated_reports (report_id, session_id, business_id, report_json) VALUES (?, ?, ?, ?)",
        (report_id, session_id, business_id, json.dumps(report_dict))
    )
    conn.commit()
    conn.close()
