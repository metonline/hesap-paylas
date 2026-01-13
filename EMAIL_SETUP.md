# 📧 EMAIL-BASED PASSWORD RESET SETUP

## Overview
Users will now:
1. Login with phone + 4-digit PIN
2. After login, they'll be prompted to add their email
3. To reset PIN, they receive a 6-digit code via email (not SMS)

## No More Twilio Needed!
This approach uses **Gmail SMTP** instead of Twilio, so no expensive phone numbers.

---

## Gmail Setup (FREE)

### Step 1: Create Gmail Account or Use Existing One
- You need a Gmail address (e.g., `hesappaylas.noreply@gmail.com`)
- OR use your personal Gmail if testing

### Step 2: Generate App Password
1. Go to: https://myaccount.google.com/security
2. Enable **2-Factor Authentication** first if not enabled
3. Go to **App Passwords** (appears after 2FA is enabled)
4. Select **Mail** and **Other (custom name)**
5. Google gives you a 16-character password (example: `abcd efgh ijkl mnop`)
6. Save this password

### Step 3: Update .env File

Add these lines to `.env`:

```env
# Email Configuration for Password Reset
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=hesappaylas.noreply@gmail.com
SENDER_PASSWORD=abcd efgh ijkl mnop
```

**Replace:**
- `hesappaylas.noreply@gmail.com` with your actual Gmail
- `abcd efgh ijkl mnop` with your app password (without spaces)

---

## How It Works

### User Flow:
1. User logs in: Phone (5323133277) + PIN (1234)
2. Backend returns: `"needs_email": true`
3. Frontend shows **"Add Your Email"** modal
4. User enters email: john@gmail.com
5. `POST /api/user/add-email` saves the email
6. Frontend shows "Email saved! ✅"

### PIN Reset Flow:
1. User clicks "Şifremi Unuttum" (Forgot Password)
2. Enters their phone number
3. System **sends 6-digit code to their email**
4. User receives email with code
5. User enters code and new 4-digit PIN
6. Done! Can login with new PIN

---

## Email Template

Users will see an email like:

```
🥄 Hesap Paylaş

Merhaba John!

PIN kodunuzu sıfırlamak için aşağıdaki kodu kullanabilirsiniz:

┌─────────────┐
│  3 4 7 8 2 1  │
└─────────────┘

Bu kod 10 dakika geçerlidir

⚠️ Güvenlik Uyarısı: Bu kodu kimseyle paylaşmayın!
```

---

## Testing Locally

1. Update your local `.env`:
```bash
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your-app-password
```

2. Run backend:
```bash
python backend/app.py
```

3. Test PIN reset flow via frontend

---

## Deployment (PythonAnywhere)

1. Add same environment variables to PythonAnywhere
2. Go to **Web** tab → Scroll down to **Environment variables**
3. Add:
   - `SMTP_SERVER`: smtp.gmail.com
   - `SMTP_PORT`: 587
   - `SENDER_EMAIL`: your-email@gmail.com
   - `SENDER_PASSWORD`: your-app-password

4. Reload web app

---

## Alternative Email Providers

Instead of Gmail, you can use:

### SendGrid (Recommended for Production)
```env
SMTP_SERVER=smtp.sendgrid.net
SMTP_PORT=587
SENDER_EMAIL=apikey
SENDER_PASSWORD=SG.xxx...
```
- Free tier: 100 emails/day
- Sign up: https://sendgrid.com

### Mailgun
```env
SMTP_SERVER=smtp.mailgun.org
SMTP_PORT=587
SENDER_EMAIL=your-email@your-domain.com
SENDER_PASSWORD=your-mailgun-password
```

---

## Troubleshooting

### "Email not configured"
- `.env` is missing `SMTP_SERVER`, `SMTP_PORT`, `SENDER_EMAIL`, or `SENDER_PASSWORD`
- Check that all 4 variables are set

### "Authentication failed"
- Check Gmail app password is correct (without spaces)
- Make sure 2FA is enabled on Gmail

### "Email not received"
- Check spam folder
- Verify sender email address is correct
- Check that user phone has a valid email in database

### "Invalid email format"
- User entered invalid email (missing @ or domain)
- Show error message to user

---

## Cost
- Gmail: FREE ✅
- SendGrid: FREE (100 emails/day) or $10/month for more
- Mailgun: FREE (600 emails/month) or paid tiers

Much cheaper than Twilio SMS! 🎉
