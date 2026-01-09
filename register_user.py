#!/usr/bin/env python
"""Register a new user in the database"""

import sys
import sqlite3
from werkzeug.security import generate_password_hash
from datetime import datetime

def register_user(first_name, last_name, email, phone, password):
    """Register a new user"""
    try:
        conn = sqlite3.connect('instance/hesap_paylas.db')
        cursor = conn.cursor()
        
        # Check if user already exists
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        existing = cursor.fetchone()
        
        if existing:
            print(f"Error: User with email {email} already exists!")
            conn.close()
            return False
        
        # Hash the password
        password_hash = generate_password_hash(password)
        
        # Insert new user
        now = datetime.utcnow().isoformat()
        cursor.execute("""
            INSERT INTO users (first_name, last_name, email, phone, password_hash, bonus_points, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, 0, ?, ?)
        """, (first_name, last_name, email, phone, password_hash, now, now))
        
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        
        print(f"✓ User registered successfully!")
        print(f"  ID: {user_id}")
        print(f"  Name: {first_name} {last_name}")
        print(f"  Email: {email}")
        print(f"  Phone: {phone}")
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    # Get user input
    first_name = input("First name: ").strip()
    last_name = input("Last name: ").strip()
    email = input("Email: ").strip()
    phone = input("Phone: ").strip()
    password = input("Password: ").strip()
    
    if not all([first_name, last_name, email, phone, password]):
        print("Error: All fields are required!")
        sys.exit(1)
    
    if register_user(first_name, last_name, email, phone, password):
        print("\nYou can now log in with these credentials.")
        sys.exit(0)
    else:
        sys.exit(1)
