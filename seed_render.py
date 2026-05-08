#!/usr/bin/env python
"""
Seed test users into Render PostgreSQL database
Run this before starting Gunicorn
"""

import os
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / 'backend'
sys.path.insert(0, str(backend_path))

from app import app, db, User

def seed_database():
    """Create test users in database"""
    
    with app.app_context():
        # Create tables
        try:
            db.create_all()
            print("✅ Database tables created")
        except Exception as e:
            print(f"⚠️  Error creating tables: {e}")
        
        # Test users to create
        test_users = [
            {
                'email': 'metonline@gmail.com',
                'password': 'test123',
                'first_name': 'Metin',
                'last_name': 'Güven',
                'phone': '05323332222'
            },
            {
                'email': 'nozcakar73@gmail.com',
                'password': '6573',
                'first_name': 'Test',
                'last_name': 'User1',
                'phone': '05551234567'
            },
            {
                'email': 'xbobix@gmail.com',
                'password': '1234',
                'first_name': 'Test',
                'last_name': 'User2',
                'phone': '05559876543'
            },
            {
                'email': 'aaa@test.com',
                'password': '123',
                'first_name': 'Test',
                'last_name': 'AAA',
                'phone': '05551111111'
            },
            {
                'email': 'bbb@test.com',
                'password': '123',
                'first_name': 'Test',
                'last_name': 'BBB',
                'phone': '05552222222'
            },
            {
                'email': 'ccc@test.com',
                'password': '123',
                'first_name': 'Test',
                'last_name': 'CCC',
                'phone': '05553333333'
            }
        ]
        
        # Create users if they don't exist
        created_count = 0
        for user_data in test_users:
            try:
                existing = User.query.filter_by(email=user_data['email']).first()
                if not existing:
                    user = User(
                        email=user_data['email'],
                        first_name=user_data['first_name'],
                        last_name=user_data['last_name'],
                        phone=user_data['phone']
                    )
                    user.set_password(user_data['password'])
                    db.session.add(user)
                    created_count += 1
                    print(f"  ➕ Creating {user_data['email']}")
                else:
                    print(f"  ✓ {user_data['email']} already exists")
            except Exception as e:
                print(f"  ❌ Error creating {user_data['email']}: {e}")
        
        try:
            db.session.commit()
            print(f"\n✅ Database seeded! Created {created_count} new users")
            
            # Verify
            all_users = User.query.all()
            print(f"📊 Total users in database: {len(all_users)}")
            for user in all_users:
                print(f"   - {user.email} ({user.first_name} {user.last_name})")
                
        except Exception as e:
            print(f"❌ Error committing seed data: {e}")
            db.session.rollback()
            return False
    
    return True

if __name__ == '__main__':
    print("🌱 Seeding Render database...")
    success = seed_database()
    sys.exit(0 if success else 1)
