# cPanel + SSH + MySQL Deployment Guide

## Hosting Info
- **Username:** mgb3dcinfo
- **Panel:** cPanel
- **Database:** MySQL
- **SSH:** Aktif
- **Python:** Mevcut

---

## ADIM 1: cPanel'de MySQL Database Oluştur

1. **cPanel'e gir** → Sağ üstte "SQL" sekmesi
2. **"MySQL Databases"** tıkla
3. **Yeni Database Oluştur:**
   - Database Name: `mgb3dcinfo_hesap_paylas`
   - İleri (Next) tıkla

4. **Yeni User Oluştur:**
   - Username: `mgb3dcinfo_user`
   - Password: **GÜVENLI BİR ŞİFRE GİR** (kopyala, lazım olacak)
   - Create User tıkla

5. **User'ı Database'e Bağla:**
   - User seç: `mgb3dcinfo_user`
   - Database seç: `mgb3dcinfo_hesap_paylas`
   - "ALL PRIVILEGES" seç
   - Make Changes tıkla

6. **Not al:**
   - Host: `localhost`
   - Database: `mgb3dcinfo_hesap_paylas`
   - User: `mgb3dcinfo_user`
   - Password: `(giriş yaptığın şifre)`

---

## ADIM 2: SSH'ye Bağlan ve Deploy Et

### Terminal/PowerShell'de:
```bash
ssh mgb3dcinfo@yourserver.com
# Şifreni gir
```

### Klonu ve Setup'ı İndir:
```bash
cd /home/mgb3dcinfo/public_html
git clone https://github.com/metonline/hesap-paylas.git
cd hesap-paylas
```

### Virtual Environment:
```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### .env Dosyasını Oluştur:
```bash
nano .env
```

Şu içeriği yapıştır (Adım 1'deki credentials'ı kullan):
```env
FLASK_ENV=production
SECRET_KEY=super-secret-key-$(date +%s)
JWT_SECRET=super-jwt-secret-$(date +%s)
DATABASE_URL=mysql+pymysql://mgb3dcinfo_user:YOUR_PASSWORD@localhost/mgb3dcinfo_hesap_paylas
```

**NOT:** `YOUR_PASSWORD` yerine Adım 1'deki şifreyi koy!

Kaydet: `Ctrl+X` → `Y` → `Enter`

---

## ADIM 3: cPanel'de Python App Konfigure Et

1. **cPanel'e gir**
2. **"Setup Python App"** ara (veya Software sekmesi → Setup Python App)
3. **"Create Application"** tıkla:
   - **Python version:** 3.9+ (en yeni)
   - **Application root:** `/home/mgb3dcinfo/public_html/hesap-paylas`
   - **Application URL:** `yourdomain.com` (SSL enabled)
   - **Application startup file:** `wsgi.py`
   - **Application entry point:** `app`
   - **Passenger log file:** `/home/mgb3dcinfo/public_html/hesap-paylas/logs/app.log`

4. **Create** tıkla ve bekle (2-3 dakika)

---

## ADIM 4: Database Migrate Et

SSH'de:
```bash
cd /home/mgb3dcinfo/public_html/hesap-paylas
source venv/bin/activate

# Test et
python -c "from backend.app import app, db; \
with app.app_context(): \
    db.create_all(); \
    print('✓ Database tables created')"
```

---

## ADIM 5: Test Et

### API Test:
```bash
# SSH'de
curl https://yourdomain.com/health

# Veya browser'da:
https://yourdomain.com/health
```

Response şöyle olmalı:
```json
{"status": "ok"}
```

### Frontend Test:
```
https://yourdomain.com
```

Login sayfası görmeli ve login yapabilmelisin.

---

## ADIM 6: Cron Job ile Auto-Sync Kur (Opsiyonel)

cPanel → Cron Jobs:

```bash
*/10 * * * * /home/mgb3dcinfo/hesap-paylas-venv/bin/python /home/mgb3dcinfo/public_html/hesap-paylas/watch_and_sync.py >> /home/mgb3dcinfo/logs/sync.log 2>&1
```

Bu her 10 dakikada bir sync çalıştıracak.

---

## ADIM 7: SSL Sertifikası

cPanel'de **AutoSSL** genelde zaten konfigüre olmuştur. Kontrol et:

1. cPanel → SSL/TLS Status
2. Eğer red ise, Auto SSL → Manage tıkla ve regenerate et

---

## Sorun Giderme

### Error Log'ları Kontrol Et:
```bash
# cPanel App Log
tail -f /home/mgb3dcinfo/public_html/hesap-paylas/logs/app.log

# Apache Error Log
tail -f /var/log/apache2/error_log | grep hesap-paylas

# MySQL Connection Test
cd /home/mgb3dcinfo/public_html/hesap-paylas
source venv/bin/activate
python -c "from sqlalchemy import create_engine; \
engine = create_engine('mysql+pymysql://mgb3dcinfo_user:PASSWORD@localhost/mgb3dcinfo_hesap_paylas'); \
print('✓ MySQL connected')"
```

### 503 Service Unavailable?
- cPanel'de Python App'in **status'ü** kontrol et (Graceful Restart)
- App log'unda **error** var mı bak
- .env dosyasında **DATABASE_URL** doğru mu?

### 404 - Frontend Not Loading?
- `/public_html/hesap-paylas/index.html` dosyası var mı?
- cPanel Python App ayarlarında **Static files** handling kontrol et

---

## Setup Özeti

| Adım | İş | Status |
|------|----|----|
| 1 | MySQL DB + User Oluştur | ▫️ |
| 2 | SSH'ye bağlan & Clone | ▫️ |
| 3 | Virtual Env + Pip Paketleri | ▫️ |
| 4 | .env Dosyası | ▫️ |
| 5 | cPanel Python App Setup | ▫️ |
| 6 | Database Migrate | ▫️ |
| 7 | Test (API + Frontend) | ▫️ |

---

## İhtiyaç Duyursan:

1. **SSH Log'ları** - SSH'de şu çalıştır ve çıktı gönder:
   ```bash
   tail -50 /home/mgb3dcinfo/public_html/hesap-paylas/logs/app.log
   ```

2. **Error Details** - Browser'da Ctrl+Shift+K (Console) ve error göster

3. **cPanel Status** - Screenshot'ını gönder

---

**Başarılar! 🚀**
