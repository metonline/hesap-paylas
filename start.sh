#!/bin/bash
# Render startup script
# 1. Install dependencies
# 2. Seed database
# 3. Start Gunicorn

echo "📦 Installing dependencies..."
pip install -r requirements.txt

echo "🌱 Seeding database..."
python seed_render.py || {
    echo "⚠️ Seed script failed, but continuing with Gunicorn..."
    echo "Database may be already seeded or will be created on first request"
}

echo "🚀 Starting Gunicorn..."
gunicorn --bind 0.0.0.0:$PORT wsgi:application
