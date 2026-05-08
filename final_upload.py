import requests
import json

# Dosya yolunu kontrol et
LOCAL_FILE = r'c:\Users\metin\Desktop\BILL\script.js'

# Dosya içeriğini oku
print("Dosya okunuyor...")
with open(LOCAL_FILE, 'r', encoding='utf-8') as f:
    content = f.read()

print(f"Dosya boyutu: {len(content)} bytes")

# İçeriğin doğru olup olmadığını kontrol et
if 'api.request(' in content:
    print("✅ Dosya DOĞRU: api.request() kullanıyor")
else:
    print("❌ UYARI: api.request() kullanmıyor!")
    
if "Authorization" in content and "loadActiveGroups" in content:
    # Kontrol et - loadActiveGroups'ta Authorization var mı?
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if 'loadActiveGroups' in line and i > 0:
            # Sonraki 50 satırı kontrol et
            snippet = '\n'.join(lines[i:min(i+50, len(lines))])
            if 'Authorization' in snippet and 'fetch' in snippet:
                print("❌ UYARI: loadActiveGroups hala Authorization header kullanıyor!")
                break
    else:
        print("✅ loadActiveGroups tamam")

# Upload et
print("\nUploading via PHP handler...")
response = requests.post(
    'http://hesappaylas.com/upload-handler.php',
    json={'content': content},
    timeout=60,
    headers={'Content-Type': 'application/json'}
)

print(f"Status: {response.status_code}")
print(f"Response:")
print(response.text[:500])

if response.status_code == 200:
    try:
        data = response.json()
        print(f"\n✅ Başarılı! {data.get('bytes', 'N/A')} bytes yazıldı")
    except:
        pass
