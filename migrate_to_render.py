#!/usr/bin/env python
"""Migrate local SQLite data to Render PostgreSQL"""
import os
import sys
from datetime import datetime

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from dotenv import load_dotenv

load_dotenv()

# Check if DATABASE_URL is set for Render
render_db_url = os.getenv('DATABASE_URL')

if not render_db_url:
    print("❌ DATABASE_URL not found in .env")
    print("\nTo use Render database locally:")
    print("1. Go to Render dashboard → Database (hesap-paylas-db) → Info")
    print("2. Copy the 'External Connection String'")
    print("3. Add to .env: DATABASE_URL=postgresql://...")
    print("\nOr add manually to .env:")
    print("DATABASE_URL=postgresql://username:password@host:5432/dbname")
    sys.exit(1)

try:
    from backend.app import db, User, Group, Order, OrderItem, MemberBill, app
    import json
    
    # Step 1: Export data from SQLite
    print("📊 Step 1: Exporting data from local SQLite...")
    
    # Temporarily use SQLite
    sqlite_url = f'sqlite:///{os.path.join(os.path.dirname(__file__), "backend", "instance", "hesap_paylas.db")}'
    
    # Create temporary app with SQLite for export
    from flask import Flask
    sqlite_app = Flask(__name__)
    sqlite_app.config['SQLALCHEMY_DATABASE_URI'] = sqlite_url
    sqlite_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    from flask_sqlalchemy import SQLAlchemy
    sqlite_db = SQLAlchemy(sqlite_app)
    
    # Import models with sqlite_db
    with sqlite_app.app_context():
        from backend.app import User as SQLiteUser, Group as SQLiteGroup
        
        users = SQLiteUser.query.all()
        groups = SQLiteGroup.query.all()
        
        print(f"✓ Found {len(users)} users")
        print(f"✓ Found {len(groups)} groups")
        
        # Step 2: Insert into Render PostgreSQL
        print("\n📤 Step 2: Uploading to Render PostgreSQL...")
        
        with app.app_context():
            # Clear existing data first (optional, comment out to keep)
            # print("Clearing Render database...")
            # db.drop_all()
            # db.create_all()
            
            # Import users
            for user in users:
                existing = User.query.filter_by(email=user.email).first()
                if not existing:
                    new_user = User(
                        first_name=user.first_name,
                        last_name=user.last_name,
                        email=user.email,
                        phone=user.phone,
                        password_hash=user.password_hash,
                        bonus_points=user.bonus_points,
                        account_type=user.account_type,
                        created_at=user.created_at
                    )
                    db.session.add(new_user)
                    print(f"  ✓ Added user: {user.first_name} {user.last_name}")
            
            db.session.commit()
            print(f"\n✅ Migration complete!")
            print(f"   {len(users)} users migrated to Render PostgreSQL")
            
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
