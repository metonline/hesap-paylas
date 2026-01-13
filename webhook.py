#!/usr/bin/env python3
"""
GitHub Webhook Handler for PythonAnywhere Auto-Deploy
Automatically pulls latest code and reloads the web app when you push to GitHub
"""

import subprocess
import os
import json
from flask import Flask, request, jsonify
import hmac
import hashlib

app = Flask(__name__)

# Get these values from PythonAnywhere Settings
PYTHONANYWHERE_API_TOKEN = '5f1a106c09b7998c71bec6aace5b9ba2a99a69ab'
PYTHONANYWHERE_USERNAME = 'metonline'
PYTHONANYWHERE_DOMAIN = 'metonline.pythonanywhere.com'
GITHUB_WEBHOOK_SECRET = 'metonline_webhook_secret_123'  # Create any secret string, use same in GitHub

REPO_PATH = '/home/metonline/mysite'

def verify_github_signature(payload_body, signature):
    """Verify GitHub webhook signature"""
    if not GITHUB_WEBHOOK_SECRET or GITHUB_WEBHOOK_SECRET == 'YOUR_WEBHOOK_SECRET_HERE':
        print('[WARN] GitHub webhook secret not configured - signature verification disabled')
        return True
    
    expected_sig = 'sha256=' + hmac.new(
        GITHUB_WEBHOOK_SECRET.encode(),
        payload_body,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(expected_sig, signature)

@app.route('/webhook', methods=['POST'])
def webhook():
    """Handle GitHub webhook events"""
    print('\n' + '='*60)
    print('[WEBHOOK] GitHub webhook received')
    print('='*60)
    
    try:
        # Get payload
        payload_body = request.get_data()
        signature = request.headers.get('X-Hub-Signature-256', '')
        
        # Verify signature
        if not verify_github_signature(payload_body, signature):
            print('[ERROR] Invalid GitHub signature!')
            return jsonify({'status': 'error', 'message': 'Invalid signature'}), 401
        
        data = json.loads(payload_body)
        event_type = request.headers.get('X-GitHub-Event', 'unknown')
        
        print(f'[WEBHOOK] Event type: {event_type}')
        print(f'[WEBHOOK] Ref: {data.get("ref", "unknown")}')
        
        # Only process push events to main branch
        if event_type != 'push' or data.get('ref') != 'refs/heads/main':
            print('[WEBHOOK] Not a push to main branch - ignoring')
            return jsonify({'status': 'ignored'}), 200
        
        print('[WEBHOOK] ✅ Valid push to main branch detected!')
        
        # Step 1: Pull latest code
        print('[DEPLOY] Pulling latest code from GitHub...')
        os.chdir(REPO_PATH)
        result = subprocess.run(['git', 'pull', 'origin', 'main'], 
                              capture_output=True, text=True, check=True)
        print(f'[DEPLOY] Git pull output:\n{result.stdout}')
        print('[DEPLOY] ✅ Code pulled successfully!')
        
        # Step 2: Reload web app
        print('[DEPLOY] Reloading PythonAnywhere web app...')
        try:
            import requests
            
            reload_url = (
                f'https://www.pythonanywhere.com/api/v0/user/{PYTHONANYWHERE_USERNAME}/webapps/'
                f'{PYTHONANYWHERE_DOMAIN}/reload/'
            )
            
            headers = {
                'Authorization': f'Token {PYTHONANYWHERE_API_TOKEN}',
                'Content-Type': 'application/json'
            }
            
            response = requests.post(reload_url, headers=headers)
            
            if response.status_code == 200:
                print('[DEPLOY] ✅ Web app reloaded successfully!')
                return jsonify({
                    'status': 'success',
                    'message': 'Code pulled and app reloaded successfully'
                }), 200
            else:
                print(f'[ERROR] Reload failed: {response.status_code} - {response.text}')
                return jsonify({
                    'status': 'partial',
                    'message': f'Code pulled but reload failed: {response.status_code}'
                }), 500
                
        except Exception as reload_error:
            print(f'[ERROR] Reload error: {str(reload_error)}')
            return jsonify({
                'status': 'partial',
                'message': f'Code pulled but reload failed: {str(reload_error)}'
            }), 500
            
    except subprocess.CalledProcessError as e:
        print(f'[ERROR] Git pull failed: {e.stderr}')
        return jsonify({
            'status': 'error',
            'message': f'Git pull failed: {e.stderr}'
        }), 500
    except Exception as e:
        print(f'[ERROR] Unexpected error: {str(e)}')
        return jsonify({
            'status': 'error',
            'message': f'Unexpected error: {str(e)}'
        }), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'service': 'github-webhook-handler'}), 200

if __name__ == '__main__':
    print('[SERVER] Starting GitHub Webhook Handler...')
    print(f'[SERVER] Listening on port 5001')
    print(f'[SERVER] Webhook URL: https://{PYTHONANYWHERE_DOMAIN}/webhook')
    print(f'[SERVER] Health check: https://{PYTHONANYWHERE_DOMAIN}/health')
    app.run(host='127.0.0.1', port=5001, debug=False)
