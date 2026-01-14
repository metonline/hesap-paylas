#!/usr/bin/env python3
"""
Migration: Add email_verified column to users table (PythonAnywhere)
Run this on PythonAnywhere console
"""
import sqlite3
import os

# PythonAnywhere database path
db_path = os.path.expanduser('~/mysite/backend/instance/hesap_paylas.db')

print(f"📦 Database: {db_path}")
print("=" * 60)

if not os.path.exists(db_path):
    print(f"❌ Database not found at {db_path}")
    exit(1)

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if column already exists
    cursor.execute("PRAGMA table_info(users)")
    columns = [row[1] for row in cursor.fetchall()]
    
    if 'email_verified' in columns:
        print("✅ email_verified column already exists")
    else:
        print("➕ Adding email_verified column...")
        cursor.execute("""
            ALTER TABLE users 
            ADD COLUMN email_verified BOOLEAN DEFAULT 0
        """)
        conn.commit()
        print("✅ email_verified column added successfully")
    
    # Verify
    cursor.execute("PRAGMA table_info(users)")
    columns = [row[1] for row in cursor.fetchall()]
    print(f"\n📋 Users table columns:")
    for col in columns:
        print(f"   ✓ {col}")
    
    conn.close()
    print("\n✅ Migration completed successfully!")
    print("⚠️  Restart PythonAnywhere web app after this!")
    
except sqlite3.OperationalError as e:
    print(f"❌ Database error: {e}")
    exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)
