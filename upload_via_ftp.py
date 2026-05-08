import ftplib
import os
import getpass

# FTP bağlantı bilgileri
FTP_HOST = 'hesappaylas.com'
FTP_USER = 'hes20caylascom'
FTP_DIR = 'public_html'

# Password güvenli olarak sor
FTP_PASS = getpass.getpass('cPanel şifrenizi girin: ')

LOCAL_FILES = [
    (r'c:\Users\metin\Desktop\BILL\script.js', 'script.js'),
    (r'c:\Users\metin\Desktop\BILL\upload-handler.php', 'upload-handler.php'),
]


try:
    print("FTP sunucusuna bağlanılıyor...")
    ftp = ftplib.FTP(FTP_HOST)
    
    print(f"Giriş yapılıyor: {FTP_USER}@{FTP_HOST}")
    ftp.login(FTP_USER, FTP_PASS)
    
    print(f"Dizin değiştiriliyor: {FTP_DIR}")
    ftp.cwd(FTP_DIR)
    
    # Her dosyayı yükle
    for local_path, remote_name in LOCAL_FILES:
        if not os.path.exists(local_path):
            print(f"⚠️  Dosya bulunamadı: {local_path}")
            continue
        
        file_size = os.path.getsize(local_path)
        print(f"\n📤 Yükleniyor: {remote_name} ({file_size:,} bytes)")
        
        try:
            with open(local_path, 'rb') as f:
                response = ftp.storbinary(f'STOR {remote_name}', f)
                print(f"   ✅ Yanıt: {response}")
        except Exception as e:
            print(f"   ❌ Hata: {e}")
    
    # Sunucudaki dosya listesini kontrol et
    print(f"\n📋 Sunucudaki dosyalar ({FTP_DIR}):")
    ftp.retrlines('LIST', lambda x: print(f"   {x}"))
    
    print("\n✅ Upload tamamlandı!")
    
    ftp.quit()
    
except ftplib.all_errors as e:
    print(f"❌ FTP Hatası: {e}")
    print("\n💡 Çözüm:")
    print("   1. cPanel kullanıcı adı: hes20caylascom")
    print("   2. Şifre doğru mu kontrol edin")
    print("   3. FTP etkinleştirilmiş mi kontrol edin (cPanel > FTP Accounts)")
except KeyboardInterrupt:
    print("\n⏸️  Kullanıcı tarafından iptal edildi")
except Exception as e:
    print(f"❌ Hata: {e}")
    import traceback
    traceback.print_exc()
