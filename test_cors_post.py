#!/usr/bin/env python
# Test if POST works in a standalone Flask app

from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)

# Same CORS config as main app
CORS(app, resources={
    r"/api/*": {
        "origins": ["*"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": False,
        "max_age": 3600
    }
})

@app.route('/api/test-post', methods=['POST'])
def test_post():
    return jsonify({'message': 'POST works!'}), 200

if __name__ == '__main__':
    # Run test server
    import threading
    import requests
    import time
    
    # Start server in background
    server_thread = threading.Thread(target=lambda: app.run(host='127.0.0.1', port=5001, debug=False), daemon=True)
    server_thread.start()
    
    # Give server time to start
    time.sleep(2)
    
    # Test POST
    try:
        response = requests.post('http://localhost:5001/api/test-post', json={})
        print(f"POST Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")
