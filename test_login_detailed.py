#!/usr/bin/env python
"""Detailed login test"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app import app, db, User
import json

with app.app_context():
    # Check users
    print("[DB CHECK]")
    users = User.query.all()
    print(f"Total users: {len(users)}")
    for u in users:
        print(f"  - ID: {u.id}, Email: {u.email}, Name: {u.first_name} {u.last_name}")
        print(f"    Password hash: {u.password_hash[:50]}...")
    
    # Test with app test client
    print("\n[TEST CLIENT]")
    client = app.test_client()
    
    # Test login
    print("\nTesting: POST /api/auth/login")
    print("Payload: {email: 'metonline@gmail.com', password: 'test123'}")
    
    resp = client.post(
        '/api/auth/login',
        json={'email': 'metonline@gmail.com', 'password': 'test123'},
        content_type='application/json'
    )
    
    print(f"\nResponse Status: {resp.status_code}")
    print(f"Response Data: {json.dumps(resp.get_json(), indent=2)}")
    
    # Check password directly
    print("\n[PASSWORD CHECK]")
    user = User.query.filter_by(email='metonline@gmail.com').first()
    if user:
        result = user.check_password('test123')
        print(f"check_password('test123'): {result}")
        
        # Try other passwords
        for pwd in ['test', '123', 'password']:
            result = user.check_password(pwd)
            print(f"check_password('{pwd}'): {result}")
