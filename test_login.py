#!/usr/bin/env python3
"""Test login API"""
import requests
import json

LOGIN_URL = "http://localhost:5000/api/auth/login"

test_data = {
    "email": "metonline@gmail.com",
    "password": "test123"
}

print(f"Testing login with: {test_data}")
print(f"URL: {LOGIN_URL}\n")

try:
    response = requests.post(LOGIN_URL, json=test_data)
    print(f"Status Code: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    print(f"Response Body: {response.text}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n✅ Login successful!")
        print(f"Token: {data.get('token')}")
        print(f"User: {data.get('user')}")
    else:
        print(f"\n❌ Login failed: {response.json()}")
        
except Exception as e:
    print(f"❌ Error: {e}")
