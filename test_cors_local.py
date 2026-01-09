#!/usr/bin/env python
"""Test CORS and request locally"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app import app
import requests
import json
import threading
import time

# Start Flask app in background
def run_app():
    with app.app_context():
        from backend.app import db
        db.create_all()
    app.run(host='127.0.0.1', port=5000, debug=False, use_reloader=False)

print("[STARTUP] Starting Flask backend on http://127.0.0.1:5000")
thread = threading.Thread(target=run_app, daemon=True)
thread.start()

# Wait for server to start
time.sleep(3)

print("\n[TEST] Testing login endpoint...")

# Test login with CORS
try:
    response = requests.post(
        'http://127.0.0.1:5000/api/auth/login',
        json={
            'email': 'metonline@gmail.com',
            'password': 'test123'
        },
        headers={
            'Content-Type': 'application/json',
            'Origin': 'https://metonline.github.io'  # Simulate browser origin
        }
    )
    
    print(f"Status: {response.status_code}")
    print(f"Headers: {dict(response.headers)}")
    print(f"Body: {json.dumps(response.json(), indent=2)}")
    
except Exception as e:
    print(f"Error: {e}")
