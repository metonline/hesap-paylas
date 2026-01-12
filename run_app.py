#!/usr/bin/env python
"""
Application entry point wrapper for Gunicorn
Ensures proper UTF-8 encoding and environment setup
"""
import os
import sys
import io

# Set UTF-8 encoding BEFORE anything else
os.environ['PYTHONIOENCODING'] = 'utf-8'
os.environ['PYTHONUNBUFFERED'] = '1'

# Rebuild stdout/stderr with UTF-8
if sys.stdout and not isinstance(sys.stdout, io.TextIOWrapper) or (hasattr(sys.stdout, 'encoding') and sys.stdout.encoding.lower() not in ('utf-8', 'utf8')):
    import codecs
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    except:
        pass

print("[RUN_APP] Starting with UTF-8 encoding", flush=True)
print(f"[RUN_APP] Python: {sys.version}", flush=True)
print(f"[RUN_APP] Working directory: {os.getcwd()}", flush=True)

# Now import Flask app
try:
    print("[RUN_APP] Importing wsgi module...", flush=True)
    from wsgi import app
    print("[RUN_APP] WSGI app imported successfully", flush=True)
except Exception as e:
    print(f"[ERROR] Failed to import WSGI app: {e}", flush=True)
    import traceback
    traceback.print_exc()
    sys.exit(1)

# The app object is now ready for Gunicorn
if __name__ == '__main__':
    print("[RUN_APP] App is ready for Gunicorn", flush=True)
