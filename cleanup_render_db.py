#!/usr/bin/env python3
"""
Delete old default users from Render PostgreSQL database
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path
import sys
sys.path.insert(0, str(Path(__file__).parent))

from backend.app import app, db, User

def cleanup_database():
    """Delete old default users from Render database"""
    with app.app_context():
        print("\n" + "="*60)
        print("RENDER DATABASE CLEANUP")
        print("="*60)
        
        # List of emails to delete
        emails_to_delete = [
            'metonline@gmail.com',
            'metin_guven@hotmail.com'
        ]
        
        print("\n[STEP 1] Checking for users to delete...")
        for email in emails_to_delete:
            user = User.query.filter_by(email=email).first()
            if user:
                print(f"  ✓ Found: {email} (ID: {user.id})")
            else:
                print(f"  ✗ Not found: {email}")
        
        print("\n[STEP 2] Deleting old users...")
        try:
            for email in emails_to_delete:
                user = User.query.filter_by(email=email).first()
                if user:
                    db.session.delete(user)
                    print(f"  ✓ Marked for deletion: {email}")
            
            db.session.commit()
            print("\n[STEP 3] Verifying deletion...")
            
            remaining = User.query.count()
            print(f"\n✓ SUCCESS! Database now has {remaining} user(s)")
            
            if remaining > 0:
                print("\nRemaining users:")
                for user in User.query.all():
                    print(f"  - {user.email} ({user.phone})")
            
        except Exception as e:
            print(f"\n✗ ERROR: {str(e)}")
            db.session.rollback()
            return False
        
        print("\n" + "="*60)
        return True

if __name__ == '__main__':
    success = cleanup_database()
    sys.exit(0 if success else 1)
