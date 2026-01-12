"""
WSGI entry point for Flask
"""
import os
import sys
from pathlib import Path

# Set UTF-8 encoding
os.environ['PYTHONIOENCODING'] = 'utf-8'

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent.absolute()))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Import Flask app - Gunicorn will use this
from backend.app import app

# That's it! Gunicorn finds 'app' and serves it

if __name__ == '__main__':
    # For local testing
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)


