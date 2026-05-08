# Turkticaret MySQL - Hızlı Referans ve Checklist

## 🚀 Deployment Özet (5 Adım)

```bash
# 1. SSH'ya bağlan
ssh username@hesappaylas.com

# 2. Dizine git
cd ~/public_html

# 3. GitHub'dan indir
git clone https://github.com/metonline/hesap-paylas.git .

# 4. Virtual environment ve dependencies
cd ~
python3 -m venv hesap_paylas_env
source hesap_paylas_env/bin/activate
cd ~/public_html && pip install -r requirements.txt

# 5. .env dosyasını düzenle (cPanel MySQL bilgileriyle)
nano .env

# 6. Database'i intiialize et
python3 init_mysql_db.py

# 7. Tarayıcıda test et
https://hesappaylas.com
```

---

## 📋 Pre-Deployment Checklist

### cPanel Hazırlık
- [ ] SSH Access etkinleştirildi (Security → SSH Access)
- [ ] MySQL Database oluşturuldu (cPanel → MySQL Databases)
- [ ] MySQL User oluşturuldu
- [ ] Domain(ler) eklenmiş (Addon Domains)
- [ ] SSL (AutoSSL) etkinleştirildi
- [ ] Email accounts oluşturuldu (opsiyonel)

### Lokal Hazırlık (Deployment Öncesi)
- [ ] GitHub repo clone edildi
- [ ] requirements.txt kontrol edildi
- [ ] Virtual environment oluşturuldu
- [ ] Dependencies kuruldu
- [ ] `.env` template oluşturuldu
- [ ] Deployment documentation okunadı

### Sunucu Hazırlık
- [ ] Python 3.8+ kurulu
- [ ] Git kurulu
- [ ] SSH key setup yapıldı
- [ ] Dizinler oluşturuldu
- [ ] File permissions kontrol edildi (755 dizin, 644 dosya)

---

## 🗄️ MySQL Configuration Quick Reference

### cPanel'de MySQL Bilgisini Bul

```
cPanel Dashboard → MySQL Databases → "User" kolonu

Formant:
Host:     localhost
Database: cpaneluser_dbname
User:     cpaneluser_dbuser
Password: [Sen oluşturduğun şifre]

.env'ye ekle:
DATABASE_URL=mysql+pymysql://cpaneluser_dbuser:password@localhost/cpaneluser_dbname
```

### MySQL Bağlantısını Test Et

```bash
# SSH'da
mysql -h localhost -u cpanel_user_hesapp -p
# Şifre sor, gir

# MySQL prompt'ta
> SHOW DATABASES;
> USE cpanel_user_hesappaylas;
> SHOW TABLES;
> SELECT COUNT(*) FROM users;  # Test
> EXIT;
```

---

## ⚙️ Passenger Python App Setup (cPanel)

1. **cPanel Dashboard**
2. **Setup Python App** ara (veya Node.js, Ruby'nin yanında olur)
3. **Python Version:** 3.8 veya 3.9+ seç
4. **Application Root:** `/home/username/public_html`
5. **Startup File:** `wsgi.py`
6. **Application URL:** `https://hesappaylas.com`
7. **Create** tıkla

cPanel otomatik olarak:
- Restart wrapper oluşturacak
- Restarted Passenger daemon
- `.htaccess` güncelleyecek

---

## 🔍 Sorun Giderme - Hızlı Komutlar

### 500 Error Alıyorsan

```bash
# 1. Error log'unu kontrol et
tail -100 ~/logs/error_log

# 2. Access log'unu kontrol et
tail -100 ~/logs/access_log

# 3. Flask app'ı manuel olarak test et
cd ~/public_html
source ~/hesap_paylas_env/bin/activate
python3 backend/app.py
# Ctrl+C ile kapat
```

### Database Bağlantısı Başarısız?

```bash
# 1. .env kontrol et
cat .env | grep DATABASE_URL

# 2. MySQL'e doğrudan bağlan
mysql -h localhost -u dbuser -p dbname

# 3. PyMySQL kurulu mu kontrol et
python3 -c "import pymysql; print('OK')"

# 4. SQLAlchemy ile test et
python3 << 'EOF'
from sqlalchemy import create_engine, text
db_url = "mysql+pymysql://user:pass@localhost/db"
engine = create_engine(db_url)
with engine.connect() as conn:
    result = conn.execute(text("SELECT VERSION()"))
    print(result.fetchone())
EOF
```

### Static Dosyalar Yüklenmiyor?

```bash
# 1. Dosya izinlerini kontrol et
ls -la ~/public_html/*.css
ls -la ~/public_html/static/

# 2. İzinleri düzelt
chmod -R 755 ~/public_html
chmod 644 ~/public_html/*.{html,css,js}

# 3. Browser cache'i temizle (Ctrl+Shift+Delete)

# 4. .htaccess'te static dosya kuralını kontrol et
cat .htaccess | grep static
```

### Application Restart Etmek İçin

```bash
# Passenger otomatik restart eder fakat manuel restart için:
touch ~/public_html/tmp/restart.txt

# veya cPanel'den: Setup Python App → Restart
```

---

## 📊 Database Yönetimi

### Regular Backups

```bash
# MySQL backup
mysqldump -h localhost -u dbuser -p dbname > ~/backups/db_backup_$(date +%Y%m%d_%H%M%S).sql

# cPanel'de Backup ayarlarını kontrol et:
# cPanel → Backups → Configure Backup → Add Backup Account
```

### Database İstatistikleri

```bash
# SSH'da
mysql -h localhost -u dbuser -p dbname -e "SELECT TABLE_NAME, TABLE_ROWS, DATA_LENGTH FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA='dbname';"
```

---

## 🔒 Security Checklist

- [ ] `.env` dosyasına cPanel'de erişim yasaklandı (`.htaccess`)
- [ ] `.git` dizinine erişim yasaklandı
- [ ] `SECRET_KEY` güvenli ve random
- [ ] HTTPS (SSL) aktif
- [ ] MySQL kullanıcısı sadece spesifik DB'ye erişebiliyor
- [ ] Database user'ının gücü sınırlandırılmış
- [ ] Regular backups alınıyor
- [ ] Error messages production'da detaylı değil (FLASK_DEBUG=False)
- [ ] Logs monitored ediliyor

---

## 📞 Sık Sorulan Sorular (SSS)

**S: Veritabanı yapısını nasıl reset etim?**
A: 
```bash
# .env kontrol et, sonra:
python3 init_mysql_db.py
```

**S: Eski veriyi yeni sunucuya nasıl taşırım?**
A:
```bash
# Eski sunucuda backup al
mysqldump -u user -p olddb > backup.sql

# Yeni sunucuya aktar
mysql -h localhost -u newuser -p newdb < backup.sql
```

**S: Node.js app değil, Flask app kullanıyorum, sorun var mı?**
A: Hayır! cPanel'de "Setup Python App" seçtiğin sürece sorun yok.

**S: Custom domain (subdomain) nasıl eklerim?**
A:
```bash
# cPanel → Addon Domains veya Subdomains
# Ardından .env dosyasında FRONTEND_URL güncelle
```

**S: Email gönderirken "SMTP Timeout" hatası alıyorum?**
A:
```
1. SMTP_SERVER ve SMTP_PORT'u kontrol et
2. SENDER_EMAIL ve SENDER_PASSWORD doğru mu?
3. cPanel Exim konfigürasyonunu kontrol et
4. Firewall 587 portunu engelliyor mu kontrol et
```

---

## 📖 İlgili Belgeler

- [TURKTICARET_DEPLOYMENT.md](TURKTICARET_DEPLOYMENT.md) - Detaylı adım adım rehber
- [SHARED_HOSTING_DEPLOYMENT.md](SHARED_HOSTING_DEPLOYMENT.md) - Genel shared hosting rehberi
- [LOCAL_DEVELOPMENT.md](LOCAL_DEVELOPMENT.md) - Lokal geliştirme
- [DATABASE_SYNC_GUIDE.md](DATABASE_SYNC_GUIDE.md) - Database senkronizasyonu

---

## 🎯 Başarı İşaretleri

Deployment başarılıysa bu işaretleri görmelisin:

✅ `https://hesappaylas.com` açılıyor  
✅ Homepage render ediliyor  
✅ Grup oluşturabiliyor  
✅ QR kod oluşturuluyor  
✅ Veritabanına veri kaydediliyor  
✅ API endpoints çalışıyor (`/api/groups` vb.)  
✅ Browser console'da hata yok  
✅ cPanel logs'unda 5xx error yok  

---

**Son Güncelleme:** 2024  
**Framework:** Flask + SQLAlchemy + MySQL  
**Hosting:** Turkticaret (cPanel)  
**Database:** MySQL/MariaDB
