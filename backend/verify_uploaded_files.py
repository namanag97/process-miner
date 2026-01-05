import sqlite3
import os

DB_PATH = "data/db/process_mining.db"

def verify():
    if not os.path.exists(DB_PATH):
        print(f"Error: {DB_PATH} not found.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Check if table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='uploaded_files'")
        if not cursor.fetchone():
            print("Table 'uploaded_files' DOES NOT EXIST.")
            return

        # Check columns
        cursor.execute("PRAGMA table_info(uploaded_files)")
        columns = [info[1] for info in cursor.fetchall()]
        print(f"Columns in uploaded_files: {columns}")
        
    except Exception as e:
        print(f"Error verifying database: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    verify()
