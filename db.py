import sqlite3
import pandas as pd
import json
import os

DB_NAME = "records.db"
DB_PATH = os.path.join(os.getcwd(), "uploads.db")

def get_conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db():
    conn = get_conn()
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS uploads (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT,
        uploaded_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS upload_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        upload_id INTEGER,
        row_json TEXT,
        FOREIGN KEY(upload_id) REFERENCES uploads(id)
    );
    """)

    conn.commit()
    conn.close()

def save_upload(filename, df):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("INSERT INTO uploads (filename) VALUES (?)", (filename,))
    upload_id = cur.lastrowid

    for _, row in df.iterrows():
        row_json = json.dumps(row.to_dict())
        cur.execute(
            "INSERT INTO upload_data (upload_id, row_json) VALUES (?,?)", (upload_id, row_json)
        )

    conn.commit()
    conn.close()
    return upload_id

def get_uploads():
    conn = get_conn()
    df = pd.read_sql_query("SELECT * FROM uploads ORDER BY uploaded_at DESC", conn)
    conn.close()
    return df


def get_upload_data(upload_id):
    conn = get_conn()
    df = pd.read_sql_query(
        "SELECT row_json FROM upload_data WHERE upload_id = ?",
        conn,
        params=(upload_id,)
    )
    conn.close()

    rows = [json.loads(r) for r in df["row_json"]]
    return pd.DataFrame(rows)