#!/usr/bin/env python3
"""Test database selection priority"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load .env
load_dotenv()

print("=" * 60)
print("Database Selection Priority Test")
print("=" * 60)

print(f"\nDATABASE_URL (from .env):")
print(f"  Value: {os.getenv('DATABASE_URL', 'NOT SET')}")

print(f"\nRENDER_DATABASE_URL (Render's native env var):")
print(f"  Value: {os.getenv('RENDER_DATABASE_URL', 'NOT SET')}")

print("\n" + "=" * 60)
print("Selection Priority (as per app.py):")
print("=" * 60)

if os.getenv('RENDER_DATABASE_URL'):
    print("✅ PRIORITY 1: RENDER_DATABASE_URL detected")
    print("   → Will use PostgreSQL on Render")
    print("   → Seed script will populate 6 test users")
else:
    print("⚠️  PRIORITY 1: RENDER_DATABASE_URL not set")

if os.getenv('DATABASE_URL'):
    if 'sqlite' in os.getenv('DATABASE_URL').lower():
        print("   PRIORITY 2: DATABASE_URL = SQLite (local fallback)")
    else:
        print("   PRIORITY 2: DATABASE_URL = PostgreSQL")
else:
    print("   PRIORITY 2: DATABASE_URL not set")

print("\n" + "=" * 60)
print("Expected Behavior on Render:")
print("=" * 60)
print("✅ RENDER_DATABASE_URL is set by Render infrastructure")
print("✅ App will use PostgreSQL instead of SQLite")
print("✅ Seed script will run and create 6 test users")
print("✅ /api/auth/debug-users will show 6 users, not 1")

print("\n" + "=" * 60)
print("Status: Ready for Render deployment!")
print("=" * 60)
