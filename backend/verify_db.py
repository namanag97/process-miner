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
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='async_jobs'")
        if not cursor.fetchone():
            print("Table 'async_jobs' DOES NOT EXIST.")
            return

        # Check columns
        cursor.execute("PRAGMA table_info(async_jobs)")
        columns = [info[1] for info in cursor.fetchall()]
        print(f"Columns in async_jobs: {columns}")
        
        if "error_message" in columns:
            print("SUCCESS: 'error_message' column exists.")
        else:
            print("FAILURE: 'error_message' column is MISSING.")
            
    except Exception as e:
        print(f"Error verifying database: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    verify()
