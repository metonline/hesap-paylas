#!/usr/bin/env python
"""
Initialize Render database before Gunicorn starts
Run this as part of render.yaml's buildCommand or as a separate step
"""
import os
import sys
from pathlib import Path

# Setup Python path
sys.path.insert(0, str(Path(__file__).parent.absolute()))

# Load environment
from dotenv import load_dotenv
load_dotenv()

print("[INIT] Starting database initialization...")

try:
    from backend.app import app, db, User
    
    with app.app_context():
        print("[INIT] Creating database tables...")
        db.create_all()
        print("[INIT] ✓ Tables created")
        
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
            print("[INIT] ✓ Default user created")
        else:
            print("[INIT] ✓ Default user exists")
        
        print("[INIT] ✓ Database initialization complete!")
        
except Exception as e:
    print(f"[INIT] ✗ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
