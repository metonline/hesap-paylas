#!/bin/bash
# Render startup script - simplified for reliability
set -e

echo "================================"
echo "🚀 Render Deployment Starting"
echo "================================"

# Ensure PORT is set
PORT=${PORT:-10000}
echo "[START] PORT: $PORT"
echo "[START] Python: $(python3 --version)"

# Install dependencies
echo "[START] Installing dependencies..."
python3 -m pip install --quiet --upgrade pip setuptools wheel
python3 -m pip install --quiet -r requirements.txt
echo "[START] ✓ Dependencies installed"

# Try seeding, but don't fail if it errors
echo "[START] Attempting to seed database (non-fatal)..."
python3 seed_render.py 2>&1 || echo "[START] ⚠️  Seed failed but continuing..."

# Give database a moment
sleep 2

# Start Gunicorn with explicit configuration
echo "[START] Starting Gunicorn on 0.0.0.0:$PORT..."
exec python3 -m gunicorn \
    --bind 0.0.0.0:$PORT \
    --workers 1 \
    --threads 4 \
    --worker-class sync \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    --log-level debug \
    wsgi:application

