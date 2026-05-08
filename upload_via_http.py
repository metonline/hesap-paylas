import requests
import json

LOCAL_FILE = r'c:\Users\metin\Desktop\BILL\script.js'

# Dosya içeriğini oku
print("Dosya okunuyor...")
with open(LOCAL_FILE, 'r', encoding='utf-8') as f:
    content = f.read()

print(f"Dosya boyutu: {len(content)} bytes")

# Yüklenecek veri
payload = {
    'content': content
}

# Deneme URLs
urls = [
    'http://hesappaylas.com/api/admin/update-script',
    'http://hesappaylas.com/admin/update-script',
]

for url in urls:
    print(f"\n{'='*60}")
    print(f"URL: {url}")
    print(f"{'='*60}")
    
    try:
        print("POST isteği gönderiliyor...")
        response = requests.post(
            url,
            json=payload,
            timeout=60,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type')}")
        
        # Yanıtı göster
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"✅ Yanıt: {json.dumps(data, indent=2)}")
                if data.get('success') or data.get('message'):
                    print("\n✅ BAŞARILI! script.js yüklendi.")
                    break
            except:
                print(f"⚠️  Status 200 ama JSON değil. Yanıt ilk 300 char:\n{response.text[:300]}")
        else:
            print(f"Yanıt ilk 300 char:\n{response.text[:300]}")
            
    except requests.exceptions.Timeout:
        print(f"⏱️  TIMEOUT - Sunucu çok yavaş veya erişilemiyor")
    except Exception as e:
        print(f"❌ Hata: {str(e)[:200]}")

print("\n" + "="*60)
print("Upload tamamlandı.")
