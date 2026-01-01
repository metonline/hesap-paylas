# 🍽️ Restaurant Bill Splitter - Görsel İyileştirmeler

## ✅ Tamamlanan Özelliker

### 1. **Menü Seçiminde Ürün Emojileri**
- Menü kategorileri gösterilirken her ürün yanında emoji gösterilir
- Örnek: `🌶️ Adana Kebap    45.00 ₺`
- Örnek: `🥗 Çoban Salatası  20.00 ₺`

### 2. **Siparış Listesinde Vizüel İyileştirmeler**
Siparişler şu formatta gösterilir:
```
👤 Ahmet Yilmaz:
   1. 🌶️ 🔸 Bireysel Adana Kebap          x2.0 @ 45.00 ₺ = 90.00 ₺
   2. 🥛 🔹 Ortak    Ayran                x1.0 @  8.00 ₺ =  8.00 ₺
```

**Anlamı:**
- 🌶️ = Ürün görseli (emoji)
- 🔸 = Bireysel ödeme
- 🔹 = Ortak tüketim
- Ürün adı + Adet + Fiyat + Toplam

### 3. **Restoran'a Gönderilen Format**
Restoran bilgilendirilmesi sırasında emojiler yer alır:
```
GRUP SİPARİŞ - #GRP-001
👤 Ahmet Yilmaz:
  🔸 🌶️ Adana Kebap x2 = 90.00₺
  🔹 🥛 Ayran x1 = 8.00₺
```

### 4. **Veri Yapısı İyileştirmeleri**

#### restaurants.json
Tüm ürünler şu alanlara sahip:
```json
{
  "name": "Adana Kebap",
  "price": 45.00,
  "emoji": "🌶️",
  "image": "https://via.placeholder.com/150?text=Adana+Kebap"
}
```

#### Sipariş Nesneleri (Order Objects)
```python
{
  'name': 'Adana Kebap',
  'quantity': 2,
  'price': 45.00,
  'total': 90.00,
  'type': 'personal',              # 'personal' | 'shared' | 'excluded'
  'emoji': '🌶️',                   # Ürün görseli
  'image': 'https://...'            # Ürün resim URL'si
}
```

## 🎨 Emojiler ve Kategoriler

### Kebap Restoranı (Tarihi Kebapçı)
- 🌶️ Adana Kebap
- 🔥 Urfa Kebap
- 🍖 İskender Kebap
- 🍢 Şiş Kebap

### Mezeler
- 🥜 Hummus
- 🍆 Baba Ganoush
- 🥒 Tzatziki
- 🥬 Yaprak Sarma

### Salatalar
- 🥗 Çoban Salatası
- 🥬 Yeşil Salata
- 🥒 Turşu Salatası

### İçecekler
- 🥛 Ayran
- 🍵 Çay
- 🥤 Kola
- 🍊 Portakal Suyu

### Modern Türk Mutfağı
- 🍯 Baklava
- 🧡 Künefe
- 🥣 Sütlaç
- 🍰 Cheesecake
- 🐟 Balık Pilaü
- 🐠 Levrek Griyeli

### Pizza Restoranı
- 🍕 Margarita Pizza
- 🍕 Pepperoni Pizza
- 🌶️ Spicy Pizza
- 🍝 Makarna Carbonara

## 📝 Değiştirilen Fonksiyonlar

### 1. `select_items_for_person()`
**Öncesi:**
```python
for i, item in enumerate(items, 1):
    print(f"  {i}. {item['name']:30s} {item['price']:>8.2f} ₺")
```

**Sonrası:**
```python
for i, item in enumerate(items, 1):
    emoji = item.get('emoji', '🍽️')
    print(f"  {i}. {emoji} {item['name']:30s} {item['price']:>8.2f} ₺")
```

Ayrıca siparış objesine emoji ve image eklendi:
```python
person_orders.append({
    'name': selected_item['name'],
    'quantity': quantity,
    'price': selected_item['price'],
    'total': item_total,
    'type': order_type,
    'emoji': selected_item.get('emoji', '🍽️'),
    'image': selected_item.get('image', '')
})
```

### 2. `show_orders_and_split()`
Siparış gösteriminde emoji eklendi:
```python
emoji = order.get('emoji', '🍽️')
print(f"   {i}. {emoji} {type_label} {order['name']:20s} x{order['quantity']:>5.1f} @ {order['price']:>8.2f} ₺ = {order['total']:>10.2f} ₺")
```

### 3. `format_order_for_restaurant()`
Restoran mesajında emoji eklendi:
```python
product_emoji = order.get('emoji', '🍽️')
message += f"  {type_emoji} {product_emoji} {order['name']} x{order['quantity']} = {order['total']:.2f}₺\n"
```

## 🚀 Özellik Geçmişi

| Aşama | Başlık | Durum |
|-------|--------|-------|
| 1 | Temel Hesap Bölüştürme | ✅ Tamamlandı |
| 2 | Grup Yönetimi & QR Kodları | ✅ Tamamlandı |
| 3 | Restaurant Menüsü Entegrasyonu | ✅ Tamamlandı |
| 4 | Üye Yönetimi (İsim/Soyad) | ✅ Tamamlandı |
| 5 | Paylaşılan vs Bireysel Harcamalar | ✅ Tamamlandı |
| 6 | Orantılı Bahşiş/Vergi | ✅ Tamamlandı |
| 7 | Restaurant Bilgilendirme (SMS/WhatsApp/Email) | ✅ Tamamlandı |
| 8 | **Görsel İyileştirmeler (Emojiler & Görseller)** | ✅ **Tamamlandı** |

## 🔮 Gelecek Geliştirmeler

### Planlanan Özellikler
- [ ] Terminal tabanlı resim gösterim (ASCII art)
- [ ] Web arayüzü (Flask/Django)
- [ ] Mobile uygulama
- [ ] Veritabanı entegrasyonu (PostgreSQL)
- [ ] Ödeme sistemi entegrasyonu
- [ ] Kullanıcı hesapları

### Pazarlama Stratejisi
1. **B2C (Tüketici)** - Mobil uygulama
2. **B2B (Restaurant)** - POS sistemi entegrasyonu
3. **Kurumsal** - Şirket etkinlikleri için

## 📂 Dosyalar

| Dosya | Açıklama |
|-------|----------|
| `bill_splitter.py` | Ana uygulama (894 satır) |
| `restaurants.json` | Restaurant menü verileri |
| `groups.json` | Grup ve sipariş verileri |
| `test_visual.py` | Görsel özelliklerin test dosyası |

## ✨ Sonuç

Restaurant hesap bölüştürme uygulaması artık:
- ✅ Menülerde ürün emojileri gösterir
- ✅ Siparişlerde görsel gösterimi yapır
- ✅ Restoran'a gönderilen mesajlarda emoji kullanır
- ✅ Her ürün için resim URL'si depolanır (gelecekte web/mobile için)
- ✅ Tüm görsel iyileştirmeler CLI ortamında çalışır

Uygulama tamamı ile fonksiyonel ve kullanıma hazırdır! 🎉
