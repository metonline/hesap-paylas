#!/usr/bin/env python
"""Check total user count in database"""
import os
import sys
from dotenv import load_dotenv

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

load_dotenv()

try:
    from backend.app import db, User, app
    
    with app.app_context():
        user_count = User.query.count()
        print(f"Total users in database: {user_count}")
        
        # Also show some stats
        users = User.query.all()
        print(f"\nUser list:")
        for user in users:
            print(f"  - {user.first_name} {user.last_name} ({user.email})")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
