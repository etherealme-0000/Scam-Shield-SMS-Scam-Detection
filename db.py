import sqlite3
from datetime import datetime

DB_NAME = "scam_shield_predictions.db"


def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message TEXT NOT NULL,
            prediction TEXT NOT NULL,
            confidence REAL NOT NULL,
            timestamp TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def save_prediction(message, prediction, confidence):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO predictions (message, prediction, confidence, timestamp) VALUES (?, ?, ?, ?)",
        (message, prediction, confidence, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()


def get_all_predictions():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT message, prediction, confidence, timestamp FROM predictions ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_stats():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM predictions")
    total = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM predictions WHERE prediction = 'SCAM'")
    scam_count = cursor.fetchone()[0]
    conn.close()
    return total, scam_count