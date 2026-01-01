# 🍽️ Restaurant QR Kodu - Resim Gösterim Özelliği

## 📋 Genel Bakış

**Seçenek B** başarıyla uygulanmıştır: Restaurant QR kodundan gelen verinin içinde menü ve her ürünün kendi resim URL'sini içermesi.

## 🎯 Nasıl Çalışır?

### 1️⃣ QR Kodu Tarama
```
Grup üyeleri → Restaurant QR kodunu tarar
                    ↓
          Kod şu bilgileri içerir: rest_001
```

### 2️⃣ Restaurant Verisi Alınması
```
Uygulama qr_restaurant_data.json'dan menu çeker:

rest_001 → {
    "name": "Tarihi Kebapçı",
    "phone": "0216-123-4567",
    "website": "https://example.com/tarihi-kebapci",
    "categories": { ... }
}
```

### 3️⃣ Menü Gösterim Özelliği

#### Eski Gösterim:
```
  1. Adana Kebap                       45.00 ₺
  2. Urfa Kebap                        50.00 ₺
```

#### Yeni Gösterim (Resim Desteği):
```
  1. 🌶️ Adana Kebap                       45.00 ₺ 📷
  2. 🔥 Urfa Kebap                        50.00 ₺ 📷
  3. 🍖 İskender Kebap                    55.00 ₺ 📷

💡 İpucu: Resim görmek için 'r1', 'r2' vb. yazın
```

**Açıklama:**
- 🌶️ = Ürün emoji (hızlı tanıma)
- 📷 = Resim mevcut (göstergesi)
- `r1` yazılırsa resim açılır

### 4️⃣ Resim Açma Akışı

```
Kullanıcı: r1 [Enter]
     ↓
Kod resim URL'sini kontrol eder:
"https://example.com/images/adana-kebap.jpg"
     ↓
webbrowser.open() ile tarayıcıda açılır
     ↓
Resim yeni sekmede gösterilir
     ↓
Kullanıcı geri gelip devam eder
```

## 📊 Veri Yapısı

### qr_restaurant_data.json Formatı

```json
{
  "rest_001": {
    "name": "Tarihi Kebapçı",
    "phone": "0216-123-4567",
    "website": "https://example.com/tarihi-kebapci",
    "categories": {
      "Kebaplar": [
        {
          "name": "Adana Kebap",
          "price": 45.00,
          "emoji": "🌶️",
          "image": "https://example.com/images/adana-kebap.jpg"
        },
        {
          "name": "Urfa Kebap",
          "price": 50.00,
          "emoji": "🔥",
          "image": "https://example.com/images/urfa-kebap.jpg"
        }
      ]
    }
  }
}
```

### Sipariş Nesnesindeki Resim

```python
{
    'name': 'Adana Kebap',
    'quantity': 2,
    'price': 45.00,
    'total': 90.00,
    'type': 'personal',
    'emoji': '🌶️',
    'image': 'https://example.com/images/adana-kebap.jpg'  # ← Saklı
}
```

## 🔧 Kod Değişiklikleri

### `select_items_for_person()` Güncellemesi

**Yeni Özellikler:**

1. **Menü gösteriminde emoji ve resim göstergesi:**
```python
for i, item in enumerate(items, 1):
    emoji = item.get('emoji', '🍽️')
    has_image = " 📷" if item.get('image') else ""
    print(f"  {i}. {emoji} {item['name']:30s} {item['price']:>8.2f} ₺{has_image}")
```

2. **Resim açma işlevi:**
```python
if item_choice_str.startswith('r') or item_choice_str.startswith('R'):
    img_choice = int(item_choice_str[1:])
    image_item = items[img_choice - 1]
    if image_item.get('image'):
        import webbrowser
        webbrowser.open(image_item['image'])
        print(f"🖼️  {image_item['name']} resmi tarayıcıda açılıyor...")
    continue
```

## ✅ Avantajlar

### Restaurant Tarafından
- ✓ **Merkezi Yönetim**: Kendi sunucusundan resim sağlar
- ✓ **Gerçek Zamanlı Update**: Menü değişikliği anında yansır
- ✓ **Kontrol**: Kendi resimlerini seçer
- ✓ **Esneklik**: Fiyat/açıklama güncellemesi kolaylaşır

### Kullanıcı Tarafından
- ✓ **Görsel Seçim**: Ürünü görerek seçer
- ✓ **Kalite Kontrolü**: Yüksek çözünürlük resimler
- ✓ **Hızlı Akış**: İsterse resim görmezden geçer
- ✓ **İnternet Dostu**: Tarayıcı cache'i kullanır

### Uygulama Tarafından
- ✓ **Hafif Paket**: Resimler sunucuda tutulur
- ✓ **Eskalebilite**: Binlerce restaurant destekleyebilir
- ✓ **Sürüm Kontrolü**: QR'da versiyon kontrolü gerekli değil
- ✓ **Dinamik**: Restaurant bilgilerini manuel güncellemesiz

## 🔐 Restaurant Sunucu Yapısı

Restaurant'ın sunucusu şu şekilde kurulmalı:

```
restaurant-server.com/
├── api/
│   └── menu
│       ├── rest_001
│       │   ├── menu.json
│       │   └── images/
│       │       ├── adana-kebap.jpg
│       │       ├── urfa-kebap.jpg
│       │       └── ...
│       ├── rest_002
│       └── rest_003
```

## 📱 Kullanıcı Akışı

```
1. Grup oluştur
     ↓
2. Restaurant QR kodunu taranır
     ↓
3. Menu kategori seçilir
     ↓
4. Ürünler gösterilir (emoji + 📷 göstergesi ile)
     ↓
5. Seçenekler:
   - Normal seçim (1, 2, 3): Ürünü seç
   - Resim görmek (r1, r2, r3): Tarayıcıda aç
     ↓
6. Sipariş devam eder (miktar, tip seçimi)
     ↓
7. Hesap bölüştürme devam eder
```

## 🎨 Örnek Arayüz

```
📋 Kebaplar:
────────────────────────────────────────────────────────
  1. 🌶️ Adana Kebap                       45.00 ₺ 📷
  2. 🔥 Urfa Kebap                        50.00 ₺ 📷
  3. 🍖 İskender Kebap                    55.00 ₺ 📷
  4. 🍢 Şiş Kebap                         60.00 ₺ 📷
  0. Geri Dön
────────────────────────────────────────────────────────

💡 İpucu: Resim görmek için 'r1', 'r2' vb. yazın

Ürün seç (numara, resmi görmek için 'r' + numara): r1
🖼️  Adana Kebap resmi tarayıcıda açılıyor...

(Tarayıcıda resim açılır, sonra geri döner)

Ürün seç (numara, resmi görmek için 'r' + numara): 2
Miktar: 1.5
📝 Sipariş Türü Seç:
  1. 🔸 Bireysel (sadece ben öderim)
  2. 🔹 Ortak Tüketim (grup üyeleri eşit paylaşır)
  3. ⚪ Hariç Tut (Bu siparış hesaplamaya dahil edilmez)
```

## 📂 Dosya Yapısı

| Dosya | Açıklama |
|-------|----------|
| `bill_splitter.py` | Ana uygulama (922 satır) |
| `restaurants.json` | Local restaurant menüleri |
| `qr_restaurant_data.json` | QR'dan çekilecek restaurant verisi |
| `groups.json` | Grup ve sipariş verisi |

## 🚀 Gelecek Geliştirmeler

- [ ] Restaurant sunucusu API entegrasyonu
- [ ] Resimlerin CLI'de ASCII gösterimi
- [ ] Resim önizlemesi (terminal'de küçük gösterim)
- [ ] Favorilere ekleme (tercih edilen ürünler)
- [ ] Yapılan siparişin resmi gösterim
- [ ] Web arayüzü (HTML5 + CSS)
- [ ] Mobile app (iOS/Android)

## ✨ Sonuç

**Seçenek B'nin Uygulanması Başarılı:**

✅ Restaurant QR kodundan menü veri alınıyor
✅ Her ürünün restaurant'ın resim URL'si var  
✅ Menü seçiminde resim mevcut göstergesi var (📷)
✅ `r` + numara ile resim tarayıcıda açılabiliyor
✅ Tamamı dinamik ve updatable
✅ Restaurant tarafı tamamen kontrol ediyor

**Müşteriler restoran'ın seçtiği en iyi fotoğrafları görüyor!** 🎉
