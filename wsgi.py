"""
WSGI entry point for Gunicorn
"""
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

# Load environment
from dotenv import load_dotenv
load_dotenv()

# Import and create database
from backend.app import app, db

# Create tables on startup
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run()
