import sqlite3

def init_db():
    conn = sqlite3.connect("smart_entry.db")
    cursor = conn.cursor()

    # Create domestic_help table if it doesn't exist
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS domestic_help (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        unique_id TEXT UNIQUE,
        name TEXT,
        apartment_number TEXT,
        owner_name TEXT,
        role TEXT,
        entry_time TEXT,
        exit_time TEXT
    )
    """)

    # Create access_logs table if it doesn't exist
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS access_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        name TEXT,
        timestamp DATETIME,
        status TEXT
    )
    """)
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized.")
