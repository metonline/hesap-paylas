#!/usr/bin/env python3
"""
Test API endpoints
"""
import urllib.request
import urllib.error
import json
import time
import random

def test_signup():
    """Test signup endpoint"""
    timestamp = int(time.time() * 1000) % 10000
    email = f"test_{timestamp}@example.com"
    
    data = {
        "firstName": "Test",
        "lastName": "User",
        "email": email,
        "password": "Test123456",
        "phone": "5551234567"
    }
    
    print("="*50)
    print("Testing Signup API")
    print("="*50)
    print(f"Email: {email}")
    print(f"Data: {json.dumps(data, indent=2)}")
    print()
    
    try:
        req = urllib.request.Request(
            'http://localhost:5000/api/auth/signup',
            data=json.dumps(data).encode('utf-8'),
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            print(f"✓ Success (Status {response.status})")
            print("Response:")
            print(json.dumps(result, indent=2))
            return email, result.get('token'), result.get('user')
    
    except urllib.error.HTTPError as e:
        print(f"✗ Error (Status {e.code})")
        try:
            error_data = json.loads(e.read().decode('utf-8'))
            print(f"Error: {error_data}")
        except:
            print(f"Error: {e}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    return None, None, None

def test_login(email):
    """Test login endpoint"""
    print()
    print("="*50)
    print("Testing Login API")
    print("="*50)
    print(f"Email: {email}")
    print()
    
    data = {
        "email": email,
        "password": "Test123456"
    }
    
    try:
        req = urllib.request.Request(
            'http://localhost:5000/api/auth/login',
            data=json.dumps(data).encode('utf-8'),
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            print(f"✓ Success (Status {response.status})")
            print("Response:")
            print(json.dumps(result, indent=2))
            return True
    
    except urllib.error.HTTPError as e:
        print(f"✗ Error (Status {e.code})")
        try:
            error_data = json.loads(e.read().decode('utf-8'))
            print(f"Error: {error_data}")
        except:
            print(f"Error: {e}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    return False

if __name__ == '__main__':
    email, token, user = test_signup()
    if email:
        test_login(email)
