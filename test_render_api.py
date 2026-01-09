#!/usr/bin/env python3
"""
Test Render API
"""
import urllib.request
import urllib.error
import json

url = 'https://hesap-paylas-api.onrender.com/api/health'

print("Testing Render API...")
print(f"URL: {url}")

try:
    with urllib.request.urlopen(url, timeout=10) as response:
        data = json.loads(response.read().decode('utf-8'))
        print(f"Status: {response.status}")
        print(f"Response: {data}")
        print("\n✓ API is working!")
except urllib.error.URLError as e:
    print(f"X Connection error: {e}")
except urllib.error.HTTPError as e:
    print(f"X HTTP Error {e.code}: {e.reason}")
except Exception as e:
    print(f"X Error: {e}")
