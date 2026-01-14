#!/usr/bin/env python
"""
Cleanup script - Delete test user account from database
Run locally to remove old test accounts
"""
import sys

# Add backend to path
sys.path.insert(0, 'backend')

from app import app, db, User

def delete_user_by_phone(phone):
    """Delete a user by phone number"""
    with app.app_context():
        user = User.query.filter_by(phone=phone).first()
        
        if user:
            print(f"\n✓ Found user:")
            print(f"  Phone: {user.phone}")
            print(f"  Name: {user.first_name} {user.last_name}")
            print(f"  Email: {user.email}")
            print(f"  ID: {user.id}")
            
            # Confirm deletion
            confirm = input(f"\nDelete this user? (yes/no): ").strip().lower()
            
            if confirm == 'yes':
                db.session.delete(user)
                db.session.commit()
                print("✓ User deleted successfully!")
            else:
                print("Deletion cancelled")
        else:
            print(f"✗ User with phone {phone} not found")
            
            # Show all users
            print("\nAll users in database:")
            users = User.query.all()
            for u in users:
                print(f"  {u.phone} -> {u.first_name}")

if __name__ == '__main__':
    phone = '+905322578837'
    print(f"========================================")
    print(f"Cleanup: Delete test user account")
    print(f"Phone: {phone}")
    print(f"========================================")
    delete_user_by_phone(phone)
