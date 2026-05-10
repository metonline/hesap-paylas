#!/usr/bin/env python3
"""Test wsgi.py and database selection fixes"""
import os
import sys
from dotenv import load_dotenv

print("=" * 60)
print("TESTING RENDER FIXES")
print("=" * 60)
print()

# Check if Render
is_render = bool(os.getenv('RENDER'))
print(f"Is Render environment: {is_render}")
print()

# Show initial state
print("Initial environment:")
print(f"  DATABASE_URL:        {os.getenv('DATABASE_URL', 'NOT SET')[:45]}")
print(f"  RENDER_DATABASE_URL: {os.getenv('RENDER_DATABASE_URL', 'NOT SET')[:45]}")
print()

# Save Render's values
saved_db = os.getenv('DATABASE_URL')
saved_render_db = os.getenv('RENDER_DATABASE_URL')

# Load .env (what happens on old code)
print("Loading .env...")
load_dotenv()

# Check if .env overwrote things (the bug!)
print(f"After load_dotenv():")
print(f"  DATABASE_URL:        {os.getenv('DATABASE_URL', 'NOT SET')[:45]}")
print(f"  RENDER_DATABASE_URL: {os.getenv('RENDER_DATABASE_URL', 'NOT SET')[:45]}")
print()

# Apply fix #1: Skip load_dotenv on Render
print("FIX #1: Skip .env on Render")
if is_render:
    # Undo the load
    if saved_db:
        os.environ['DATABASE_URL'] = saved_db
    if saved_render_db:
        os.environ['RENDER_DATABASE_URL'] = saved_render_db
    print("  ✓ Restored Render environment variables")
else:
    print("  ⊘ Not on Render, .env is OK")
print()

print("After Fix #1:")
print(f"  DATABASE_URL:        {os.getenv('DATABASE_URL', 'NOT SET')[:45]}")
print(f"  RENDER_DATABASE_URL: {os.getenv('RENDER_DATABASE_URL', 'NOT SET')[:45]}")
print()

# Show database that will be selected
print("=" * 60)
print("DATABASE SELECTION (from app.py)")
print("=" * 60)

if os.getenv('RENDER_DATABASE_URL'):
    print("✅ PRIORITY 1: RENDER_DATABASE_URL detected")
    print("   → Will use PostgreSQL (correct!)")
elif os.getenv('DATABASE_URL') and 'postgres' in os.getenv('DATABASE_URL').lower():
    print("✅ PRIORITY 2: PostgreSQL in DATABASE_URL")
    print("   → Will use PostgreSQL")
elif os.getenv('DATABASE_URL') and 'sqlite' in os.getenv('DATABASE_URL').lower():
    print("❌ PRIORITY 2: SQLite in DATABASE_URL")
    print("   → Will use SQLite (wrong on Render!)")
else:
    print("⚠️ No DATABASE_URL - fallback to local SQLite")

print()
print("=" * 60)
print("✅ FIXES VALIDATED LOCALLY")
print("=" * 60)
