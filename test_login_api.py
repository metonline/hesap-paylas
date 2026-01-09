#!/usr/bin/env python
"""Test login API endpoint"""

import requests
import json

BASE_URL = "http://127.0.0.1:5000/api"

def test_login_api(email, password):
    """Test the login API endpoint"""
    try:
        print(f"Testing login API: {BASE_URL}/auth/login")
        print(f"Credentials: {email} / {password}\n")
        
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json={"email": email, "password": password},
            timeout=5
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        return response.status_code == 200
        
    except requests.exceptions.ConnectionError:
        print(f"❌ ERROR: Cannot connect to backend at {BASE_URL}")
        print("   Make sure the backend is running!")
        return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

if __name__ == "__main__":
    email = "metin_guven@hotmail.com"
    password = "YourPassword123"
    
    test_login_api(email, password)
