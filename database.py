import sqlite3
from datetime import datetime
import pandas as pd

def init_db():
    conn = sqlite3.connect("legalease.db")
    c = conn.cursor()
    # Create main cases table with all metadata
    c.execute('''CREATE TABLE IF NOT EXISTS cases (
        case_id           TEXT PRIMARY KEY,
        sender_name       TEXT,
        sender_address    TEXT,
        problem           TEXT,
        issue_type        TEXT,
        notice_draft      TEXT,
        status            TEXT,
        created_at        TEXT,
        recipient_name    TEXT,
        recipient_address TEXT,
        extra_details     TEXT,
        recipient_email   TEXT
    )''')
    
    # Run dynamic SQLite migrations to add missing columns in older databases
    c.execute("PRAGMA table_info(cases)")
    columns = [col[1] for col in c.fetchall()]
    new_cols = {
        "sender_address": "TEXT",
        "recipient_name": "TEXT",
        "recipient_address": "TEXT",
        "extra_details": "TEXT"
    }
    for col_name, col_type in new_cols.items():
        if col_name not in columns:
            try:
                c.execute(f"ALTER TABLE cases ADD COLUMN {col_name} {col_type}")
            except Exception as e:
                print(f"Migration error for {col_name}: {e}")

    # Create settings table for persistence
    c.execute('''CREATE TABLE IF NOT EXISTS settings (
        key   TEXT PRIMARY KEY,
        value TEXT
    )''')
    conn.commit()
    conn.close()

def save_case(case_id, sender_name, sender_address, problem, issue_type, notice_draft, recipient_name, recipient_address, extra_details, recipient_email, status):
    conn = sqlite3.connect("legalease.db")
    c = conn.cursor()
    c.execute('''INSERT OR REPLACE INTO cases (
        case_id, sender_name, sender_address, problem, issue_type, notice_draft, 
        status, created_at, recipient_name, recipient_address, extra_details, recipient_email
    ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)''',
              (case_id, sender_name, sender_address, problem, issue_type, notice_draft,
               status, datetime.now().strftime("%d-%m-%Y %H:%M"), recipient_name, recipient_address, extra_details, recipient_email))
    conn.commit()
    conn.close()

def update_status(case_id, new_status):
    conn = sqlite3.connect("legalease.db")
    c = conn.cursor()
    c.execute("UPDATE cases SET status=? WHERE case_id=?", (new_status, case_id))
    conn.commit()
    conn.close()

def get_all_cases():
    conn = sqlite3.connect("legalease.db")
    df = pd.read_sql("SELECT case_id, sender_name, issue_type, status, created_at FROM cases ORDER BY created_at DESC", conn)
    conn.close()
    return df

def get_case_by_id(case_id):
    conn = sqlite3.connect("legalease.db")
    c = conn.cursor()
    c.execute("SELECT * FROM cases WHERE case_id=?", (case_id,))
    row = c.fetchone()
    conn.close()
    if not row:
        return None
    return {
        "case_id": row[0],
        "sender_name": row[1],
        "sender_address": row[2] if len(row) > 2 else "",
        "problem": row[3] if len(row) > 3 else "",
        "issue_type": row[4] if len(row) > 4 else "",
        "notice_draft": row[5] if len(row) > 5 else "",
        "status": row[6] if len(row) > 6 else "",
        "created_at": row[7] if len(row) > 7 else "",
        "recipient_name": row[8] if len(row) > 8 else "",
        "recipient_address": row[9] if len(row) > 9 else "",
        "extra_details": row[10] if len(row) > 10 else "",
        "recipient_email": row[11] if len(row) > 11 else ""
    }
