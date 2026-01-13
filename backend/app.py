"""
Hesap Paylaş Backend
Flask + SQLAlchemy + PostgreSQL
"""

import os
import jwt
import random
import string
from datetime import datetime, timedelta
from functools import wraps
from pathlib import Path
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token

# Load env
load_dotenv()

# Get parent directory (main project root)
# On Render, working directory is /app, so this will resolve to /app
BASE_DIR = Path(__file__).parent.parent

# Fallback: if BASE_DIR/index.html doesn't exist, check common Render paths
if not (BASE_DIR / 'index.html').exists():
    # Try /app (Render default)
    alt_dir = Path('/app')
    if (alt_dir / 'index.html').exists():
        BASE_DIR = alt_dir
        print(f"[APP] Using alternative BASE_DIR: {BASE_DIR}", flush=True)

print(f"[APP] BASE_DIR: {BASE_DIR}")
print(f"[APP] BASE_DIR exists: {BASE_DIR.exists()}")
print(f"[APP] index.html exists: {(BASE_DIR / 'index.html').exists()}")
print(f"[APP] Files in BASE_DIR: {sorted([f.name for f in BASE_DIR.glob('*') if f.is_file()])[:10]}", flush=True)

# Initialize Flask - DON'T use static_folder for now, serve manually
# Using explicit path serving instead of Flask's static system
print(f"[INIT] Creating Flask app", flush=True)
app = Flask(__name__)
print(f"[INIT] Flask app created successfully", flush=True)

# Print all registered routes at startup (for debugging Render)
def print_routes():
    """Print all registered Flask routes"""
    routes = []
    for rule in app.url_map.iter_rules():
        routes.append(f"{rule.rule} -> {rule.endpoint}")
    print(f"[ROUTES] Registered {len(routes)} routes", flush=True)

# Will be called after app is fully initialized
# print_routes() is called later in the code

# CORS configuration for GitHub Pages and local development
CORS(app, resources={
    r"/api/*": {
        "origins": ["*"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": False,
        "max_age": 3600
    }
})

# ==================== Database Initialization ====================
# Initialize database on first startup
@app.before_request
def init_db():
    """Initialize database if needed (runs once per process)"""
    if not hasattr(app, '_db_initialized'):
        try:
            db.create_all()
            # Ensure default user exists
            user = User.query.filter_by(email='metonline@gmail.com').first()
            if not user:
                user = User(
                    first_name='Metin',
                    last_name='Güven',
                    email='metonline@gmail.com',
                    phone='05323332222'
                )
                user.set_password('test123')
                db.session.add(user)
                db.session.commit()
            app._db_initialized = True
            print("[DB] Database initialized on first request", flush=True)
        except Exception as e:
            print(f"[DB] Initialization error: {e}", flush=True)
            # Don't crash, just log the error
            pass

# Config
# ABSOLUTE path for database - avoid path conflicts
database_url = None
db_type = None

# Try to use DATABASE_URL if available and valid
if os.getenv('DATABASE_URL'):
    test_url = os.getenv('DATABASE_URL')
    # Check if we can actually use this database
    if 'postgres' in test_url.lower():
        # Try to import psycopg2 to check if PostgreSQL is available
        try:
            import psycopg2
            database_url = test_url
            if database_url.startswith('postgres://'):
                database_url = database_url.replace('postgres://', 'postgresql://', 1)
            db_type = 'PostgreSQL (Render)'
        except ImportError:
            # psycopg2 not installed - will fall back to SQLite below
            print("[WARN] psycopg2 not installed - falling back to SQLite")
            pass
    elif 'mysql' in test_url.lower():
        database_url = test_url
        db_type = 'MySQL (cPanel)'

if not database_url:
    # Check RENDER_DATABASE_URL as backup
    if os.getenv('RENDER_DATABASE_URL'):
        test_url = os.getenv('RENDER_DATABASE_URL')
        try:
            import psycopg2
            database_url = test_url
            if database_url.startswith('postgres://'):
                database_url = database_url.replace('postgres://', 'postgresql://', 1)
            db_type = 'PostgreSQL (Render)'
        except ImportError:
            print("[WARN] psycopg2 not installed, RENDER_DATABASE_URL ignored")
            pass

if not database_url:
    # Fall back to local SQLite
    instance_path = os.path.join(BASE_DIR, 'backend', 'instance')
    os.makedirs(instance_path, exist_ok=True)
    db_path = os.path.join(instance_path, 'hesap_paylas.db')
    database_url = f'sqlite:///{db_path}'
    db_type = 'SQLite (Local)'

# Log database selection
print(f"\n{'='*60}")
print(f"Database: {db_type}")
print(f"Status: {'Configured' if 'sqlite' not in database_url else 'Ready'}")
print(f"{'='*60}\n")

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret')
app.config['JWT_SECRET'] = os.getenv('JWT_SECRET', 'jwt-secret')
app.config['JWT_EXPIRATION'] = 86400 * 7  # 7 days

# Connection pooling for PostgreSQL
if 'postgresql' in database_url:
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_size': 10,
        'pool_recycle': 3600,
        'pool_pre_ping': True,
        'max_overflow': 20,
    }

db = SQLAlchemy(app)

# ==================== Real-time Database Sync ====================

# Store Render connection for sync
render_db = None

def get_render_connection():
    """Get Render PostgreSQL connection for real-time sync"""
    global render_db
    if render_db is None and os.getenv('RENDER_DATABASE_URL'):
        try:
            from sqlalchemy import create_engine
            render_url = os.getenv('RENDER_DATABASE_URL')
            if render_url.startswith('postgres://'):
                render_url = render_url.replace('postgres://', 'postgresql://', 1)
            render_db = create_engine(render_url, echo=False)
            print("✓ Render sync connection established")
        except Exception as e:
            print(f"⚠️  Render sync not available: {e}")
    return render_db

def sync_to_render(table_name, operation, data):
    """Sync data to Render PostgreSQL in real-time"""
    if os.getenv('FLASK_ENV') == 'development' and 'sqlite' in database_url:
        # Only sync if we're using SQLite locally and Render is configured
        if os.getenv('RENDER_DATABASE_URL'):
            try:
                render_conn = get_render_connection()
                if render_conn:
                    with render_conn.connect() as conn:
                        if operation == 'insert':
                            # SQL insert will be handled by the sync script
                            pass
                        elif operation == 'update':
                            pass
                        elif operation == 'delete':
                            pass
            except Exception as e:
                print(f"⚠️  Sync to Render failed: {e}")

# ==================== Models ====================

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    password_hash = db.Column(db.String(255), nullable=True)
    avatar_url = db.Column(db.String(255), nullable=True)
    bonus_points = db.Column(db.Integer, default=0)
    reset_token = db.Column(db.String(255), nullable=True)
    reset_token_expires = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, default=True)  # Hesap kapalı/açık
    is_deleted = db.Column(db.Boolean, default=False)  # Hesap silindi mi?
    account_type = db.Column(db.String(20), default='owner')  # 'owner' (hesap açan) or 'member' (invite edilen)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    orders = db.relationship('Order', backref='creator', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'firstName': self.first_name,
            'lastName': self.last_name,
            'email': self.email,
            'phone': self.phone,
            'bonusPoints': self.bonus_points,
            'createdAt': self.created_at.isoformat(),
            'is_account_owner': self.account_type == 'owner'  # Frontend tarafı için
        }

class Group(db.Model):
    __tablename__ = 'groups'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    code = db.Column(db.String(10), unique=True, nullable=False, default=lambda: generate_group_code())  # 6 digit code: XXX-XXX
    qr_code = db.Column(db.String(255), nullable=True)
    category = db.Column(db.String(100), nullable=True, default='Genel Yaşam')  # Cafe/Restaurant, Genel Yaşam, Seyahat/Konaklama
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)  # Grup kapalı/açık
    
    # Many-to-many relationship with users
    members = db.relationship('User', secondary='group_members', backref='groups')
    orders = db.relationship('Order', backref='group', lazy=True)

# Association table for group members (many-to-many)
group_members = db.Table('group_members',
    db.Column('group_id', db.Integer, db.ForeignKey('groups.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True)
)

class Order(db.Model):
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), nullable=True)
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    restaurant = db.Column(db.String(100), nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    tax = db.Column(db.Float, default=0)
    delivery = db.Column(db.Float, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')
    bills = db.relationship('MemberBill', backref='order', lazy=True, cascade='all, delete-orphan')

class OrderItem(db.Model):
    __tablename__ = 'order_items'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, default=1)

class MemberBill(db.Model):
    __tablename__ = 'member_bills'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    items = db.Column(db.JSON, nullable=True)  # JSON array of items

@app.after_request
def sync_to_render_after_request(response):
    """After each request, sync local changes to Render if using SQLite locally"""
    if os.getenv('FLASK_ENV') == 'development' and 'sqlite' in database_url:
        if os.getenv('RENDER_DATABASE_URL') and request.method in ['POST', 'PUT', 'DELETE']:
            try:
                # Queue async sync to Render (non-blocking)
                import threading
                def background_sync():
                    try:
                        import sqlite3
                        import json as json_lib
                        from sqlalchemy import create_engine, text
                        
                        sqlite_path = os.path.join(BASE_DIR, 'backend', 'instance', 'hesap_paylas.db')
                        render_url = os.getenv('RENDER_DATABASE_URL')
                        if render_url.startswith('postgres://'):
                            render_url = render_url.replace('postgres://', 'postgresql://', 1)
                        
                        # Read from SQLite
                        sqlite_conn = sqlite3.connect(sqlite_path)
                        sqlite_conn.row_factory = sqlite3.Row
                        sqlite_cursor = sqlite_conn.cursor()
                        
                        # Connect to Render
                        render_engine = create_engine(render_url)
                        render_conn = render_engine.connect()
                        
                        # Sync users
                        sqlite_cursor.execute("SELECT * FROM users")
                        for row in sqlite_cursor.fetchall():
                            check_sql = text("SELECT id FROM users WHERE email = :email LIMIT 1")
                            result = render_conn.execute(check_sql, {"email": row['email']})
                            if not result.fetchone():
                                insert_sql = text("""
                                    INSERT INTO users (first_name, last_name, email, phone, password_hash, is_active)
                                    VALUES (:fn, :ln, :em, :ph, :ph_hash, :active)
                                    ON CONFLICT (email) DO NOTHING
                                """)
                                render_conn.execute(insert_sql, {
                                    "fn": row['first_name'],
                                    "ln": row['last_name'],
                                    "em": row['email'],
                                    "ph": row['phone'],
                                    "ph_hash": row['password_hash'],
                                    "active": row['is_active']
                                })
                        
                        render_conn.commit()
                        sqlite_conn.close()
                        render_conn.close()
                    except Exception as sync_err:
                        print(f"⚠️  Background sync error: {sync_err}")
                
                # Run sync in background thread (non-blocking)
                sync_thread = threading.Thread(target=background_sync, daemon=True)
                sync_thread.start()
            except Exception as e:
                print(f"⚠️  Sync setup failed: {e}")
    
    return response

# ==================== Auth Routes ====================

@app.route('/api/auth/signup', methods=['POST'])
def signup():
    """User signup"""
    try:
        data = request.get_json()
        
        if not data or not all(k in data for k in ['email', 'password', 'firstName', 'lastName']):
            return jsonify({'error': 'Missing required fields'}), 400
        
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already exists'}), 409
        
        user = User(
            first_name=data['firstName'],
            last_name=data['lastName'],
            email=data['email'],
            phone=data.get('phone')
        )
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        # Note: Do NOT auto-add user to groups here
        # Users should only join groups via explicit invitation links or manual join
        # This was causing users to be added to ALL groups on signup
        
        token = generate_token(user.id)
        print(f"[SIGNUP] User created: {data['email']}")
        return jsonify({
            'message': 'User created successfully',
            'user': user.to_dict(),
            'token': token
        }), 201
    except Exception as e:
        db.session.rollback()
        print(f"[ERROR] Signup failed: {str(e)}")
        return jsonify({'error': 'Signup failed. Please try again.'}), 500

@app.route('/api/auth/login', methods=['POST', 'OPTIONS'])
def login():
    """User login"""
    if request.method == 'OPTIONS':
        return '', 200
    
    data = request.get_json()
    print(f"[LOGIN] Request - Email: {data.get('email') if data else 'No data'}")
    
    if not data or not all(k in data for k in ['email', 'password']):
        print("[LOGIN] Missing email or password")
        return jsonify({'error': 'Missing email or password'}), 400
    
    user = User.query.filter_by(email=data['email']).first()
    if not user:
        print(f"[LOGIN] User not found: {data['email']}")
        return jsonify({'error': 'user_not_found'}), 404
    if not user.check_password(data['password']):
        print(f"[LOGIN] Password mismatch for user: {data['email']}")
        return jsonify({'error': 'wrong_password'}), 401
    
    print(f"[LOGIN] Successful login for: {data['email']}")
    token = generate_token(user.id)
    return jsonify({
        'message': 'Login successful',
        'user': user.to_dict(),
        'token': token
    }), 200

@app.route('/api/auth/debug-users', methods=['GET'])
def debug_users():
    """Debug endpoint - list all users (remove in production)"""
    users = User.query.all()
    return jsonify({
        'total_users': len(users),
        'users': [{'id': u.id, 'email': u.email, 'name': f"{u.first_name} {u.last_name}"} for u in users]
    }), 200

@app.route('/api/auth/google', methods=['POST'])
def google_signup():
    """Google OAuth signup/login"""
    data = request.get_json()
    
    if not data or 'token' not in data:
        return jsonify({'error': 'Missing token'}), 400
    
    try:
        # Verify Google token
        idinfo = id_token.verify_oauth2_token(
            data['token'],
            google_requests.Request(),
            '625132087724-43j0qmqgh8kds471d73oposqthr8tt1h.apps.googleusercontent.com'
        )
        
        # Extract user info from Google token
        google_id = idinfo['sub']
        email = idinfo['email']
        first_name = idinfo.get('given_name', 'User')
        last_name = idinfo.get('family_name', '')
        
        # Check if user exists
        user = User.query.filter_by(email=email).first()
        
        if not user:
            # Create new user
            user = User(
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=None
            )
            # Random password (user won't need it with Google auth)
            user.set_password(f"google_{google_id}")
            db.session.add(user)
            db.session.commit()
        
        # Generate token
        token = generate_token(user.id)
        return jsonify({
            'message': 'Login successful',
            'user': user.to_dict(),
            'token': token
        }), 200
    
    except Exception as e:
        return jsonify({'error': f'Invalid token: {str(e)}'}), 401

@app.route('/api/auth/request-password-reset', methods=['POST'])
def request_password_reset():
    """Request password reset - send reset code to email"""
    try:
        data = request.get_json()
        
        if not data or 'email' not in data:
            return jsonify({'error': 'Email is required'}), 400
        
        user = User.query.filter_by(email=data['email']).first()
        
        if not user:
            # Don't reveal if email exists
            return jsonify({'message': 'If email exists, reset instructions have been sent'}), 200
        
        # Generate reset token (simple approach: use JWT)
        reset_payload = {
            'user_id': user.id,
            'purpose': 'password_reset',
            'exp': datetime.utcnow() + timedelta(hours=1)  # 1 hour expiration
        }
        reset_token = jwt.encode(reset_payload, app.config['JWT_SECRET'], algorithm='HS256')
        
        # Store reset token in database
        user.reset_token = reset_token
        user.reset_token_expires = datetime.utcnow() + timedelta(hours=1)
        db.session.commit()
        
        # In a real app, send email here with reset link/code
        # For now, return the token in response (frontend will store it)
        print(f"[PASSWORD] Reset token generated for {data['email']}")
        return jsonify({
            'message': 'Password reset token generated',
            'resetToken': reset_token,
            'expiresIn': 3600  # 1 hour in seconds
        }), 200
    except Exception as e:
        db.session.rollback()
        print(f"[ERROR] Password reset request failed: {str(e)}")
        return jsonify({'error': 'Password reset request failed. Please try again.'}), 500

@app.route('/api/auth/reset-password', methods=['POST'])
def reset_password():
    """Reset password using reset token"""
    try:
        data = request.get_json()
        
        if not data or not all(k in data for k in ['resetToken', 'newPassword']):
            return jsonify({'error': 'Reset token and new password are required'}), 400
        
        try:
            # Verify reset token
            payload = jwt.decode(data['resetToken'], app.config['JWT_SECRET'], algorithms=['HS256'])
            
            if payload.get('purpose') != 'password_reset':
                return jsonify({'error': 'Invalid reset token'}), 401
            
            user = User.query.get(payload['user_id'])
            
            if not user or user.reset_token != data['resetToken']:
                return jsonify({'error': 'Invalid or expired reset token'}), 401
            
            if user.reset_token_expires < datetime.utcnow():
                return jsonify({'error': 'Reset token has expired'}), 401
            
            # Update password
            user.set_password(data['newPassword'])
            user.reset_token = None
            user.reset_token_expires = None
            db.session.commit()
            
            print(f"[PASSWORD] Password reset successful")
            return jsonify({'message': 'Password reset successful'}), 200
            
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Reset token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid reset token'}), 401
    except Exception as e:
        db.session.rollback()
        print(f"[ERROR] Password reset failed: {str(e)}")
        return jsonify({'error': 'Password reset failed. Please try again.'}), 500

# ==================== Helper Functions ====================

def format_group_code(code):
    """Format 6-digit code as XXX-XXX (e.g., 123456 -> 123-456)"""
    if not code:
        return code
    code_str = str(code)
    if len(code_str) == 6:
        return f"{code_str[:3]}-{code_str[3:]}"
    return code_str

def generate_group_code():
    """Generate random 6-digit group code (stored as pure number)"""
    code = f"{random.randint(0, 999999):06d}"
    return code

def generate_token(user_id):
    """Generate JWT token"""
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(seconds=app.config['JWT_EXPIRATION'])
    }
    return jwt.encode(payload, app.config['JWT_SECRET'], algorithm='HS256')

def token_required(f):
    """Decorator for protected routes"""
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            token = request.headers.get('Authorization', '').replace('Bearer ', '')
            
            print(f"[AUTH] Token check - Headers: {request.headers.get('Authorization')[:20] if request.headers.get('Authorization') else 'NONE'}")
            
            if not token:
                print(f"[AUTH] Missing token!")
                return jsonify({'error': 'Missing token'}), 401
            
            try:
                payload = jwt.decode(token, app.config['JWT_SECRET'], algorithms=['HS256'])
                request.user_id = payload['user_id']
                print(f"[AUTH] Token valid - User ID: {request.user_id}")
            except jwt.ExpiredSignatureError:
                print(f"[AUTH] Token expired")
                return jsonify({'error': 'Token expired'}), 401
            except jwt.InvalidTokenError as e:
                print(f"[AUTH] Invalid token: {str(e)}")
                return jsonify({'error': 'Invalid token'}), 401
            
            return f(*args, **kwargs)
        except Exception as e:
            print(f"[AUTH] DECORATOR ERROR: {str(e)}", flush=True)
            import traceback
            traceback.print_exc()
            return jsonify({'error': f'Server error: {str(e)}'}), 500
    return decorated

# ==================== User Routes ====================

@app.route('/api/debug/token-test', methods=['GET'])
@token_required
def token_test():
    """Debug endpoint to test token"""
    print(f"[DEBUG] Token test - user_id: {request.user_id}", flush=True)
    user = User.query.get(request.user_id)
    return jsonify({
        'user_id': request.user_id,
        'user_email': user.email if user else 'NOT FOUND'
    }), 200

@app.route('/api/user/profile', methods=['GET'])
@token_required
def get_profile():
    """Get user profile"""
    user = User.query.get(request.user_id)
    return jsonify(user.to_dict()), 200

@app.route('/api/user/profile', methods=['PUT'])
@token_required
def update_profile():
    """Update user profile"""
    try:
        user = User.query.get(request.user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json() or {}
        
        if 'firstName' in data:
            user.first_name = data['firstName']
        if 'lastName' in data:
            user.last_name = data['lastName']
        if 'phone' in data:
            user.phone = data['phone']
        
        db.session.commit()
        print(f"[PROFILE] Updated for user {user.id}")
        return jsonify({'message': 'Profile updated', 'user': user.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        print(f"[ERROR] Profile update failed: {str(e)}")
        return jsonify({'error': 'Profile update failed. Please try again.'}), 500

@app.route('/api/user/change-password', methods=['POST'])
@token_required
def change_password():
    """Change user password"""
    try:
        user = User.query.get(request.user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        if not data or not all(k in data for k in ['oldPassword', 'newPassword']):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Verify old password
        if not user.check_password(data['oldPassword']):
            return jsonify({'error': 'Old password is incorrect'}), 401
        
        # Set new password
        user.set_password(data['newPassword'])
        db.session.commit()
        
        print(f"[PROFILE] Password changed for user {user.id}")
        return jsonify({'message': 'Password changed successfully'}), 200
    except Exception as e:
        db.session.rollback()
        print(f"[ERROR] Password change failed: {str(e)}")
        return jsonify({'error': 'Password change failed. Please try again.'}), 500

@app.route('/api/user/close-account', methods=['POST'])
@token_required
def close_account():
    """Close user account (deactivate) - keeps all data - only for account owners"""
    try:
        user = User.query.get(request.user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Sadece hesap sahibi hesabı kapatabilir
        if user.account_type != 'owner':
            return jsonify({
                'error': 'Only account owner can close this account. You are a member.'
            }), 403
        
        if not user.is_active:
            return jsonify({'error': 'Account is already closed'}), 400
        
        user.is_active = False
        db.session.commit()
        
        print(f"[ACCOUNT] Closed for user {user.id}")
        return jsonify({
            'message': 'Account closed successfully. Your data is preserved.',
            'is_active': user.is_active
        }), 200
    except Exception as e:
        db.session.rollback()
        print(f"[ERROR] Account close failed: {str(e)}")
        return jsonify({'error': 'Account close failed. Please try again.'}), 500

@app.route('/api/user/delete-account', methods=['DELETE'])
@token_required
def delete_account():
    """Permanently delete user account - only for active accounts and owners"""
    try:
        user = User.query.get(request.user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json() or {}
        
        # Sadece hesap sahibi hesabı silebilir
        if user.account_type != 'owner':
            return jsonify({
                'error': 'Only account owner can delete this account. You are a member.'
            }), 403
        
        # Kapalı hesaplar silinemez
        if not user.is_active:
            return jsonify({
                'error': 'Cannot delete closed accounts. Open the account first or contact support.'
            }), 400
        
        # İsteğe bağlı şifre doğrulama
        password = data.get('password')
        if password and not user.check_password(password):
            return jsonify({'error': 'Invalid password'}), 401
        
        # Hesabı mark as deleted yap (hard delete yerine soft delete)
        user.is_deleted = True
        user.is_active = False
        db.session.commit()
        
        print(f"[ACCOUNT] Deleted for user {user.id}")
        return jsonify({
            'message': 'Account permanently deleted. All data has been removed.'
        }), 200
    except Exception as e:
        db.session.rollback()
        print(f"[ERROR] Account delete failed: {str(e)}")
        return jsonify({'error': 'Account delete failed. Please try again.'}), 500

@app.route('/api/user/reopen-account', methods=['POST'])
@token_required
def reopen_account():
    """Reopen a closed account"""
    try:
        user = User.query.get(request.user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        if user.is_deleted:
            return jsonify({'error': 'Cannot reopen deleted accounts'}), 400
        
        if user.is_active:
            return jsonify({'error': 'Account is already active'}), 400
        
        user.is_active = True
        db.session.commit()
        
        print(f"[ACCOUNT] Reopened for user {user.id}")
        return jsonify({
            'message': 'Account reopened successfully',
            'is_active': user.is_active
        }), 200
    except Exception as e:
        db.session.rollback()
        print(f"[ERROR] Account reopen failed: {str(e)}")
        return jsonify({'error': 'Account reopen failed. Please try again.'}), 500

# ==================== Health Check ====================

@app.route('/health')
def health():
    """Simple health check endpoint"""
    return jsonify({'status': 'ok', 'timestamp': str(datetime.now())}), 200

# ==================== Static Files & Root Route ====================

@app.route('/')
def serve_index():
    """Serve index.html for root path"""
    try:
        index_file = BASE_DIR / 'index.html'
        print(f"[SERVE /] Attempting to serve from: {index_file}", flush=True)
        print(f"[SERVE /] File exists: {index_file.exists()}", flush=True)
        
        if not index_file.exists():
            print(f"[ERROR] index.html not found", flush=True)
            return jsonify({'error': f'Frontend not found at {index_file}'}), 503
        
        with open(index_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"[SERVE /] SUCCESS: Serving {len(content)} bytes", flush=True)
        return content, 200, {'Content-Type': 'text/html; charset=utf-8'}
    except Exception as e:
        import traceback
        print(f"[ERROR] serve_index failed: {e}", flush=True)
        print(traceback.format_exc(), flush=True)
        return jsonify({'error': f'Error: {str(e)}'}), 500



# ==================== Group Routes ====================

@app.route('/api/groups', methods=['POST'])
@token_required
def create_group():
    """Create new group with random color name and 6-digit QR code"""
    print("[GROUP] create_group called", flush=True)
    try:
        data = request.get_json()
        print(f"[GROUP] Request data: {data}", flush=True)
        if not data:
            return jsonify({'error': 'Invalid request data'}), 400
        
        # Color names for auto-generated group names
        colors_tr = [
            'Kırmızı', 'Yeşil', 'Mavi', 'Sarı', 'Mor', 'Turuncu', 'Pembe', 'Kahverengi',
            'Siyah', 'Beyaz', 'Gri', 'Camgöbeği', 'Krem', 'Leylak', 'Turkuaz', 'Füme',
            'İnci', 'Altın', 'Gümüş', 'Bakır', 'Bronz', 'Lacivert', 'Haki', 'Zeytin'
        ]
        
        # Generate unique 6-digit code (store as: 123456, display as: 123-456)
        group_code = generate_group_code()
        
        # Ensure code is unique
        attempts = 0
        while Group.query.filter_by(code=group_code).first() and attempts < 100:
            group_code = generate_group_code()
            attempts += 1
        
        # Generate random color name if no name provided
        group_name = data.get('name')
        if not group_name:
            group_name = random.choice(colors_tr)
        
        group = Group(
            name=group_name,
            description=data.get('description'),
            code=group_code,
            qr_code=None,
            category=data.get('category', 'Genel Yaşam'),
            created_by=request.user_id
        )
        
        db.session.add(group)
        
        # Add creator to group members BEFORE commit
        user = User.query.get(request.user_id)
        if user:
            group.members.append(user)
        else:
            print(f"[ERROR] User {request.user_id} not found!")
            return jsonify({'error': 'User not found'}), 500
        
        # Commit both group and membership at same time
        db.session.commit()
        print(f"[GROUP] Created: {group.name} (ID: {group.id}, Code: {group_code})")
        
        return jsonify({
            'success': True,
            'message': 'Group created successfully',
            'group': {
                'id': group.id,
                'name': group.name,
                'description': group.description,
                'category': group.category,
                'code': group.code,  # Raw 6-digit code (123456)
                'code_formatted': format_group_code(group.code),  # Formatted code (123-456)
                'created_at': group.created_at.isoformat()
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"[ERROR] Group creation failed: {str(e)}", flush=True)
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Failed to create group: {str(e)}'}), 500

@app.route('/api/groups/<int:group_id>', methods=['GET'])
@token_required
def get_group(group_id):
    """Get group details"""
    group = Group.query.get_or_404(group_id)
    creator = User.query.get(group.created_by) if group.created_by else None
    return jsonify({
        'id': group.id,
        'name': group.name,
        'description': group.description,
        'category': group.category,
        'code': group.code,
        'code_formatted': format_group_code(group.code),
        'qr_code': group.qr_code,
        'created_at': group.created_at.isoformat(),
        'created_by': group.created_by,
        'creator': creator.to_dict() if creator else None,
        'members': [u.to_dict() for u in group.members],
        'orders': [{
            'id': o.id,
            'restaurant': o.restaurant,
            'total_amount': o.total_amount,
            'created_at': o.created_at.isoformat() if o.created_at else None
        } for o in group.orders]
    }), 200

@app.route('/api/groups/join', methods=['POST'])
@token_required
def join_group():
    """Join group using QR code or group code"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid request data'}), 400
        
        qr_code = data.get('qr_code')
        group_code = data.get('code')
        
        group = None
        
        # Try to find by group code
        if group_code:
            # Handle both formats: "123456" (raw) and "123-456" (formatted)
            clean_code = group_code.replace('-', '')
            group = Group.query.filter_by(code=clean_code).first()
        
        # Fallback to QR code if not found
        if not group and qr_code:
            group = Group.query.filter_by(qr_code=qr_code).first()
        
        if not group:
            return jsonify({'error': 'Group not found'}), 404
        
        # Kullanıcıyı grup üyelerine ekle (zaten üyeyse kontrol et)
        user = User.query.get(request.user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        if user in group.members:
            return jsonify({
                'message': 'Already a member of this group',
                'id': group.id,
                'name': group.name
            }), 200
        
        group.members.append(user)
        db.session.commit()
        
        print(f"[GROUP] User {user.id} joined group {group.id}")
        return jsonify({
            'message': 'Successfully joined group',
            'id': group.id,
            'name': group.name,
            'description': group.description
        }), 201
    except Exception as e:
        db.session.rollback()
        print(f"[ERROR] Group join failed: {str(e)}")
        return jsonify({'error': 'Failed to join group. Please try again.'}), 500

@app.route('/api/user/groups', methods=['GET'])
@token_required
def get_user_groups():
    """Get all groups for current user - using ORM for reliability"""
    user = User.query.get(request.user_id)
    
    print(f"[GROUPS] User ID: {request.user_id}", flush=True)
    print(f"[GROUPS] User found: {user is not None}", flush=True)
    
    if not user:
        print(f"[GROUPS] User not found, returning empty array", flush=True)
        return jsonify([]), 200
    
    # Use ORM relationship instead of raw SQL to avoid tuple issues
    groups = [g for g in user.groups if g.is_active]
    
    print(f"[GROUPS] Found {len(groups)} active groups")
    
    groups_data = []
    for group in groups:
        print(f"[GROUPS] Group: {group.id} - {group.name}")
        groups_data.append({
            'id': group.id,
            'name': group.name,
            'description': group.description,
            'category': group.category,
            'code': group.code,
            'code_formatted': format_group_code(group.code),
            'qr_code': group.qr_code,
            'created_at': group.created_at.isoformat(),
            'members_count': len(group.members),
            'members': [{'id': m.id, 'first_name': m.first_name, 'last_name': m.last_name} for m in group.members],
            'status': 'active' if group.is_active else 'closed'
        })
    
    print(f"[GROUPS] Returning {len(groups_data)} groups")
    
    return jsonify(groups_data), 200

@app.route('/api/groups/<int:group_id>/close', methods=['POST'])
@token_required
def close_group(group_id):
    """Close a group - soft delete"""
    try:
        group = Group.query.get(group_id)
        if not group:
            return jsonify({'error': 'Group not found'}), 404
        
        user = User.query.get(request.user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Check if user is group creator (first member)
        if user not in group.members:
            return jsonify({'error': 'Unauthorized'}), 403
        
        # Mark as inactive (soft delete)
        group.is_active = False
        db.session.commit()
        
        print(f"[GROUP] Closed group {group_id} by user {user.id}")
        return jsonify({'message': 'Group closed successfully'}), 200
    except Exception as e:
        db.session.rollback()
        print(f"[ERROR] Group close failed: {str(e)}")
        return jsonify({'error': 'Failed to close group. Please try again.'}), 500

@app.route('/api/groups/<int:group_id>/delete', methods=['DELETE'])
@token_required
def delete_group(group_id):
    """Delete a group permanently - hard delete"""
    try:
        group = Group.query.get(group_id)
        if not group:
            return jsonify({'error': 'Group not found'}), 404
        
        user = User.query.get(request.user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json() or {}
        
        # Check if user is group creator
        if user not in group.members:
            return jsonify({'error': 'Unauthorized'}), 403
        
        # Password verification
        password = data.get('password')
        if password and not user.check_password(password):
            return jsonify({'error': 'Invalid password'}), 401
        
        # Only delete active groups
        if not group.is_active:
            return jsonify({'error': 'Cannot delete closed groups'}), 400
        
        # Hard delete
        db.session.delete(group)
        db.session.commit()
        
        print(f"[GROUP] Deleted group {group_id} by user {user.id}")
        return jsonify({'message': 'Group permanently deleted'}), 200
    except Exception as e:
        db.session.rollback()
        print(f"[ERROR] Group delete failed: {str(e)}")
        return jsonify({'error': 'Failed to delete group. Please try again.'}), 500

# ==================== Order Routes ====================

@app.route('/api/orders', methods=['POST'])
@token_required
def create_order():
    """Create new order"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid request data'}), 400
        
        order = Order(
            group_id=data.get('groupId'),
            creator_id=request.user_id,
            restaurant=data.get('restaurant'),
            total_amount=data.get('totalAmount', 0),
            tax=data.get('tax', 0),
            delivery=data.get('delivery', 0)
        )
        
        # Add items
        for item in data.get('items', []):
            order_item = OrderItem(
                name=item.get('name'),
                price=item.get('price'),
                quantity=item.get('quantity', 1)
            )
            order.items.append(order_item)
        
        db.session.add(order)
        db.session.commit()
        
        print(f"[ORDER] Created order {order.id}")
        return jsonify({
            'message': 'Order created',
            'orderId': order.id
        }), 201
    except Exception as e:
        db.session.rollback()
        print(f"[ERROR] Order creation failed: {str(e)}")
        return jsonify({'error': 'Failed to create order. Please try again.'}), 500

@app.route('/api/orders/<int:order_id>', methods=['GET'])
@token_required
def get_order(order_id):
    """Get order details"""
    order = Order.query.get_or_404(order_id)
    return jsonify({
        'id': order.id,
        'restaurant': order.restaurant,
        'totalAmount': order.total_amount,
        'tax': order.tax,
        'delivery': order.delivery,
        'items': [{'name': i.name, 'price': i.price, 'quantity': i.quantity} for i in order.items],
        'bills': [{'userId': b.user_id, 'amount': b.amount} for b in order.bills]
    }), 200

# ==================== Error Handlers ====================

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({'error': 'Server error'}), 500

@app.route('/api/debug/database', methods=['GET'])
def debug_database():
    """Debug endpoint - check database status"""
    from sqlalchemy import text
    
    try:
        # Check users
        user_count = db.session.execute(text("SELECT COUNT(*) FROM users")).scalar()
        
        # Check groups
        group_count = db.session.execute(text("SELECT COUNT(*) FROM groups")).scalar()
        
        # Check group_members
        gm_count = db.session.execute(text("SELECT COUNT(*) FROM group_members")).scalar()
        
        # Check group_members details
        gm_data = db.session.execute(text("SELECT * FROM group_members LIMIT 10")).fetchall()
        gm_list = [{'group_id': row[0], 'user_id': row[1]} for row in gm_data]
        
        return jsonify({
            'users': user_count,
            'groups': group_count,
            'group_members_total': gm_count,
            'group_members_sample': gm_list
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/debug/current-user', methods=['GET'])
@token_required
def debug_current_user():
    """Debug endpoint - check current logged-in user"""
    from sqlalchemy import text
    
    user_id = request.user_id
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Raw SQL query for groups
    sql = text("""
        SELECT DISTINCT g.id, g.name, g.code FROM groups g
        INNER JOIN group_members gm ON g.id = gm.group_id
        WHERE gm.user_id = :user_id AND g.is_active = true
    """)
    
    groups_result = db.session.execute(sql, {"user_id": user_id}).fetchall()
    groups_list = [{'id': row[0], 'name': row[1], 'code': row[2]} for row in groups_result]
    
    return jsonify({
        'user': {
            'id': user.id,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name
        },
        'groups_from_sql': groups_list,
        'groups_count': len(groups_list)
    }), 200

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get database statistics"""
    try:
        user_count = User.query.count()
        group_count = Group.query.count()
        order_count = Order.query.count()
        
        return jsonify({
            'users': user_count,
            'groups': group_count,
            'orders': order_count,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Root index.html - must be BEFORE wildcard route
@app.route('/api/admin/init-db', methods=['POST', 'GET'])
def init_db_admin():
    """Initialize database with default user and test group - Admin endpoint"""
    try:
        # Initialize tables
        db.create_all()
        print("✓ Database tables created")
        
        # Check/Create default user
        user = User.query.filter_by(email='metonline@gmail.com').first()
        if not user:
            user = User(
                first_name='Metin',
                last_name='Güven',
                email='metonline@gmail.com',
                phone='05323332222'
            )
            user.set_password('test123')
            db.session.add(user)
            db.session.flush()  # Flush to get user.id without committing
            db.session.commit()
            print(f"✓ Default user created (ID: {user.id})")
        else:
            print("✓ Default user already exists")
            # Reset password
            user.set_password('test123')
            db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Database initialized successfully',
            'user': user.email,
            'groups': len(user.groups)
        }), 200
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/')
def index():
    try:
        index_path = BASE_DIR / 'index.html'
        print(f'[DEBUG] Trying to load index.html from: {index_path}')
        print(f'[DEBUG] BASE_DIR: {BASE_DIR}')
        print(f'[DEBUG] Index exists: {index_path.exists()}')
        with open(index_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f'[ERROR] Failed to load index.html: {e}')
        return f'Error loading index.html: {e}', 500

# Serve static files (CSS, JS, etc)
@app.route('/css/<path:filename>')
def serve_css(filename):
    return send_from_directory(str(BASE_DIR), f'css/{filename}')

@app.route('/js/<path:filename>')
def serve_js(filename):
    return send_from_directory(str(BASE_DIR), f'js/{filename}')

# ==================== 404 Handler - Serve SPA ====================
# This catches ALL 404s and serves index.html for SPA routing

@app.errorhandler(404)
def not_found(error):
    """Handle 404 by serving index.html for SPA routing"""
    try:
        # First check if it's a real static file that exists
        requested_path = request.path.lstrip('/')
        if requested_path and not requested_path.startswith('api/'):
            file_path = BASE_DIR / requested_path
            if file_path.exists() and file_path.is_file():
                return send_from_directory(str(BASE_DIR), requested_path)
        
        # Otherwise serve index.html for SPA routing
        index_file = BASE_DIR / 'index.html'
        if index_file.exists():
            print(f"[SPA-404] Serving index.html for path: {request.path}", flush=True)
            with open(index_file, 'r', encoding='utf-8') as f:
                content = f.read()
            return content, 200, {'Content-Type': 'text/html; charset=utf-8'}
        
        # If index.html doesn't exist, return error
        print(f"[ERROR-404] index.html not found, path: {request.path}", flush=True)
        return jsonify({'error': 'Not Found'}), 404
    except Exception as e:
        print(f"[ERROR-404] Exception: {e}", flush=True)
        return jsonify({'error': 'Server Error'}), 500

# Print registered routes for debugging
print(f"[INIT] Flask app fully initialized", flush=True)
print_routes()

# ==================== Main ====================

if __name__ == '__main__':
    with app.app_context():
        # Create tables if they don't exist (preserve existing data)
        db.create_all()
        
        # Only create default users if none exist
        if User.query.count() == 0:
            # Initialize default user 1
            user1 = User(
                first_name='Metin',
                last_name='Güven',
                email='metonline@gmail.com',
                phone='05323332222',
                account_type='owner'
            )
            user1.set_password('test123')
            db.session.add(user1)
            
            # Initialize default user 2
            user2 = User(
                first_name='Metin',
                last_name='Güven',
                email='metin_guven@hotmail.com',
                phone='05323332222',
                account_type='owner'
            )
            user2.set_password('12345')
            db.session.add(user2)
            
            db.session.commit()
            print("[INIT] Database initialized with default users")
        else:
            print(f"[INIT] Database ready - {User.query.count()} users, {Group.query.count()} groups")
    
    port = int(os.getenv('PORT', 5000))
    # Debug mode ON for development (shows detailed error tracebacks)
    app.run(host='0.0.0.0', port=port, debug=True, use_reloader=False)
