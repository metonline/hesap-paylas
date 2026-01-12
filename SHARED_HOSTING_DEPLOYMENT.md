# Shared Linux Hosting'de Deployment Guide

## 1. SSH Bağlantı Kur
```bash
ssh username@yourserver.com
# Şifrenizi girin
```

## 2. Python Ortamı Hazırla
```bash
# Python 3.9+ olup olmadığını kontrol et
python3 --version

# Virtual environment oluştur
python3 -m venv /home/username/hesap-paylas-env

# Activate et
source /home/username/hesap-paylas-env/bin/activate

# pip'i upgrade et
pip install --upgrade pip
```

## 3. Uygulamayı İndir
```bash
cd /home/username/public_html
# veya /home/username/www

# GitHub'dan clone et
git clone https://github.com/metonline/hesap-paylas.git
cd hesap-paylas

# Virtual environment'ı bağla
source /home/username/hesap-paylas-env/bin/activate
```

## 4. Dependencies Kur
```bash
pip install -r requirements.txt
```

## 5. Database Setup

### Seçenek A: MySQL (Shared Hosting'de yaygın)
```bash
# .env dosyasını düzenle
nano .env

# Şu satırı ekle:
DATABASE_URL=mysql+pymysql://username:password@localhost/database_name
```

### Seçenek B: PostgreSQL (Varsa)
```bash
DATABASE_URL=postgresql://username:password@localhost/database_name
```

### Seçenek C: SQLite (En basit)
```bash
DATABASE_URL=sqlite:///./backend/instance/hesap_paylas.db
```

## 6. cPanel/WHM ile Web Server Konfigurasyonu

### Apache + WSGI için:
```bash
# .htaccess dosyası oluştur (public_html root'ta)
nano /home/username/public_html/.htaccess
```

**.htaccess içeriği:**
```apache
<IfModule mod_wsgi.c>
    WSGIScriptAlias / /home/username/public_html/hesap-paylas/wsgi.py
    WSGIPythonPath /home/username/hesap-paylas:/home/username/hesap-paylas-env/lib/python3.9/site-packages
    
    <Directory /home/username/public_html/hesap-paylas>
        <Files wsgi.py>
            Require all granted
        </Files>
    </Directory>
</IfModule>

# Rewrite kuralları
<IfModule mod_rewrite.c>
    RewriteEngine On
    RewriteCond %{REQUEST_FILENAME} !-f
    RewriteRule ^(?!static/)(.*)$ /hesap-paylas/wsgi.py [L]
</IfModule>
```

## 7. Supervisor ile Process Yönetimi (Opsiyonel)

Eğer VPS ise, Supervisor kurarak Flask'ı daemon olarak çalıştırabilirsin:

```bash
pip install supervisor

# Config dosyası oluştur
sudo nano /etc/supervisor/conf.d/hesap-paylas.conf
```

**Config içeriği:**
```ini
[program:hesap-paylas]
directory=/home/username/public_html/hesap-paylas
command=/home/username/hesap-paylas-env/bin/gunicorn --workers 2 --bind 0.0.0.0:5000 wsgi:app
user=username
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/home/username/logs/hesap-paylas.log
```

## 8. Nginx Reverse Proxy (VPS için)

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /static/ {
        alias /home/username/public_html/hesap-paylas/;
    }
}
```

## 9. Environment Değişkenleri Ayarla

**.env dosyası:**
```env
FLASK_ENV=production
SECRET_KEY=your-secret-key-here
JWT_SECRET=your-jwt-secret-here
DATABASE_URL=your-database-url
```

## 10. Cron Job ile Sync (Opsiyonel)

Database sync'i otomatik çalıştırmak için:

```bash
# Crontab aç
crontab -e

# Her 10 dakikada bir sync çalıştır
*/10 * * * * /home/username/hesap-paylas-env/bin/python /home/username/public_html/hesap-paylas/watch_and_sync.py >> /home/username/logs/sync.log 2>&1
```

## 11. SSL Sertifikası (HTTPS)

cPanel'de **AutoSSL** etkinleştir veya Let's Encrypt kullan:

```bash
# Let's Encrypt ile
sudo certbot certonly --webroot -w /home/username/public_html -d yourdomain.com
```

## 12. Test Et

```bash
# Lokal test
curl http://localhost:5000/health

# Uzaktan test
curl https://yourdomain.com/health
```

## 13. Sorun Giderme

**Logs'u kontrol et:**
```bash
# Apache logs
tail -f /var/log/apache2/error_log
tail -f /var/log/apache2/access_log

# Flask logs
tail -f /home/username/logs/hesap-paylas.log
```

**Database bağlantısını test et:**
```bash
source /home/username/hesap-paylas-env/bin/activate
python -c "from backend.app import app, db; 
with app.app_context(): 
    db.create_all(); 
    print('✓ Database connected')"
```

---

## Özetle

1. SSH'ye gir
2. Virtual environment kur
3. Repo clone et
4. `pip install -r requirements.txt`
5. `.env` dosyasını configure et
6. Web server'ı konfigure et (Apache/Nginx)
7. Test et

**Hangi adımda takılırsan yardımcı olurum!**
