# Render.com Deployment Guide

## Adımlar:

### 1. Render.com Hesabı Oluştur
- https://render.com adresine git
- GitHub ile oturum aç
- Repository'e erişim izni ver

### 2. Yeni Web Service Oluştur
- Dashboard'a git → "New +" → "Web Service"
- "Connect a repository" → `metonline/hesap-paylas` seç
- "Create Web Service" tıkla

### 3. Ayarları Doldur
**Name:** `hesap-paylas-api` (veya istediğin isim)

**Environment:** `Python 3`

**Build Command:**
```
pip install -r requirements.txt
```

**Start Command:**
```
gunicorn backend.app:app
```

**Instance Type:** Free (ilk test için)

### 4. Environment Variables Ekle
Render dashboard'da "Environment" sekmesinde ekle:

- `DATABASE_URL` = `sqlite:///hesap_paylas.db` (SQLite geçici için)
  - *Not: Production'da PostgreSQL kullan - Render free tier'da dahil gelir*
- `JWT_SECRET` = `your-secret-key-here` (güvenli bir key seç)
- `SECRET_KEY` = `your-secret-key-here`
- `FLASK_ENV` = `production`

### 5. Deploy Et
"Deploy" tıkla ve bekle (2-5 dakika)

### 6. URL'yi Al
Deployment başarılı olduktan sonra, Render dashboard'da:
- Servis URL'si: `https://hesap-paylas-api.onrender.com`
- Bu URL'yi kopyala

### 7. Frontend'de API URL'yi Güncelle
`script.js` satır 77'de:
```javascript
return 'https://hesap-paylas-api.onrender.com/api';  // Senin Render URL'ine değiştir
```

Veya otomatik olacak - zaten code'a ekleme yaptık!

### 8. GitHub Pages'i Refresh Et
- `index.html` dosyasında minimal değişiklik yap
- Git push et
- GitHub Actions tarafından otomatik deploy olacak
- veya https://metonline.github.io'yu Ctrl+Shift+R ile hard refresh et

## Sorun Giderme

**"Failed to fetch" hatası alıyorsan:**
1. Render'da Deploy başarılı mı kontrolet
2. API URL'nin doğru olduğunu kontrol et
3. Render'da CORS settings'i kontrol et (zaten eklendi)
4. Browser console'da exact error mesajını oku

**Database errors:**
- SQLite SQLite local development için kullanılıyor
- Production'da Postgres tercih et (Render'da free tier'da dahil)
- DATABASE_URL çevresel değişkeni ayarla

---

**Deployment tamamlandıktan sonra, app login/signup yapmaya hazır olacak!**
