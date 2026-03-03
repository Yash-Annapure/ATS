import sqlite3
import os

# Path to the database
DB_PATH = os.path.join(os.path.dirname(__file__), '../database/database.db')

def setup_users_table():
    print(f"Connecting to database at {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL CHECK(role IN ('Candidate', 'recruiter'))
    )
    ''')
    
    # Create assignments table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS assignments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        recruiter_id TEXT NOT NULL,
        candidate_username TEXT NOT NULL,
        question_id INTEGER NOT NULL,
        question_title TEXT NOT NULL,
        status TEXT DEFAULT 'assigned',
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Insert dummy users if they don't exist
    users = [
        ('student1', 'password123', 'Candidate'),
        ('recruiter1', 'admin123', 'recruiter')
    ]

    for username, password, role in users:
        try:
            cursor.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)', (username, password, role))
            print(f"Added user: {username} ({role})")
        except sqlite3.IntegrityError:
            print(f"User {username} already exists")

    conn.commit()
    conn.close()
    print("Users table setup completed.")

if __name__ == "__main__":
    setup_users_table()
