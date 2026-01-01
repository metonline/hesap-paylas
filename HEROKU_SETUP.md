# Heroku Deployment Guide

## 1. Heroku CLI Kur
```bash
# Windows
choco install heroku-cli

# macOS
brew tap heroku/brew && brew install heroku

# Verify
heroku --version
```

## 2. Heroku Account Oluştur
- https://signup.heroku.com
- Email doğrula

## 3. GitHub Secrets Ayarla

GitHub repo settings → Secrets and variables → Actions

**Ekle:**

### HEROKU_API_KEY
1. https://dashboard.heroku.com/account/applications/authorizations git
2. Create authorization
3. Token'i kopyala
4. GitHub Secret olarak ekle: `HEROKU_API_KEY`

### HEROKU_EMAIL
- Heroku account email'in

### SLACK_WEBHOOK (Optional)
- https://api.slack.com/messaging/webhooks
- Heroku deployment notifications için

## 4. Heroku App Oluştur

```bash
heroku login
heroku create hesap-paylas-api

# PostgreSQL ekle
heroku addons:create heroku-postgresql:hobby-dev -a hesap-paylas-api

# Config vars ayarla
heroku config:set SECRET_KEY=your-secret-key-here -a hesap-paylas-api
heroku config:set JWT_SECRET=your-jwt-secret-here -a hesap-paylas-api
heroku config:set FLASK_ENV=production -a hesap-paylas-api
```

## 5. Deploy

### Manual Deploy
```bash
git push heroku main
```

### Automatic Deploy
- https://dashboard.heroku.com/apps/hesap-paylas-api/deploy
- GitHub seçin
- metonline/hesap-paylas repo seçin
- Enable Automatic Deploys

## 6. Database Migration

```bash
heroku run python -a hesap-paylas-api
>>> from backend.app import db
>>> db.create_all()
>>> exit()
```

## 7. Logs

```bash
# Real-time logs
heroku logs --tail -a hesap-paylas-api

# Error logs
heroku logs --ps web -a hesap-paylas-api

# Database logs
heroku pg:logs -a hesap-paylas-api
```

## 8. Environment Variables

```bash
# View all
heroku config -a hesap-paylas-api

# Add/Update
heroku config:set KEY=value -a hesap-paylas-api

# Remove
heroku config:unset KEY -a hesap-paylas-api
```

## 9. App Status

```bash
# Open app
heroku open -a hesap-paylas-api

# Dyno status
heroku ps -a hesap-paylas-api

# Resource usage
heroku metrics -a hesap-paylas-api
```

## 10. Database Backup

```bash
# Create backup
heroku pg:backups:capture -a hesap-paylas-api

# List backups
heroku pg:backups:info -a hesap-paylas-api

# Download backup
heroku pg:backups:download -a hesap-paylas-api
```

## Troubleshooting

### App not starting
```bash
heroku logs -a hesap-paylas-api
heroku restart -a hesap-paylas-api
```

### Database connection error
```bash
heroku config -a hesap-paylas-api
heroku pg:reset DATABASE -a hesap-paylas-api  # ⚠️ Destructive
```

### Scale workers
```bash
heroku ps:scale web=2 -a hesap-paylas-api
heroku ps:scale web=1 -a hesap-paylas-api  # Scale down
```

### Restart app
```bash
heroku restart -a hesap-paylas-api
```

## Cost & Limits (Free Tier)

- **Dyno Hours**: 1000 free/month
- **Database**: 10k row limit
- **Uptime**: ~99.95%

⚠️ **Not recommended for production** - upgrade to paid dyno

## API Health Check

```bash
curl https://hesap-paylas-api.herokuapp.com/api/health
```

## Custom Domain (Optional)

```bash
# Add domain
heroku domains:add yourdomain.com -a hesap-paylas-api

# Check DNS setup
heroku domains -a hesap-paylas-api
```

---

🎉 **Live App**: https://hesap-paylas-api.herokuapp.com
📊 **Dashboard**: https://dashboard.heroku.com/apps/hesap-paylas-api
