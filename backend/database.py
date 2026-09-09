import sqlite3
import json
from datetime import datetime

DB_PATH = "compliscan.db"


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            image_name TEXT,
            overall_status TEXT,
            missing_required_count INTEGER,
            extracted_fields TEXT,
            details TEXT,
            scanned_at TEXT
        )
    """)
    conn.commit()
    conn.close()


def save_scan(image_name, report):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO scans (image_name, overall_status, missing_required_count, extracted_fields, details, scanned_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        image_name,
        report["overall_status"],
        report["missing_required_count"],
        json.dumps(report.get("extracted_fields", {})),
        json.dumps(report["details"]),
        datetime.now().isoformat(timespec="seconds")
    ))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return new_id


def get_history(limit=50):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, image_name, overall_status, missing_required_count, scanned_at
        FROM scans
        ORDER BY id DESC
        LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_scan_by_id(scan_id):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM scans WHERE id = ?", (scan_id,))
    row = cursor.fetchone()
    conn.close()
    if row is None:
        return None
    scan = dict(row)
    scan["extracted_fields"] = json.loads(scan["extracted_fields"])
    scan["details"] = json.loads(scan["details"])
    return scan