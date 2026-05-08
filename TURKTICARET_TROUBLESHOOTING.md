# Turkticaret MySQL Deployment - Troubleshooting Rehberi

Bu rehber Turkticaret cPanel'de MySQL ile deployment sırasında karşılaşılabilecek sorunları ve çözümleri içerir.

---

## 🔴 Sorun: "Error 500 Internal Server Error"

### Sebep A: Python Module Import Hatası

**Belirti:**
- Browser'da 500 error
- cPanel logs'unda: `ImportError`, `ModuleNotFoundError`

**Çözüm:**
```bash
# SSH'da
cd ~/public_html
source ~/hesap_paylas_env/bin/activate

# requirements'leri yeniden yükle
pip install --upgrade -r requirements.txt

# Tüm paketleri kontrol et
pip list | grep -i flask
pip list | grep -i sqlalchemy
pip list | grep -i pymysql

# App'ı manuel olarak test et
python3 -c "from backend.app import app; print('Flask app imported successfully!')"
```

### Sebep B: Database Connection Hatası

**Belirti:**
- `sqlalchemy.exc.ArgumentError: Could not parse rfc1738 URL`
- `pymysql.err.OperationalError: (2003, "Can't connect to MySQL server")`

**Çözüm:**
```bash
# 1. .env dosyasını kontrol et
cat .env | head -20

# DATABASE_URL formatı kontrol et:
# ✅ DOĞRU: mysql+pymysql://user:pass@localhost/db
# ✗ YANLIŞ: mysql://user:pass@localhost/db (pymysql eksik)

# 2. MySQL bağlantısını test et
mysql -h localhost -u dbuser -p -D dbname -e "SELECT 1;"

# 3. Kullanıcı ve şifre kontrol et
# cPanel → MySQL Databases → User kontrolü yap

# 4. Veritabanı var mı kontrol et
mysql -h localhost -u dbuser -p -e "SHOW DATABASES;"
```

### Sebep C: SECRET_KEY Ayarlanmamış

**Belirti:**
- Logging'de: `ValueError: You must provide a SECRET_KEY`

**Çözüm:**
```bash
# .env'yi düzenle
nano .env

# SECRET_KEY oluştur
python3 -c "import secrets; print('SECRET_KEY=' + secrets.token_hex(32))"

# Çıkışı .env'ye ekle
# SECRET_KEY=e4f3a7c8d2b1f9e3a6c8d2b1f9e3a6c8d2b1f9e3a6c8d2b1f9e3a6c8

# Dosyayı kaydet
# Passenger app'ı restart et
touch ~/public_html/tmp/restart.txt
```

### Sebep D: Bağımlı Dosya Bulunamıyor

**Belirti:**
- logs'unda: `FileNotFoundError`, `No such file or directory`

**Çözüm:**
```bash
# index.html, styles.css vb. dosyalar var mı kontrol et
ls -la ~/public_html/index.html
ls -la ~/public_html/styles.css
ls -la ~/public_html/script.js

# Dosya izinlerini kontrol et
chmod 644 ~/public_html/*.html
chmod 644 ~/public_html/*.css
chmod 644 ~/public_html/*.js

# Dizin izinlerini kontrol et
chmod 755 ~/public_html
chmod 755 ~/public_html/static 2>/dev/null

# Dosyalar git'e erişilemiyor mu kontrol et
git status ~/public_html
```

---

## 🔴 Sorun: "Can't connect to MySQL server on 'localhost'"

### Sebep A: MySQL Sunucu Çalışmıyor

**Çözüm:**
```bash
# cPanel'de MySQL status'unu kontrol et
# cPanel → Home → MySQL Databases
# Green "Running" yazısı olmalı

# SSH'da
mysql -h localhost -u root -p  # cPanel'de root şifresi sorulmaz
# Sorun varsa contact hosting support

# .env'de host doğru mu kontrol et
grep DATABASE_URL .env
# localhost veya 127.0.0.1 olmalı
```

### Sebep B: Wrong Username/Password

**Çözüm:**
```bash
# cPanel'de MySQL user'ının şifresini resetle
# cPanel → MySQL Databases → "User" bölümü → Change Password

# Ardından .env'yi güncelle
nano .env
# DATABASE_URL satırında yeni şifre ekle

# Bağlantıyı test et
mysql -h localhost -u dbuser -p dbname -e "SELECT 1;"
```

### Sebep C: User Database İzni Yok

**Çözüm:**
```bash
# cPanel'de kontrol et:
# MySQL Databases → "User" → seçilen user'ın
# "Database" kolonu'nda ilgili database var mı?

# Eğer yoksa:
# 1. "Add User to Database" tıkla
# 2. User seç
# 3. Database seç
# 4. "ALL PRIVILEGES" seç
# 5. Add tıkla
```

---

## 🔴 Sorun: "Static files not loading" (CSS/JS yüklenmediği)

### Sebep: .htaccess kuralları hatalı

**Belirti:**
- HTML yükleniyor ama CSS/JS boş
- Browser console'da 404 hatalar

**Çözüm:**
```bash
# .htaccess dosyasını kontrol et
cat .htaccess

# Eğer Static dosyaları hizmet eden kurallar eksikse:
nano .htaccess

# Şu blokları .htaccess'e ekle:
```

**.htaccess içinde:**
```apache
# Static assets doğrudan sunulmalı
<FilesMatch "\.(css|js|jpg|png|gif|ico|woff|woff2|ttf|svg)$">
    Order allow,deny
    Allow from all
</FilesMatch>

# Kompress etme
<IfModule mod_deflate.c>
    AddOutputFilterByType DEFLATE text/css application/javascript
</IfModule>

# Caching
<IfModule mod_expires.c>
    ExpiresActive On
    ExpiresByType text/css "access plus 1 year"
    ExpiresByType application/javascript "access plus 1 year"
</IfModule>
```

---

## 🔴 Sorun: "Permission Denied" hataları

### Sebep: Dosya izinleri yanlış

**Çözüm:**
```bash
# Tüm dosya izinlerini düzelt
cd ~/public_html

# Dizinler 755 (rwxr-xr-x) olmalı
find . -type d -exec chmod 755 {} \;

# Dosyalar 644 (rw-r--r--) olmalı
find . -type f -exec chmod 644 {} \;

# Executable dosyalara +x ver (Python scriptleri)
chmod 755 *.py
chmod 755 init_mysql_db.py

# Passenger'ın process'ini restart et
touch ~/public_html/tmp/restart.txt

# Iznleri kontrol et
ls -la ~/public_html | head
```

---

## 🔴 Sorun: "ModuleNotFoundError: No module named 'flask'"

### Sebep: Dependencies yüklü değil veya venv aktif değil

**Çözüm:**
```bash
# 1. Virtual environment'ı kontrol et
ls -la ~/hesap_paylas_env/

# 2. Eğer yoksa oluştur
python3 -m venv ~/hesap_paylas_env

# 3. Activate et
source ~/hesap_paylas_env/bin/activate

# 4. Requirements'i yükle
cd ~/public_html
pip install -r requirements.txt

# 5. Python path'ini kontrol et
python3 -c "import sys; print('\n'.join(sys.path))"
# ~/hesap_paylas_env/lib/python3.x/site-packages olmalı

# 6. Flask kuruldu mu kontrol et
python3 -c "import flask; print(flask.__version__)"
```

---

## 🔴 Sorun: "Broken pipe" veya "Connection reset"

### Sebep: Passenger timeout

**Çözüm:**
```bash
# 1. Passenger'ı restart et
touch ~/public_html/tmp/restart.txt

# 2. Log'ları kontrol et
tail -50 ~/logs/error_log

# 3. Uzun işlemler varsa timeout'u arttır
# .htaccess'e ekle:
SetEnvIf Request_URI "^/api/long-process" long_request=1
<If "%{ENV:long_request} == 1">
    SetEnvIf REQUEST_METHOD . long_timeout=1
</If>

# 4. Backend'de timeout'u arttır (app.py'de)
# @app.route('/api/...')
# def long_task():
#     # timeout > 300 saniye işlemler
```

---

## 🔴 Sorun: "Email/SMTP hataları"

### Sebep A: SMTP Konfigürasyonu Yanlış

**Çözüm:**
```bash
# .env'de kontrol et
grep -i smtp .env
grep -i sender .env

# Doğru format:
# SMTP_SERVER=smtp.gmail.com
# SMTP_PORT=587
# SENDER_EMAIL=your-email@gmail.com
# SENDER_PASSWORD=your-app-password

# Gmail kullanıyorsan:
# 1. https://myaccount.google.com/apppasswords git
# 2. App Password oluştur (2FA gerekli)
# 3. 16 karakterlik şifreyi .env'ye koy
```

### Sebep B: Firewall SMTP Portunu Blokluyor

**Çözüm:**
```bash
# cPanel'de kontrol et:
# cPanel → Home → Hosting Settings → Outgoing Email (SMTP)
# Enable seçili olmalı

# Eğer sorun devam ederse:
# Contact hosting support - SMTP portları açılması için
```

---

## 🔴 Sorun: "Database tables not created"

### Sebep: init_mysql_db.py çalıştırılmadı

**Çözüm:**
```bash
# SSH'da
cd ~/public_html
source ~/hesap_paylas_env/bin/activate

# Database initialization script'i çalıştır
python3 init_mysql_db.py

# Çıktıda 4️⃣ bölümü başarılı olmalı
# Tabloların oluşturulup oluşturulmadığını kontrol et
mysql -h localhost -u dbuser -p dbname -e "SHOW TABLES;"
```

---

## 🔴 Sorun: "Changes not reflecting" (Kod değişimi site'de görünmüyor)

### Sebep A: Browser Cache

**Çözüm:**
```bash
# Hard refresh yap
# Ctrl+Shift+Delete (Windows/Linux)
# Cmd+Shift+Delete (Mac)

# veya
# F12 → Settings → Disable cache yap
```

### Sebep B: Passenger Cache

**Çözüm:**
```bash
# Passenger'ı restart et
cd ~/public_html
touch tmp/restart.txt

# Veya cPanel'den:
# Setup Python App → [App adı] → Restart
```

### Sebep C: Git'ten pull edilmedi

**Çözüm:**
```bash
# En son kodu çek
cd ~/public_html
git pull origin main

# Dosyaları kontrol et
ls -la | grep -E 'app.py|wsgi.py|requirements'

# Eğer yeni requirements varsa
source ~/hesap_paylas_env/bin/activate
pip install -r requirements.txt
```

---

## 🟡 Sorun: Yavaş Veritabanı İşlemleri

### Sebep: Database query optimizasyonu

**Çözüm:**
```bash
# Database istatistikleri kontrol et
mysql -h localhost -u dbuser -p dbname -e \
"SELECT TABLE_NAME, TABLE_ROWS, DATA_LENGTH FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA='dbname';"

# Eğer veri çok büyükse:
# 1. Eski veriyi archive'le (tarihi veriler)
# 2. Indexleri kontrol et
# 3. Queries optimize et

# Slow query log'unu aktifleştir
mysql -h localhost -u dbuser -p dbname -e \
"SET GLOBAL slow_query_log = 'ON';"
"SET GLOBAL long_query_time = 2;"
```

---

## 📊 Diagnostik Checklist

Sorun çözerken sırasıyla kontrol et:

1. **Browser Developer Tools**
   - [ ] F12 → Console tab'ında hatalar var mı?
   - [ ] Network tab'ında 404/500 status'lar var mı?
   - [ ] Request headers'da content-type doğru mu?

2. **SSH Terminal**
   ```bash
   tail -100 ~/logs/error_log
   tail -100 ~/logs/access_log
   ```

3. **.env File**
   ```bash
   cat .env | grep -E 'DATABASE_URL|FLASK_ENV|SECRET_KEY'
   ```

4. **Database Connection**
   ```bash
   mysql -h localhost -u dbuser -p dbname -e "SELECT 1;"
   ```

5. **Python Environment**
   ```bash
   source ~/hesap_paylas_env/bin/activate
   python3 -c "from backend.app import app; print('OK')"
   ```

6. **File Permissions**
   ```bash
   ls -la ~/public_html | head
   ```

7. **Passenger Status**
   - [ ] cPanel → Setup Python App → Status "Running"?

---

## 📞 Destek İstediğinde Hazır Olması Gerekenler

Hosting support ile iletişim kurarken:

```markdown
**Hosting Provider:** Turkticaret
**Panel:** cPanel
**Issue Description:** [Detailed explanation]

**Error Messages:**
[Full error text from browser console and cPanel logs]

**Configuration:**
- Flask Version: [pip list | grep Flask]
- Python Version: [python3 --version]
- Database: [mysql -h localhost -u user -p db -e "SELECT VERSION();"]
- Passenger Version: [From cPanel Setup Python App]

**Attempted Solutions:**
- [ ] Cleared browser cache
- [ ] Restarted Passenger app
- [ ] Checked .env file
- [ ] Verified database connection
- [ ] Checked file permissions

**Logs:**
[tail -50 ~/logs/error_log]
[tail -50 ~/logs/access_log]
```

---

**Son Güncelleme:** 2024  
**Hosting:** Turkticaret (cPanel)  
**Database:** MySQL/MariaDB  
**Web Server:** Apache + Passenger
