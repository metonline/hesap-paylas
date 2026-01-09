#!/usr/bin/env python
import requests
import json

BASE_URL = 'https://hesap-paylas.onrender.com/api'

# Test hesapları
test_accounts = [
    {'email': 'test1@example.com', 'password': '12345', 'firstName': 'Test', 'lastName': 'User1'},
    {'email': 'test2@example.com', 'password': '12345', 'firstName': 'Test', 'lastName': 'User2'},
    {'email': 'ahmet@example.com', 'password': 'ahmet123', 'firstName': 'Ahmet', 'lastName': 'Yilmaz'},
    {'email': 'fatma@example.com', 'password': 'fatma123', 'firstName': 'Fatma', 'lastName': 'Kaya'},
]

print("=" * 60)
print("TEST HESAPLARI OLUŞTURULUYOR")
print("=" * 60)

created_accounts = []

for acc in test_accounts:
    try:
        r = requests.post(f'{BASE_URL}/auth/signup',
            json={
                'email': acc['email'],
                'password': acc['password'],
                'firstName': acc['firstName'],
                'lastName': acc['lastName'],
                'phone': '05323332222'
            },
            timeout=10)
        
        if r.status_code == 201:
            print(f"\n✅ BAŞARILI: {acc['email']}")
            print(f"   Şifre: {acc['password']}")
            created_accounts.append(acc)
        elif r.status_code == 409:
            print(f"\n⚠️  ZATİ VAR: {acc['email']}")
        else:
            print(f"\n❌ HATA ({r.status_code}): {acc['email']}")
            print(f"   Response: {r.json()}")
    except Exception as e:
        print(f"\n❌ BAĞLANTI HATASI: {acc['email']}")
        print(f"   {str(e)[:100]}")

print("\n" + "=" * 60)
print("ÖZET - GİRİŞ İÇİN KULLANABİLECEĞİN HESAPLAR:")
print("=" * 60)

for acc in created_accounts:
    print(f"\n📧 E-posta: {acc['email']}")
    print(f"🔐 Şifre: {acc['password']}")

print("\n" + "=" * 60)
