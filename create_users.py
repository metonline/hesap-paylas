#!/usr/bin/env python3
"""Create new user accounts"""
import requests
import json
import sys

BASE_URL = "http://localhost:5000"
SIGNUP_URL = f"{BASE_URL}/api/auth/signup"

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

print("=" * 60)
print("Yeni Kullanıcı Oluşturma")
print("=" * 60)

for i, user_data in enumerate(users_to_create, 1):
    print(f"\n{i}️⃣  Kullanıcı oluşturuluyor: {user_data['email']}")
    print(f"   Şifre: {user_data['password']}")
    
    try:
        response = requests.post(SIGNUP_URL, json=user_data, timeout=10)
        print(f"   Status Code: {response.status_code}")
        
        result = response.json()
        
        if response.status_code in [200, 201]:
            print(f"   ✅ Başarılı!")
            print(f"   User ID: {result.get('user', {}).get('id')}")
            print(f"   Name: {result.get('user', {}).get('firstName')} {result.get('user', {}).get('lastName')}")
            if 'token' in result:
                print(f"   Token: {result.get('token')[:30]}...")
        else:
            print(f"   ❌ Hata: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"   ❌ Bağlantı hatası: {e}")

print("\n" + "=" * 60)
print("İşlem tamamlandı!")
print("=" * 60)
print("\n🔐 Login Yapılabilecek Hesaplar:")
print("─" * 60)
for user in users_to_create:
    print(f"📧 {user['email']}")
    print(f"🔑 Şifre: {user['password']}")
    print()
