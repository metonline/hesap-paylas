# Railway Deployment Guide

## Adımlar:

### 1. Railway Hesabı Oluştur
https://railway.app → GitHub ile login yap

### 2. Yeni Project Oluştur
- "New Project" tıkla
- "Deploy from GitHub repo" seç
- metonline/hesap-paylas repo'sunu bul ve seç

### 3. Konfigürasyon (Otomatik Yapılır)
Railway otomatik olarak:
- Procfile okuyor → `web: gunicorn wsgi:app`
- requirements.txt yüklenmiş paketleri install ediyor
- PostgreSQL database dahil geliyor (free tier)

### 4. Deploy
- "Deploy" tıkla
- 2-3 dakika bekle
- Otomatik URL oluşturulacak: `https://xxxxx.up.railway.app`

### 5. Oturum Aç
- Service seç
- URL'yi kopyala
- script.js'de güncelle:
```javascript
return 'https://[RAILWAY-URL]/api';
```

## Avantajları:
✓ Otomatik PostgreSQL dahil
✓ Çok hızlı deploy (2 dakika)
✓ Gratis tier'da yeterli
✓ Heroku'dan daha basit

---

**Railway'e geçmek ister misin? Yoksa Render'daki sorunu çözeceğiz?**
