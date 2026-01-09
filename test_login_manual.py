#!/usr/bin/env python
"""Test login manually"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app import app, db, User
import json

# Create test user
with app.app_context():
    # Check existing users
    users = User.query.all()
    print(f"[DB] Total users: {len(users)}")
    for u in users:
        print(f"  - {u.email}: {u.first_name} {u.last_name}")
    
    # Test user exists?
    test_user = User.query.filter_by(email='test@test.com').first()
    
    if not test_user:
        print("\n[CREATE] Creating test user...")
        test_user = User(
            first_name='Test',
            last_name='User',
            email='test@test.com',
            phone='0532333222'
        )
        test_user.set_password('test123')
        db.session.add(test_user)
        db.session.commit()
        print("[CREATE] Test user created!")
    else:
        print(f"\n[EXISTS] Test user exists: {test_user.email}")
    
    # Test login
    print("\n[LOGIN] Testing login...")
    client = app.test_client()
    
    response = client.post('/api/auth/login', 
        json={
            'email': 'test@test.com',
            'password': 'test123'
        },
        content_type='application/json'
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.get_json(), indent=2)}")
