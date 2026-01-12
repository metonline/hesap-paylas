"""
WSGI entry point for Flask - Render Production
"""
import os
import sys
import traceback
from pathlib import Path

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
    
    # Load environment variables
    from dotenv import load_dotenv
    print("[WSGI] Loading .env...", flush=True)
    load_dotenv()
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

# Local testing only
if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    print(f"[WSGI] Starting Flask on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)




