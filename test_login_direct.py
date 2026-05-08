#!/usr/bin/env python3
"""Test login directly without dev_server"""
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

# Set environment
os.environ['PYTHONIOENCODING'] = 'utf-8'
os.environ['DATABASE_URL'] = 'sqlite:///hesap_paylas.db'
os.environ['FLASK_ENV'] = 'development'

from dotenv import load_dotenv
load_dotenv()

print("=" * 60)
print("Testing Login Functionality")
print("=" * 60)

try:
    print("\n1️⃣  Importing Flask app...")
    from backend.app import app, db, User
    print("✓ Flask app imported successfully\n")
    
    print("2️⃣  Creating database tables...")
    with app.app_context():
        db.create_all()
        print("✓ Database tables created\n")
        
        # Check existing users
        users = User.query.all()
        print(f"📊 Existing users: {len(users)}")
        for user in users:
            print(f"   - {user.email}")
        
        # Create test user if not exists
        test_email = "metonline@gmail.com"
        existing_user = User.query.filter_by(email=test_email).first()
        
        if not existing_user:
            print(f"\n3️⃣  Creating test user: {test_email}")
            test_user = User(
                first_name="Test",
                last_name="User",
                email=test_email,
                phone="+905551234567"
            )
            test_user.set_password("test123")
            db.session.add(test_user)
            db.session.commit()
            print(f"✓ Test user created\n")
        else:
            print(f"\n3️⃣  Test user already exists: {test_email}\n")
    
    # Now test login via Flask test client
    print("4️⃣  Testing login endpoint...")
    client = app.test_client()
    
    response = client.post('/api/auth/login', 
        json={
            'email': test_email,
            'password': 'test123'
        },
        content_type='application/json'
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.get_json()}")
    
    if response.status_code == 200:
        data = response.get_json()
        print(f"\n✅ LOGIN SUCCESSFUL!")
        print(f"   Token: {data.get('token')[:20]}...")
        print(f"   User: {data.get('user').get('email')}")
    else:
        print(f"\n❌ Login failed!")
        print(f"   Error: {response.get_json().get('error')}")
        
except Exception as e:
    print(f"\n❌ Error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
