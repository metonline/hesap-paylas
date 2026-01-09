#!/usr/bin/env python3
import sqlite3
import json

conn = sqlite3.connect('instance/hesap_paylas.db')
cursor = conn.cursor()

# Get first user
cursor.execute("SELECT * FROM users LIMIT 1")
user = cursor.fetchone()

if user:
    print("Found test user in database:")
    print(f"ID: {user[0]}")
    print(f"Name: {user[1]} {user[2]}")
    print(f"Email: {user[3]}")
    print(f"Phone: {user[4]}")
    print(f"Password Hash: {user[5][:50]}...")
    
    # Now test if Flask can work with this
    print("\n" + "="*50)
    print("Testing auth with backend...")
    print("="*50)
    
    import urllib.request
    import urllib.error
    
    login_data = {
        "email": user[3],
        "password": "Ahmet123456"  # Test with original password
    }
    
    print(f"\nAttempting login with email: {user[3]}")
    
    try:
        req = urllib.request.Request(
            'http://localhost:5000/api/auth/login',
            data=json.dumps(login_data).encode('utf-8'),
            headers={'Content-Type': 'application/json'},
            method='POST',
            timeout=5
        )
        
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            print(f"SUCCESS! Status: {response.status}")
            print(f"Response: {json.dumps(result, indent=2)}")
    
    except urllib.error.HTTPError as e:
        print(f"HTTP Error {e.code}")
        try:
            error = json.loads(e.read().decode('utf-8'))
            print(f"Error: {error}")
        except:
            print(f"Error: {e.read()}")
    except Exception as e:
        print(f"Error: {e}")
else:
    print("No users found")

conn.close()
