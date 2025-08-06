import sqlite3
import os

# Since we're now in the db directory, use the current directory for logs.db
DB_PATH = os.path.join(os.path.dirname(__file__), "logs.db")

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