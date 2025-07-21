# import sqlite3, os

# DB_PATH = os.path.join("db", "logs.db")
# os.makedirs("db", exist_ok=True)

# conn = sqlite3.connect(DB_PATH)
# conn.execute("""CREATE TABLE IF NOT EXISTS advice_log (
#     id INTEGER PRIMARY KEY,
#     input_type TEXT,
#     user_input TEXT,
#     generated_advice TEXT,
#     audio_path TEXT,
#     timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
# );""")
# conn.commit()

# def log_entry(input_type, user_input, generated_advice, audio_path=None):
#     conn.execute("INSERT INTO advice_log (input_type, user_input, generated_advice, audio_path) VALUES (?, ?, ?, ?)",
#                  (input_type, user_input, generated_advice, audio_path))
#     conn.commit()

import sqlite3
import os

DB_PATH = os.path.join("db", "logs.db")

def get_db_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def log_entry(input_type, user_input, generated_advice, audio_path=""):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS advice_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            input_type TEXT,
            user_input TEXT,
            generated_advice TEXT,
            audio_path TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        INSERT INTO advice_log (input_type, user_input, generated_advice, audio_path)
        VALUES (?, ?, ?, ?)
    ''', (input_type, user_input, generated_advice, audio_path))

    conn.commit()
    conn.close()
