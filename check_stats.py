#!/usr/bin/env python
"""Check stats from backend API"""
import requests
import json

try:
    response = requests.get('http://localhost:5000/api/stats')
    stats = response.json()
    
    print("=== Database Statistics ===")
    print(f"Total Users: {stats.get('users', 0)}")
    print(f"Total Groups: {stats.get('groups', 0)}")
    print(f"Total Orders: {stats.get('orders', 0)}")
    print(f"Timestamp: {stats.get('timestamp', 'N/A')}")
    
except Exception as e:
    print(f"Error: {e}")
