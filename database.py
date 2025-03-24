import sqlite3

# Connect to SQLite database (creates if it doesn't exist)
conn = sqlite3.connect("smart_entry.db")
cursor = conn.cursor()

# Create table if not exists
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

# Function to insert a domestic help record
def insert_domestic_help(unique_id, name, apartment_number, owner_name, role, entry_time, exit_time):
    cursor.execute("INSERT INTO domestic_help (unique_id, name, apartment_number, owner_name, role, entry_time, exit_time) VALUES (?, ?, ?, ?, ?, ?, ?)", 
                   (unique_id, name, apartment_number, owner_name, role, entry_time, exit_time))
    conn.commit()

# Function to fetch details using unique_id
def get_domestic_help_by_id(unique_id):
    cursor.execute("SELECT * FROM domestic_help WHERE unique_id = ?", (unique_id,))
    return cursor.fetchone()


conn.close()
