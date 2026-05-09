#!/bin/bash
# Render startup script
# 1. Install dependencies
# 2. Seed database
# 3. Start Gunicorn

set -e  # Exit on any error

echo "================================"
echo "📦 Render Deployment Starting"
echo "================================"

echo "🔧 Python version:"
python3 --version

echo "📦 Installing dependencies..."
python3 -m pip install --upgrade pip setuptools wheel
python3 -m pip install -r requirements.txt

echo "✅ Dependencies installed"
echo ""

echo "🌱 Seeding database..."
python3 seed_render.py 2>&1 | tee /tmp/seed_output.log
SEED_EXIT=$?
if [ $SEED_EXIT -ne 0 ]; then
    echo ""
    echo "⚠️  Seed script exited with code $SEED_EXIT"
    echo "⚠️  Full output saved to /tmp/seed_output.log"
    echo "⚠️  BUT CONTINUING WITH GUNICORN ANYWAY..."
    echo ""
fi

# Give database time to be ready
sleep 2

echo "🚀 Starting Gunicorn on port $PORT..."
exec python3 -m gunicorn --bind 0.0.0.0:$PORT wsgi:application
