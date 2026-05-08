# Turkticaret Deployment Checklist

Bu checklist, hesappaylas.com sitesini Turkticaret cPanel'de başarıyla deploy etmek için tüm adımları içerir.

**Domain:** hesappaylas.com  
**Hosting:** Turkticaret  
**Panel:** cPanel  
**Database:** MySQL/MariaDB  
**Framework:** Flask (Python)

---

## 📋 PHASE 1: Hazırlık (Local)

### Lokal Makine'de
- [ ] Proje GitHub'dan clone edildi
  ```bash
  git clone https://github.com/metonline/hesap-paylas.git
  cd hesap-paylas
  ```
- [ ] Deployment rehberleri okundu:
  - [ ] TURKTICARET_DEPLOYMENT.md
  - [ ] TURKTICARET_QUICK_REFERENCE.md
  - [ ] requirements.txt kontrol edildi
- [ ] `.env.example` incelendi
- [ ] SSH key'i oluşturdu ve cPanel'e yükleyecek duruma getirildi

### Hosting Provider (Turkticaret)
- [ ] Hosting paketi aktifleştirildi
- [ ] cPanel erişimi test edildi (https://hesappaylas.com:2083)
- [ ] cPanel kullanıcı adı ve şifresi not edildi

---

## 🔐 PHASE 2: cPanel Konfigürasyonu

### Domain Setup
- [ ] Ana domain (hesappaylas.com) eklenmiş
- [ ] WWW version yönlendirmesi ayarlandı
- [ ] SSL Sertifikası (AutoSSL) aktif
  - [ ] cPanel → AutoSSL → Tetikle
  - [ ] Sertifika oluşturuldu ve aktif

### SSH Access
- [ ] SSH Access etkinleştirildi (Security → SSH Access)
- [ ] Public Key yüklendi
- [ ] Local'den SSH bağlantısı test edildi:
  ```bash
  ssh -i "path/to/key" username@hesappaylas.com
  ```

### MySQL Database
- [ ] MySQL Database oluşturuldu:
  - Database Name: `cpanel_hesappaylas_db`
  - [ ] Database silme işlemi cancel'ledisi
- [ ] MySQL User oluşturuldu:
  - Username: `cpanel_hesappaylas_user`
  - Password: [Güçlü şifre oluşturuldu]
- [ ] User → Database bağlantısı yapıldı:
  - [ ] ALL PRIVILEGES verildi
- [ ] MySQL Connection Information not edildi:
  ```
  Host: localhost
  Database: cpanel_hesappaylas_db
  User: cpanel_hesappaylas_user
  Password: ___________________
  ```

### Email Configuration (Opsiyonel)
- [ ] Email account oluşturuldu (opsiyonel)
- [ ] Email routing ayarlandı

---

## 📁 PHASE 3: Sunucu Hazırlığı

### SSH'a Bağlan
```bash
ssh -i "key.pem" username@hesappaylas.com
```

### Dizin Yapısını Oluştur
- [ ] Mevcut dosyalar yedeklendi (varsa)
  ```bash
  cd ~/public_html
  # Dosyalar kontrol et
  ```
- [ ] `public_html` temizlendi (yeni domain ise)
  ```bash
  cd ~/public_html
  rm -rf *
  ```

### GitHub'dan Proje İndir
- [ ] Git kurulu kontrol edildi:
  ```bash
  git --version  # 2.x olmalı
  ```
- [ ] Repository clone edildi:
  ```bash
  cd ~/public_html
  git clone https://github.com/metonline/hesap-paylas.git .
  ```
- [ ] Dosyalar doğru yerde:
  - [ ] `index.html` var
  - [ ] `backend/app.py` var
  - [ ] `wsgi.py` var
  - [ ] `requirements.txt` var
  - [ ] `.gitignore` var

---

## 🐍 PHASE 4: Python Environment

### Virtual Environment Oluştur
- [ ] venv oluşturuldu:
  ```bash
  cd ~
  python3 -m venv hesap_paylas_env
  ```
- [ ] venv başarıyla oluşturuldu kontrol edildi:
  ```bash
  ls -la ~/hesap_paylas_env/bin/python3
  ```

### Dependencies Yükle
- [ ] venv activate edildi:
  ```bash
  source ~/hesap_paylas_env/bin/activate
  ```
- [ ] pip upgraded edildi:
  ```bash
  pip install --upgrade pip setuptools wheel
  ```
- [ ] Requirements yüklendi:
  ```bash
  cd ~/public_html
  pip install -r requirements.txt
  ```
- [ ] PyMySQL kuruldu (MySQL için):
  ```bash
  pip install pymysql==1.0.2
  ```
- [ ] Kurulum doğrulandı:
  ```bash
  pip list | grep -E 'Flask|SQLAlchemy|pymysql|gunicorn'
  ```

### Python Version Kontrol
- [ ] Python 3.8+ kullanılıyor:
  ```bash
  python3 --version  # 3.8.0 veya üzeri
  ```

---

## 🔧 PHASE 5: Uygulama Konfigürasyonu

### .env Dosyası Oluştur
- [ ] SSH'da .env oluşturuldu:
  ```bash
  cd ~/public_html
  nano .env
  ```
- [ ] Zorunlu değişkenler eklendi:
  - [ ] `FLASK_ENV=production`
  - [ ] `FLASK_DEBUG=False`
  - [ ] `SECRET_KEY=` (32+ karakter, random)
    ```bash
    python3 -c "import secrets; print(secrets.token_hex(32))"
    ```
  - [ ] `DATABASE_URL=mysql+pymysql://cpanel_hesappaylas_user:password@localhost/cpanel_hesappaylas_db`
  - [ ] `BASE_URL=https://hesappaylas.com`
  - [ ] `FRONTEND_URL=https://hesappaylas.com`

- [ ] Opsiyonel değişkenler (varsa):
  - [ ] STRIPE_SECRET_KEY (ödeme için)
  - [ ] TWILIO_ACCOUNT_SID (SMS için)
  - [ ] GOOGLE_CLIENT_ID (OAuth için)
  - [ ] SENDER_EMAIL (email gönderme için)

### WSGI Dosyası Kontrol Et
- [ ] `wsgi.py` açık kontrol edildi:
  ```bash
  cat ~/public_html/wsgi.py | head -30
  ```
- [ ] `from backend.app import app` satırı var
- [ ] Database path'ler doğru

### File Permissions
- [ ] Dizin izinleri (755):
  ```bash
  chmod -R 755 ~/public_html
  ```
- [ ] Dosya izinleri (644):
  ```bash
  find ~/public_html -type f -exec chmod 644 {} \;
  ```
- [ ] Python scripts'e execute permission:
  ```bash
  chmod 755 ~/public_html/*.py
  chmod 755 ~/public_html/init_mysql_db.py
  ```

---

## 🗄️ PHASE 6: Database Setup

### MySQL Bağlantısını Test Et
- [ ] MySQL'e bağlanıldı:
  ```bash
  mysql -h localhost -u cpanel_hesappaylas_user -p cpanel_hesappaylas_db
  > SELECT 1;
  > SHOW TABLES;  (boş olmalı ilk olarak)
  > EXIT;
  ```

### Database Initialization Script'i Çalıştır
- [ ] init_mysql_db.py çalıştırıldı:
  ```bash
  cd ~/public_html
  source ~/hesap_paylas_env/bin/activate
  python3 init_mysql_db.py
  ```
- [ ] Script tamamlandı (✅ tüm 5 adım)
- [ ] Tables oluşturuldu kontrol edildi:
  ```bash
  mysql -h localhost -u cpanel_hesappaylas_user -p cpanel_hesappaylas_db -e "SHOW TABLES;"
  ```
- [ ] En az 5+ tablo oluşturulmuş olmalı

### Database Tablo Doğrulama
- [ ] Tabloların yapısı doğru:
  ```bash
  mysql -h localhost -u cpanel_hesappaylas_user -p cpanel_hesappaylas_db -e "DESCRIBE users;"
  ```

---

## ⚙️ PHASE 7: cPanel Python App Setup (Passenger)

### Setup Python App'ı Yapılandır
- [ ] cPanel'e girdim (https://hesappaylas.com:2083)
- [ ] **Setup Python App** (veya Node.js/Python yanında) bölümünü buldum
- [ ] **Create Application** tıklandı
- [ ] Aşağıdaki değerleri ayarlandı:
  - [ ] **Python Version:** 3.8 atau 3.9+
  - [ ] **Application Root:** `/home/username/public_html`
  - [ ] **Application Startup File:** `wsgi.py`
  - [ ] **Application URL:** `https://hesappaylas.com`
  - [ ] **Create** tıklandı

- [ ] cPanel Application oluşturuldu ve "Running" durumunda:
  - cPanel → Setup Python App → [App Name] → Status: Running ✅

---

## 📄 PHASE 8: Apache / Rewrite Rules

### .htaccess Dosyası
- [ ] `.htaccess` dosyası oluşturuldu veya güncellenildi:
  ```bash
  cd ~/public_html
  nano .htaccess
  ```

- [ ] Şu kurallar eklendi:
  - [ ] HTTPS redirect
  - [ ] Static dosya kuralları
  - [ ] Frontend routing (SPA)
  - [ ] Güvenlik kuralları (.env, .git erişim yasakları)

- [ ] .htaccess test edildi:
  ```bash
  # Syntax kontrol
  apachectl configtest
  ```

### Static Dosya Servisi
- [ ] CSS/JS dosyaları doğru konumda:
  ```bash
  ls -la ~/public_html/styles.css
  ls -la ~/public_html/script.js
  ```

---

## 🚀 PHASE 9: Testing

### Manual Flask Test (SSH'da)
- [ ] Flask app manuel olarak test edildi:
  ```bash
  cd ~/public_html
  source ~/hesap_paylas_env/bin/activate
  python3 backend/app.py
  # "Running on..." yazısı görmeli
  # Ctrl+C ile exit
  ```

### Browser Test
- [ ] `https://hesappaylas.com` açıldı
- [ ] Homepage yüklendi ve render edildi ✅
- [ ] Tarayıcı console'da error yok ✅

### API Test (opsiyonel)
- [ ] API endpoints test edildi:
  ```bash
  curl -k https://hesappaylas.com/api/groups
  curl -k https://hesappaylas.com/api/health
  ```

### Database Test
- [ ] Veri yazılıp okunabiliyor mu test edildi:
  ```bash
  mysql -h localhost -u dbuser -p dbname -e "SELECT COUNT(*) FROM users;"
  ```

### Log Kontrol
- [ ] Error logs kontrol edildi:
  ```bash
  tail -20 ~/logs/error_log
  tail -20 ~/logs/access_log
  ```
  - [ ] 5xx error yok
  - [ ] 404 error'lar beklenen (örn: favicon.ico)

---

## 🔒 PHASE 10: Güvenlik

### File Security
- [ ] `.env` dosyasına erişim yasaklandı (.htaccess'te)
- [ ] `.git` dizinine erişim yasaklandı
- [ ] `.gitignore` uygulanıyor mu kontrol et
- [ ] Database credentials sadece `.env`'de (code'da değil)

### Database Security
- [ ] MySQL user'ı sadece ilgili database'ye erişebiliyor
- [ ] MySQL user password güvenli (12+ karakter, random)
- [ ] Root account password değiştirildi (varsa)

### Application Security
- [ ] `SECRET_KEY` güvenli ve random (32+ char)
- [ ] `FLASK_DEBUG = False` (production'da)
- [ ] HTTPS aktif ve working
- [ ] Session cookies `SECURE=True` ve `HTTPONLY=True`

### SSL/TLS
- [ ] HTTPS sertifikası geçerli:
  ```bash
  openssl s_client -connect hesappaylas.com:443 -showcerts
  ```
- [ ] HTTP → HTTPS redirect çalışıyor
- [ ] Mixed content warnings yok (F12 → Console)

---

## 📊 PHASE 11: Monitoring & Backups

### Logging Setup
- [ ] Error logs monitored ediliyor:
  ```bash
  tail -f ~/logs/error_log
  ```
- [ ] Günlük log review programı
- [ ] Log rotation ayarlanmış (cPanel'de)

### Database Backups
- [ ] Backup script oluşturuldu:
  ```bash
  nano ~/backup_db.sh
  ```
  İçeriği:
  ```bash
  #!/bin/bash
  mysqldump -h localhost -u cpanel_hesappaylas_user -p "password" cpanel_hesappaylas_db > ~/backups/db_$(date +%Y%m%d).sql
  ```

- [ ] Backup cronjob ayarlandı:
  ```bash
  crontab -e
  # Şu satır eklendi:
  0 2 * * * ~/backup_db.sh
  ```

- [ ] Manuel backup test edildi:
  ```bash
  bash ~/backup_db.sh
  ls -la ~/backups/
  ```

### cPanel Backups
- [ ] cPanel → Backups → Configure Backup ayarlandı
- [ ] Auto-backup etkinleştirildi (opsiyonel)

---

## 📞 PHASE 12: Post-Launch

### Monitoring
- [ ] Daily error logs kontrol edilecek
- [ ] Database size monitored edilecek
- [ ] Disk space kontrol edilecek

### Documentation
- [ ] Deployment notes saklandı
- [ ] MySQL credentials güvenli yerde:
  - [ ] Not: password.txt (şifreli)
  - [ ] Backup: Cloud storage (encrypted)

### Backup Düzeni
- [ ] **Günlük:** Database backup
- [ ] **Haftalık:** Full cPanel backup
- [ ] **Aylık:** Off-site backup (Google Drive, S3, vb.)

### Update Schedule
- [ ] Python packages: Aylık güvenlik kontrol
- [ ] Flask: Açık güvenlik güncellemeleri
- [ ] MySQL: Hosting provider tarafından handle edilir

---

## ✅ PHASE 13: Success Verification

Deployment başarılıysa, şu kriterlerin tümü karşılanmalı:

### Frontend
- [ ] ✅ https://hesappaylas.com açılıyor
- [ ] ✅ Homepage render ediliyor (CSS/JS yüklü)
- [ ] ✅ Mobile responsive
- [ ] ✅ PWA install butonu çalışıyor

### Functionality
- [ ] ✅ Grup oluşturabiliyor
- [ ] ✅ QR kod oluşturuluyor
- [ ] ✅ Veritabanına veri kaydediliyor
- [ ] ✅ Hesap bölüştürme çalışıyor

### API
- [ ] ✅ /api/groups endpoint'i çalışıyor
- [ ] ✅ Authentication çalışıyor
- [ ] ✅ CORS properly configured

### Performance
- [ ] ✅ Page load time < 3 saniye
- [ ] ✅ API response < 500ms
- [ ] ✅ 500 error yok logs'ta

### Security
- [ ] ✅ HTTPS aktif (https:// url'de)
- [ ] ✅ SSL sertifikası geçerli (F12 → Security)
- [ ] ✅ No console errors
- [ ] ✅ No sensitive data in logs

### Monitoring
- [ ] ✅ Error logs kontrol edildi
- [ ] ✅ Database connectivity çalışıyor
- [ ] ✅ Backup script test edildi

---

## 🎉 Deployment Tamamlandı!

Şayet tüm checkboxlar ✅ işaretlendiyse, **hesappaylas.com sitesi Turkticaret'de başarıyla deploy edilmiştir!**

### Sonraki Adımlar:
1. **Monitor** - Ilk 24 saatte logs'ları yakın takip et
2. **Test** - Mobile cihazlarda ve farklı browsers'ta test et
3. **Notify** - Kullanıcılar ve stakeholders'a haber ver
4. **Backup** - İlk backup'ı al ve test et restore işlemini
5. **Document** - Deployment notes'ları sakla ve share et

### Destek:
- **Sorun bulursan:** TURKTICARET_TROUBLESHOOTING.md'ye bak
- **Referans gerek:** TURKTICARET_QUICK_REFERENCE.md kısayol komutları için
- **Detaylı rehber:** TURKTICARET_DEPLOYMENT.md full talimatlar için

---

**Deployment Tarihi:** _______________  
**Deployed By:** _______________  
**Notes:** _______________________________________________

---

*Bu checklist şablonunu kaydet ve future deployments için kullan.*
