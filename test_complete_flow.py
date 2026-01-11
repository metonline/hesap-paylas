#!/usr/bin/env python3
"""Test script for the complete group code formatting flow"""

import requests
import json
import re

BASE_URL = 'http://localhost:5000'

# Test credentials
TEST_EMAIL = 'metonline@gmail.com'
TEST_PASSWORD = 'test123'

print("=" * 70)
print("COMPLETE GROUP CODE FORMATTING TEST")
print("=" * 70)

# Step 1: Login
print("\n[1] Logging in...")
login_response = requests.post(
    f'{BASE_URL}/api/auth/login',
    json={'email': TEST_EMAIL, 'password': TEST_PASSWORD},
    headers={'Content-Type': 'application/json'}
)

if login_response.status_code != 200:
    print(f"❌ Login failed: {login_response.text}")
    exit(1)

login_data = login_response.json()
token = login_data.get('token')
print(f"✅ Login successful! Token: {token[:20]}...")

# Step 2: Create a group
print("\n[2] Creating a group...")
create_group_response = requests.post(
    f'{BASE_URL}/api/groups',
    json={'name': 'Test Group'},
    headers={
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
)

if create_group_response.status_code != 201:
    print(f"❌ Group creation failed: {create_group_response.text}")
    exit(1)

group_data = create_group_response.json().get('group', {})
raw_code = group_data.get('code')
formatted_code = group_data.get('code_formatted')
group_id = group_data.get('id')

print(f"✅ Group created!")
print(f"   - Group ID: {group_id}")
print(f"   - Raw Code (stored): {raw_code}")
print(f"   - Formatted Code (display): {formatted_code}")

# Validate formats
if not raw_code or len(raw_code) != 6 or not raw_code.isdigit():
    print(f"❌ Invalid raw code format: {raw_code}")
    exit(1)

if not formatted_code or not re.match(r'^\d{3}-\d{3}$', formatted_code):
    print(f"❌ Invalid formatted code format: {formatted_code}")
    exit(1)

# Validate formatting conversion
expected_formatted = f"{raw_code[:3]}-{raw_code[3:]}"
if formatted_code != expected_formatted:
    print(f"❌ Formatting mismatch: {formatted_code} != {expected_formatted}")
    exit(1)

print(f"✅ Code formats validated correctly!")

# Step 3: Get user groups and verify code appears in responses
print("\n[3] Retrieving user groups...")
get_groups_response = requests.get(
    f'{BASE_URL}/api/groups/user',
    headers={'Authorization': f'Bearer {token}'}
)

if get_groups_response.status_code != 200:
    print(f"❌ Failed to get user groups: {get_groups_response.text}")
    exit(1)

groups = get_groups_response.json()
found_group = None
for group in groups:
    if group['id'] == group_id:
        found_group = group
        break

if not found_group:
    print(f"❌ Group not found in user groups list")
    exit(1)

print(f"✅ Group found in user groups!")
print(f"   - Code from /user endpoint: {found_group.get('code')}")
print(f"   - Formatted from /user endpoint: {found_group.get('code_formatted')}")

# Step 4: Test joining with formatted code
print("\n[4] Testing join with formatted code...")
# First, create a second user/account scenario by clearing membership
# For this test, we'll test with the existing code

join_response = requests.post(
    f'{BASE_URL}/api/groups/join',
    json={'code': formatted_code},  # Test with formatted code
    headers={
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
)

# Should return 200 (already member) since we just created it
if join_response.status_code not in [200, 201]:
    print(f"❌ Join with formatted code failed: {join_response.text}")
    exit(1)

join_data = join_response.json()
print(f"✅ Join with formatted code successful!")
print(f"   - Response: {join_data.get('message')}")

# Step 5: Test joining with raw code
print("\n[5] Testing join with raw code...")
join_raw_response = requests.post(
    f'{BASE_URL}/api/groups/join',
    json={'code': raw_code},  # Test with raw code
    headers={
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
)

if join_raw_response.status_code not in [200, 201]:
    print(f"❌ Join with raw code failed: {join_raw_response.text}")
    exit(1)

print(f"✅ Join with raw code successful!")
print(f"   - Response: {join_raw_response.json().get('message')}")

print("\n" + "=" * 70)
print("✅ ALL TESTS PASSED!")
print("=" * 70)
print(f"\nSummary:")
print(f"  ✅ Code generation: {raw_code} (6-digit pure number)")
print(f"  ✅ Code formatting: {formatted_code} (XXX-XXX display format)")
print(f"  ✅ API returns both formats")
print(f"  ✅ Join works with formatted code")
print(f"  ✅ Join works with raw code")
