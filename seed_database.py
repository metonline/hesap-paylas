#!/usr/bin/env python
"""
Database seeding script - Initialize both local and remote databases with test data
Run this to sync databases across environments
"""

import os
from backend.app import app, db, User, Group

def seed_database():
    """Create test users and groups in current environment's database"""
    with app.app_context():
        # Clean existing data (optional - comment out if you want to keep data)
        # print('Clearing existing data...')
        # db.session.query(Group).delete()
        # db.session.query(User).delete()
        # db.session.commit()
        
        print('Seeding database...')
        
        # Create test user
        existing_user = User.query.filter_by(email='metonline@gmail.com').first()
        if not existing_user:
            user = User(
                first_name='Metin',
                last_name='Online',
                email='metonline@gmail.com',
                password_hash=None  # Will be set by set_password
            )
            user.set_password('test123')
            db.session.add(user)
            db.session.commit()
            print(f'✓ Created user: {user.email}')
        else:
            user = existing_user
            print(f'✓ User already exists: {user.email}')
        
        # Create test groups
        test_groups = [
            {'name': 'Arkadaşlar', 'description': 'Arkadaş grubu'},
            {'name': 'Aile', 'description': 'Aile üyeleri'},
            {'name': 'İş', 'description': 'İş arkadaşları'},
        ]
        
        for group_data in test_groups:
            existing_group = Group.query.filter_by(name=group_data['name']).first()
            if not existing_group:
                group = Group(
                    name=group_data['name'],
                    description=group_data['description'],
                    created_by=user.id
                )
                db.session.add(group)
                db.session.commit()
                
                # Add user to group
                if user not in group.members:
                    group.members.append(user)
                    db.session.commit()
                
                print(f'✓ Created group: {group.name} (code: {group.code})')
            else:
                print(f'✓ Group already exists: {group_data["name"]}')
        
        print('\n✅ Database seeding completed!')
        print(f'\nTest credentials:')
        print(f'  Email: metonline@gmail.com')
        print(f'  Password: test123')

if __name__ == '__main__':
    seed_database()
