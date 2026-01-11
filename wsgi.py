"""
WSGI entry point for Flask
FORCE DEPLOY: 2026-01-11 13:45:00 - Service Worker disable fix v2.0.7
"""
import os
import sys
import random
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

# Load environment
from dotenv import load_dotenv
load_dotenv()

# Import and create database
from backend.app import app, db, User, Group

# Create tables on startup
with app.app_context():
    db.create_all()
    print("✓ Database initialized")
    
    # Initialize default user
    user = User.query.filter_by(email='metonline@gmail.com').first()
    if not user:
        try:
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
            print("✓ Default user created")
            
        except Exception as e:
            print(f"✗ Error creating default user: {str(e)}")
            db.session.rollback()
    else:
        # Reset password if exists (for deployment stability)
        user.set_password('test123')
        db.session.commit()
        print("✓ Default user password reset")
        
        # DON'T automatically create test groups - let users create their own
        group_count = len(user.groups) if user.groups else 0
        print(f"ℹ User has {group_count} group(s)")

# WSGI app must be available for Gunicorn
# This is the main entry point for production servers like Gunicorn

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    print(f"Starting Flask server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)

