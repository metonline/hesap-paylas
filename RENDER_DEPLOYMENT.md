# Render.com Deployment Guide - Single Database Setup
# Tek Veritabanı ile Render Deployment

## 📌 ÖNEMLİ: Veri Senkronizasyonu
Lokal ve Render veritabanlarını senkronize etmek için:
```bash
python sync_databases.py status      # Durum kontrol et
python sync_databases.py local2render # Lokal → Render taşı
python sync_databases.py render2local # Render → Lokal (yedek)
```

Detaylı rehber: [DATABASE_SYNC_GUIDE.md](DATABASE_SYNC_GUIDE.md)

---

## Adımlar:

### 1. Render.com Hesabı Oluştur
- https://render.com adresine git
- GitHub ile oturum aç
- Repository'e erişim izni ver

### 2. PostgreSQL Database Oluştur
- Dashboard'a git → "New +" → "PostgreSQL"
- **Name:** `hesap-paylas-db` (veya istediğin isim)
- **Instance Type:** Free
- **Region:** Senin bölgen (örn: Frankfurt)
- "Create Database" tıkla
- Taslak olarak **External Database URL** kopyala (adım 4'te kullanacaksın)

### 3. Web Service Oluştur
- Dashboard'a git → "New +" → "Web Service"
- "Connect a repository" → `metonline/hesap-paylas` seç
- "Create Web Service" tıkla

### 4. Web Service Ayarlarını Doldur

**Name:** `hesap-paylas-api` (veya istediğin isim)

**Environment:** `Python 3`

**Build Command:**
```bash
pip install -r requirements.txt
```

**Start Command:**
```bash
gunicorn backend.app:app
```

**Instance Type:** Free (ilk test için)

### 5. Environment Variables Ekle
Render dashboard'da "Environment" sekmesinde ekle:

| Variable | Değer | Açıklama |
|----------|-------|----------|
| `DATABASE_URL` | `postgresql://...` | PostgreSQL bağlantı string'i (Adım 2'den kopyala) |
| `RENDER_DATABASE_URL` | `postgresql://...` | Aynısı (backup için) |
| `JWT_SECRET` | `hesap-paylas-jwt-secret-2025` | Secret key (güvenli yap!) |
| `SECRET_KEY` | `hesap-paylas-secret-2025` | Flask secret key |
| `FLASK_ENV` | `production` | Production ortamı |
| `GOOGLE_CLIENT_ID` | `your-google-id` | OAuth için |
| `STRIPE_SECRET_KEY` | `sk_live_...` | Stripe API key |

✅ **DATABASE_URL İçin:**
- Render Dashboard → PostgreSQL database
- "Info" sekmesine tıkla
- **External Database URL** kopyala ve yapıştır

### 6. Deploy Et
- "Deploy" tıkla ve bekle (3-5 dakika)
- Deployment logs'u kontrol et
- ✅ "Your service is live" görmeli

### 7. Database İnitialize Et
Deploy başarılı olduktan sonra:

```bash
# Terminal'de (lokal)
python sync_databases.py status  # Bağlantı kontrol et

# Lokal verini (varsa) Render'a taşı
python sync_databases.py local2render

# Veya Render URL'ini test et
curl https://hesap-paylas-api.onrender.com/api/health
```

### 8. Frontend'de API URL'yi Güncelle
`script.js` satır 77'de:
```javascript
return 'https://hesap-paylas-api.onrender.com/api';  // Senin Render URL'ine değiştir
```

Veya otomatik olacak - zaten code'a ekleme yaptık!

### 9. GitHub Pages Frontend Deploy
- `index.html` dosyasında minimal değişiklik yap
- Git push et
- GitHub Pages otomatik deploy edilecek
- veya https://metonline.github.io'yu Ctrl+Shift+R ile hard refresh et

---

## 🔄 Veritabanı Yönetimi

### Her Deploy Sonrasında
```bash
# Lokal değişiklikleri Render'a gönder
python sync_databases.py local2render

# Push et
git add .
git commit -m "Update database"
git push origin main
```

### Render'da Database Yönetimi
Render Dashboard → PostgreSQL → Management:

- **Backups**: Otomatik günlük backup
- **Users**: Database user yönet
- **Extensions**: PostgreSQL extensions ekle
- **Metrics**: CPU, RAM, Disk monitoring

### Veri Yedekleme
```bash
# Render'daki veriyi lokal'a yedekle
python sync_databases.py render2local

# Veya Render dashboard'dan:
PostgreSQL → Backups → Download
```

---

## ⚠️ Sorun Giderme

### "Failed to fetch" hatası alıyorsan:
1. ✅ Render'da Deploy başarılı mı kontrol et
2. ✅ API URL'nin doğru olduğunu kontrol et (script.js)
3. ✅ CORS ayarları (zaten backend'de var)
4. ✅ Browser console'da exact error mesajını oku

### "Database connection error":
1. ✅ DATABASE_URL env variable set mi?
2. ✅ PostgreSQL database running mi?
3. ✅ Connection string doğru mu?
4. ✅ Render free tier quota aşıldı mı?

```bash
# Lokal'dan test et
python -c "
from dotenv import load_dotenv
import os
load_dotenv()
print(os.getenv('DATABASE_URL'))
"
```

### "Connection timeout":
- Render free tier'ı yavaş olabilir
- PostgreSQL hızlıdır ama cold start varsa bekle
- Batch sync kullan (sync_databases.py)

### API Health Check:
```bash
curl https://hesap-paylas-api.onrender.com/api/health

# Çıktı şöyle olmalı:
# {"status":"healthy","timestamp":"2026-01-12T..."}
```

---

## 📊 Tüm Veritabanları Karşılaştırma

| Özellik | SQLite | PostgreSQL |
|---------|--------|-----------|
| **Konum** | Lokal dosya | Render cloud |
| **Concurrent** | Zayıf | Güçlü ✅ |
| **Backup** | Manual | Otomatik ✅ |
| **Scale** | Kısıtlı | Sınırsız ✅ |
| **Persistence** | Ephemeral Render'da | Persistent ✅ |
| **Üretim** | ❌ Kullanma | ✅ Kullan |

### Tavsiye Edilen Setup:
- **Geliştirme**: SQLite lokal
- **Test**: Render PostgreSQL (production)
- **Sync**: `python sync_databases.py local2render`
- **Deploy**: Git push → Render auto-deploys

---

## 🚀 Tam Deployment Prosedürü

```bash
# 1. Lokal geliş (SQLite)
python dev_server.py
# ... test yap ...

# 2. Render'a hazırla
python sync_databases.py status          # Kontrol et
python sync_databases.py local2render    # Taşı

# 3. Deploy
git add .
git commit -m "Ready for production"
git push origin main

# 4. Render Dashboard'da kontrol et
# ✅ Deploy successful

# 5. Frontend deploy
# GitHub Pages otomatik deploy (zaten yapılandırıldı)

# 6. Test
curl https://hesap-paylas-api.onrender.com/api/health
# Visit: https://metonline.github.io
```

---

## ✅ Deployment Checklist

- [ ] PostgreSQL database oluşturdu
- [ ] DATABASE_URL set (Web Service Environment)
- [ ] SECRET_KEY ve JWT_SECRET ayarlandı
- [ ] Deploy başarılı (logs kontrol)
- [ ] Database senkronizasyonu yapıldı
- [ ] API health check çalışıyor (`/api/health`)
- [ ] Frontend API URL güncellendi
- [ ] GitHub Pages deploy başarılı
- [ ] Login/Signup test edildi
- [ ] Backups enabled (Render Dashboard)

---

## 📞 İlgili Dosyalar
- [sync_databases.py](sync_databases.py) - Database sync tool
- [DATABASE_SYNC_GUIDE.md](DATABASE_SYNC_GUIDE.md) - Detaylı rehber
- [backend/app.py](backend/app.py) - Flask app
- [.env](.env) - Environment variables

---

**Başlamaya hazır mısınız?**
1. Render PostgreSQL oluştur
2. DATABASE_URL set et
3. `python sync_databases.py status` çalıştır
4. Deploy et!

```bash
python sync_databases.py status
```

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
