# 🔧 Run Migration on PythonAnywhere

The production database is missing the `email_verified` column. Follow these steps:

## Step 1: Upload Migration Script
```bash
git add migrate_pythonanywhere.py
git commit -m "Add PythonAnywhere migration script"
git push
```

## Step 2: SSH into PythonAnywhere
1. Go to https://www.pythonanywhere.com/user/metonline/account
2. Click **Account** tab
3. Scroll to **SSH key**
4. Copy the SSH command
5. Open terminal and paste it

## Step 3: Run Migration
Once SSH connected:
```bash
cd ~/mysite
python migrate_pythonanywhere.py
```

Expected output:
```
📦 Database: /home/metonline/mysite/backend/instance/hesap_paylas.db
============================================================
➕ Adding email_verified column...
✅ email_verified column added successfully

📋 Users table columns:
   ✓ id
   ✓ first_name
   ...
   ✓ email_verified
   ✓ is_active

✅ Migration completed successfully!
⚠️  Restart PythonAnywhere web app after this!
```

## Step 4: Reload Web App
1. Go to https://www.pythonanywhere.com/user/metonline/webapps
2. Click your web app
3. Click the **Reload** button (green)

## ✅ Done!
The production database should now have the `email_verified` column and all PIN reset/email features will work!
