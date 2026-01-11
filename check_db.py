import sqlite3
import os

db_path = r'backend\instance\hesap_paylas.db'
print(f"Database path: {db_path}")
print(f"Database exists: {os.path.exists(db_path)}")

if not os.path.exists(db_path):
    print(f"ERROR: Database file not found at {db_path}")
    print(f"Files in backend/instance: {os.listdir('backend/instance') if os.path.exists('backend/instance') else 'Directory does not exist'}")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("Tables:", tables)

# Check users if exists
if ('users',) in tables:
    cursor.execute("SELECT * FROM users;")
    users = cursor.fetchall()
    print(f"Users ({len(users)}):", users)

conn.close()
