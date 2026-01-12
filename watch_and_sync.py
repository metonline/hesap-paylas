#!/usr/bin/env python
"""
Real-time Database Sync Watcher
Lokal SQLite'deki değişiklikleri sürekli Render'a aktarır
Watches local SQLite for changes and syncs to Render in real-time
"""

import os
import sys
import time
import sqlite3
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

load_dotenv()

# Track last sync time per table
last_sync_times = {}

def sync_users_realtime(sqlite_path, render_url):
    """Sync users from SQLite to Render in real-time"""
    try:
        from sqlalchemy import create_engine, text
        
        sqlite_conn = sqlite3.connect(sqlite_path)
        sqlite_conn.row_factory = sqlite3.Row
        sqlite_cursor = sqlite_conn.cursor()
        
        # Connect to Render
        render_engine = create_engine(render_url, echo=False)
        render_conn = render_engine.connect()
        
        # Get all users from SQLite
        sqlite_cursor.execute("SELECT * FROM users ORDER BY updated_at DESC LIMIT 1")
        latest = sqlite_cursor.fetchone()
        
        if latest:
            # Check if there are new/updated users since last sync
            sqlite_cursor.execute("""
                SELECT * FROM users 
                WHERE updated_at > datetime('now', '-30 seconds')
            """)
            
            new_users = sqlite_cursor.fetchall()
            synced = 0
            
            for row in new_users:
                # Check if exists in Render
                check_sql = text("SELECT id FROM users WHERE email = :email LIMIT 1")
                result = render_conn.execute(check_sql, {"email": row['email']})
                
                if result.fetchone():
                    # Update
                    update_sql = text("""
                        UPDATE users 
                        SET first_name = :fn, last_name = :ln, phone = :ph,
                            password_hash = :ph_hash, bonus_points = :bp,
                            is_active = :active, is_deleted = :deleted,
                            account_type = :at, updated_at = NOW()
                        WHERE email = :email
                    """)
                    render_conn.execute(update_sql, {
                        "fn": row['first_name'],
                        "ln": row['last_name'],
                        "ph": row['phone'],
                        "ph_hash": row['password_hash'],
                        "bp": row['bonus_points'],
                        "active": row['is_active'],
                        "deleted": row['is_deleted'],
                        "at": row['account_type'],
                        "email": row['email']
                    })
                    synced += 1
                else:
                    # Insert
                    insert_sql = text("""
                        INSERT INTO users 
                        (first_name, last_name, email, phone, password_hash, 
                         bonus_points, is_active, is_deleted, account_type, created_at, updated_at)
                        VALUES (:fn, :ln, :em, :ph, :ph_hash, :bp, :active, :deleted, :at, NOW(), NOW())
                        ON CONFLICT (email) DO NOTHING
                    """)
                    render_conn.execute(insert_sql, {
                        "fn": row['first_name'],
                        "ln": row['last_name'],
                        "em": row['email'],
                        "ph": row['phone'],
                        "ph_hash": row['password_hash'],
                        "bp": row['bonus_points'],
                        "active": row['is_active'],
                        "deleted": row['is_deleted'],
                        "at": row['account_type']
                    })
                    synced += 1
            
            if synced > 0:
                render_conn.commit()
                print(f"✅ Synced {synced} users")
        
        sqlite_conn.close()
        render_conn.close()
        return True
        
    except Exception as e:
        print(f"❌ User sync error: {e}")
        return False

def sync_groups_realtime(sqlite_path, render_url):
    """Sync groups from SQLite to Render in real-time"""
    try:
        from sqlalchemy import create_engine, text
        
        sqlite_conn = sqlite3.connect(sqlite_path)
        sqlite_conn.row_factory = sqlite3.Row
        sqlite_cursor = sqlite_conn.cursor()
        
        # Connect to Render
        render_engine = create_engine(render_url, echo=False)
        render_conn = render_engine.connect()
        
        # Get all groups (simple approach - get all and upsert)
        sqlite_cursor.execute("SELECT * FROM groups")
        
        all_groups = sqlite_cursor.fetchall()
        synced = 0
        
        for row in all_groups:
            try:
                # Check if exists in Render
                check_sql = text("SELECT id FROM groups WHERE code = :code LIMIT 1")
                result = render_conn.execute(check_sql, {"code": row['code']})
                
                if not result.fetchone():
                    # Insert
                    insert_sql = text("""
                        INSERT INTO groups 
                        (name, code, description, created_by, is_active)
                        VALUES (:name, :code, :desc, :cb, :active)
                        ON CONFLICT (code) DO NOTHING
                    """)
                    render_conn.execute(insert_sql, {
                        "name": row['name'],
                        "code": row['code'],
                        "desc": row['description'] if row['description'] else None,
                        "cb": row['created_by'] if row['created_by'] else 1,
                        "active": row['is_active'] if row['is_active'] else True
                    })
                    synced += 1
            except Exception as row_err:
                print(f"⚠️  Row sync error for group {row['code']}: {row_err}")
                continue
        
        if synced > 0:
            try:
                render_conn.commit()
                print(f"✅ Synced {synced} groups")
            except Exception as commit_err:
                print(f"⚠️  Commit error: {commit_err}")
        
        sqlite_conn.close()
        render_conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Group sync error: {e}")
        return False

def watch_and_sync():
    """Watch SQLite and sync changes to Render in real-time"""
    
    render_url = os.getenv('RENDER_DATABASE_URL') or os.getenv('DATABASE_URL')
    if not render_url:
        print("❌ RENDER_DATABASE_URL not found in .env")
        print("Add: RENDER_DATABASE_URL=postgresql://...")
        return
    
    if render_url.startswith('postgres://'):
        render_url = render_url.replace('postgres://', 'postgresql://', 1)
    
    sqlite_path = os.path.join(os.path.dirname(__file__), 'backend', 'instance', 'hesap_paylas.db')
    
    if not os.path.exists(sqlite_path):
        print(f"❌ SQLite database not found: {sqlite_path}")
        return
    
    print("\n" + "="*70)
    print("🔄 REAL-TIME DATABASE SYNC WATCHER")
    print("="*70)
    print(f"📦 Local: {sqlite_path}")
    print(f"🌐 Render: {render_url[:50]}...")
    print("✅ Watching for changes... (Ctrl+C to stop)")
    print("="*70 + "\n")
    
    try:
        while True:
            # Sync users
            sync_users_realtime(sqlite_path, render_url)
            
            # Sync groups
            sync_groups_realtime(sqlite_path, render_url)
            
            # Check every 10 seconds
            time.sleep(10)
    
    except KeyboardInterrupt:
        print("\n\n❌ Watcher stopped")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    watch_and_sync()
