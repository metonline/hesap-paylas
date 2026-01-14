#!/usr/bin/env python
"""Test phone check endpoint"""
import sys
import requests
import json

sys.path.insert(0, 'backend')
from app import app, db, User

# Test phone numbers
test_phones = [
    "5323133277",      # Metin Güven
    "5324417909",      # Müfit  
    "5325551234",      # ahmet
    "5325551236",      # memet
    "5325551237",      # Pınar
    "5551234567",      # Test User
    "5557654321",      # Metin Tester
]

print("=" * 60)
print("DATABASE CHECK")
print("=" * 60)

with app.app_context():
    print("\nUsers in database:")
    users = User.query.all()
    for u in users:
        if u.phone:
            print(f"  {u.phone:15} -> {u.first_name}")

print("\n" + "=" * 60)
print("API ENDPOINT TEST")
print("=" * 60)

# Start test server in background
import threading
import time

server_thread = threading.Thread(target=lambda: app.run(port=5001, debug=False, use_reloader=False), daemon=True)
server_thread.start()
time.sleep(2)  # Wait for server to start

for phone in test_phones:
    print(f"\nTesting: {phone}")
    try:
        response = requests.post(
            'http://localhost:5001/api/auth/check-phone',
            json={'phone': phone},
            timeout=5
        )
        data = response.json()
        print(f"  Response: {data}")
        print(f"  Exists: {data.get('exists')}")
    except Exception as e:
        print(f"  Error: {e}")

print("\nDone!")
