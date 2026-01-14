#!/usr/bin/env python3
"""
Migration: Add email_verified column to users table
"""
import sqlite3
import os
from pathlib import Path

# Get database path
BASE_DIR = Path(__file__).parent
db_path = BASE_DIR / 'backend' / 'instance' / 'hesap_paylas.db'

if not db_path.exists():
    print(f"❌ Database not found at {db_path}")
    exit(1)

print(f"📦 Database: {db_path}")
print("=" * 60)

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
    
except sqlite3.OperationalError as e:
    print(f"❌ Database error: {e}")
    exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)
