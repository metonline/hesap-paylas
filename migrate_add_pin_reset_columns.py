#!/usr/bin/env python3
"""
Automated migration: Add PIN reset columns to users table in PostgreSQL
"""
import os
import sys
from dotenv import load_dotenv

load_dotenv()

from backend.app import app, db
from sqlalchemy import text

def add_pin_reset_columns():
    with app.app_context():
        try:
            print("\n=== Adding PIN reset columns to users table ===")
            alter_sql = '''
            ALTER TABLE users
                ADD COLUMN IF NOT EXISTS reset_otp VARCHAR(10),
                ADD COLUMN IF NOT EXISTS reset_otp_expiry TIMESTAMP,
                ADD COLUMN IF NOT EXISTS reset_otp_verified BOOLEAN DEFAULT FALSE;
            '''
            db.session.execute(text(alter_sql))
            db.session.commit()
            print("✓ Columns added or already exist.")
            return True
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    success = add_pin_reset_columns()
    sys.exit(0 if success else 1)
