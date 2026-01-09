"""
Hesap Paylaş Backend
Flask + SQLAlchemy + PostgreSQL
"""

import os
import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token

# Load env
load_dotenv()

# Initialize
app = Flask(__name__)

# CORS configuration for GitHub Pages and local development
CORS(app, resources={
    r"/api/*": {
        "origins": [
            "https://metonline.github.io",
            "http://localhost:8000",
            "http://localhost:3000",
            "http://127.0.0.1:8000"
        ],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
    }
})

# Config
database_url = os.getenv('DATABASE_URL', 'sqlite:///hesap_paylas.db')
# Heroku PostgreSQL fix for SQLAlchemy 2.0
if database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret')
app.config['JWT_SECRET'] = os.getenv('JWT_SECRET', 'jwt-secret')
app.config['JWT_EXPIRATION'] = 86400 * 7  # 7 days

db = SQLAlchemy(app)

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
            'createdAt': self.created_at.isoformat()
        }

class Group(db.Model):
    __tablename__ = 'groups'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    qr_code = db.Column(db.String(255), nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
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

# ==================== Auth Routes ====================

@app.route('/api/auth/signup', methods=['POST'])
def signup():
    """User signup"""
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
    
    token = generate_token(user.id)
    return jsonify({
        'message': 'User created successfully',
        'user': user.to_dict(),
        'token': token
    }), 201

@app.route('/api/auth/login', methods=['POST'])
def login():
    """User login"""
    data = request.get_json()
    
    if not data or not all(k in data for k in ['email', 'password']):
        return jsonify({'error': 'Missing email or password'}), 400
    
    user = User.query.filter_by(email=data['email']).first()
    
    if not user or not user.check_password(data['password']):
        return jsonify({'error': 'Invalid email or password'}), 401
    
    token = generate_token(user.id)
    return jsonify({
        'message': 'Login successful',
        'user': user.to_dict(),
        'token': token
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
    return jsonify({
        'message': 'Password reset token generated',
        'resetToken': reset_token,
        'expiresIn': 3600  # 1 hour in seconds
    }), 200

@app.route('/api/auth/reset-password', methods=['POST'])
def reset_password():
    """Reset password using reset token"""
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
        
        return jsonify({'message': 'Password reset successful'}), 200
        
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Reset token has expired'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Invalid reset token'}), 401
    except Exception as e:
        return jsonify({'error': f'Password reset failed: {str(e)}'}), 500

# ==================== Helper Functions ====================

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
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        if not token:
            return jsonify({'error': 'Missing token'}), 401
        
        try:
            payload = jwt.decode(token, app.config['JWT_SECRET'], algorithms=['HS256'])
            request.user_id = payload['user_id']
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
        
        return f(*args, **kwargs)
    return decorated

# ==================== User Routes ====================

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
    user = User.query.get(request.user_id)
    data = request.get_json()
    
    if 'firstName' in data:
        user.first_name = data['firstName']
    if 'lastName' in data:
        user.last_name = data['lastName']
    if 'phone' in data:
        user.phone = data['phone']
    
    db.session.commit()
    return jsonify({'message': 'Profile updated', 'user': user.to_dict()}), 200

# ==================== Group Routes ====================

@app.route('/api/groups', methods=['POST'])
@token_required
def create_group():
    """Create new group"""
    data = request.get_json()
    
    group = Group(
        name=data.get('name', 'New Group'),
        description=data.get('description'),
        created_by=request.user_id
    )
    
    db.session.add(group)
    db.session.commit()
    
    return jsonify({
        'message': 'Group created',
        'groupId': group.id
    }), 201

@app.route('/api/groups/<int:group_id>', methods=['GET'])
@token_required
def get_group(group_id):
    """Get group details"""
    group = Group.query.get_or_404(group_id)
    return jsonify({
        'id': group.id,
        'name': group.name,
        'description': group.description,
        'members': [u.to_dict() for u in group.members],
        'orders': [o.id for o in group.orders]
    }), 200

@app.route('/api/groups/join', methods=['POST'])
@token_required
def join_group():
    """Join group using QR code"""
    data = request.get_json()
    qr_code = data.get('qr_code')
    
    if not qr_code:
        return jsonify({'error': 'QR code is required'}), 400
    
    # QR kodu ile grup bul
    group = Group.query.filter_by(qr_code=qr_code).first()
    
    if not group:
        return jsonify({'error': 'Group not found'}), 404
    
    # Kullanıcıyı grup üyelerine ekle (zaten üyeyse kontrol et)
    user = User.query.get(request.user_id)
    
    if user in group.members:
        return jsonify({
            'message': 'Already a member of this group',
            'id': group.id,
            'name': group.name
        }), 200
    
    group.members.append(user)
    db.session.commit()
    
    return jsonify({
        'message': 'Successfully joined group',
        'id': group.id,
        'name': group.name,
        'description': group.description
    }), 201

@app.route('/api/user/groups', methods=['GET'])
@token_required
def get_user_groups():
    """Get all groups for current user"""
    user = User.query.get(request.user_id)
    
    # Kullanıcının üyesi olduğu grupları getir
    user_groups = user.groups
    
    groups_data = []
    for group in user_groups:
        groups_data.append({
            'id': group.id,
            'name': group.name,
            'description': group.description,
            'qr_code': group.qr_code,
            'created_at': group.created_at.isoformat(),
            'status': 'active'  # TODO: Gerçek status kontrolü (kapalı/açık)
        })
    
    return jsonify(groups_data), 200

# ==================== Order Routes ====================

@app.route('/api/orders', methods=['POST'])
@token_required
def create_order():
    """Create new order"""
    data = request.get_json()
    
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
    
    return jsonify({
        'message': 'Order created',
        'orderId': order.id
    }), 201

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

# ==================== Health Check ====================

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'service': 'hesap-paylas-api'}), 200

# ==================== Main ====================

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=os.getenv('FLASK_ENV') == 'development')
