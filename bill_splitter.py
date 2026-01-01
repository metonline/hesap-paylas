#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Restoran Hesabı Bölüştürücü - Grup Yönetimi
Restaurant Bill Splitter - Group Management
"""

import json
import os
import uuid
import qrcode
from pathlib import Path
import datetime

# Twilio için (isteğe bağlı)
try:
    from twilio.rest import Client
    TWILIO_AVAILABLE = True
except ImportError:
    TWILIO_AVAILABLE = False

def load_restaurants():
    """Restaurant menüsünü yükle"""
    script_dir = Path(__file__).parent
    restaurants_file = script_dir / "restaurants.json"
    
    if restaurants_file.exists():
        with open(restaurants_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def load_groups():
    """Grup verilerini yükle"""
    script_dir = Path(__file__).parent
    groups_file = script_dir / "groups.json"
    
    if groups_file.exists():
        with open(groups_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_groups(groups):
    """Grup verilerini kaydet"""
    script_dir = Path(__file__).parent
    groups_file = script_dir / "groups.json"
    
    with open(groups_file, 'w', encoding='utf-8') as f:
        json.dump(groups, f, indent=2, ensure_ascii=False)

def generate_group_id():
    """Benzersiz grup ID'si oluştur"""
    return str(uuid.uuid4())[:8].upper()

def generate_qr_code(group_id):
    """Grup ID'sinden QR kod oluştur ve kaydet"""
    script_dir = Path(__file__).parent
    qr_file = script_dir / f"group_qr_{group_id}.png"
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(group_id)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(qr_file)
    
    return str(qr_file)

def display_qr_code_info(group_id, qr_file):
    """QR kod bilgisini göster"""
    print("\n" + "="*60)
    print("📱 GRUP QR KODU OLUŞTURULDU!")
    print("="*60)
    print(f"Grup ID: {group_id}")
    print(f"QR Kod Dosyası: {qr_file}")
    print("\n📋 Paylaşma Seçenekleri:")
    print(f"  1. QR kodu göster (dosyayı açın)")
    print(f"  2. Grup ID'sini paylaş: {group_id}")
    print("  3. QR kodunu fotografla ve paylaş")
    print("\n✅ Diğer kişiler aynı Grup ID'sini girerek katılabilir!")
    print("="*60 + "\n")

def add_member_to_group(group_id, first_name, last_name):
    """Gruba yeni üye ekle"""
    groups = load_groups()
    if group_id not in groups:
        return False
    
    member_name = f"{first_name} {last_name}"
    member_id = str(uuid.uuid4())[:8]
    
    groups[group_id]['members'][member_id] = {
        'name': member_name,
        'joined_at': str(datetime.datetime.now()),
        'orders': []
    }
    save_groups(groups)
    return True

def show_group_members(group_id):
    """Grup üyelerini göster"""
    groups = load_groups()
    if group_id not in groups:
        return
    
    members = groups[group_id]['members']
    print("\n" + "="*60)
    print(f"👥 GRUP #{group_id} ÜYELERİ")
    print("="*60)
    
    if not members:
        print("Henüz hiç üye yoktur.")
    else:
        for i, (member_id, member_info) in enumerate(members.items(), 1):
            print(f"{i}. {member_info['name']:30s} (Katıldığı saat: {member_info['joined_at'][-8:]})")
    
    print("="*60 + "\n")

def set_group_restaurant(group_id, rest_id, restaurant):
    """Grubun restaurant menüsünü ayarla"""
    groups = load_groups()
    if group_id not in groups:
        return False
    
    groups[group_id]['restaurant'] = {
        'id': rest_id,
        'name': restaurant['name'],
        'phone': restaurant['phone'],
        'categories': restaurant['categories']
    }
    save_groups(groups)
    return True

def get_group_restaurant(group_id):
    """Grup restaurant menüsünü getir"""
    groups = load_groups()
    if group_id not in groups:
        return None
    
    if 'restaurant' not in groups[group_id]:
        return None
    
    return groups[group_id]['restaurant']

def show_group_restaurant(group_id):
    """Grup restaurant bilgisini göster"""
    group_restaurant = get_group_restaurant(group_id)
    
    if not group_restaurant:
        print("❌ Grup için restaurant seçilmemiş!")
        return False
    
    print("\n" + "="*60)
    print("🍽️  GRUP RESTAURANT BİLGİSİ")
    print("="*60)
    print(f"Restaurant: {group_restaurant['name']}")
    print(f"Tel: {group_restaurant['phone']}")
    print("="*60 + "\n")
    
    return True

def format_order_for_restaurant(group_members, group_id, total_bill, tip_amount, tax_amount, total_with_extras):
    """Restoran için sipariş özeti oluştur"""
    message = f"""GRUP SİPARİŞ - #{group_id}
════════════════════════════════════════

"""
    
    for person, orders in group_members.items():
        if orders:
            message += f"👤 {person}:\n"
            for order in orders:
                type_emoji = "🔸" if order['type'] == 'personal' else "🔹" if order['type'] == 'shared' else "⚪"
                product_emoji = order.get('emoji', '🍽️')
                message += f"  {type_emoji} {product_emoji} {order['name']} ({int(order['quantity'])} adet) = {order['total']:.2f}₺\n"
            message += "\n"
    
    message += f"""════════════════════════════════════════
📊 ÖZET:
  Hesap Toplam: {total_bill:.2f}₺
  Bahşiş: {tip_amount:.2f}₺
  Vergi: {tax_amount:.2f}₺
  ────────────────
  GENEL TOPLAM: {total_with_extras:.2f}₺

📍 Grup Üye Sayısı: {len(group_members)}
⏰ Tarih: {datetime.datetime.now().strftime('%d.%m.%Y %H:%M')}
════════════════════════════════════════"""
    
    return message

def send_order_via_sms(phone_number, message):
    """SMS ile sipariş gönder"""
    if not TWILIO_AVAILABLE:
        print("⚠️  Twilio kütüphanesi yüklü değil: pip install twilio")
        return False
    
    account_sid = input("Twilio Account SID (https://www.twilio.com/console): ").strip()
    auth_token = input("Twilio Auth Token (https://www.twilio.com/console): ").strip()
    from_number = input("Twilio telefon numarası (+1234567890 formatında): ").strip()
    
    if not all([account_sid, auth_token, from_number]):
        print("❌ Eksik Twilio bilgileri!")
        return False
    
    try:
        client = Client(account_sid, auth_token)
        sms = client.messages.create(
            body=message,
            from_=from_number,
            to=phone_number
        )
        print(f"✅ SMS gönderildi! (ID: {sms.sid})")
        return True
    except Exception as e:
        print(f"❌ SMS gönderilemedi: {str(e)}")
        return False

def send_order_via_whatsapp(phone_number, message):
    """WhatsApp ile sipariş gönder"""
    if not TWILIO_AVAILABLE:
        print("⚠️  Twilio kütüphanesi yüklü değil: pip install twilio")
        return False
    
    account_sid = input("Twilio Account SID (https://www.twilio.com/console): ").strip()
    auth_token = input("Twilio Auth Token (https://www.twilio.com/console): ").strip()
    from_number = input("Twilio WhatsApp numarası (whatsapp:+1234567890 formatında): ").strip()
    
    if not all([account_sid, auth_token, from_number]):
        print("❌ Eksik Twilio bilgileri!")
        return False
    
    try:
        client = Client(account_sid, auth_token)
        whatsapp = client.messages.create(
            body=message,
            from_=from_number,
            to=f"whatsapp:{phone_number.replace('+', '')}"
        )
        print(f"✅ WhatsApp mesajı gönderildi! (ID: {whatsapp.sid})")
        return True
    except Exception as e:
        print(f"❌ WhatsApp gönderilemedi: {str(e)}")
        return False

def send_order_via_link(phone_number, message):
    """WhatsApp linki ile gönder (Web tarayıcıda açılır)"""
    import urllib.parse
    
    # Mesajı URL'ye uygun hale getir
    encoded_message = urllib.parse.quote(message)
    whatsapp_link = f"https://wa.me/{phone_number.replace('+', '')}?text={encoded_message}"
    
    print(f"\n📱 WhatsApp Linki:")
    print(f"{whatsapp_link}\n")
    print("💡 Link tarayıcıda açılacak veya WhatsApp'ta açılabilir.")
    print("   Linki manuel olarak kullanabilirsiniz.")
    
    return True

def send_order_via_email(restaurant_email, message):
    """Email ile sipariş gönder"""
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    
    print("\n📧 Email ile gönderim için:")
    sender_email = input("Gönderen email (Gmail örneği): ").strip()
    sender_password = input("Email şifresi (Gmail App Password): ").strip()
    
    if not sender_email or not sender_password:
        print("❌ Email bilgileri gerekli!")
        return False
    
    try:
        msg = MIMEMultipart()
        msg['Subject'] = 'Grup Sipariş Özeti'
        msg['From'] = sender_email
        msg['To'] = restaurant_email
        
        msg.attach(MIMEText(message, 'plain', 'utf-8'))
        
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        
        print(f"✅ Email gönderildi: {restaurant_email}")
        return True
    except Exception as e:
        print(f"❌ Email gönderilemedi: {str(e)}")
        return False

def get_positive_float(prompt):
    """Kullanıcıdan pozitif bir sayı al"""
    while True:
        try:
            value = float(input(prompt))
            if value < 0:
                print("❌ Lütfen pozitif bir sayı girin!")
                continue
            return value
        except ValueError:
            print("❌ Geçersiz giriş! Lütfen geçerli bir sayı girin.")

def get_positive_int(prompt):
    """Kullanıcıdan pozitif bir tam sayı al"""
    while True:
        try:
            value = int(input(prompt))
            if value <= 0:
                print("❌ Lütfen 0'dan büyük bir sayı girin!")
                continue
            return value
        except ValueError:
            print("❌ Geçersiz giriş! Lütfen geçerli bir tam sayı girin.")

def scan_qr_code():
    """QR kodu okut (simülasyon veya manuel)"""
    print("\n📱 QR KOD OKUMA:")
    print("-" * 50)
    print("1. QR kodu oku (kamera)")
    print("2. Restaurant ID'sini manuel gir")
    print("-" * 50)
    
    choice = input("Seçim (1 veya 2): ").strip()
    
    if choice == "1":
        try:
            import cv2
            from pyzbar.pyzbar import decode
            
            print("\n🎥 Kamera açılıyor...")
            cap = cv2.VideoCapture(0)
            
            if not cap.isOpened():
                print("❌ Kamera bulunamadı! Manuel giriş yapılacak.")
                return None
            
            print("QR kodu kameraya gösterin (q tuşuna basarak çıkın)...")
            
            while True:
                ret, frame = cap.read()
                
                if not ret:
                    break
                
                decoded_objects = decode(frame)
                
                if decoded_objects:
                    for obj in decoded_objects:
                        qr_data = obj.data.decode('utf-8')
                        cap.release()
                        cv2.destroyAllWindows()
                        return qr_data
                
                cv2.imshow('QR Kod Okutucu', frame)
                
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            
            cap.release()
            cv2.destroyAllWindows()
            
        except ImportError:
            print("⚠️  pyzbar veya opencv-python yüklü değil.")
            print("   Kurulum: pip install pyzbar opencv-python")
            return None
    
    # Manuel giriş
    print("\n📋 Mevcut Restaurant Kimlik Kodları:")
    restaurants = load_restaurants()
    for rest_id, rest_info in restaurants.items():
        print(f"  • {rest_id}: {rest_info['name']}")
    
    rest_id = input("\nRestaurant ID'sini girin: ").strip()
    return rest_id

def select_restaurant():
    """Restaurant seç ve menüsünü göster"""
    restaurants = load_restaurants()
    
    if not restaurants:
        print("❌ Restaurant verisi bulunamadı!")
        return None, None
    
    rest_id = scan_qr_code()
    
    if not rest_id or rest_id not in restaurants:
        print("\n❌ Geçersiz Restaurant ID!")
        return None, None
    
    restaurant = restaurants[rest_id]
    return rest_id, restaurant

def select_items_for_person(restaurant, person_orders, person_name):
    """Bir kişi için menüden ürün seç"""
    print("\n🛒 MENÜDEN ÜRÜN SEÇİN (Bitirmek için 0 girin):\n")
    
    while True:
        current_personal = sum(order['total'] for order in person_orders if order['type'] == 'personal')
        current_shared = sum(order['total'] for order in person_orders if order['type'] == 'shared')
        current_excluded = sum(order['total'] for order in person_orders if order['type'] == 'excluded')
        
        print(f"Bireysel: {current_personal:>10.2f} ₺  |  Ortak: {current_shared:>10.2f} ₺  |  Hariç: {current_excluded:>10.2f} ₺")
        print("\nMevcut Kategoriler:")
        
        categories = list(restaurant['categories'].keys())
        for i, cat in enumerate(categories, 1):
            print(f"  {i}. {cat}")
        print(f"  0. Bitir")
        
        try:
            cat_choice = int(input("\nKategori seç (numara): "))
            
            if cat_choice == 0:
                break
            
            if cat_choice < 1 or cat_choice > len(categories):
                print("❌ Geçersiz seçim!")
                continue
            
            selected_category = categories[cat_choice - 1]
            items = restaurant['categories'][selected_category]
            
            print(f"\n📋 {selected_category}:")
            for i, item in enumerate(items, 1):
                emoji = item.get('emoji', '🍽️')
                has_image = " 📷" if item.get('image') else ""
                print(f"  {i}. {emoji} {item['name']:30s} {item['price']:>8.2f} ₺{has_image}")
            print(f"  0. Geri Dön")
            print("\n💡 İpucu: Resim görmek için 'r1', 'r2' vb. yazın")
            
            item_choice_str = input("\nÜrün seç (numara, resmi görmek için 'r' + numara): ").strip()
            
            # Resim görmek isterse
            if item_choice_str.startswith('r') or item_choice_str.startswith('R'):
                try:
                    img_choice = int(item_choice_str[1:])
                    if img_choice < 1 or img_choice > len(items):
                        print("❌ Geçersiz seçim!")
                        continue
                    image_item = items[img_choice - 1]
                    if image_item.get('image'):
                        import webbrowser
                        webbrowser.open(image_item['image'])
                        print(f"🖼️  {image_item['name']} resmi tarayıcıda açılıyor...")
                    else:
                        print("❌ Bu ürünün resmi mevcut değil.")
                    continue
                except (ValueError, IndexError):
                    print("❌ Geçersiz giriş!")
                    continue
            
            try:
                item_choice = int(item_choice_str)
            except ValueError:
                print("❌ Geçersiz giriş!")
                continue
            
            if item_choice == 0:
                continue
            
            if item_choice < 1 or item_choice > len(items):
                print("❌ Geçersiz seçim!")
                continue
            
            selected_item = items[item_choice - 1]
            quantity = float(input("Miktar: "))
            
            if quantity <= 0:
                print("❌ Geçersiz miktar!")
                continue
            
            # Sipariş türü seçimi
            print("\n📝 Sipariş Türü Seç:")
            print("  1. 🔸 Bireysel (sadece ben öderim)")
            print("  2. 🔹 Ortak Tüketim (grup üyeleri eşit paylaşır)")
            print("  3. ⚪ Hariç Tut (Bu siparış hesaplamaya dahil edilmez)")
            order_type_choice = input("\nSeçim (1, 2 veya 3): ").strip()
            
            if order_type_choice == "2":
                order_type = "shared"
                type_label = "🔹 Ortak"
            elif order_type_choice == "3":
                order_type = "excluded"
                type_label = "⚪ Hariç"
            else:
                order_type = "personal"
                type_label = "🔸 Bireysel"
            
            item_total = quantity * selected_item['price']
            person_orders.append({
                'name': selected_item['name'],
                'quantity': quantity,
                'price': selected_item['price'],
                'total': item_total,
                'type': order_type,
                'emoji': selected_item.get('emoji', '🍽️'),
                'image': selected_item.get('image', ''),
                'person': person_name
            })
            
            print(f"✅ Eklendi ({type_label}): {selected_item['name']} x{quantity} = {item_total:.2f} ₺\n")
            
        except ValueError:
            print("❌ Geçersiz giriş!")
            continue

def show_orders_and_split(group_members, group_id):
    """Tüm siparişleri göster ve böl"""
    # Siparışları göster
    total_personal = 0
    total_shared = 0
    total_excluded = 0
    
    print("\n" + "="*80)
    print("📋 TÜM SİPARİŞLER:")
    print("="*80)
    
    # Tüm ortak ürünleri topla
    shared_items = {}
    
    for person, orders in group_members.items():
        person_personal = sum(order['total'] for order in orders if order['type'] == 'personal')
        person_shared = sum(order['total'] for order in orders if order['type'] == 'shared')
        person_excluded = sum(order['total'] for order in orders if order['type'] == 'excluded')
        person_total = person_personal + person_shared + person_excluded
        
        total_personal += person_personal
        total_shared += person_shared
        total_excluded += person_excluded
        
        print(f"\n👤 {person}:")
        if orders:
            personal_orders = [o for o in orders if o['type'] == 'personal']
            shared_orders = [o for o in orders if o['type'] == 'shared']
            excluded_orders = [o for o in orders if o['type'] == 'excluded']
            
            # Bireysel siparişler
            for i, order in enumerate(personal_orders, 1):
                emoji = order.get('emoji', '🍽️')
                print(f"   {i}. 🔸 {emoji} {order['name']} ({int(order['quantity'])} adet) = {order['total']:.2f} ₺")
            
            # Ortak siparişler ve kim ekledi
            for i, order in enumerate(shared_orders, 1):
                emoji = order.get('emoji', '🍽️')
                order_person = order.get('person', person)
                print(f"   {i}. 🔹 {emoji} {order['name']} ({int(order['quantity'])} adet) - {order_person} ekledi")
                
                # Ortak ürünü sakla (benzersiz kombinasyon için)
                item_key = f"{order['name']}_{order['quantity']}"
                if item_key not in shared_items:
                    shared_items[item_key] = {'order': order, 'people': set()}
                shared_items[item_key]['people'].add(order_person)
            
            # Hariç tutulan siparişler
            for i, order in enumerate(excluded_orders, 1):
                emoji = order.get('emoji', '🍽️')
                print(f"   {i}. ⚪ {emoji} {order['name']} ({int(order['quantity'])} adet) [Hariç]")
            
            print(f"   {'-'*70}")
            print(f"   Toplam: {person_total:>10.2f} ₺")
        else:
            print("   (Sipariş yok)")
    
    print(f"\n{'='*80}")
    print(f"Bireysel Toplam:                       {total_personal:>10.2f} ₺")
    print(f"Ortak Toplam:                          {total_shared:>10.2f} ₺")
    if total_excluded > 0:
        print(f"Hariç Toplam (Hesaplamaya dahil değil): {total_excluded:>10.2f} ₺")
    print(f"HESAPLANAN GENEL TOPLAM:               {total_personal + total_shared:>10.2f} ₺")
    print("="*80 + "\n")
    
    total_bill = total_personal + total_shared
    
    if total_bill == 0:
        print("❌ Hiç ürün seçilmedi!")
        return
    
    num_people = len(group_members)
    
    # Bahşiş
    print("📊 BAHŞİŞ AYARLARI:")
    tip_choice = input("Bahşiş eklemek ister misiniz? (e/h): ").lower().strip()
    
    tip_percent = 0
    tip_amount = 0
    
    if tip_choice in ['e', 'yes', 'y', 'evet']:
        tip_type = input("Bahşiş türü: (1) Yüzde, (2) Sabit tutar: ").strip()
        
        if tip_type == "1":
            tip_percent = get_positive_float("Bahşiş yüzdesi (%): ")
            tip_amount = total_bill * (tip_percent / 100)
            print(f"✅ Grup toplam bahşişi: {tip_amount:.2f} ₺ ({tip_percent}%)")
        elif tip_type == "2":
            tip_amount = get_positive_float("Bahşiş tutarı (₺): ")
            tip_percent = (tip_amount / total_bill * 100) if total_bill > 0 else 0
            print(f"✅ Bahşiş tutarı: {tip_amount:.2f} ₺ (Oranı: %{tip_percent:.1f})")
        else:
            print("⚠️  Geçersiz seçim, bahşiş eklenmedi.")
    
    # Vergi
    print("\n📊 VERGİ AYARLARI:")
    tax_choice = input("Vergi eklemek ister misiniz? (e/h): ").lower().strip()
    
    tax_amount = 0
    if tax_choice in ['e', 'yes', 'y', 'evet']:
        tax_percent = get_positive_float("Vergi yüzdesi (%): ")
        tax_amount = total_bill * (tax_percent / 100)
    
    # Toplam hesaplama
    total_with_extras = total_bill + tip_amount + tax_amount
    
    # Ortak sipariş payı (eşit bölüş)
    shared_per_person = total_shared / num_people if num_people > 0 else 0
    
    # Sonuçlar
    print("\n" + "="*80)
    print("💰 FINAL HESAPLAMA:")
    print("="*80)
    print(f"Bireysel Toplam:       {total_personal:>15.2f} ₺")
    print(f"Ortak Toplam:          {total_shared:>15.2f} ₺")
    if total_excluded > 0:
        print(f"Hariç Toplam (Dahil değil): {total_excluded:>15.2f} ₺")
    
    if tip_amount > 0:
        print(f"Bahşiş:                {tip_amount:>15.2f} ₺")
    
    if tax_amount > 0:
        print(f"Vergi:                 {tax_amount:>15.2f} ₺")
    
    print(f"{'-'*50}")
    print(f"Hesaplanan Toplam:     {total_with_extras:>15.2f} ₺")
    print(f"Grup Üyesi Sayısı:     {num_people:>15} kişi")
    print(f"Ortak Payı (Kişi):     {shared_per_person:>15.2f} ₺")
    print(f"{'-'*50}")
    print("="*80 + "\n")
    
    # Grup bilgisi
    if group_id:
        print(f"👥 GRUP BİLGİSİ:")
        print(f"   Grup ID: {group_id}")
        print(f"   Üye Sayısı: {num_people}")
        print()
    
    # Kişiye göre ödeme özeti
    print("="*80)
    print("💸 KİŞİYE GÖRE ÖDEME ÖZETI:")
    print("="*80)
    print(f"{'Kişi':20s} {'Tüketim':>12} {'Oran':>10} {'Bireysel':>12} {'Ortak':>12} {'Bahşiş':>12} {'TOPLAM':>12}")
    print("-"*80)
    
    # Her kişinin detaylı hesabını sakla
    person_accounts = {}
    
    for person, orders in group_members.items():
        person_personal = sum(order['total'] for order in orders if order['type'] == 'personal')
        person_excluded = sum(order['total'] for order in orders if order['type'] == 'excluded')
        person_consumption = person_personal + shared_per_person * num_people  # Tüketim oranı hesaplaması için
        
        # Her kişinin tüketiminin toplam oranı
        consumption_ratio = person_consumption / total_bill if total_bill > 0 else 0
        
        # Her kişinin bahşişi, tüketim oranına göre dağıtılır
        person_tip = tip_amount * consumption_ratio
        
        # Vergi hesaplaması
        person_tax = tax_amount * consumption_ratio if tax_amount > 0 else 0
        
        person_total = person_personal + shared_per_person + person_tip + person_tax
        
        # Hesabı sakla
        person_accounts[person] = {
            'orders': orders,
            'personal': person_personal,
            'shared': shared_per_person,
            'tip': person_tip,
            'tax': person_tax,
            'total': person_total,
            'ratio': consumption_ratio
        }
        
        print(f"{person:20s} {person_consumption:>12.2f} ₺ {consumption_ratio*100:>9.1f}% {person_personal:>12.2f} ₺ {shared_per_person:>12.2f} ₺ {person_tip:>12.2f} ₺ {person_total:>12.2f} ₺")
    
    print("="*80 + "\n")
    
    # KİŞİSEL HESAP ÖZETLERİ
    print("="*80)
    print("👤 KİŞİSEL HESAP ÖZETLERİ")
    print("="*80)
    
    for person, account in person_accounts.items():
        print(f"\n{'='*80}")
        print(f"👤 {person} - KİŞİSEL HESABI")
        print(f"{'='*80}")
        
        # Ürün detayları
        print(f"\n📝 ÜRÜN DETAYLARı:")
        print(f"{'-'*80}")
        
        personal_items = [o for o in account['orders'] if o['type'] == 'personal']
        shared_items_set = [o for o in account['orders'] if o['type'] == 'shared']
        
        if personal_items:
            print(f"\n🔸 BİREYSEL SİPARİŞLER:")
            for item in personal_items:
                emoji = item.get('emoji', '🍽️')
                print(f"   {emoji} {item['name']:30s} x {int(item['quantity']):2d} adet @ {item['price']:>8.2f} ₺ = {item['total']:>10.2f} ₺")
            personal_subtotal = sum(item['total'] for item in personal_items)
            print(f"   {'-'*76}")
            print(f"   Bireysel Toplam:                                             {personal_subtotal:>10.2f} ₺")
        
        if shared_items_set:
            print(f"\n🔹 ORTAK SİPARİŞLER (PAYLAŞILAN):")
            print(f"   Ortak ürünlerin grup içinde eşit bölüşüm payı:")
            for item in shared_items_set:
                emoji = item.get('emoji', '🍽️')
                person_who_ordered = item.get('person', 'Bilinmeyen')
                print(f"   {emoji} {item['name']:30s} - {person_who_ordered} ekledi")
            print(f"   {'-'*76}")
            print(f"   Ortak Payı (Grup Toplamının 1/{num_people}'i):              {account['shared']:>10.2f} ₺")
        
        # Adisyon detayları
        print(f"\n💰 ADİSYON DETAYLARI:")
        print(f"{'-'*80}")
        print(f"   Bireysel Tüketim:                                {account['personal']:>10.2f} ₺")
        print(f"   Ortak Tüketim Payı:                              {account['shared']:>10.2f} ₺")
        print(f"   ──────────────────────────────────────────────────────────")
        print(f"   Ara Toplam:                                      {account['personal'] + account['shared']:>10.2f} ₺")
        
        if account['tip'] > 0:
            print(f"   Bahşiş ({account['ratio']*100:.1f}% tüketim oranı):              {account['tip']:>10.2f} ₺")
        
        if account['tax'] > 0:
            print(f"   Vergi ({account['ratio']*100:.1f}% tüketim oranı):               {account['tax']:>10.2f} ₺")
        
        print(f"   ──────────────────────────────────────────────────────────")
        print(f"   💳 GENEL TOPLAM (ÖDEYECEK TUTAR):               {account['total']:>10.2f} ₺")
        print(f"   ══════════════════════════════════════════════════════════")
    
    print("\n")
    
    # Açıklamalar
    print("   🔸 Bireysel = Sadece bu kişinin ödediği tutarlar")
    print("   🔹 Ortak Pay = Grup üyeleri tarafından eşit paylaştırılan tutarlar")
    print("   ⚪ Hariç = Hesaplamaya dahil edilmeyen (ayrıca ödenen) tutarlar")
    print()
    
    # Restoran'a sipariş gönderme
    group_restaurant = get_group_restaurant(group_id)
    
    if group_restaurant:
        print("="*80)
        print("📞 RESTORAN'A SİPARİŞ GÖNDER:")
        print("="*80)
        
        order_message = format_order_for_restaurant(
            group_members, 
            group_id, 
            total_bill, 
            tip_amount, 
            tax_amount, 
            total_with_extras
        )
        
        print("\n📋 SİPARİŞ ÖZETI:")
        print(order_message)
        print()
        
        send_choice = input("\nRestoran'a nasıl göndermek istersiniz?\n1. WhatsApp Linki\n2. SMS (Twilio)\n3. WhatsApp (Twilio)\n4. Email\n5. Göndermeme\nSeçim (1-5): ").strip()
        
        restaurant_phone = group_restaurant['phone']
        
        if send_choice == "1":
            send_order_via_link(restaurant_phone, order_message)
        elif send_choice == "2":
            send_order_via_sms(restaurant_phone, order_message)
        elif send_choice == "3":
            send_order_via_whatsapp(restaurant_phone, order_message)
        elif send_choice == "4":
            restaurant_email = input("Restoran email adresini girin: ").strip()
            if restaurant_email:
                send_order_via_email(restaurant_email, order_message)
        elif send_choice == "5":
            print("⏭️  Atlandı.")
        else:
            print("❌ Geçersiz seçim.")
    
    print()
    
    # Tekrar sorma
    again = input("Başka bir hesap bölüştürmek ister misiniz? (e/h): ").lower().strip()
    if again in ['e', 'yes', 'y', 'evet']:
        main()

def main():
    print("\n" + "="*60)
    print("🍽️  RESTORAN HESABI BÖLÜŞTÜRÜCÜ  🍽️")
    print("="*60 + "\n")
    
    # Grup seçim
    print("👥 GRUP SEÇENEĞI:")
    print("1. Yeni grup oluştur (QR koduyla paylaş)")
    print("2. Mevcut gruba katıl (QR kod / Grup ID)")
    print("3. Bireysel sipariş ver (grup yok)")
    
    mode_choice = input("\nSeçim (1, 2 veya 3): ").strip()
    
    group_id = None
    group_members = {}
    
    if mode_choice == "1":
        # Yeni grup oluştur
        group_id = generate_group_id()
        qr_file = generate_qr_code(group_id)
        
        groups = load_groups()
        groups[group_id] = {
            'created_at': str(datetime.datetime.now()),
            'members': {},
            'orders': {},
            'restaurant': None
        }
        save_groups(groups)
        
        display_qr_code_info(group_id, qr_file)
        
        print("👤 GRUP KURUCUSUNUN BİLGİLERİ:")
        first_name = input("Adınız: ").strip()
        if not first_name:
            first_name = "Kullanıcı"
        
        last_name = input("Soyadınız: ").strip()
        if not last_name:
            last_name = "1"
        
        full_name = f"{first_name} {last_name}"
        add_member_to_group(group_id, first_name, last_name)
        show_group_members(group_id)
        
        group_members = {full_name: []}
        
    elif mode_choice == "2":
        # Mevcut gruba katıl
        print("\n📱 Gruba Katılma:")
        print("1. QR kod oku")
        print("2. Grup ID'sini manuel gir")
        
        join_choice = input("Seçim (1 veya 2): ").strip()
        
        if join_choice == "1":
            try:
                from pyzbar.pyzbar import decode
                import cv2
                
                cap = cv2.VideoCapture(0)
                if cap.isOpened():
                    print("\n🎥 QR kodu kameraya gösterin...")
                    while True:
                        ret, frame = cap.read()
                        if not ret:
                            break
                        
                        decoded_objects = decode(frame)
                        if decoded_objects:
                            group_id = decoded_objects[0].data.decode('utf-8')
                            cap.release()
                            cv2.destroyAllWindows()
                            break
                        
                        if cv2.waitKey(1) & 0xFF == ord('q'):
                            cap.release()
                            cv2.destroyAllWindows()
                            group_id = None
                            break
                else:
                    print("⚠️  Kamera bulunamadı.")
                    group_id = None
            except ImportError:
                print("⚠️  pyzbar yüklü değil, manuel giriş yapılacak.")
                group_id = None
        
        if not group_id:
            group_id = input("Grup ID'sini girin: ").strip().upper()
        
        groups = load_groups()
        if group_id not in groups:
            print("❌ Grup bulunamadı!")
            return
        
        print("👤 BİLGİLERİNİZ:")
        first_name = input("Adınız: ").strip()
        if not first_name:
            first_name = "Kullanıcı"
        
        last_name = input("Soyadınız: ").strip()
        if not last_name:
            last_name = str(len(groups[group_id]['members']) + 1)
        
        full_name = f"{first_name} {last_name}"
        add_member_to_group(group_id, first_name, last_name)
        
        print(f"\n✅ {full_name}, grup #{group_id} na katıldınız!")
        show_group_members(group_id)
        
        group_members = {full_name: []}
        
    else:
        # Bireysel sipariş
        group_id = None
        your_name = input("Sizin adınız: ").strip()
        if not your_name:
            your_name = "Müşteri 1"
        group_members = {your_name: []}
    
    # Restaurant seç (Sadece grup modunda)
    if group_id and mode_choice in ["1", "2"]:
        print("\n" + "="*60)
        print("🍽️  RESTAURANT MENÜSÜ SEÇIMI")
        print("="*60)
        
        group_restaurant = get_group_restaurant(group_id)
        
        if group_restaurant:
            # Restaurant zaten seçilmiş
            print(f"\n✅ Grup için zaten restaurant seçilmiş: {group_restaurant['name']}")
            show_group_restaurant(group_id)
            restaurant = group_restaurant
        else:
            # Restaurant seçilmemiş, seçmek gerekli
            print("\n📱 Restoran Menüsünü Yükle...")
            rest_id, restaurant = select_restaurant()
            
            if not restaurant:
                print("\n❌ Program sonlandırılıyor...")
                return
            
            # Restaurant gruba kaydet
            set_group_restaurant(group_id, rest_id, restaurant)
            show_group_restaurant(group_id)
    else:
        # Bireysel mod - restaurant seçimi
        print("\n📱 Restoran Menüsünü Yükle...")
        rest_id, restaurant = select_restaurant()
        
        if not restaurant:
            print("\n❌ Program sonlandırılıyor...")
            return
    
    print(f"✅ Seçilen Restaurant: {restaurant['name']}")
    print(f"📞 Tel: {restaurant['phone']}\n")
    
    # Grup üyeleri ve siparişler
    if group_id and mode_choice in ["1", "2"]:
        print(f"👥 Grup #{group_id}")
        print("=" * 60)
        
        while True:
            print(f"\n🛒 MENU:")
            print("1. Ürün sipariş ver")
            print("2. Tüm grup üyelerini gör")
            print("3. Restaurant bilgisini gör")
            print("4. Siparişleri göster ve hesapla (Bitir)")
            
            menu_choice = input("\nSeçim (1, 2, 3 veya 4): ").strip()
            
            if menu_choice == "2":
                show_group_members(group_id)
                continue
            
            if menu_choice == "3":
                show_group_restaurant(group_id)
                continue
            
            if menu_choice == "4":
                break
            
            if menu_choice != "1":
                print("❌ Geçersiz seçim!")
                continue
            
            person_name = input("\n🛒 Siparış veren kişinin adı (veya Kendi adını yazın): ").strip()
            
            if not person_name:
                continue
            
            if person_name not in group_members:
                group_members[person_name] = []
            
            print(f"\n{person_name} için ürün seçin (kategoriye göre):")
            
            # Ürün seçimi
            select_items_for_person(restaurant, group_members[person_name], person_name)
    
    else:
        # Bireysel sipariş
        print(f"\n🛒 SİPARİŞ ALMAK İSTEYEN KİŞİ: {your_name}")
        select_items_for_person(restaurant, group_members[your_name], your_name)
    
    # Siparışları göster ve hesapla
    show_orders_and_split(group_members, group_id)

if __name__ == "__main__":
    main()
