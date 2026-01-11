# Database Synchronization Instructions

## Local Development Database (SQLite)
- Location: `backend/instance/hesap_paylas.db`
- Status: ✅ Synced with test data

## Production Database (Render PostgreSQL)

### To sync production database with local test data:

1. **Via Render Dashboard:**
   - Go to https://dashboard.render.com
   - Select your PostgreSQL database
   - Click "Connect" → Copy "External Database URL"
   - Use it with this Python script:

```bash
# Set DATABASE_URL environment variable (optional)
set DATABASE_URL=postgresql://user:pass@host/dbname

# Run seed script against production database
python seed_database.py
```

2. **Via GitHub Actions (Automated):**
   - Add `.github/workflows/seed-db.yml` to auto-seed on deployment
   - Currently manual approach is recommended

### Current Test Data:

**User:**
- Email: metonline@gmail.com
- Password: test123

**Groups:**
- Arkadaşlar (code: 471056)
- Aile (code: 031655)  
- İş (code: 495661)

### To manually sync:

1. Get Render PostgreSQL connection string from dashboard
2. Update `.env` file with `DATABASE_URL`
3. Run: `python seed_database.py`

### Warnings:
- ⚠️ Only seed production if you're sure you want to overwrite existing data
- Test in local environment first
- Keep backups of production data
