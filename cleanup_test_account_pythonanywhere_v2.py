#!/usr/bin/env python3
"""
PythonAnywhere Cleanup Script
Removes duplicate test account from PythonAnywhere SQLite database

Usage:
    - SSH into PythonAnywhere
    - Run: cd ~/mysite && python cleanup_test_account_pythonanywhere_v2.py yes
"""

import sys
import sqlite3
import os

# Phone number to delete
PHONE_TO_DELETE = '+905322578837'

def cleanup():
    """Delete test account from PythonAnywhere SQLite database"""
    
    # Find the database file
    db_path = '/home/metonline/mysite/hesap_paylas.db'
    
    if not os.path.exists(db_path):
        print(f"Database not found at: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Find user
        cursor.execute('SELECT id, phone, first_name, email FROM user WHERE phone = ?', (PHONE_TO_DELETE,))
        user = cursor.fetchone()
        
        if not user:
            print(f"User not found: {PHONE_TO_DELETE}")
            conn.close()
            return False
        
        user_id, phone, name, email = user
        
        # Display user info
        print(f"Found user:")
        print(f"  Phone: {phone}")
        print(f"  Name: {name}")
        print(f"  Email: {email}")
        print(f"  ID: {user_id}")
        print()
        
        # Check for auto-confirmation
        auto_confirm = len(sys.argv) > 1 and sys.argv[1].lower() == 'yes'
        
        if auto_confirm:
            confirm = 'yes'
            print("(Auto-confirming deletion)")
        else:
            confirm = input("Delete this user? (yes/no): ").strip().lower()
        
        if confirm == 'yes':
            cursor.execute('DELETE FROM user WHERE id = ?', (user_id,))
            conn.commit()
            print("User deleted successfully!")
            conn.close()
            return True
        else:
            print("Cancelled.")
            conn.close()
            return False
            
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == '__main__':
    success = cleanup()
    sys.exit(0 if success else 1)
