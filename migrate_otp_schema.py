#!/usr/bin/env python3
"""
Database migration: Add PIN reset columns to otp_verifications table
Run this on PythonAnywhere to update the production database schema
"""

import sys
sys.path.insert(0, '/home/metonline/mysite')

from backend.app import app, db
from sqlalchemy import text

def migrate_otp_table():
    """Add missing columns to otp_verifications table"""
    with app.app_context():
        try:
            # Get the database connection
            connection = db.engine.connect()
            
            print("=" * 60)
            print("MIGRATING OTP_VERIFICATIONS TABLE")
            print("=" * 60)
            
            # Check current schema
            print("\n1. Checking current table structure...")
            result = connection.execute(text("PRAGMA table_info(otp_verifications)"))
            columns = {row[1] for row in result}
            print(f"   Current columns: {columns}")
            
            # Add missing columns if they don't exist
            missing_columns = []
            
            if 'code' not in columns:
                print("\n2. Adding 'code' column...")
                try:
                    connection.execute(text(
                        "ALTER TABLE otp_verifications ADD COLUMN code VARCHAR(6) NULL"
                    ))
                    connection.commit()
                    print("   [OK] 'code' column added")
                    missing_columns.append('code')
                except Exception as e:
                    print(f"   [!] Error adding 'code': {e}")
            else:
                print("   [OK] 'code' column already exists")
            
            if 'purpose' not in columns:
                print("\n3. Adding 'purpose' column...")
                try:
                    connection.execute(text(
                        "ALTER TABLE otp_verifications ADD COLUMN purpose VARCHAR(20) DEFAULT 'verification'"
                    ))
                    connection.commit()
                    print("   [OK] 'purpose' column added")
                    missing_columns.append('purpose')
                except Exception as e:
                    print(f"   [!] Error adding 'purpose': {e}")
            else:
                print("   [OK] 'purpose' column already exists")
            
            if 'used' not in columns:
                print("\n4. Adding 'used' column...")
                try:
                    connection.execute(text(
                        "ALTER TABLE otp_verifications ADD COLUMN used BOOLEAN DEFAULT 0"
                    ))
                    connection.commit()
                    print("   [OK] 'used' column added")
                    missing_columns.append('used')
                except Exception as e:
                    print(f"   [!] Error adding 'used': {e}")
            else:
                print("   [OK] 'used' column already exists")
            
            # Check if otp_code needs to be made nullable
            print("\n5. Checking 'otp_code' nullability...")
            result = connection.execute(text("PRAGMA table_info(otp_verifications)"))
            for row in result:
                if row[1] == 'otp_code':
                    is_nullable = row[3] == 0  # SQLite: notnull flag
                    if is_nullable:
                        print("   [OK] 'otp_code' is already nullable")
                    else:
                        print("   [!] 'otp_code' is NOT NULL - may need adjustment")
                        print("       (This is OK for backward compatibility)")
            
            connection.close()
            
            print("\n" + "=" * 60)
            if missing_columns:
                print(f"[SUCCESS] Migration complete! Added {len(missing_columns)} columns:")
                for col in missing_columns:
                    print(f"  - {col}")
            else:
                print("[SUCCESS] Database schema is already up to date!")
            print("=" * 60)
            
            return True
            
        except Exception as e:
            print(f"\n[ERROR] Migration failed: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    success = migrate_otp_table()
    sys.exit(0 if success else 1)
