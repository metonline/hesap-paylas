#!/bin/bash

# Turkticaret Deployment Setup Script
# Bu script hesappaylas.com sitesini Turkticaret'te setup et

set -e  # Exit on error

echo "=========================================="
echo "  Hesap Paylaş - Turkticaret Setup"
echo "=========================================="
echo ""

# 1. public_html'in içinde ne var kontrol et
echo "📁 1️⃣  public_html içeriği kontrol ediliyor..."
cd ~/public_html
echo "   Dosya sayısı: $(ls -1 | wc -l)"
ls -la | head -10
echo ""

# 2. Python sürümü kontrol et
echo "🐍 2️⃣  Python sürümü kontrol ediliyor..."
python3 --version
echo ""

# 3. Venv'i düzgün oluştur (--without-pip ile)
echo "📦 3️⃣  Virtual environment oluşturuluyor..."
cd ~
rm -rf hesap_paylas_env 2>/dev/null || true
python3 -m venv hesap_paylas_env --without-pip
echo "   ✅ Virtual environment oluşturuldu"
echo ""

# 4. Pip'i upgrade et
echo "📥 4️⃣  Pip kurulup upgrade ediliyor..."
source ~/hesap_paylas_env/bin/activate
python3 -m ensurepip --upgrade
pip --version
echo "   ✅ Pip kuruldu ve upgrade edildi"
echo ""

# 5. public_html'i temizle ve GitHub'dan clone et
echo "🔄 5️⃣  GitHub'dan proje indiriliyor..."
cd ~/public_html
ls -la | wc -l
echo "   Eski dosyalar temizleniyor..."
rm -rf * .git* .htaccess 2>/dev/null || true
echo "   GitHub'dan clone ediliyor..."
git clone https://github.com/metonline/hesap-paylas.git .
echo "   ✅ Proje indirildi"
echo "   Dosya sayısı: $(ls -1 | wc -l)"
echo ""

# 6. Requirements yükle
echo "📦 6️⃣  Requirements yükleniyor..."
if [ -f requirements.txt ]; then
    pip install -r requirements.txt
    echo "   ✅ Requirements yüklendi"
else
    echo "   ❌ requirements.txt bulunamadı!"
    exit 1
fi
echo ""

# 7. Python sürümü ve kurulumları doğrula
echo "✔️  7️⃣  Kurulumlar doğrulanıyor..."
python3 -c "import flask; import sqlalchemy; print('   ✅ Flask ve SQLAlchemy OK')" || {
    echo "   ⚠️  Flask veya SQLAlchemy yüklü değil!"
    pip install -r requirements.txt
}
echo ""

# 8. init_mysql_db.py dosyasını kontrol et
echo "🗄️  8️⃣  Database setup dosyası kontrol ediliyor..."
if [ -f init_mysql_db.py ]; then
    echo "   ✅ init_mysql_db.py var"
else
    echo "   ❌ init_mysql_db.py yok - GitHub'da olmalı"
fi
echo ""

# 9. .env dosyasını kontrol et ve template oluştur
echo "🔐 9️⃣  Environment dosyası kontrol ediliyor..."
if [ ! -f .env ]; then
    echo "   .env dosyası oluşturuluyor..."
    cat > .env << 'ENVEOF'
# Hesap Paylaş - Turkticaret Environment
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=your-secret-key-min-32-chars-CHANGE-THIS

# MySQL Database (cPanel'den al)
DATABASE_URL=mysql+pymysql://user:password@localhost/database_name

# URLs
BASE_URL=https://hesappaylas.com
FRONTEND_URL=https://hesappaylas.com
ENVEOF
    echo "   📝 .env template oluşturuldu - değerleri doldur!"
else
    echo "   ✅ .env dosyası var"
fi
echo ""

# 10. File permissions
echo "🔒 1️⃣  0️⃣  File izinleri ayarlanıyor..."
chmod -R 755 ~/public_html
find ~/public_html -type f -exec chmod 644 {} \; 2>/dev/null || true
chmod 755 ~/public_html/*.py 2>/dev/null || true
echo "    ✅ İzinler ayarlandı"
echo ""

# 11. WSGI dosyasını kontrol et
echo "⚙️  1️⃣  1️⃣  WSGI dosyası kontrol ediliyor..."
if [ -f wsgi.py ]; then
    echo "   ✅ wsgi.py var"
    head -3 wsgi.py
else
    echo "   ❌ wsgi.py bulunamadı!"
fi
echo ""

# 12. Status
echo "=========================================="
echo "  ✅ Setup tamamlandı!"
echo "=========================================="
echo ""
echo "📋 Sonraki adımlar:"
echo ""
echo "1️⃣  .env dosyasını doldur:"
echo "   nano ~/public_html/.env"
echo ""
echo "2️⃣  SECRET_KEY oluştur:"
echo "   python3 -c \"import secrets; print(secrets.token_hex(32))\""
echo ""
echo "3️⃣  DATABASE_URL ayarla:"
echo "   DATABASE_URL=mysql+pymysql://user:password@localhost/db"
echo ""
echo "4️⃣  Database initialize et:"
echo "   source ~/hesap_paylas_env/bin/activate"
echo "   cd ~/public_html"
echo "   python3 init_mysql_db.py"
echo ""
echo "5️⃣  cPanel'de Passenger setup et"
echo ""
echo "=========================================="
