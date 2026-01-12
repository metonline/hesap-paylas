# 🚀 Hızlı Başlangıç - Database Senkronizasyonu

## ⚡ 5 Dakikada Kurulum

### 1️⃣ Render PostgreSQL URL'ini Al
```
https://dashboard.render.com
→ PostgreSQL → Info → External Database URL kopyala
```

### 2️⃣ .env'ye Ekle
```bash
# .env dosyasında
RENDER_DATABASE_URL=postgresql://user:password@host:5432/dbname
```

### 3️⃣ Durumu Kontrol Et
```bash
python sync_databases.py status
```

### 4️⃣ Lokal'dan Render'a Taşı
```bash
python sync_databases.py local2render
```

### 5️⃣ Deploy Et
```bash
git add .
git commit -m "Database sync"
git push origin main
```

---

## 📝 Komutlar

| Komut | Açıklama |
|-------|----------|
| `python sync_databases.py status` | Lokal ve Render DB durumunu göster |
| `python sync_databases.py local2render` | Lokal veriyi Render'a taşı |
| `python sync_databases.py render2local` | Render veriyi lokal'a yedekle |

---

## ✅ Kontrol Listesi

```bash
# Step 1: Render PostgreSQL oluştur (Dashboard)
✓ https://dashboard.render.com → New → PostgreSQL

# Step 2: DATABASE_URL'i al ve .env'ye ekle
✓ RENDER_DATABASE_URL=postgresql://...

# Step 3: Lokal development
✓ python dev_server.py
✓ Veri gir (users, groups, orders)

# Step 4: Senkronize et
✓ python sync_databases.py status
✓ python sync_databases.py local2render

# Step 5: Deploy
✓ git push origin main
✓ Render Dashboard → Deploy başarılı?
✓ curl https://hesap-paylas-api.onrender.com/api/health

# Step 6: Frontend
✓ GitHub Pages otomatik deploy
✓ https://metonline.github.io test et

# Bitti! 🎉
```

---

## 🔗 Kaynaklar

- 📖 [Detaylı Rehber](DATABASE_SYNC_GUIDE.md)
- 🚀 [Render Deployment](RENDER_DEPLOYMENT.md)
- 💻 [Lokal Geliştirme](LOCAL_DEVELOPMENT.md)
- 🔧 [Sync Script](sync_databases.py)

---

## 💡 İpuçları

### Hızlı Test
```bash
# Status
python sync_databases.py status

# Sync + Push
python sync_databases.py local2render && git push
```

### Problemler
```bash
# DATABASE_URL kontrol et
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print(os.getenv('RENDER_DATABASE_URL'))"

# Postgres bağlantısını test et
psql postgresql://user:pass@host:5432/dbname -c "SELECT 1"
```

---

**Ready? Run:**
```bash
python sync_databases.py status
```
