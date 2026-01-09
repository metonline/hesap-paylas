#!/usr/bin/env python
"""Test login with existing user"""

import sys
import sqlite3
from werkzeug.security import check_password_hash

def test_login(email, password):
    """Test if the password works"""
    try:
        conn = sqlite3.connect('instance/hesap_paylas.db')
        cursor = conn.cursor()
        
        # Get user
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()
        conn.close()
        
        if not user:
            print(f"❌ User not found: {email}")
            return False
        
        user_id, first_name, last_name, email_db, phone, password_hash, avatar, points, created, updated = user
        
        print(f"✓ User found: {first_name} {last_name}")
        print(f"  Email: {email_db}")
        print(f"  Password Hash: {password_hash[:50]}...")
        
        # Check password
        if check_password_hash(password_hash, password):
            print(f"✓ Password is CORRECT!")
            return True
        else:
            print(f"❌ Password is WRONG!")
            return False
            
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    email = "metin_guven@hotmail.com"
    password = "YourPassword123"
    
    print(f"Testing login for {email} with password '{password}'...\n")
    test_login(email, password)
