#!/usr/bin/env python3
"""
Direct cleanup of Render database using psycopg2
"""
import os
from pathlib import Path
from dotenv import load_dotenv
import psycopg2

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL', '')

if not DATABASE_URL:
    print("ERROR: DATABASE_URL not set in .env")
    exit(1)

print("\n" + "="*60)
print("RENDER DATABASE CLEANUP - DIRECT SQL")
print("="*60)

try:
    # Connect directly to database
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    print("\n[STEP 1] Checking for users to delete...")
    
    emails_to_delete = [
        'metonline@gmail.com',
        'metin_guven@hotmail.com'
    ]
    
    for email in emails_to_delete:
        cursor.execute("SELECT id, email, phone FROM users WHERE email = %s", (email,))
        row = cursor.fetchone()
        if row:
            print(f"  ✓ Found: {email} (ID: {row[0]})")
        else:
            print(f"  ✗ Not found: {email}")
    
    print("\n[STEP 2] Deleting old users...")
    
    for email in emails_to_delete:
        cursor.execute("DELETE FROM users WHERE email = %s", (email,))
        deleted = cursor.rowcount
        if deleted > 0:
            print(f"  ✓ Deleted: {email} ({deleted} row)")
    
    conn.commit()
    
    print("\n[STEP 3] Verifying deletion...")
    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]
    print(f"\n✓ SUCCESS! Database now has {count} user(s)")
    
    if count > 0:
        cursor.execute("SELECT id, email, phone FROM users")
        print("\nRemaining users:")
        for row in cursor.fetchall():
            print(f"  - ID: {row[0]}, Email: {row[1]}, Phone: {row[2]}")
    
    cursor.close()
    conn.close()
    
    print("\n" + "="*60 + "\n")
    
except Exception as e:
    print(f"\n✗ ERROR: {str(e)}")
    exit(1)
