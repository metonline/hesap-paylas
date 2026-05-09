"""
WSGI entry point for Flask - Render Production
Version: 1fc57da-enhanced (2026-05-09 02:30 UTC)
"""
import os
import sys
import traceback
from pathlib import Path
from dotenv import load_dotenv

print("[WSGI] ===== WSGI INITIALIZATION START (v1fc57da-enhanced) =====", flush=True)
print(f"[WSGI] Python: {sys.version}", flush=True)
print(f"[WSGI] CWD: {os.getcwd()}", flush=True)

try:
    # Set UTF-8 encoding
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    
    # Add project root to Python path
    project_root = Path(__file__).parent.absolute()
    sys.path.insert(0, str(project_root))
    print(f"[WSGI] Project root: {project_root}", flush=True)
    
    # Detect if running on Render
    is_render = bool(os.getenv('RENDER'))
    print(f"[WSGI] Running on Render: {is_render}", flush=True)
    
    # Load environment variables - BUT preserve Render's settings
    print("[WSGI] Loading .env...", flush=True)
    
    # Save Render's environment variables BEFORE loading .env
    render_database_url = os.getenv('DATABASE_URL')
    render_render_database_url = os.getenv('RENDER_DATABASE_URL')
    
    # Load .env file (except on Render, where we trust env vars)
    if not is_render:
        load_dotenv()
        print("[WSGI] .env loaded (local development)", flush=True)
    else:
        print("[WSGI] Skipping .env on Render - using only environment variables", flush=True)
    
    # RESTORE Render's environment variables (they take priority over .env)
    if render_database_url:
        os.environ['DATABASE_URL'] = render_database_url
        print(f"[WSGI] ✓ Using Render's DATABASE_URL from environment", flush=True)
    if render_render_database_url:
        os.environ['RENDER_DATABASE_URL'] = render_render_database_url
        print(f"[WSGI] ✓ Using Render's RENDER_DATABASE_URL from environment", flush=True)
    
    # WORKAROUND: If on Render but DATABASE_URL not set, construct from component variables
    if is_render and not os.getenv('DATABASE_URL'):
        print("[WSGI] ⚠️  DATABASE_URL not set, checking for component database variables...", flush=True)
        
        # Check for Render's component-based DB variables
        db_host = os.getenv('DATABASE_URL_HOST') or os.getenv('POSTGRES_HOST') or "hesap-paylas-db.render.internal"
        db_port = os.getenv('DATABASE_URL_PORT') or os.getenv('POSTGRES_PORT') or "5432"
        db_user = os.getenv('DATABASE_URL_USER') or os.getenv('POSTGRES_USER') or "postgres"
        db_pass = os.getenv('DATABASE_URL_PASSWORD') or os.getenv('POSTGRES_PASSWORD') or os.getenv('PGPASSWORD', '')
        db_name = os.getenv('DATABASE_URL_DATABASE') or os.getenv('POSTGRES_DB') or "hesap_paylas"
        
        if db_host and db_user and db_name:
            database_url = f"postgresql://{db_user}"
            if db_pass:
                database_url += f":{db_pass}"
            database_url += f"@{db_host}:{db_port}/{db_name}"
            os.environ['DATABASE_URL'] = database_url
            print(f"[WSGI] ✓ Constructed DATABASE_URL from components", flush=True)
    
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




