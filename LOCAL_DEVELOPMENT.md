# Local Development Guide

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Start Backend API

The backend runs on SQLite by default in development mode:

```bash
python backend/app.py
```

API will be available at: `http://localhost:5000`

**Health Check:**
```bash
curl http://localhost:5000/api/health
```

### 3. Start Frontend (in another terminal)

```bash
python -m http.server 8000
```

Frontend will be available at: `http://localhost:8000`

---

## API Endpoints (Local Testing)

### Authentication

**Signup:**
```bash
curl -X POST http://localhost:5000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "firstName": "Ahmet",
    "lastName": "Yilmaz",
    "email": "ahmet@example.com",
    "password": "secure123",
    "phone": "5501234567"
  }'
```

**Response:**
```json
{
  "message": "User created successfully",
  "user": {
    "id": 1,
    "first_name": "Ahmet",
    "last_name": "Yilmaz",
    "email": "ahmet@example.com",
    "phone": "5501234567",
    "bonus_points": 0
  },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Login:**
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "ahmet@example.com",
    "password": "secure123"
  }'
```

### Protected Endpoints (Requires Authorization Header)

**Get Profile:**
```bash
TOKEN="your_jwt_token_from_signup"
curl -X GET http://localhost:5000/api/user/profile \
  -H "Authorization: Bearer $TOKEN"
```

---

## Database

Development uses SQLite at `hesap_paylas.db` (auto-created on first run).

### Reset Database

```bash
rm hesap_paylas.db
python backend/app.py  # This will recreate the database
```

---

## Frontend Testing

1. Go to `http://localhost:8000`
2. Click "Üye Ol" (Signup)
3. Fill in the form:
   - Ad: Ahmet
   - Soyad: Yilmaz
   - Telefon: 0541234567
   - E-posta: ahmet@example.com
   - Şifre: MyPassword123

4. Submit - you'll be registered with the backend API
5. Token will be saved to LocalStorage
6. You'll be redirected to home page

---

## Troubleshooting

### Port Already in Use

If port 5000 is already in use:
```bash
# Kill the existing process
lsof -ti :5000 | xargs kill -9  # macOS/Linux
taskkill /F /IM python.exe      # Windows (then restart)

# Or use a different port
PORT=5001 python backend/app.py
```

### CORS Issues

If you get CORS errors, make sure:
1. Frontend is on `http://localhost:8000`
2. Backend is on `http://localhost:5000`
3. API base URL in `script.js` is set to `http://localhost:5000/api`

### Import Errors

Make sure you've installed requirements:
```bash
pip install -r requirements.txt
```

---

## Next Steps

1. **Test Signup/Login** - Create a new user account
2. **Create Groups** - Test group creation API
3. **Add Orders** - Test order creation and bill splitting
4. **Deploy to Heroku** - Follow HEROKU_SETUP.md
5. **Enable GitHub Pages** - Frontend auto-deploy
