# Hesap Paylaş - Deployment Guide

## GitHub Setup

```bash
# Initialize git repo
git init
git add .
git commit -m "Initial commit: PWA app with Flask backend"

# Add remote (replace hesappaylas with your username)
git remote add origin https://github.com/hesappaylas/hesap-paylas.git
git branch -M main
git push -u origin main
```

## Heroku Deployment

### 1. Create Heroku Account
- https://signup.heroku.com

### 2. Install Heroku CLI
```bash
# Windows: Download from https://devcenter.heroku.com/articles/heroku-cli
# or use chocolatey:
choco install heroku-cli

# Verify
heroku --version
```

### 3. Login to Heroku
```bash
heroku login
```

### 4. Create Heroku App
```bash
heroku create hesap-paylas
```

### 5. Set Environment Variables
```bash
heroku config:set SECRET_KEY=your-secret-key-here
heroku config:set FLASK_ENV=production
heroku config:set DATABASE_URL=postgres://...  # (if using database)
```

### 6. Deploy
```bash
git push heroku main
```

### 7. View Logs
```bash
heroku logs --tail
```

## GitHub Actions CI/CD

### 1. Add Heroku Secrets
Go to: GitHub → Settings → Secrets and variables → Actions

Add:
- `HEROKU_API_KEY`: Get from https://dashboard.heroku.com/account/applications/authorizations
- `HEROKU_EMAIL`: Your Heroku account email
- `SLACK_WEBHOOK` (optional): For Slack notifications

### 2. Automatic Deployment
Every push to `main` branch will:
1. Run tests
2. Build application
3. Deploy to Heroku
4. Send Slack notification

## Domain Setup (Optional)

### Custom Domain
```bash
heroku domains:add yourdomain.com
```

### GitHub Pages (Frontend only)
- Push to `gh-pages` branch for GitHub Pages
- Or configure in repository settings

## Monitoring

### Heroku Logs
```bash
heroku logs --tail
heroku logs --dyno=web
heroku logs --dyno=worker
```

### Heroku Metrics
```bash
heroku metrics
```

### App Status
```bash
heroku status
```

## Useful Commands

```bash
# View app info
heroku apps:info

# Run command on Heroku
heroku run python

# Scale dynos
heroku ps:scale web=2

# Restart app
heroku restart

# Open app
heroku open

# View config vars
heroku config

# Remove app
heroku apps:destroy --app hesap-paylas
```

## Troubleshooting

### App not starting
```bash
heroku logs --tail
heroku events
```

### Database issues
```bash
heroku addons:create heroku-postgresql:hobby-dev
heroku config
```

### Clear cache & rebuild
```bash
git commit --allow-empty -m "Rebuild"
git push heroku main
```

## Next Steps

1. ✅ GitHub + Heroku setup
2. [ ] Database (PostgreSQL)
3. [ ] User authentication (JWT)
4. [ ] Restaurant API integration
5. [ ] Payment processing (Stripe)
6. [ ] Mobile app builds (React Native)
