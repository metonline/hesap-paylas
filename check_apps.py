#!/usr/bin/env python
"""Check which app.py is running"""
import os
import sys

print(f"Current Python: {sys.executable}")
print(f"Current dir: {os.getcwd()}")

# Check for app.py files
for root, dirs, files in os.walk('c:\\Users\\metin\\Desktop\\BILL'):
    if 'app.py' in files:
        full_path = os.path.join(root, 'app.py')
        print(f"Found app.py at: {full_path}")
        with open(full_path, 'r') as f:
            first_lines = f.read(200)
            print(f"  First 200 chars: {first_lines[:200]}")
            print()
