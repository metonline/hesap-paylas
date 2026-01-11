#!/usr/bin/env python
"""Verbose login test"""
import http.client
import json

# Direct HTTP request (bypass requests library)
conn = http.client.HTTPConnection("localhost", 5000)
payload = json.dumps({"email": "metonline@gmail.com", "password": "test123"})
headers = {
    "Content-Type": "application/json",
    "Content-Length": str(len(payload))
}

print(f"Connecting to: localhost:5000")
print(f"Payload: {payload}")
print(f"Headers: {headers}")
print()

try:
    conn.request("POST", "/api/auth/login", payload, headers)
    response = conn.getresponse()
    data = response.read().decode()
    
    print(f"Status: {response.status}")
    print(f"Response: {data}")
    print()
    
    if response.status == 200:
        print("✅ SUCCESS!")
    else:
        print(f"❌ ERROR - Status {response.status}")
        
except Exception as e:
    print(f"❌ Connection error: {e}")
finally:
    conn.close()
