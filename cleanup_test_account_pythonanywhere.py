#!/usr/bin/env python3
"""
PythonAnywhere Cleanup Script
Removes duplicate test account from PythonAnywhere SQLite database

Usage:
    - SSH into PythonAnywhere
    - Run: cd ~/hesap-paylas && python cleanup_test_account_pythonanywhere.py
"""

import sys
import os

# PythonAnywhere path configuration
pythonanywhere_path = '/home/metonline/mysite'
if os.path.exists(pythonanywhere_path):
    sys.path.insert(0, pythonanywhere_path)
    sys.path.insert(0, os.path.join(pythonanywhere_path, 'backend'))
else:
    # Fallback for local testing
    sys.path.insert(0, 'backend')

try:
    from backend.app import app, db, User
except ImportError:
    try:
        from app import app, db, User
    except ImportError as e:
        print(f"Error: Could not import app. Make sure you're in the correct directory.")
        print(f"Error details: {e}")
        sys.exit(1)

# Phone number to delete
PHONE_TO_DELETE = '+905322578837'

def cleanup():
    """Delete test account from PythonAnywhere database"""
    print("=" * 50)
    print("Cleanup: Delete test user account (PythonAnywhere)")
    print("=" * 50)
    print()
    
    with app.app_context():
        # Find user
        user = User.query.filter_by(phone=PHONE_TO_DELETE).first()
        
        if not user:
            print(f"❌ User not found: {PHONE_TO_DELETE}")
            print()
            
            # List all users if not found
            all_users = User.query.all()
            if all_users:
                print("Available users in database:")
                for u in all_users:
                    print(f"  - {u.phone}: {u.first_name} {u.last_name} ({u.email})")
            else:
                print("No users in database.")
            return False
        
        # Display user info
        print(f"✓ Found user:")
        print(f"  Phone: {user.phone}")
        print(f"  Name: {user.first_name}")
        print(f"  Email: {user.email}")
        print(f"  ID: {user.id}")
        print()
        
        # Confirm deletion
        confirm = input("Delete this user? (yes/no): ").strip().lower()
        
        if confirm == 'yes':
            try:
                db.session.delete(user)
                db.session.commit()
                print("✓ User deleted successfully!")
                return True
            except Exception as e:
                db.session.rollback()
                print(f"❌ Error deleting user: {e}")
                return False
        else:
            print("Cancelled.")
            return False

if __name__ == '__main__':
    success = cleanup()
    sys.exit(0 if success else 1)
