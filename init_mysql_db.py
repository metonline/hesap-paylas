#!/usr/bin/env python3
"""
Turkticaret MySQL Database Initialization Script
Bu script MySQL veritabanını Hesap Paylaş uygulaması için hazırlar.

Kullanım:
    python3 init_mysql_db.py
"""

import os
import sys
import subprocess
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

def print_section(title):
    """Print formatted section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def check_env_file():
    """Check if .env file exists and has required variables"""
    print_section("1️⃣  .env Dosyası Kontrol Ediliyor")
    
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ .env dosyası bulunamadı!")
        print("\n📝 .env dosyası oluştur. Şu satırları ekle:\n")
        print("""DATABASE_URL=mysql+pymysql://username:password@localhost/database_name
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=your-secret-key-min-32-chars
BASE_URL=https://hesappaylas.com
FRONTEND_URL=https://hesappaylas.com
""")
        sys.exit(1)
    
    # Check required variables
    required_vars = ['DATABASE_URL', 'FLASK_ENV', 'SECRET_KEY']
    missing = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing.append(var)
    
    if missing:
        print(f"❌ Eksik değişkenler: {', '.join(missing)}")
        sys.exit(1)
    
    db_url = os.getenv('DATABASE_URL')
    print(f"✅ .env dosyası bulundu")
    print(f"   Database URL: {db_url.split('@')[1] if '@' in db_url else '***'}")
    print(f"   Flask Environment: {os.getenv('FLASK_ENV')}")
    print(f"   Secret Key: {'✓ Set' if os.getenv('SECRET_KEY') else '✗ Not Set'}")

def check_python_packages():
    """Check if required Python packages are installed"""
    print_section("2️⃣  Python Paketleri Kontrol Ediliyor")
    
    required_packages = [
        'flask',
        'sqlalchemy',
        'pymysql',
        'flask_cors',
        'flask_sqlalchemy'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package}")
            missing.append(package)
    
    if missing:
        print(f"\n⚠️  Eksik paketler: {', '.join(missing)}")
        print(f"\nBunları yüklemek için çalıştır:")
        print(f"   pip install {' '.join(missing)}")
        sys.exit(1)
    
    print("\n✅ Tüm paketler yüklü!")

def test_database_connection():
    """Test MySQL database connection"""
    print_section("3️⃣  Veritabanı Bağlantısı Test Ediliyor")
    
    try:
        from sqlalchemy import create_engine, text
        
        db_url = os.getenv('DATABASE_URL')
        engine = create_engine(db_url, echo=False)
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT VERSION()"))
            version = result.fetchone()[0]
            print(f"✅ Bağlantı başarılı!")
            print(f"   MySQL Version: {version}")
        
        return True
    
    except Exception as e:
        print(f"❌ Bağlantı başarısız!")
        print(f"   Hata: {str(e)}\n")
        print("🔧 Çözüm Önerileri:")
        print("   1. .env dosyasında DATABASE_URL'yi kontrol et")
        print("   2. MySQL sunucusu çalışıyor mu kontrol et")
        print("   3. Kullanıcı adı ve şifre doğru mu kontrol et")
        print("   4. Veritabanı var mı kontrol et: mysql -u user -p")
        return False

def initialize_database():
    """Create database tables"""
    print_section("4️⃣  Veritabanı Tabloları Oluşturuluyor")
    
    try:
        # Import Flask app to trigger table creation
        print("Flask uygulaması başlatılıyor...")
        sys.path.insert(0, str(Path(__file__).parent))
        
        from backend.app import app, db
        
        with app.app_context():
            print("Tabloları oluşturuyor...")
            db.create_all()
            print("✅ Tabloları oluştur tamamlandı!")
            
            # Show created tables
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            if tables:
                print(f"\n   Oluşturulan tablolar ({len(tables)} adet):")
                for table in sorted(tables):
                    print(f"      - {table}")
            else:
                print("\n⚠️  Hiçbir tablo oluşturulmadı!")
                print("   app.py'de models tanımlandı mı kontrol et")
        
        return True
    
    except Exception as e:
        print(f"❌ Tablo oluşturulamadı!")
        print(f"   Hata: {str(e)}\n")
        import traceback
        traceback.print_exc()
        return False

def create_sample_data():
    """Optionally create sample data"""
    print_section("5️⃣  Örnek Veriler Oluşturuluyor (Opsiyonel)")
    
    try:
        sys.path.insert(0, str(Path(__file__).parent))
        from backend.app import app, db
        
        with app.app_context():
            print("⏭️  Örnek veri oluşturma atlanıyor")
            print("   (Production'da gerekli değildir)")
        
        return True
    
    except Exception as e:
        print(f"⚠️  Örnek veriler oluşturulamadı (opsiyonel)")
        print(f"   Hata: {str(e)}")
        return False

def print_next_steps():
    """Print next steps"""
    print_section("✅ Setup Tamamlandı!")
    
    print("Yapılması gerekenler:")
    print("\n1. cPanel'de Passenger Python App'i konfigure et:")
    print("   - Application Root: /home/username/public_html")
    print("   - Startup File: wsgi.py")
    print("   - Node.js Version: Python 3.8+")
    
    print("\n2. .htaccess dosyasının doğru olup olmadığını kontrol et:")
    print("   - HTTPS redirect aktif mi?")
    print("   - Frontend routing doğru mu?")
    
    print("\n3. Application'ı kontrol et:")
    print(f"   - https://hesappaylas.com adresine git")
    print(f"   - Homepagesini yükleniyorsa ✅ Başarılı")
    print(f"   - 500 error alırsan logs kontrol et:")
    print(f"     tail -50 ~/logs/error_log")
    
    print("\n4. SSL sertifikasını kontrol et:")
    print("   - cPanel → AutoSSL → HTTPS'in aktif olduğundan emin ol")
    
    print("\n5. Regular backups ayarla:")
    print("   - cPanel → Backups → Auto-Backup konfigüre et")
    
    print("\n6. Database backups:")
    print("   - Hergün MySQL veritabanını backup al")
    print("   - Command: mysqldump -h localhost -u user -p db > backup.sql")

def main():
    """Main execution"""
    print("\n" + "="*60)
    print("  Hesap Paylaş - Turkticaret MySQL Setup Wizard")
    print("="*60)
    print(f"\nÇalışan dizin: {Path.cwd()}")
    print(f"Python sürümü: {sys.version.split()[0]}")
    
    # Run checks
    check_env_file()
    check_python_packages()
    
    if not test_database_connection():
        print("\n❌ Setup iptal edildi. Veritabanı bağlantısını düzelt.")
        sys.exit(1)
    
    # Initialize database
    if not initialize_database():
        print("\n❌ Setup başarısız. Ayrıntılar için çıktıyı kontrol et.")
        sys.exit(1)
    
    create_sample_data()
    print_next_steps()
    
    print("\n" + "="*60)
    print("  Setup Başarıyla Tamamlandı! 🎉")
    print("="*60 + "\n")

if __name__ == '__main__':
    main()
