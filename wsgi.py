"""
WSGI entry point for Flask
FORCE DEPLOY: 2026-01-11 13:45:00 - Service Worker disable fix v2.0.7
"""
import os
import sys
import random
from pathlib import Path

# Set UTF-8 encoding from the start
if sys.stdout.encoding != 'utf-8':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

print("[WSGI] Starting WSGI initialization...", flush=True)
print(f"[WSGI] Python: {sys.version}", flush=True)
print(f"[WSGI] Working directory: {os.getcwd()}", flush=True)

# Add project root to path
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))
print(f"[WSGI] Project root: {project_root}", flush=True)

# Load environment
from dotenv import load_dotenv
print("[WSGI] Loading environment...", flush=True)
load_dotenv()

# Import and create database
print("[WSGI] Importing Flask app...", flush=True)
from backend.app import app, db, User, Group
print("[WSGI] Flask app imported successfully", flush=True)

# Create tables on startup
print("[WSGI] Creating database tables...", flush=True)
with app.app_context():
    db.create_all()
    print("[WSGI] Database initialized", flush=True)
    
    # Initialize default user
    print("[WSGI] Checking default user...", flush=True)
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
            db.session.flush()
            db.session.commit()
            print("[WSGI] Default user created", flush=True)
            
        except Exception as e:
            print(f"[WSGI] Error creating default user: {str(e)}", flush=True)
            db.session.rollback()
    else:
        user.set_password('test123')
        db.session.commit()
        print("[WSGI] Default user password reset", flush=True)
        
        group_count = len(user.groups) if user.groups else 0
        print(f"[WSGI] User has {group_count} group(s)", flush=True)

print("[WSGI] WSGI initialization complete!", flush=True)
print(f"[WSGI] App routes registered: {len(app.url_map._rules)}", flush=True)

# WSGI app must be available for Gunicorn
# This is the main entry point for production servers like Gunicorn

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    print(f"Starting Flask server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)

