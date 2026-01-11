#!/usr/bin/env python
"""Check Render production database stats"""
import requests
import json

url = 'https://hesap-paylas.onrender.com/api/stats'

try:
    print(f"Fetching {url}...")
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    
    stats = response.json()
    
    print("\n=== RENDER Production Database Statistics ===")
    print(f"Total Users: {stats.get('users', 0)}")
    print(f"Total Groups: {stats.get('groups', 0)}")
    print(f"Total Orders: {stats.get('orders', 0)}")
    print(f"Timestamp: {stats.get('timestamp', 'N/A')}")
    
except requests.exceptions.RequestException as e:
    print(f"Error connecting to Render API: {e}")
except Exception as e:
    print(f"Error: {e}")
