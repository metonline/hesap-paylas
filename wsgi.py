"""
WSGI entry point for Flask
"""
import os
import sys
from pathlib import Path

# Set UTF-8 encoding
os.environ['PYTHONIOENCODING'] = 'utf-8'

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent.absolute()))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Import Flask app
from backend.app import app

# Initialize database on startup
def init_database():
    """Initialize database on first startup"""
    try:
        from backend.app import db, User
        with app.app_context():
            db.create_all()
            user = User.query.filter_by(email='metonline@gmail.com').first()
            if not user:
                user = User(first_name='Metin', last_name='Güven', email='metonline@gmail.com', phone='05323332222')
                user.set_password('test123')
                db.session.add(user)
                db.session.commit()
    except Exception as e:
        print(f"[WSGI] Database init error (non-blocking): {e}")

if __name__ == '__main__':
    # Initialize database
    init_database()
    
    # Get port from environment or use default
    port = int(os.getenv('PORT', 10000))
    print(f"[WSGI] Starting Flask on port {port}")
    
    # For Render: use development server (not production-grade but works)
    # Render's free tier doesn't support Gunicorn well, use Flask dev server
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)



