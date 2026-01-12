#!/usr/bin/env python
"""
Database Synchronization Script
Senkronize lokal ve Render PostgreSQL veritabanları
Sync local SQLite and Render PostgreSQL databases
"""

import os
import sys
from datetime import datetime
from pathlib import Path

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from dotenv import load_dotenv
load_dotenv()

def sync_local_to_render():
    """Lokal SQLite'den Render PostgreSQL'e veri taşı"""
    print("\n" + "="*70)
    print("📤 LOCAL → RENDER: Lokal veriler Render'a aktarılıyor...")
    print("="*70)
    
    render_db_url = os.getenv('RENDER_DATABASE_URL') or os.getenv('DATABASE_URL')
    if not render_db_url:
        print("❌ RENDER_DATABASE_URL veya DATABASE_URL .env'de bulunamadı!")
        print("\nRender Database URL'i almak için:")
        print("  1. Render Dashboard → PostgreSQL → Info")
        print("  2. 'External Connection String' kopyala")
        print("  3. .env'ye ekle: RENDER_DATABASE_URL=postgresql://...")
        return False
    
    try:
        from backend.app import db, app, User, Group, Order, OrderItem, MemberBill
        import sqlite3
        
        # 1. Lokal SQLite'den veri oku
        print("\n1️⃣  Lokal SQLite verisi okunuyor...")
        sqlite_path = os.path.join(os.path.dirname(__file__), 'backend', 'instance', 'hesap_paylas.db')
        
        if not os.path.exists(sqlite_path):
            print(f"⚠️  SQLite database bulunamadı: {sqlite_path}")
            print("   Lokal database yoksa, Render'dan indir veya yeni başla")
            return False
        
        # Render'a taşı
        print("\n2️⃣  Render PostgreSQL'e bağlanılıyor ve tablolar oluşturuluyor...")
        
        with app.app_context():
            # Tablolar oluştur
            db.create_all()
            print("   ✓ Render tablolar hazır")
            
            # SQLite'den oku, Render'a yaz
            conn = sqlite3.connect(sqlite_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Users
            print("\n   Kullanıcılar aktarılıyor...")
            cursor.execute("SELECT * FROM users")
            users = cursor.fetchall()
            user_count = 0
            for row in users:
                existing = User.query.filter_by(email=row['email']).first()
                if not existing:
                    new_user = User(
                        first_name=row['first_name'],
                        last_name=row['last_name'],
                        email=row['email'],
                        phone=row['phone'] if row['phone'] else None,
                        password_hash=row['password_hash'] if row['password_hash'] else None,
                        avatar_url=row['avatar_url'] if row['avatar_url'] else None,
                        bonus_points=row['bonus_points'] if row['bonus_points'] else 0,
                        is_active=bool(row['is_active']) if row['is_active'] is not None else True,
                        is_deleted=bool(row['is_deleted']) if row['is_deleted'] is not None else False,
                        account_type=row['account_type'] if row['account_type'] else 'owner'
                    )
                    db.session.add(new_user)
                    user_count += 1
            
            if user_count > 0:
                db.session.commit()
                print(f"   ✓ {user_count} yeni kullanıcı eklendi")
            else:
                print(f"   ✓ Tüm kullanıcılar zaten mevcut")
            
            # Groups
            print("   Gruplar aktarılıyor...")
            cursor.execute("SELECT * FROM groups")
            groups = cursor.fetchall()
            group_count = 0
            for row in groups:
                existing = Group.query.filter_by(code=row['code']).first()
                if not existing:
                    new_group = Group(
                        name=row['name'],
                        code=row['code'],
                        description=row['description'] if row['description'] else None,
                        created_by=row['created_by'] if row['created_by'] else 1
                    )
                    db.session.add(new_group)
                    group_count += 1
            
            if group_count > 0:
                db.session.commit()
                print(f"   ✓ {group_count} yeni grup eklendi")
            else:
                print(f"   ✓ Tüm gruplar zaten mevcut")
            
            # Group Members (many-to-many relationships) - RAW SQL kullanarak
            print("   Grup üyelikleri aktarılıyor...")
            cursor.execute("SELECT * FROM group_members")
            memberships = cursor.fetchall()
            membership_count = 0
            
            for row in memberships:
                group_id = row['group_id']
                user_id = row['user_id']
                
                # Render'da aynı membership var mı kontrol et (raw SQL)
                from sqlalchemy import text
                check_sql = text("SELECT COUNT(*) FROM group_members WHERE group_id = :gid AND user_id = :uid")
                result = db.session.execute(check_sql, {"gid": group_id, "uid": user_id})
                exists = result.scalar() > 0
                
                if not exists:
                    # Membership'i ekle (raw SQL - daha güvenilir)
                    insert_sql = text("""
                        INSERT INTO group_members (group_id, user_id)
                        VALUES (:gid, :uid)
                        ON CONFLICT DO NOTHING
                    """)
                    try:
                        db.session.execute(insert_sql, {"gid": group_id, "uid": user_id})
                        membership_count += 1
                    except Exception as e:
                        print(f"   ⚠️  Membership insert error: {e}")
            
            if membership_count > 0:
                db.session.commit()
                print(f"   ✓ {membership_count} grup üyeliği eklendi")
            else:
                print(f"   ✓ Tüm üyelikler zaten mevcut")
            
            conn.close()
        
        print("\n✅ Senkronizasyon başarılı!")
        print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        return True
        
    except Exception as e:
        print(f"\n❌ Hata: {e}")
        import traceback
        traceback.print_exc()
        return False


def sync_render_to_local():
    """Render PostgreSQL'den lokal SQLite'e veri taşı (backup)"""
    print("\n" + "="*70)
    print("📥 RENDER → LOCAL: Render verileri lokal'a yedekleniyor...")
    print("="*70)
    
    render_db_url = os.getenv('RENDER_DATABASE_URL') or os.getenv('DATABASE_URL')
    if not render_db_url:
        print("❌ RENDER_DATABASE_URL .env'de bulunamadı!")
        return False
    
    try:
        from flask import Flask
        from flask_sqlalchemy import SQLAlchemy
        from backend.app import User, Group
        
        # Render app
        render_app = Flask(__name__)
        render_app.config['SQLALCHEMY_DATABASE_URI'] = render_db_url
        render_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        render_db = SQLAlchemy(render_app)
        
        # Lokal app
        sqlite_path = os.path.join(os.path.dirname(__file__), 'backend', 'instance', 'hesap_paylas.db')
        local_app = Flask(__name__)
        local_app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{sqlite_path}'
        local_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        local_db = SQLAlchemy(local_app)
        
        print("\n1️⃣  Render PostgreSQL verisi okunuyor...")
        with render_app.app_context():
            users = render_db.session.query(User).all()
            groups = render_db.session.query(Group).all()
            
            print(f"   ✓ {len(users)} kullanıcı")
            print(f"   ✓ {len(groups)} grup")
        
        print("\n2️⃣  Lokal SQLite'e yazılıyor...")
        with local_app.app_context():
            local_db.create_all()
            
            with render_app.app_context():
                for user in render_db.session.query(User).all():
                    existing = local_db.session.query(User).filter_by(email=user.email).first()
                    if not existing:
                        new_user = User(
                            first_name=user.first_name,
                            last_name=user.last_name,
                            email=user.email,
                            phone=user.phone,
                            password_hash=user.password_hash,
                            avatar_url=user.avatar_url,
                            bonus_points=user.bonus_points,
                            is_active=user.is_active,
                            is_deleted=user.is_deleted,
                            account_type=user.account_type,
                            created_at=user.created_at,
                            updated_at=user.updated_at
                        )
                        local_db.session.add(new_user)
                
                local_db.session.commit()
                print(f"   ✓ {len([u for u in local_db.session.query(User).all()])} kullanıcı eklendi/güncellendi")
        
        print("\n✅ Yedekleme başarılı!")
        print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        return True
        
    except Exception as e:
        print(f"\n❌ Hata: {e}")
        import traceback
        traceback.print_exc()
        return False


def check_database_status():
    """Veritabanları kontrol et"""
    print("\n" + "="*70)
    print("🔍 DATABASE STATUS")
    print("="*70)
    
    # Lokal kontrol
    sqlite_path = os.path.join(os.path.dirname(__file__), 'backend', 'instance', 'hesap_paylas.db')
    print(f"\n📦 Local SQLite:")
    print(f"   Path: {sqlite_path}")
    print(f"   Exists: {'✓ Evet' if os.path.exists(sqlite_path) else '✗ Hayır'}")
    
    if os.path.exists(sqlite_path):
        try:
            from flask import Flask
            from flask_sqlalchemy import SQLAlchemy
            from backend.app import User, Group
            
            local_app = Flask(__name__)
            local_app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{sqlite_path}'
            local_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
            local_db = SQLAlchemy(local_app)
            
            with local_app.app_context():
                user_count = local_db.session.query(User).count()
                group_count = local_db.session.query(Group).count()
                print(f"   Users: {user_count}")
                print(f"   Groups: {group_count}")
        except Exception as e:
            print(f"   Error: {e}")
    
    # Render kontrol
    render_db_url = os.getenv('RENDER_DATABASE_URL') or os.getenv('DATABASE_URL')
    print(f"\n🌐 Render PostgreSQL:")
    
    if render_db_url:
        print(f"   Status: ✓ Configured")
        # URL'yi maskeleyerek göster
        masked_url = render_db_url.replace(render_db_url.split('@')[0].split('//')[1], '***')
        print(f"   URL: {masked_url[:50]}...")
        
        try:
            from flask import Flask
            from flask_sqlalchemy import SQLAlchemy
            from backend.app import User, Group
            
            render_app = Flask(__name__)
            render_app.config['SQLALCHEMY_DATABASE_URI'] = render_db_url
            render_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
            render_db = SQLAlchemy(render_app)
            
            with render_app.app_context():
                user_count = render_db.session.query(User).count()
                group_count = render_db.session.query(Group).count()
                print(f"   Users: {user_count}")
                print(f"   Groups: {group_count}")
                print(f"   Connection: ✓ Active")
        except Exception as e:
            print(f"   Connection: ✗ Failed")
            print(f"   Error: {str(e)[:60]}...")
    else:
        print(f"   Status: ✗ Not configured")
        print(f"   Add RENDER_DATABASE_URL to .env")


if __name__ == '__main__':
    print("\n" + "█"*70)
    print("█  HESAP PAYLAŞ - DATABASE SYNC TOOL")
    print("█"*70)
    
    if len(sys.argv) < 2:
        check_database_status()
        print("\n" + "="*70)
        print("KULLANIM:")
        print("="*70)
        print("  python sync_databases.py status      - Durum kontrol et")
        print("  python sync_databases.py local2render - Lokal → Render taşı")
        print("  python sync_databases.py render2local - Render → Lokal taşı (yedekle)")
        print("\nÖRNEKLER:")
        print("  python sync_databases.py status")
        print("  python sync_databases.py local2render")
        sys.exit(0)
    
    command = sys.argv[1].lower()
    
    if command == 'status':
        check_database_status()
    elif command == 'local2render':
        success = sync_local_to_render()
        sys.exit(0 if success else 1)
    elif command == 'render2local':
        success = sync_render_to_local()
        sys.exit(0 if success else 1)
    else:
        print(f"❌ Bilinmeyen komut: {command}")
        print("Desteklenen komutlar: status, local2render, render2local")
        sys.exit(1)
