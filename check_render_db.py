#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Check Render database status"""

import os
from dotenv import load_dotenv
from sqlalchemy import text

load_dotenv()

database_url = os.getenv('DATABASE_URL')
if database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)

print(f"Database URL: {database_url[:80]}...")
print(f"Checking if Render PostgreSQL is active...\n")

from backend.app import db, app, User, Group

with app.app_context():
    # Check users
    users = User.query.all()
    print(f"Users in Render: {len(users)}")
    for u in users:
        print(f"  - ID: {u.id}, Email: {u.email}, Name: {u.first_name}")
    
    # Check groups
    groups = Group.query.all()
    print(f"\nGroups in Render: {len(groups)}")
    for g in groups:
        print(f"  - ID: {g.id}, Name: {g.name}, Code: {g.code}, is_active: {g.is_active}")
    
    # Check group members
    result = db.session.execute(text("SELECT COUNT(*) as cnt FROM group_members"))
    gm_count = result.scalar()
    print(f"\nGroup Members in Render: {gm_count}")
    
    # SQL check
    result = db.session.execute(text("SELECT group_id, user_id FROM group_members"))
    for row in result:
        print(f"  - Group {row[0]} <-> User {row[1]}")
