#!/bin/bash
# Hesap Paylaş - cPanel + SSH + MySQL Deployment Script
# Kullanım: Bu scripti SSH'ye kopyala ve çalıştır
# chmod +x deploy.sh && ./deploy.sh

set -e  # Exit on error

echo "================================"
echo "Hesap Paylaş cPanel Deployment"
echo "================================"

# 1. VARIABLES
USERNAME="mgb3dcinfo"
HOMEDIR="/home/$USERNAME"
APPDIR="$HOMEDIR/public_html/hesap-paylas"
VENVDIR="$HOMEDIR/hesap-paylas-venv"
GITHUB_REPO="https://github.com/metonline/hesap-paylas.git"

echo "[1/8] SSH'ye hoş geldin! Şimdi deployment başlıyor..."
echo "Uygulama kurulum yolu: $APPDIR"

# 2. CLEANUP (existing installation)
echo "[2/8] Eski kurulum temizleniyor..."
if [ -d "$APPDIR" ]; then
    echo "Mevcut klasör bulundu, backup alınıyor..."
    mv "$APPDIR" "${APPDIR}.backup.$(date +%s)"
fi

# 3. CLONE REPOSITORY
echo "[3/8] GitHub'dan repo klonlanıyor..."
cd "$HOMEDIR/public_html"
git clone $GITHUB_REPO
cd "$APPDIR"
echo "✓ Repo klonlandı"

# 4. VIRTUAL ENVIRONMENT
echo "[4/8] Python virtual environment oluşturuluyor..."
if [ -d "$VENVDIR" ]; then
    rm -rf "$VENVDIR"
fi
python3 -m venv "$VENVDIR"
source "$VENVDIR/bin/activate"
pip install --upgrade pip setuptools wheel
echo "✓ Virtual environment hazır"

# 5. INSTALL DEPENDENCIES
echo "[5/8] Python dependencies kuruluyor..."
pip install -r requirements.txt
echo "✓ Tüm dependencies kuruldu"

# 6. CREATE .env FILE
echo "[6/8] .env dosyası oluşturuluyor..."
cat > "$APPDIR/.env" << 'EOF'
FLASK_ENV=production
SECRET_KEY=your-secret-key-change-this-please-$(date +%s)
JWT_SECRET=your-jwt-secret-change-this-please-$(date +%s)

# MySQL Database Configuration
# cPanel'de "SQL" sekmesinden yeni database oluştur ve buraya koy
DATABASE_URL=mysql+pymysql://mgb3dcinfo_user:password@localhost/mgb3dcinfo_hesap_paylas

# CORS Settings
CORS_ORIGINS=https://yourdomain.com,http://localhost:8000
EOF

echo "⚠️  ÖNEMLI: .env dosyasını düzenle ve şu değerleri değiştir:"
echo "   - DATABASE_URL: cPanel'den MySQL credentials'ı al"
echo "   - SECRET_KEY & JWT_SECRET: güvenli keys gir"
echo "   - CORS_ORIGINS: domain'inizi girin"
echo ""
echo "   Dosya: $APPDIR/.env"

# 7. CREATE STARTUP SCRIPT
echo "[7/8] Startup script oluşturuluyor..."
cat > "$APPDIR/start.sh" << EOF
#!/bin/bash
source $VENVDIR/bin/activate
cd $APPDIR
gunicorn --workers 2 --bind 127.0.0.1:5000 wsgi:app
EOF
chmod +x "$APPDIR/start.sh"
echo "✓ Startup script hazır"

# 8. SETUP INSTRUCTIONS
echo "[8/8] Kurulum tamamlandı!"
echo ""
echo "================================"
echo "SONRAKI ADIMLAR:"
echo "================================"
echo ""
echo "1. cPanel'de MySQL Database Oluştur:"
echo "   - cPanel → MySQL Databases"
echo "   - Database: mgb3dcinfo_hesap_paylas"
echo "   - User: mgb3dcinfo_user"
echo "   - Password: (güvenli bir şey gir)"
echo ""
echo "2. .env Dosyasını Düzenle:"
cat "$APPDIR/.env"
echo ""
echo "3. cPanel'de Python App Konfigure Et:"
echo "   - cPanel → Setup Python App"
echo "   - Seç: Python 3.9+ (en yeni)"
echo "   - App root: $APPDIR"
echo "   - App startup file: $APPDIR/wsgi.py"
echo "   - App entry point: app"
echo ""
echo "4. Test Et:"
echo "   - https://yourdomain.com (frontend)"
echo "   - https://yourdomain.com/health (API)"
echo ""
echo "================================"
echo "✓ Kurulum hazır!"
echo "================================"
