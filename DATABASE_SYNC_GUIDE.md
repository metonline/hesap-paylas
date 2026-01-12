# Veritabanı Senkronizasyon Rehberi
# Database Synchronization Guide

## 🎯 Amaç
Lokal SQLite ve Render PostgreSQL veritabanlarını senkronize ederek, veri kaybı olmadan üretim ortamında çalışmak.

**Purpose**: Synchronize local SQLite and Render PostgreSQL databases to work in production without data loss.

---

## 📋 Hızlı Başlangıç

### 1️⃣ Veritabanı Durumunu Kontrol Et
```bash
python sync_databases.py status
```
Çıktı:
```
🔍 DATABASE STATUS
📦 Local SQLite:
   Path: backend/instance/hesap_paylas.db
   Exists: ✓ Evet
   Users: 5
   Groups: 3

🌐 Render PostgreSQL:
   Status: ✓ Configured
   URL: postgresql://***
   Users: 2
   Groups: 1
   Connection: ✓ Active
```

### 2️⃣ Lokal'dan Render'a Veri Taşı
Lokal'daki tüm verileri (kullanıcılar, gruplar, siparişler) Render'a yükle:

```bash
python sync_databases.py local2render
```

### 3️⃣ Render'dan Lokal'a Yedekle
Render'daki verileri güvenlik için lokal'a indir:

```bash
python sync_databases.py render2local
```

---

## 🔧 Kurulum

### Adım 1: Render PostgreSQL Bağlantısını Al
1. https://dashboard.render.com adresine git
2. PostgreSQL database'ini seç (örn: `hesap-paylas-db`)
3. **Info** sekmesine tıkla
4. **External Database URL** kopyala (looks like: `postgresql://user:pass@host:5432/dbname`)

### Adım 2: .env'ye Ekle
```env
# .env dosyasında
RENDER_DATABASE_URL=postgresql://user:password@host:5432/dbname
```

**UYARI**: Bu URL'i hiçbir yerde paylaşma! `.gitignore`'da `.env` zaten var.

### Adım 3: Bağlantıyı Test Et
```bash
python sync_databases.py status
```
PostgreSQL bağlantısı aktif olmalı.

---

## 🔄 Senkronizasyon Stratejileri

### Strateji 1: Lokal Geliştirme + Render Üretim
**Senaryo**: Lokal'da SQLite ile geliş, Render'a hazır olduğunda taşı.

```bash
# Geliştirme sırasında
python dev_server.py  # SQLite kullanır

# Hazırlanıp push yapmadan önce
python sync_databases.py local2render  # Lokal veriyi Render'a taşı
git push  # GitHub'a push et
```

### Strateji 2: Her Zaman Render Kullan
**Senaryo**: Lokal development'ta da Render PostgreSQL kullan.

`.env` dosyasında:
```env
# DATABASE_URL=sqlite:///hesap_paylas.db  # Yorum yap
DATABASE_URL=postgresql://user:password@host:5432/dbname  # Aç
```

Sonra:
```bash
python dev_server.py  # Aynı Render DB'yi kullanır
```

### Strateji 3: Hibrit (Tavsiye Edilen)
- **Lokal geliştirme**: SQLite (hızlı, dependency yok)
- **Test öncesi**: Render'a sync et
- **Üretim**: Render PostgreSQL (dayanıklı, scalable)

```bash
# Geliştir
python dev_server.py

# Hazırlan
python sync_databases.py local2render

# Deploy
git push origin main
# Render otomatik deploy eder
```

---

## 📊 Veritabanı Yapısı

### SQLite (Lokal)
- **Konum**: `backend/instance/hesap_paylas.db`
- **Avantaj**: Dosya tabanlı, dependency yok
- **Dezavantaj**: Concurrency sorunları, scale etmez

### PostgreSQL (Render)
- **Konum**: Render cloud
- **Avantaj**: Prod-ready, scalable, backup'ı otomatik
- **Dezavantaj**: Lokal'da kurulumu gerekir (opsiyonel)

### Tablolar (Her iki database'de de same schema)
```
users
├─ id, first_name, last_name, email, phone
├─ password_hash, avatar_url, bonus_points
└─ reset_token, is_active, is_deleted, account_type

groups
├─ id, group_name, group_code, group_description
├─ created_by (FK: users.id)
└─ members (many-to-many)

orders
├─ id, group_id (FK), creator_id (FK)
├─ restaurant_name, total_amount
└─ created_at, updated_at

order_items
├─ id, order_id (FK), item_name, price, quantity
└─ notes

member_bills
├─ id, order_id (FK), member_id (FK)
└─ amount, paid_status
```

---

## ⚠️ Önemli Notlar

### Veri Çatışmaları
Aynı email'e sahip kullanıcı varsa taşıma sırasında atlanır:

```python
# sync_databases.py'de
existing = db.session.query(User).filter_by(email=user.email).first()
if not existing:  # Sadece yenileri taşı
    # Taşı...
```

Eğer güncelleme istiyorsan:
```bash
# Render'daki eski verileri temizle (DİKKAT!)
# sync_databases.py'deki commented satırları aç
render_db.session.query(User).delete()
render_db.session.commit()

# Sonra sync et
python sync_databases.py local2render
```

### Üretim Güvenliği
1. **Backup al**: Render dashboard'da `Backups` sekmesine tıkla
2. **Test ortamında dene**: Staging database'de test et
3. **Sinkronize et**: Production'a push yap

```bash
# Güvenli senkronizasyon
python sync_databases.py status        # Kontrol et
python sync_databases.py render2local  # Yedekle
python sync_databases.py local2render  # Taşı
```

---

## 🚀 Render Deployment

### .env Ayarlaması
Render dashboard'da **Environment** sekmesinde:

```env
DATABASE_URL=postgresql://...      # Render tarafından sağlanır
FLASK_ENV=production
SECRET_KEY=your-secret-key
JWT_SECRET=your-jwt-secret
GOOGLE_CLIENT_ID=your-google-id
STRIPE_SECRET_KEY=your-stripe-key
```

### Deploy Edilen Backend Hangi DB Kullanır?
```
Render ortamında:
├─ DATABASE_URL env variable mevcekse → PostgreSQL kullan
└─ Yoksa → SQLite (/app/hesap_paylas.db) - ⚠️ Ephemeral!
```

**Önemli**: SQLite Render'da ephemeral storage'da olduğu için,
pod yeniden başlarsa veri silinir. **PostgreSQL kullan!**

---

## 🔐 Güvenlik İpuçları

### .env Dosyasını Gizle
```bash
# Zaten .gitignore'da var
git check-ignore .env  # Kontrol et
```

### DATABASE_URL'i Loglardan Uzak Tut
```python
# Gerek yoksa logla
print(database_url)  # ✗ Yapma
print("Database connected ✓")  # ✓ Yap
```

### Render Database Erişimi
- **Public access**: Render Dashboard → Database → Manage → Network → Allow connections
- Lokal'dan bağlanmadan önce enable et

---

## 🐛 Sorun Giderme

### "DATABASE_URL not found"
```bash
# .env'i kontrol et
cat .env | grep DATABASE_URL

# DATABASE_URL satırını uncomment et ve doldur
RENDER_DATABASE_URL=postgresql://...
```

### "Connection refused"
```bash
# 1. PostgreSQL running mi kontrol et
# 2. URL doğru mu
# 3. Network erişimi enable et (Render dashboard)
# 4. Firewalls kontrol et
```

### "Foreign key constraint error"
```bash
# Users önce, Groups sonra taşınmalı
# sync_databases.py zaten bunu yapıyor ama

# Manuel olarak:
python -c "
from backend.app import db, User, Group
# Önce User.query.all() sync et
# Sonra Group'ları sync et (created_by foreign key'i için)
"
```

### "Connection timeout"
```bash
# Network bağlantısı yetersiz olabilir
# Render free tier'ıda slow
# Daha büyük parçalarla taşı veya manual SQL kullan
```

---

## 📈 Performance İpuçları

### Büyük Veri Senkronizasyonu
```python
# Batch taşıma (sync_databases.py'e ekle)
batch_size = 100
for i in range(0, len(users), batch_size):
    batch = users[i:i+batch_size]
    for user in batch:
        db.session.add(user)
    db.session.commit()
```

### Connection Pooling
SQLAlchemy otomatik olarak yapıyor, ama:
```python
# app.py'de
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_size': 10,
    'pool_recycle': 3600,
    'pool_pre_ping': True,
}
```

---

## ✅ Checklist: Üretim'e Hazır Olma

- [ ] Render PostgreSQL bağlantısı ayarlandı
- [ ] RENDER_DATABASE_URL .env'de var
- [ ] Lokal veriler test edildi
- [ ] `python sync_databases.py status` çalışıyor
- [ ] Lokal → Render senkronizasyonu test edildi
- [ ] Render backup alındı
- [ ] API test edildi (POST, GET, DELETE)
- [ ] GitHub Pages frontend API URL'si doğru
- [ ] CORS ayarları kontrol edildi
- [ ] Stripe/OAuth keys ayarlandı

---

## 📞 Kısayollar

```bash
# Status kontrol
python sync_databases.py status

# Hızlı sync
python sync_databases.py local2render && python sync_databases.py render2local

# Render'dan oku
python -c "
import os
from dotenv import load_dotenv
load_dotenv()
url = os.getenv('RENDER_DATABASE_URL')
print(f'Render DB: {url[:30]}...' if url else 'Not configured')
"
```

---

## 📚 İlgili Dosyalar
- [backend/app.py](backend/app.py) - Flask + SQLAlchemy app
- [.env](.env) - Environment variables
- [LOCAL_DEVELOPMENT.md](LOCAL_DEVELOPMENT.md) - Lokal geliştirme
- [RENDER_DEPLOYMENT.md](RENDER_DEPLOYMENT.md) - Render deployment

---

**Hazır mısınız? Başlayın:** `python sync_databases.py status`
