#!/usr/bin/env python3
import urllib.request
import urllib.error
import json
import time

# Test signup
email = f"testuser_{int(time.time())}@example.com"
data = {
    "firstName": "Test",
    "lastName": "User",
    "email": email,
    "password": "Test123456",
    "phone": "5551234567"
}

print("Testing Signup...")
print(f"Email: {email}")

try:
    req = urllib.request.Request(
        'http://localhost:5000/api/auth/signup',
        data=json.dumps(data).encode('utf-8'),
        headers={'Content-Type': 'application/json'},
        method='POST'
    )
    
    with urllib.request.urlopen(req, timeout=5) as response:
        result = json.loads(response.read().decode('utf-8'))
        print(f"Status: {response.status}")
        print(f"Message: {result.get('message')}")
        print(f"User: {result.get('user')}")
        print(f"Token: {result.get('token')[:20]}..." if result.get('token') else "No token")
        
        # Test login
        print("\nTesting Login...")
        login_data = {
            "email": email,
            "password": "Test123456"
        }
        
        req2 = urllib.request.Request(
            'http://localhost:5000/api/auth/login',
            data=json.dumps(login_data).encode('utf-8'),
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        
        with urllib.request.urlopen(req2, timeout=5) as response2:
            result2 = json.loads(response2.read().decode('utf-8'))
            print(f"Status: {response2.status}")
            print(f"Message: {result2.get('message')}")
            print(f"Token received: {result2.get('token')[:20]}..." if result2.get('token') else "No token")

except urllib.error.HTTPError as e:
    print(f"Error {e.code}")
    try:
        error_data = json.loads(e.read().decode('utf-8'))
        print(f"Response: {error_data}")
    except:
        print(f"Response: {e.read()}")
except Exception as e:
    print(f"Error: {e}")

print("\nDone!")
