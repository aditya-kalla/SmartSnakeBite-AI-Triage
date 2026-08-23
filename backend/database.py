import sqlite3
import json
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

DB_PATH = Path(__file__).parent / "cases.db"

def get_connection():
    return sqlite3.connect(str(DB_PATH))

def init_db():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cases (
                id INTEGER PRIMARY KEY,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                data TEXT NOT NULL
            )
        ''')
        conn.commit()

def create_case(case_id: int, data: Dict):
    now = datetime.utcnow().isoformat()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO cases (id, created_at, updated_at, data) VALUES (?, ?, ?, ?)',
            (case_id, now, now, json.dumps(data))
        )
        conn.commit()

def get_case(case_id: int) -> Optional[Dict]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT data FROM cases WHERE id = ?', (case_id,))
        row = cursor.fetchone()
        if row:
            return json.loads(row[0])
        return None

def get_all_cases() -> List[Dict]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT data FROM cases ORDER BY created_at DESC')
        rows = cursor.fetchall()
        return [json.loads(row[0]) for row in rows]

def update_case(case_id: int, data: Dict):
    now = datetime.utcnow().isoformat()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE cases SET updated_at = ?, data = ? WHERE id = ?',
            (now, json.dumps(data), case_id)
        )
        conn.commit()
