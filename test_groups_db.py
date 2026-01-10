#!/usr/bin/env python
from backend.app import app, db, User, Group

with app.app_context():
    user = User.query.filter_by(email='metonline@gmail.com').first()
    if user:
        print(f"User found: {user.email}")
        print(f"Number of groups: {len(user.groups)}")
        for group in user.groups:
            print(f"  Group: {group.name} (Active: {group.is_active})")
    else:
        print("User not found")
    
    # Check all groups in database
    all_groups = Group.query.all()
    print(f"\nTotal groups in DB: {len(all_groups)}")
    for g in all_groups:
        print(f"  - {g.name} (Members: {len(g.members)})")
