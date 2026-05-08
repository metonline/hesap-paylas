#!/bin/bash
# Render startup script
# 1. Install dependencies
# 2. Seed database
# 3. Start Gunicorn

echo "📦 Installing dependencies..."
pip install -r requirements.txt

echo "🌱 Seeding database..."
python seed_render.py 2>&1 | tee /tmp/seed_output.log || {
    SEED_EXIT=$?
    echo "⚠️ Seed script exited with code $SEED_EXIT"
    echo "⚠️ Full output saved to /tmp/seed_output.log"
    echo "⚠️ Continuing with Gunicorn anyway..."
}

# Give database time to be ready
sleep 2

echo "🚀 Starting Gunicorn..."
exec gunicorn --bind 0.0.0.0:$PORT wsgi:application
