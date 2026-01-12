#!/usr/bin/env python3
"""
Emergency: Directly insert group_members into Render PostgreSQL
"""

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

render_url = os.getenv('DATABASE_URL')

if not render_url:
    print("❌ DATABASE_URL not found")
    exit(1)

print(f"Connecting to Render PostgreSQL...")
engine = create_engine(render_url)

try:
    with engine.connect() as conn:
        # First check current state
        result = conn.execute(text("SELECT COUNT(*) FROM group_members"))
        current_count = result.scalar()
        print(f"Current group_members count: {current_count}")
        
        result = conn.execute(text("SELECT COUNT(*) FROM users"))
        user_count = result.scalar()
        print(f"Users count: {user_count}")
        
        result = conn.execute(text("SELECT COUNT(*) FROM groups"))
        group_count = result.scalar()
        print(f"Groups count: {group_count}")
        
        # Check which users and groups exist
        result = conn.execute(text("SELECT id, email FROM users"))
        users = result.fetchall()
        print(f"\nUsers:")
        for u in users:
            print(f"  - ID: {u[0]}, Email: {u[1]}")
        
        result = conn.execute(text("SELECT id, name, code FROM groups"))
        groups = result.fetchall()
        print(f"\nGroups:")
        for g in groups:
            print(f"  - ID: {g[0]}, Name: {g[1]}, Code: {g[2]}")
        
        # If both exist, create memberships
        if user_count > 0 and group_count > 0:
            print("\n🔄 Creating group memberships...")
            
            # Get first user
            result = conn.execute(text("SELECT id FROM users LIMIT 1"))
            user_id = result.scalar()
            
            # Add to all groups
            result = conn.execute(text("SELECT id FROM groups"))
            groups = result.fetchall()
            
            inserted = 0
            for group in groups:
                group_id = group[0]
                
                # Check if membership exists
                check = conn.execute(
                    text("SELECT COUNT(*) FROM group_members WHERE user_id = :uid AND group_id = :gid"),
                    {"uid": user_id, "gid": group_id}
                )
                exists = check.scalar()
                
                if not exists:
                    # Insert
                    conn.execute(
                        text("INSERT INTO group_members (user_id, group_id) VALUES (:uid, :gid)"),
                        {"uid": user_id, "gid": group_id}
                    )
                    inserted += 1
                    print(f"  ✓ Added user {user_id} to group {group_id}")
            
            conn.commit()
            print(f"\n✅ {inserted} memberships added!")
            
            # Final check
            result = conn.execute(text("SELECT COUNT(*) FROM group_members"))
            final_count = result.scalar()
            print(f"Final group_members count: {final_count}")
        else:
            print("❌ No users or groups found to create memberships")
            
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
