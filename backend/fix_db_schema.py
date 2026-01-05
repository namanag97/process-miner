import sqlite3
import os

DB_PATH = "data/db/process_mining.db"

def fix_schema():
    if not os.path.exists(DB_PATH):
        print(f"Error: {DB_PATH} not found.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Check if column exists
        cursor.execute("PRAGMA table_info(async_jobs)")
        columns = [info[1] for info in cursor.fetchall()]
        
        if "error_message" in columns:
            print("Column 'error_message' in async_jobs already exists.")
        else:
            print("Column 'error_message' missing in async_jobs. Adding it...")
            cursor.execute("ALTER TABLE async_jobs ADD COLUMN error_message TEXT")
            print("Successfully added 'error_message' column.")

        # Check process_events
        cursor.execute("PRAGMA table_info(process_events)")
        pe_columns = [info[1] for info in cursor.fetchall()]

        if "activity_id" in pe_columns:
            print("Column 'activity_id' in process_events already exists.")
        else:
            print("Column 'activity_id' missing in process_events. Adding it...")
            cursor.execute("ALTER TABLE process_events ADD COLUMN activity_id INTEGER")
            print("Successfully added 'activity_id' column.")

        if "resource_id" in pe_columns:
            print("Column 'resource_id' in process_events already exists.")
        else:
            print("Column 'resource_id' missing in process_events. Adding it...")
            cursor.execute("ALTER TABLE process_events ADD COLUMN resource_id INTEGER")
            print("Successfully added 'resource_id' column.")

        conn.commit()
            
    except Exception as e:
        print(f"Error patching database: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    fix_schema()
