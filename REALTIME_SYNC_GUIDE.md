## 🔄 Real-Time Database Sync - Kullanım Kılavuzu

### Nedir?
Lokal SQLite'deki **her değişiklik** otomatik olarak Render PostgreSQL'e aktarılır.

---

## 🚀 Başlama

### Terminal 1: Backend Server
```bash
python dev_server.py
# veya
python backend/app.py
```

### Terminal 2: Real-time Sync Watcher
```bash
python watch_and_sync.py
```

**Output örneği:**
```
======================================================================
🔄 REAL-TIME DATABASE SYNC WATCHER
======================================================================
📦 Local: C:\Users\metin\Desktop\BILL\backend\instance\hesap_paylas.db
🌐 Render: postgresql://***@dpg-d5ibasp5...
✅ Watching for changes... (Ctrl+C to stop)
======================================================================

✅ Synced 1 users
✅ Synced 0 groups
```

---

## 📊 Nasıl Çalışır?

```
Local Development
    ↓
1. Frontend üzerinden signup/login yap
    ↓
2. Backend SQLite'ye kaydeder
    ↓
3. watch_and_sync.py bunu görür
    ↓
4. Otomatik Render PostgreSQL'e gönderir
    ↓
5. Her iki DB senkronize olur
```

---

## ✅ Kontrol Etme

### Terminal 3: Status Check
```bash
# Real-time durumu görmek için
python sync_databases.py status
```

Çıktı:
```
📦 Local SQLite:
   Users: 1, Groups: 2

🌐 Render PostgreSQL:
   Users: 1, Groups: 2
   Connection: ✓ Active
```

---

## ⚙️ Özellikler

- ✅ 10 saniye arayla kontrol
- ✅ Son 30 saniyede yapılan değişiklikleri senkronize
- ✅ Duplicate'leri otomatik atla
- ✅ Non-blocking (arka planda çalışır)
- ✅ Hata toleransı (hata olsa da devam eder)

---

## 📋 Komutlar

| Komut | İşlev |
|-------|-------|
| `python dev_server.py` | Backend + Frontend başlat |
| `python watch_and_sync.py` | Real-time sync watcher başlat |
| `python sync_databases.py status` | Durumu kontrol et |
| `python sync_databases.py local2render` | Manual full sync |

---

## 🎯 İş Akışı (Recommendation)

```bash
# Terminal 1: Backend + Frontend
python dev_server.py

# Terminal 2: Real-time Sync (başka cmd açıp)
python watch_and_sync.py

# Terminal 3: Monitor (isteğe bağlı)
python sync_databases.py status

# Şimdi lokal'da yaptığın her değişiklik
# otomatik Render'a gidiyor!
```

---

## ⚠️ Notlar

1. **watch_and_sync.py mutlaka çalışmalı** - sync için
2. **Dev server da çalışmalı** - veri girmek için
3. **İki terminal açık tutman gerekir**
4. **Ctrl+C** - syncer'ı durdurmak için
5. **Render DB'sine bağlantı olmalı**

---

## 🚀 Deploy Öncesi

Deploy etmeden önce:
```bash
# Tüm verileri senkronize et
python sync_databases.py status

# Render'da görüntüle
# https://dashboard.render.com → PostgreSQL → Data Browser
```

---

**Hazır?**
```bash
# Terminal 1
python dev_server.py

# Terminal 2
python watch_and_sync.py
```

Bu kadar! Artık real-time sync! 🎉
