# Hesap Paylaş 💰

Hızlı ve adil hesap bölüştürme uygulaması. Restoran, seyahat ve ortak ev harcamalarını kolayca paylaşın.

![Hesap / Paylaş](docs/header.png)

## Features ✨

- 🍽️ **Restoran Paylaşması** - Grup olarak sipariş verin, adil şekilde bölüştürün
- ✈️ **Seyahat Harcamaları** - Ortak tatilinizin masraflarını takip edin
- 🏠 **Ev Harcamaları** - Ortak yaşayanlarla harcamaları paylaşın
- 📱 **Mobile-First** - PWA teknolojisi ile offline çalışır
- 👥 **QR Code** - Grup arkadaşlarını kolayca davet edin
- 💳 **Güvenli Ödeme** - Kredi kartı integrasyonu
- 🎟️ **Kupon & Promosyon** - Üyelik avantajlarından yararlanın

## Stack 🛠️

- **Frontend**: HTML5, CSS3, Vanilla JavaScript, PWA
- **Backend**: Python Flask, PostgreSQL
- **Deployment**: Heroku, GitHub Pages
- **APIs**: Stripe, Google/Facebook OAuth
- **Tools**: GitHub Actions, Docker

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
python app.py

# Frontend
# http://localhost:5000 or http://localhost:8000
```

### Installation (Mobile)

1. `https://hesappaylas.herokuapp.com` adresine gidin
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
└── README.md
```

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
