"""
WSGI entry point for Flask - Render Production
"""
import os
import sys
import traceback
from pathlib import Path
from dotenv import load_dotenv

print("[WSGI] ===== WSGI INITIALIZATION START =====", flush=True)
print(f"[WSGI] Python: {sys.version}", flush=True)
print(f"[WSGI] CWD: {os.getcwd()}", flush=True)

try:
    # Set UTF-8 encoding
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    
    # Add project root to Python path
    project_root = Path(__file__).parent.absolute()
    sys.path.insert(0, str(project_root))
    print(f"[WSGI] Project root: {project_root}", flush=True)
    
    # Load environment variables - BUT preserve Render's settings
    print("[WSGI] Loading .env...", flush=True)
    
    # Save Render's environment variables BEFORE loading .env
    render_database_url = os.getenv('DATABASE_URL')
    render_render_database_url = os.getenv('RENDER_DATABASE_URL')
    
    # Load .env file
    load_dotenv()
    
    # RESTORE Render's environment variables (they take priority over .env)
    if render_database_url:
        os.environ['DATABASE_URL'] = render_database_url
        print(f"[WSGI] ✓ Restored Render's DATABASE_URL from environment (overrides .env)", flush=True)
    if render_render_database_url:
        os.environ['RENDER_DATABASE_URL'] = render_render_database_url
        print(f"[WSGI] ✓ Restored Render's RENDER_DATABASE_URL from environment", flush=True)
    
    print(f"[WSGI] DATABASE_URL set: {bool(os.getenv('DATABASE_URL'))}", flush=True)
    
    # Import Flask app - this is where errors usually happen
    print("[WSGI] Importing Flask app from backend.app...", flush=True)
    from backend.app import app
    print("[WSGI] ✓ Flask app imported successfully!", flush=True)
    
    print("[WSGI] ===== WSGI INITIALIZATION COMPLETE =====", flush=True)
    
except Exception as e:
    print(f"[WSGI] ✗ CRITICAL ERROR during import:", flush=True)
    print(f"[WSGI] {type(e).__name__}: {e}", flush=True)
    print("[WSGI] Full traceback:", flush=True)
    traceback.print_exc(file=sys.stdout)
    print("[WSGI] Flask app will NOT be available!", flush=True)
    sys.exit(1)

# Gunicorn entry point
application = app




