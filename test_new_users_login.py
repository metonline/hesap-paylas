#!/usr/bin/env python3
"""Test login for new users"""
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

os.environ['PYTHONIOENCODING'] = 'utf-8'
os.environ['DATABASE_URL'] = 'sqlite:///hesap_paylas.db'
os.environ['FLASK_ENV'] = 'development'

from dotenv import load_dotenv
load_dotenv()

print("=" * 60)
print("Yeni Kullanıcılar Login Test")
print("=" * 60)

try:
    from backend.app import app
    
    client = app.test_client()
    
    test_logins = [
        {
            "email": "nozcakar73@gmail.com",
            "password": "6573",
            "name": "Naz Çakar"
        },
        {
            "email": "xbobix@gmail.com",
            "password": "1234",
            "name": "Xbobix"
        }
    ]
    
    for login_data in test_logins:
        print(f"\n🔐 Login Test: {login_data['name']}")
        print(f"   Email: {login_data['email']}")
        print(f"   Şifre: {login_data['password']}")
        
        response = client.post('/api/auth/login', 
            json={
                'email': login_data['email'],
                'password': login_data['password']
            },
            content_type='application/json'
        )
        
        if response.status_code == 200:
            data = response.get_json()
            user = data.get('user', {})
            print(f"\n   ✅ LOGIN BAŞARILI!")
            print(f"   👤 Kullanıcı: {user.get('firstName')} {user.get('lastName')}")
            print(f"   📧 Email: {user.get('email')}")
            print(f"   🔑 Token: {data.get('token')[:40]}...")
        else:
            error = response.get_json()
            print(f"\n   ❌ LOGIN BAŞARISIZ")
            print(f"   Hata: {error.get('error', 'Bilinmeyen hata')}")
    
    print(f"\n{'=' * 60}")
    print("✅ Tüm testler tamamlandı!")
    print(f"{'=' * 60}")
    
except Exception as e:
    print(f"\n❌ Hata: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
