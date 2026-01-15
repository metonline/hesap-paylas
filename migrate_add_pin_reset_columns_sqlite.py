#!/usr/bin/env python3
"""
Automated migration: Add PIN reset columns to users table in local SQLite database
"""
import os
import sqlite3

db_path = os.path.join(os.path.dirname(__file__), 'backend', 'instance', 'hesap_paylas.db')

print(f"📦 SQLite DB Path: {db_path}")
if not os.path.exists(db_path):
    print(f"❌ Database not found at {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check existing columns
cursor.execute("PRAGMA table_info(users)")
columns = [row[1] for row in cursor.fetchall()]

# Add columns if missing
if 'reset_otp' not in columns:
    print("➕ Adding reset_otp column...")
    cursor.execute("ALTER TABLE users ADD COLUMN reset_otp VARCHAR(10)")
if 'reset_otp_expiry' not in columns:
    print("➕ Adding reset_otp_expiry column...")
    cursor.execute("ALTER TABLE users ADD COLUMN reset_otp_expiry TIMESTAMP")
if 'reset_otp_verified' not in columns:
    print("➕ Adding reset_otp_verified column...")
    cursor.execute("ALTER TABLE users ADD COLUMN reset_otp_verified BOOLEAN DEFAULT 0")

conn.commit()
conn.close()
print("✅ Migration complete! Columns added if missing.")
