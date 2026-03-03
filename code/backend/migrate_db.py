import sqlite3
import os

# Path to the database
DB_PATH = os.path.join(os.path.dirname(__file__), '../database/database.db')

def migrate_assignments_table():
    print(f"Connecting to database at {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    columns_to_add = [
        ("submitted_code", "TEXT"),
        ("outcome", "TEXT"),
        ("score", "INTEGER"),
        ("total_test_cases", "INTEGER"),
        ("execution_log", "TEXT")
    ]

    for col_name, col_type in columns_to_add:
        try:
            cursor.execute(f"ALTER TABLE assignments ADD COLUMN {col_name} {col_type}")
            print(f"Added column: {col_name}")
        except sqlite3.OperationalError as e:
            if "duplicate column" in str(e).lower():
                print(f"Column {col_name} already exists.")
            else:
                print(f"Error adding {col_name}: {e}")

    conn.commit()
    conn.close()
    print("Migration completed.")

if __name__ == "__main__":
    migrate_assignments_table()
