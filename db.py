import sqlite3

def init_db():
    conn = sqlite3.connect("leads.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            method TEXT,
            amount TEXT,
            date TEXT,
            time TEXT,
            ref TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_to_db(data: dict):
    conn = sqlite3.connect("leads.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO leads (username, method, amount, date, time, ref)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        data.get("username", ""),
        data.get("method", ""),
        data.get("amount", ""),
        data.get("date", ""),
        data.get("time", ""),
        data.get("ref", ""),
    ))
    conn.commit()
    conn.close()

