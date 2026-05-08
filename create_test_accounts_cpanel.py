#!/usr/bin/env python
import requests
import json

# cPanel deployment URL
BASE_URL = 'https://hesappaylas.com/api'

# Test hesapları
test_accounts = [
    {'email': 'test1@example.com', 'password': 'Test123456!', 'firstName': 'Test', 'lastName': 'User1'},
    {'email': 'test2@example.com', 'password': 'Test123456!', 'firstName': 'Test', 'lastName': 'User2'},
    {'email': 'test3@example.com', 'password': 'Test123456!', 'firstName': 'Test', 'lastName': 'User3'},
]

print("=" * 60)
print("TEST HESAPLARI OLUŞTURULUYOR (cPanel)")
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
            timeout=10,
            verify=True)  # SSL verification enabled
        
        if r.status_code in [201, 200]:
            print(f"\n✅ BAŞARILI: {acc['email']}")
            print(f"   Password: {acc['password']}")
            created_accounts.append(acc)
        elif r.status_code == 409:
            print(f"\n⚠️  ZATİ VAR: {acc['email']}")
        else:
            print(f"\n❌ HATA ({r.status_code}): {acc['email']}")
            try:
                print(f"   Response: {r.json()}")
            except:
                print(f"   Response: {r.text[:200]}")
    except Exception as e:
        print(f"\n❌ BAĞLANTI HATASI: {acc['email']}")
        print(f"   {str(e)[:200]}")

print("\n" + "=" * 60)
print("ÖZET - GİRİŞ İÇİN KULLANABİLECEĞİN HESAPLAR:")
print("=" * 60)

if created_accounts:
    for acc in created_accounts:
        print(f"\nEmail: {acc['email']}")
        print(f"Password: {acc['password']}")
else:
    print("\n⚠️  Hiçbir hesap oluşturulamadı.")
    print("Kontrol et: Backend /api/auth/signup endpoint'i çalışıyor mu?")

print("\n" + "=" * 60)
