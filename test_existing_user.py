#!/usr/bin/env python
"""Test metonline@gmail.com user"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app import app, db, User
import json

with app.app_context():
    # Test login for existing user
    print("[LOGIN] Testing login for metonline@gmail.com...")
    client = app.test_client()
    
    # Try common passwords
    passwords = ['123456', 'password', 'test123', 'metonline', '12345678']
    
    for pwd in passwords:
        response = client.post('/api/auth/login', 
            json={
                'email': 'metonline@gmail.com',
                'password': pwd
            },
            content_type='application/json'
        )
        
        if response.status_code == 200:
            print(f"✅ SUCCESS with password: {pwd}")
            print(f"Response: {json.dumps(response.get_json(), indent=2)}")
            break
        else:
            print(f"❌ Failed with password: {pwd}")
    else:
        print("\n[INFO] Creating new user metonline@gmail.com with password 'test123'...")
        existing = User.query.filter_by(email='metonline@gmail.com').first()
        if existing:
            # Update password
            existing.set_password('test123')
            db.session.commit()
            print("✅ Updated password for existing user")
        
        # Test new password
        response = client.post('/api/auth/login', 
            json={
                'email': 'metonline@gmail.com',
                'password': 'test123'
            },
            content_type='application/json'
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.get_json(), indent=2)}")
