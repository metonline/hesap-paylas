# Hesap Paylaş 💰

Hızlı ve adil hesap bölüştürme uygulaması. Restoran, seyahat ve ortak ev harcamalarını kolayca paylaşın.

![Hesap / Paylaş](docs/header.png)

## 📌 Önemli: Database Senkronizasyonu

Lokal SQLite ve Render PostgreSQL'i senkronize ederek veri kaybı olmadan çalışın:

```bash
# Durumu kontrol et
python sync_databases.py status

# Lokal → Render taşı
python sync_databases.py local2render

# Hızlı başlangıç
python sync_databases.py status && python sync_databases.py local2render
```

👉 **Detaylı rehber:** [DATABASE_SYNC_GUIDE.md](DATABASE_SYNC_GUIDE.md) | [Hızlı Başlangıç](DATABASE_QUICKSTART.md)

---

## Features ✨

- 🍽️ **Restoran Paylaşması** - Grup olarak sipariş verin, adil şekilde bölüştürün
- ✈️ **Seyahat Harcamaları** - Ortak tatilinizin masraflarını takip edin
- 🏠 **Ev Harcamaları** - Ortak yaşayanlarla harcamaları paylaşın
- 📱 **Mobile-First** - PWA teknolojisi ile offline çalışır
- 👥 **QR Code** - Grup arkadaşlarını kolayca davet edin
- 💳 **Güvenli Ödeme** - Kredi kartı integrasyonu
- 🎟️ **Kupon & Promosyon** - Üyelik avantajlarından yararlanın
- 🔄 **Database Senkronizasyon** - Lokal ve Render veritabanları otomatik senkronize

## Stack 🛠️

- **Frontend**: HTML5, CSS3, Vanilla JavaScript, PWA
- **Backend**: Python Flask, PostgreSQL, SQLAlchemy
- **Deployment**: Render (PostgreSQL), GitHub Pages
- **APIs**: Stripe, Google/Facebook OAuth
- **Tools**: GitHub Actions, Docker, Database Sync Script
- **Database**: SQLite (lokal), PostgreSQL (production)

## Quick Start 🚀

### Local Development

```bash
# Clone repo
git clone https://github.com/hesappaylas/hesap-paylas.git
cd hesap-paylas

# Python backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Check database status
python sync_databases.py status

# Start development
python dev_server.py
# or
python backend/app.py
```

### Database Setup (Before Deploy)

```bash
# 1. Render PostgreSQL oluştur
#    https://dashboard.render.com → New → PostgreSQL

# 2. .env'ye DATABASE_URL ekle
#    RENDER_DATABASE_URL=postgresql://...

# 3. Senkronize et
python sync_databases.py status
python sync_databases.py local2render

# 4. Deploy
git push origin main
```

### Installation (Mobile)

1. `https://metonline.github.io` adresine gidin
2. Share/Menu → "Add to Home Screen" seçin
3. Uygulama masaüstünüze kurulacak

## Usage 📖

### Grup Oluşturma
1. "Grup Modu" seçin
2. QR kod taratarak arkadaşlarınızı davet edin
3. Restoran seçin

### Hesap Bölüştürme
1. Sipariş oluşturun
2. Kimin ne aldığını ekleyin
3. Vergi & teslimat otomatik bölüştürülür
4. Paylaş butonuyla WhatsApp/SMS ile gönderin

## Architecture 📐

```
hesap-paylas/
├── frontend/
│   ├── index.html
│   ├── styles.css
│   ├── script.js
│   └── manifest.json
├── backend/
│   ├── app.py (Flask)
│   ├── models.py
│   ├── routes/
│   └── utils/
├── docs/
├── .github/
│   └── workflows/
├── Procfile
├── requirements.txt
├── sync_databases.py
├── DATABASE_SYNC_GUIDE.md
├── DATABASE_QUICKSTART.md
├── DATABASE_SYNC_SUMMARY.md
└── README.md
```

## 📚 Rehberler

| Rehber | Açıklama |
|--------|----------|
| [DATABASE_QUICKSTART.md](DATABASE_QUICKSTART.md) | 5 dakika kurulum |
| [DATABASE_SYNC_GUIDE.md](DATABASE_SYNC_GUIDE.md) | Detaylı database rehberi |
| [DATABASE_SYNC_SUMMARY.md](DATABASE_SYNC_SUMMARY.md) | Senkronizasyon özeti |
| [RENDER_DEPLOYMENT.md](RENDER_DEPLOYMENT.md) | Render deployment |
| [LOCAL_DEVELOPMENT.md](LOCAL_DEVELOPMENT.md) | Lokal geliştirme |

## API Endpoints (TBD)

```
POST   /api/auth/signup
POST   /api/auth/login
GET    /api/user/profile
POST   /api/groups
POST   /api/orders
GET    /api/orders/:id
POST   /api/payments
```

## Contributing 🤝

1. Fork repo
2. Feature branch oluştur (`git checkout -b feature/amazing-feature`)
3. Commit et (`git commit -m 'Add amazing feature'`)
4. Push et (`git push origin feature/amazing-feature`)
5. Pull Request aç

## Roadmap 🗺️

- [ ] Backend API (Flask + PostgreSQL)
- [ ] Real Google/Facebook OAuth
- [ ] Stripe payment integration
- [ ] Restaurant menu API integration
- [ ] QR code scanning
- [ ] SMS/WhatsApp integration
- [ ] Analytics dashboard
- [ ] iOS/Android native apps

## License 📝

MIT License - see LICENSE file

## Contact 📧

- GitHub: [@hesappaylas](https://github.com/hesappaylas)
- Email: info@hesappaylas.com

---

Made with ❤️ for fair bill splitting
