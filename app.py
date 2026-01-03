"""
Hesap Paylaş - Backend Flask Application
A fair and quick bill splitting app for restaurants, travel, and shared expenses
"""

import os
import json
import hashlib
import uuid
from flask import Flask, render_template, jsonify, request, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__, static_folder='.')
CORS(app)

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['DEBUG'] = os.getenv('FLASK_ENV') == 'development'

# In-memory database for demo
users_db = {}
sessions = {}

def hash_password(password):
    """Hash password for storage"""
    return hashlib.sha256(password.encode()).hexdigest()

def generate_token():
    """Generate a unique token"""
    return str(uuid.uuid4())

# ==================== Routes ====================

@app.route('/')
def index():
    """Serve main HTML"""
    return send_from_directory('.', 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    """Serve static files"""
    if filename.endswith(('.css', '.js', '.json')):
        return send_from_directory('.', filename)
    return send_from_directory('.', 'index.html')

# ==================== API Routes (Placeholder) ====================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'message': 'Hesap Paylaş API is running',
        'version': '1.0.0'
    }), 200

@app.route('/api/auth/signup', methods=['POST'])
def signup():
    """User signup endpoint"""
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email ve şifre gerekli'}), 400
    
    email = data.get('email').lower().strip()
    password = data.get('password')
    first_name = data.get('first_name', '').strip()
    last_name = data.get('last_name', '').strip()
    phone = data.get('phone', '').strip()
    
    # Check if user already exists
    if email in users_db:
        return jsonify({'error': 'Bu e-posta zaten kayıtlı'}), 409
    
    # Create user
    user_id = str(uuid.uuid4())
    user = {
        'id': user_id,
        'email': email,
        'password_hash': hash_password(password),
        'first_name': first_name,
        'last_name': last_name,
        'phone': phone,
        'created_at': str(uuid.uuid4())  # timestamp placeholder
    }
    
    users_db[email] = user
    
    # Generate token
    token = generate_token()
    sessions[token] = {
        'user_id': user_id,
        'email': email
    }
    
    return jsonify({
        'message': 'Kaydolma başarılı',
        'token': token,
        'user': {
            'id': user['id'],
            'email': user['email'],
            'first_name': user['first_name'],
            'last_name': user['last_name'],
            'phone': user['phone']
        }
    }), 201

@app.route('/api/auth/login', methods=['POST'])
def login():
    """User login endpoint"""
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'E-posta ve şifre gerekli'}), 400
    
    email = data.get('email').lower().strip()
    password = data.get('password')
    
    # Check if user exists
    if email not in users_db:
        return jsonify({'error': 'E-posta veya şifre hatalı'}), 401
    
    user = users_db[email]
    
    # Verify password
    if user['password_hash'] != hash_password(password):
        return jsonify({'error': 'E-posta veya şifre hatalı'}), 401
    
    # Generate token
    token = generate_token()
    sessions[token] = {
        'user_id': user['id'],
        'email': email
    }
    
    return jsonify({
        'message': 'Giriş başarılı',
        'token': token,
        'user': {
            'id': user['id'],
            'email': user['email'],
            'first_name': user['first_name'],
            'last_name': user['last_name'],
            'phone': user['phone']
        }
    }), 200

@app.route('/api/user/profile', methods=['GET'])
def get_profile():
    """Get user profile"""
    # TODO: Implement profile endpoint
    return jsonify({
        'message': 'Profile endpoint - Coming soon'
    }), 200

@app.route('/api/groups', methods=['POST'])
def create_group():
    """Create a new group"""
    data = request.get_json()
    # TODO: Implement group creation
    return jsonify({
        'message': 'Group creation - Coming soon',
        'groupId': 'TMP-GROUP-ID'
    }), 201

@app.route('/api/orders', methods=['POST'])
def create_order():
    """Create a new order"""
    data = request.get_json()
    # TODO: Implement order creation and splitting
    return jsonify({
        'message': 'Order creation - Coming soon',
        'orderId': 'TMP-ORDER-ID'
    }), 201

@app.route('/api/orders/<order_id>', methods=['GET'])
def get_order(order_id):
    """Get order details"""
    # TODO: Implement order retrieval
    return jsonify({
        'message': 'Order retrieval - Coming soon',
        'orderId': order_id
    }), 200

# ==================== Error Handlers ====================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'error': 'Not Found',
        'message': 'The requested resource was not found'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({
        'error': 'Internal Server Error',
        'message': 'An unexpected error occurred'
    }), 500

# ==================== Main ====================

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)
