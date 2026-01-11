#!/usr/bin/env python3
"""Test API endpoint directly - no server startup"""

import requests
import json
import re

BASE_URL = 'http://localhost:5000'

# Test credentials
TEST_EMAIL = 'metonline@gmail.com'
TEST_PASSWORD = 'test123'

print("Testing Group Code Formatting API")
print("=" * 70)

# Step 1: Login
print("\n[1] Logging in...")
try:
    login_response = requests.post(
        f'{BASE_URL}/api/auth/login',
        json={'email': TEST_EMAIL, 'password': TEST_PASSWORD},
        headers={'Content-Type': 'application/json'},
        timeout=5
    )

    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.text}")
        exit(1)

    login_data = login_response.json()
    token = login_data.get('token')
    print(f"✅ Login successful!")

except Exception as e:
    print(f"❌ Connection error: {e}")
    print("Make sure the server is running on http://localhost:5000")
    exit(1)

# Step 2: Create a group
print("\n[2] Creating a group...")
try:
    create_group_response = requests.post(
        f'{BASE_URL}/api/groups',
        json={'name': 'Test Group'},
        headers={
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        },
        timeout=5
    )

    if create_group_response.status_code != 201:
        print(f"❌ Group creation failed ({create_group_response.status_code}): {create_group_response.text}")
        exit(1)

    group_data = create_group_response.json().get('group', {})
    raw_code = group_data.get('code')
    formatted_code = group_data.get('code_formatted')
    group_id = group_data.get('id')

    print(f"✅ Group created!")
    print(f"   - Group ID: {group_id}")
    print(f"   - Raw Code (API): {raw_code}")
    print(f"   - Formatted Code (API): {formatted_code}")

    # Validate formats
    if not raw_code or len(str(raw_code)) != 6 or not str(raw_code).isdigit():
        print(f"❌ Invalid raw code format: {raw_code} (expected 6-digit number)")
        print(f"   Raw code type: {type(raw_code)}, repr: {repr(raw_code)}")
        exit(1)

    if not formatted_code or not re.match(r'^\d{3}-\d{3}$', str(formatted_code)):
        print(f"❌ Invalid formatted code format: {formatted_code} (expected XXX-XXX)")
        exit(1)

    print(f"✅ Code formats validated!")

except Exception as e:
    print(f"❌ Request error: {e}")
    exit(1)

print("\n" + "=" * 70)
print("✅ API TESTS PASSED!")
print("=" * 70)
print(f"\nResult:")
print(f"  ✅ Raw Code (stored): {raw_code}")
print(f"  ✅ Formatted Code (display): {formatted_code}")
