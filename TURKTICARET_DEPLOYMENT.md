# Turkticaret cPanel'de Deployment Rehberi

**Hosting:** Shared Hosting (cPanel)  
**Veritabanı:** MySQL/MariaDB  
**Domain:** hesappaylas.com  
**Framework:** Flask (Python)

---

## 1. 📋 Ön Koşullar Kontrol Listesi

- [ ] SSH erişimi etkinleştirildi (cPanel → SSH Access)
- [ ] MySQL veritabanı oluşturuldu
- [ ] Domainler cPanel'e eklenmiş
- [ ] Git kurulu (SSH ile repo çekebilmek için)

---

## 2. 🔐 cPanel'de SSH Erişimini Etkinleştir

1. **cPanel Dashboard'a gir** → hesappaylas.com
2. **Security → SSH Access** → "Manage SSH Keys"
3. **Generate a New Key** seçin
4. İlkinin (public key) otomatik yüklenmesine izin ver
5. Private key'i **indirip güvenli bir yere sakla** (birden fazla erişim için)

```bash
# Lokal bilgisayarında, SSH key'in konumu
# Windows PowerShell'de:
# C:\Users\YourUsername\.ssh\id_rsa
```

---

## 3. 🌐 SSH ile Sunucuya Bağlan

```bash
# SSH bağlantı bilgilerini cPanel'den kopyala
ssh username@hesappaylas.com
# veya
ssh -i "path/to/your/key" username@hesappaylas.com
```

Bağlandıktan sonra aşağıdaki komutları çalıştır.

---

## 4. 📁 Proje Dizini Hazırla

```bash
# Public HTML dizinine git (veya www)
cd ~/public_html

# Tüm dosyaları sil ve GitHub'dan clone et
# (NOT: Mevcut dosyalar varsa yedek al)
rm -rf *  # Eğer yeni bir domain ise

# GitHub'dan projeyi indir
git clone https://github.com/metonline/hesap-paylas.git .
# veya SSH ile:
git clone git@github.com:metonline/hesap-paylas.git .

# Dosyaları bir seviye yukarı taşı (opsiyonel)
# Eğer hesap-paylas/ dizini oluşturulduysa
cd hesap-paylas && mv * ../ && cd .. && rmdir hesap-paylas
```

---

## 5. 🐍 Python Virtual Environment Kur

```bash
# Python sürümünü kontrol et
python3 --version  # 3.8+ gerekli

# home directory'de venv oluştur
cd ~
python3 -m venv hesap_paylas_env

# Activate et
source hesap_paylas_env/bin/activate

# pip'i upgrade et
pip install --upgrade pip setuptools wheel
```

---

## 6. 📦 Dependencies Yükle

```bash
# public_html'e dön
cd ~/public_html

# requirements.txt dosyasından bağımlılık yükle
pip install -r requirements.txt

# gunicorn'u ekleyerek WSGI sunucusu kurmuş ol
pip install gunicorn==20.1.0
```

---

## 7. 🗄️ MySQL Veritabanı Konfigürasyonu

### Adım 7.1: cPanel'de MySQL Veritabanı Oluştur

1. cPanel → **MySQL Databases**
2. **Create New Database**
   - Database Name: `hesappaylas_db` (cPanel kendi prefix'ini ekleyecek)
3. **Create MySQL User**
   - Username: `hesappaylas_user`
   - Password: Güçlü bir şifre oluştur ve KAYDEDİ
4. **Add User to Database**
   - Privilege: **ALL PRIVILEGES** seçin

Kurulduktan sonra, bağlantı bilgisini not et:
```
Host: localhost
Database: cpanel_username_hesappaylas_db
User: cpanel_username_hesappaylas_user
Password: [senin şifren]
```

### Adım 7.2: .env Dosyası Oluştur

SSH'da aşağıdaki komutu çalıştır:

```bash
cd ~/public_html
nano .env
```

**.env dosyasının içeriği:**

```
# Flask Konfigürasyonu
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=your-very-secure-random-key-here-min-32-chars

# MySQL Veritabanı
DATABASE_URL=mysql+pymysql://cpanel_username_hesappaylas_user:your_db_password@localhost/cpanel_username_hesappaylas_db

# Domain ve URL
BASE_URL=https://hesappaylas.com
FRONTEND_URL=https://hesappaylas.com

# API Keys (Varsa doldur - opsiyonel)
STRIPE_SECRET_KEY=
STRIPE_PUBLIC_KEY=
TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
TWILIO_PHONE_NUMBER=

# OAuth (Opsiyonel)
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
FACEBOOK_APP_ID=
FACEBOOK_APP_SECRET=
```

**Dosyayı kaydet:** `Ctrl+O` → `Enter` → `Ctrl+X`

### Adım 7.3: Secret Key Oluştur (Güvenlik için)

```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

Çıkışı `.env` dosyasında `SECRET_KEY=` değerine yapıştır.

---

## 8. 🗃️ Veritabanı Migrasyonları Çalıştır

```bash
cd ~/public_html

# Activate et
source ~/hesap_paylas_env/bin/activate

# Flask app'in içinde veritabanı intialization'ı yap
python3 backend/app.py  # İlk çalıştırmada tabloları oluşturacak

# Veya Flask CLI ile:
export FLASK_APP=backend/app.py
flask db upgrade  # Eğer Alembic kullanıyorsa
```

---

## 9. ⚙️ cPanel - Apache/Passenger Konfigürasyonu

cPanel genellikle **Passenger** kullanır. Setup etmek için:

### Adım 9.1: cPanel'de Passenger'ı Etkinleştir

1. **cPanel → Setup Python App (Node.js, Python)**
2. **Create Application** seçin
3. Aşağıdaki bilgileri doldur:

```
Node.js Version: (Python seç) 3.8 or newer
Application Root: /home/username/public_html
Application Startup File: wsgi.py
Application URL: https://hesappaylas.com
```

4. **Create** butonuna bas

### Adım 9.2: WSGI Dosyası Düzelt

`wsgi.py` dosyasını kontrol et ve aşağıdaki gibi olduğundan emin ol:

```python
import sys
import os

# Virtual environment path
venv_path = os.path.expanduser('~/hesap_paylas_env')
if venv_path not in sys.path:
    sys.path.insert(0, venv_path)

# Django/Flask app'i import et
from backend.app import create_app

app = create_app()

if __name__ == "__main__":
    app.run()
```

---

## 10. 🔗 Redirect ve .htaccess Ayarları

```bash
cd ~/public_html
nano .htaccess
```

**.htaccess dosyasının içeriği:**

```apache
# HTTPS'e yönlendir
<IfModule mod_rewrite.c>
    RewriteEngine On
    RewriteCond %{HTTPS} off
    RewriteRule ^(.*)$ https://%{HTTP_HOST}%{REQUEST_URI} [L,R=301]
</IfModule>

# Index dosyaları
DirectoryIndex index.html index.py

# Frontend routing
<IfModule mod_rewrite.c>
    RewriteBase /
    
    # API istekleri Flask'a git
    RewriteCond %{REQUEST_URI} ^/api/
    RewriteCond %{REQUEST_URI} !^/api/static/
    RewriteRule ^api/(.*)$ - [L]
    
    # Varsa ve dosya veya dizin değilse, index.html'e git
    RewriteCond %{REQUEST_FILENAME} !-f
    RewriteCond %{REQUEST_FILENAME} !-d
    RewriteRule ^ index.html [QSA,L]
</IfModule>

# Statik dosya sıkıştırması
<IfModule mod_deflate.c>
    AddOutputFilterByType DEFLATE text/html text/plain text/xml text/css text/javascript application/javascript application/json
</IfModule>

# Güvenlik
<FilesMatch "\.env">
    Order allow,deny
    Deny from all
</FilesMatch>

<FilesMatch "\.git">
    Order allow,deny
    Deny from all
</FilesMatch>
```

Dosyayı kaydet: `Ctrl+O` → `Enter` → `Ctrl+X`

---

## 11. 🔄 Database Senkronizasyonu (Opsiyonel)

Eğer mevcut veriler varsa (production'dan migrate ediyorsan):

```bash
cd ~/public_html
source ~/hesap_paylas_env/bin/activate

# Dump'u MySQL'e yükle
mysql -h localhost -u cpanel_username_hesappaylas_user -p cpanel_username_hesappaylas_db < backup.sql
```

---

## 12. 🚀 Uygulama Test Et

### SSH'da:

```bash
cd ~/public_html
source ~/hesap_paylas_env/bin/activate

# Flask app'i local'de test et (sadece SSH'da)
python3 backend/app.py
# 'Running on ...' yazısını görmelisin
# Ctrl+C ile durdur
```

### Tarayıcıda:

1. `https://hesappaylas.com` adresine git
2. Homepage yükleniyorsa → Başarılı! ✅
3. Eğer hata alırsan → Adım 13'e bak

---

## 13. 🐛 Hata Giderme (Troubleshooting)

### Sorun: 500 Internal Server Error

**Çözüm 1:** cPanel logs'unu kontrol et
```bash
tail -100 ~/logs/error_log
tail -100 ~/logs/access_log
```

**Çözüm 2:** .env dosyasında DATABASE_URL'nin doğru olup olmadığını kontrol et
```bash
mysql -h localhost -u cpanel_username_hesappaylas_user -p
> SELECT VERSION();  # Bağlantıyı test et
```

**Çözüm 3:** WSGI dosyası yollarını kontrol et
```bash
python3 -c "from backend.app import create_app; app = create_app(); print('App başarıyla oluşturuldu')"
```

### Sorun: MySQL bağlantısı başarısız

```bash
# Doğru kullanıcı adı ve şifreyi kontrol et
mysql -h localhost -u cpanel_username_hesappaylas_user -p cpanel_username_hesappaylas_db

# Veritabanı var mı kontrol et
> SHOW TABLES;
```

### Sorun: Static dosyalar yüklenmiyor

```bash
# Dosya izinlerini kontrol et
chmod -R 755 ~/public_html
chmod 644 ~/public_html/*.html
chmod 644 ~/public_html/*.css
chmod 644 ~/public_html/*.js
```

---

## 14. 📊 Monitoring ve Maintenance

### Günlük Kontrol

```bash
# Error loglarını kontrol et
tail -50 ~/logs/error_log

# Database backup'ı al
mysqldump -h localhost -u cpanel_username_hesappaylas_user -p cpanel_username_hesappaylas_db > ~/backups/db_backup_$(date +%Y%m%d).sql
```

### Oto-Backup (cPanel'de)

1. cPanel → **Backup** → Configure Backup
2. **Add New Account**
3. Backups ayarlarını güvenli bir yer (GitHub, Google Drive vb.)

---

## 15. 🔒 Güvenlik Kontrol Listesi

- [ ] `.env` dosyasına `.gitignore` ile erişim yasaklandı
- [ ] `SECRET_KEY` güvenli ve random (32+ char)
- [ ] MySQL kullanıcısı sadece gerekli veritabanına erişebiliyor
- [ ] `.htaccess` ile `/.env` ve `/.git` erişimi engellendi
- [ ] HTTPS (SSL) etkinleştirildi (cPanel → AutoSSL)
- [ ] Regular backups alınıyor
- [ ] logs monitored ediliyor

---

## 16. 🎉 Başarı Kriterleri

Deployment'ınız başarılıysa:

✅ `https://hesappaylas.com` açılıyor  
✅ Grup oluşturabiliyorsun  
✅ Veritabanına veri kaydediliyor  
✅ API endpoint'leri çalışıyor (`/api/groups` vb.)  
✅ QR kodlar oluşturuluyor  
✅ Mobil cihazda PWA yüklenebiliyor  

---

## 📞 Destek ve Sorular

Sorun yaşarsan, hataya ait tam error mesajını ve aşağıdaki bilgileri not et:

```
- .env dosyasındaki hata ne?
- cPanel logs'unda ne yazıyor?
- Hangi endpoint çalışmıyor?
- Database bağlantısı başarılı mı?
```

Başarılar! 🚀
