#!/usr/bin/env python
"""
Seed test users into Render PostgreSQL database
Run this before starting Gunicorn
"""

import os
import sys
from pathlib import Path

print("[SEED] Starting seed script...", flush=True)
print(f"[SEED] DATABASE_URL: {os.getenv('DATABASE_URL', 'NOT SET')}", flush=True)
print(f"[SEED] RENDER_DATABASE_URL: {os.getenv('RENDER_DATABASE_URL', 'NOT SET')}", flush=True)

# Add backend to path
backend_path = Path(__file__).parent / 'backend'
sys.path.insert(0, str(backend_path))

try:
    print("[SEED] Importing Flask app...", flush=True)
    from app import app, db, User
    print("[SEED] ✓ Flask app imported", flush=True)
except Exception as e:
    print(f"[SEED] ❌ Failed to import Flask app: {e}", flush=True)
    import traceback
    traceback.print_exc()
    sys.exit(1)

def seed_database():
    """Create test users in database"""
    
    with app.app_context():
        # Create tables
        try:
            print("[SEED] Creating database tables...", flush=True)
            db.create_all()
            print("[SEED] ✅ Database tables created", flush=True)
        except Exception as e:
            print(f"[SEED] ❌ Error creating tables: {e}", flush=True)
            import traceback
            traceback.print_exc()
            return False
        
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
        print(f"[SEED] Processing {len(test_users)} test users...", flush=True)
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
                    print(f"[SEED]   ➕ Creating {user_data['email']}", flush=True)
                else:
                    print(f"[SEED]   ✓ {user_data['email']} already exists", flush=True)
            except Exception as e:
                print(f"[SEED]   ❌ Error creating {user_data['email']}: {e}", flush=True)
        
        print(f"[SEED] Committing {created_count} new users to database...", flush=True)
        try:
            db.session.commit()
            print(f"[SEED] ✅ Database seeded! Created {created_count} new users", flush=True)
            
            # Verify
            all_users = User.query.all()
            print(f"[SEED] 📊 Total users in database: {len(all_users)}", flush=True)
            for user in all_users:
                print(f"[SEED]    - {user.email} ({user.first_name} {user.last_name})", flush=True)
                
        except Exception as e:
            print(f"[SEED] ❌ Error committing seed data: {e}", flush=True)
            import traceback
            traceback.print_exc()
            db.session.rollback()
            return False
    
    return True

if __name__ == '__main__':
    print("[SEED] 🌱 Seeding Render database...", flush=True)
    try:
        success = seed_database()
        if success:
            print("[SEED] ✅ Seed script completed successfully", flush=True)
            sys.exit(0)
        else:
            print("[SEED] ⚠️  Seed script completed with errors", flush=True)
            sys.exit(0)  # Don't fail startup
    except Exception as e:
        print(f"[SEED] ❌ Seed script failed with exception: {e}", flush=True)
        import traceback
        traceback.print_exc()
        sys.exit(0)  # Don't fail startup - database might auto-initialize later
