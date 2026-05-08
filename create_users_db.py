#!/usr/bin/env python3
"""Create users directly in database"""
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

# Set environment
os.environ['PYTHONIOENCODING'] = 'utf-8'
os.environ['DATABASE_URL'] = 'sqlite:///hesap_paylas.db'
os.environ['FLASK_ENV'] = 'development'

from dotenv import load_dotenv
load_dotenv()

print("=" * 60)
print("Yeni Kullanıcı Oluşturma (Database)")
print("=" * 60)

try:
    from backend.app import app, db, User
    
    with app.app_context():
        users_to_create = [
            {
                "email": "nozcakar73@gmail.com",
                "password": "6573",
                "firstName": "Naz",
                "lastName": "Çakar",
                "phone": "+905551234567"
            },
            {
                "email": "xbobix@gmail.com",
                "password": "1234",
                "firstName": "Xbobix",
                "lastName": "User",
                "phone": "+905559876543"
            }
        ]
        
        for user_data in users_to_create:
            email = user_data['email']
            
            # Check if user exists
            existing = User.query.filter_by(email=email).first()
            
            if existing:
                print(f"\n⏭️  Mevcut: {email}")
                print(f"   ID: {existing.id}")
                print(f"   Ad: {existing.first_name} {existing.last_name}")
            else:
                print(f"\n✨ Oluşturuluyor: {email}")
                
                user = User(
                    first_name=user_data['firstName'],
                    last_name=user_data['lastName'],
                    email=email,
                    phone=user_data['phone']
                )
                user.set_password(user_data['password'])
                
                db.session.add(user)
                db.session.commit()
                
                print(f"   ✅ Başarılı!")
                print(f"   ID: {user.id}")
                print(f"   Ad: {user.first_name} {user.last_name}")
        
        # List all users
        print("\n" + "=" * 60)
        print("Tüm Kullanıcılar:")
        print("=" * 60)
        
        all_users = User.query.all()
        for user in all_users:
            print(f"\n👤 {user.first_name} {user.last_name}")
            print(f"   📧 Email: {user.email}")
            print(f"   📱 Telefon: {user.phone}")
            print(f"   🔑 ID: {user.id}")
        
        print(f"\n{'=' * 60}")
        print(f"Toplam: {len(all_users)} kullanıcı")
        print(f"{'=' * 60}")
        
except Exception as e:
    print(f"\n❌ Hata: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
