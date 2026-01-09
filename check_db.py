import sqlite3

conn = sqlite3.connect('instance/hesap_paylas.db')
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
