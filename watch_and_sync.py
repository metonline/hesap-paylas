#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Real-time Database Sync Watcher
Watches local SQLite for changes and syncs to Render in real-time
Lokal SQLite'deki değişiklikleri sürekli Render'a aktarır
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

# Force UTF-8 on Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

last_sync_times = {}

def log(message):
    """Print with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}", flush=True)

def sync_users_realtime(sqlite_path, render_url):
    """Sync users from SQLite to Render in real-time"""
    try:
        from sqlalchemy import create_engine, text
        
        sqlite_conn = sqlite3.connect(sqlite_path)
        sqlite_conn.row_factory = sqlite3.Row
        sqlite_cursor = sqlite_conn.cursor()
        
        render_engine = create_engine(render_url, echo=False, pool_pre_ping=True)
        render_conn = render_engine.connect()
        
        sqlite_cursor.execute("SELECT * FROM users ORDER BY updated_at DESC")
        all_users = sqlite_cursor.fetchall()
        synced = 0
        
        for row in all_users:
            try:
                check_sql = text("SELECT id FROM users WHERE email = :email LIMIT 1")
                result = render_conn.execute(check_sql, {"email": row['email']})
                existing = result.fetchone()
                
                if existing:
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
                        "active": bool(row['is_active']),
                        "deleted": bool(row['is_deleted']),
                        "at": row['account_type'],
                        "email": row['email']
                    })
                else:
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
                        "active": bool(row['is_active']),
                        "deleted": bool(row['is_deleted']),
                        "at": row['account_type']
                    })
                
                synced += 1
            except Exception as row_err:
                log(f"[WARN] User sync error for {row['email']}: {str(row_err)[:100]}")
                continue
        
        if synced > 0:
            try:
                render_conn.commit()
                log(f"[SYNC] Synced {synced} users to Render")
            except Exception as e:
                log(f"[ERROR] Commit error: {str(e)[:100]}")
                render_conn.rollback()
        
        sqlite_conn.close()
        render_conn.close()
        return True
        
    except Exception as e:
        log(f"[ERROR] User sync failed: {str(e)[:100]}")
        return False

def sync_groups_realtime(sqlite_path, render_url):
    """Sync groups from SQLite to Render in real-time"""
    try:
        from sqlalchemy import create_engine, text
        
        sqlite_conn = sqlite3.connect(sqlite_path)
        sqlite_conn.row_factory = sqlite3.Row
        sqlite_cursor = sqlite_conn.cursor()
        
        render_engine = create_engine(render_url, echo=False, pool_pre_ping=True)
        render_conn = render_engine.connect()
        
        sqlite_cursor.execute("SELECT * FROM groups")
        all_groups = sqlite_cursor.fetchall()
        synced = 0
        
        for row in all_groups:
            try:
                check_sql = text("SELECT id FROM groups WHERE code = :code LIMIT 1")
                result = render_conn.execute(check_sql, {"code": row['code']})
                existing = result.fetchone()
                
                if not existing:
                    insert_sql = text("""
                        INSERT INTO groups 
                        (name, code, description, created_by, is_active, created_at, updated_at)
                        VALUES (:name, :code, :desc, :cb, :active, NOW(), NOW())
                        ON CONFLICT (code) DO NOTHING
                    """)
                    render_conn.execute(insert_sql, {
                        "name": row['name'],
                        "code": row['code'],
                        "desc": row.get('description'),
                        "cb": row.get('created_by', 1),
                        "active": bool(row.get('is_active', True))
                    })
                    synced += 1
            except Exception as row_err:
                log(f"[WARN] Group sync error for {row['code']}: {str(row_err)[:100]}")
                continue
        
        if synced > 0:
            try:
                render_conn.commit()
                log(f"[SYNC] Synced {synced} groups to Render")
            except Exception as e:
                log(f"[ERROR] Commit error: {str(e)[:100]}")
                render_conn.rollback()
        
        sqlite_conn.close()
        render_conn.close()
        return True
        
    except Exception as e:
        log(f"[ERROR] Group sync failed: {str(e)[:100]}")
        return False

def sync_group_members_realtime(sqlite_path, render_url):
    """Sync group members from SQLite to Render"""
    try:
        from sqlalchemy import create_engine, text
        
        sqlite_conn = sqlite3.connect(sqlite_path)
        sqlite_conn.row_factory = sqlite3.Row
        sqlite_cursor = sqlite_conn.cursor()
        
        render_engine = create_engine(render_url, echo=False, pool_pre_ping=True)
        render_conn = render_engine.connect()
        
        sqlite_cursor.execute("SELECT group_id, user_id FROM group_members")
        all_members = sqlite_cursor.fetchall()
        synced = 0
        
        for row in all_members:
            try:
                insert_sql = text("""
                    INSERT INTO group_members (group_id, user_id)
                    VALUES (:gid, :uid)
                    ON CONFLICT (group_id, user_id) DO NOTHING
                """)
                result = render_conn.execute(insert_sql, {
                    "gid": row['group_id'],
                    "uid": row['user_id']
                })
                synced += 1
            except Exception as row_err:
                log(f"[WARN] Group member sync error: {str(row_err)[:100]}")
                continue
        
        if synced > 0:
            try:
                render_conn.commit()
                log(f"[SYNC] Synced {synced} group members to Render")
            except Exception as e:
                log(f"[ERROR] Commit error: {str(e)[:100]}")
                render_conn.rollback()
        
        sqlite_conn.close()
        render_conn.close()
        return True
        
    except Exception as e:
        log(f"[ERROR] Group member sync failed: {str(e)[:100]}")
        return False

def watch_and_sync():
    """Main watch and sync loop"""
    
    render_url = os.getenv('RENDER_DATABASE_URL') or os.getenv('DATABASE_URL')
    if not render_url:
        log("[ERROR] RENDER_DATABASE_URL not found in .env")
        return
    
    if render_url.startswith('postgres://'):
        render_url = render_url.replace('postgres://', 'postgresql://', 1)
    
    sqlite_path = os.path.join(os.path.dirname(__file__), 'backend', 'instance', 'hesap_paylas.db')
    
    if not os.path.exists(sqlite_path):
        log(f"[ERROR] SQLite database not found: {sqlite_path}")
        return
    
    log("="*70)
    log("[START] Real-Time Database Sync Watcher")
    log("="*70)
    log(f"[CONFIG] Local DB: {sqlite_path}")
    log(f"[CONFIG] Render DB: {render_url[:50]}...")
    log("[CONFIG] Sync interval: 10 seconds")
    log("[STATUS] Watching for changes... (Press Ctrl+C to stop)")
    log("="*70)
    
    sync_count = 0
    
    try:
        while True:
            sync_count += 1
            log(f"\n[CYCLE {sync_count}] Starting sync cycle...")
            
            sync_users_realtime(sqlite_path, render_url)
            sync_groups_realtime(sqlite_path, render_url)
            sync_group_members_realtime(sqlite_path, render_url)
            
            log(f"[CYCLE {sync_count}] Waiting 10 seconds until next cycle...")
            
            time.sleep(10)
    
    except KeyboardInterrupt:
        log("\n" + "="*70)
        log("[STOPPED] Watcher stopped by user")
        log("="*70)
        sys.exit(0)
    except Exception as e:
        log("\n" + "="*70)
        log(f"[FATAL] Critical error: {e}")
        log("="*70)
        sys.exit(1)

if __name__ == '__main__':
    watch_and_sync()
