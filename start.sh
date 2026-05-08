#!/bin/bash
# Render startup script
# 1. Install dependencies
# 2. Seed database
# 3. Start Gunicorn

set -e

echo "📦 Installing dependencies..."
pip install -r requirements.txt

echo "🌱 Seeding database..."
python seed_render.py

echo "🚀 Starting Gunicorn..."
gunicorn --bind 0.0.0.0:$PORT wsgi:application
