#!/usr/bin/env python
"""
Hesap Paylaş Local Development Server
Frontend + Backend + Database
"""

import os
import sys
import subprocess
import threading
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

# Load environment
from dotenv import load_dotenv
load_dotenv()

def create_db():
    """Create SQLite database"""
    print("\n📦 Creating database...")
    from backend.app import app, db
    with app.app_context():
        db.create_all()
        print("✓ Database created successfully")

def run_flask():
    """Run Flask development server"""
    print("\n🚀 Starting Flask backend on http://localhost:5000")
    from backend.app import app
    app.run(
        host='127.0.0.1',
        port=5000,
        debug=True,
        use_reloader=False  # Disable reloader to avoid port conflicts
    )

def run_static_server():
    """Run static file server for frontend"""
    print("📄 Starting frontend server on http://localhost:8000")
    os.chdir(project_root)
    import http.server
    import socketserver
    
    PORT = 8000
    Handler = http.server.SimpleHTTPRequestHandler
    
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"✓ Serving at http://localhost:8000")
        httpd.serve_forever()

def main():
    print("=" * 60)
    print("Hesap Paylaş - Local Development Server")
    print("=" * 60)
    
    try:
        # Create database
        create_db()
        
        # Start servers in separate threads
        print("\n🔧 Starting servers...")
        
        flask_thread = threading.Thread(target=run_flask, daemon=True)
        static_thread = threading.Thread(target=run_static_server, daemon=True)
        
        flask_thread.start()
        time.sleep(2)
        static_thread.start()
        
        print("\n" + "=" * 60)
        print("✓ All services running!")
        print("=" * 60)
        print("\n📋 Services:")
        print("  - Frontend: http://localhost:8000")
        print("  - Backend:  http://localhost:5000")
        print("  - API:      http://localhost:5000/api")
        print("\n⚠️  Press Ctrl+C to stop")
        print("=" * 60 + "\n")
        
        # Keep main thread alive
        while True:
            time.sleep(1)
    
    except KeyboardInterrupt:
        print("\n\n✓ Shutting down...")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
