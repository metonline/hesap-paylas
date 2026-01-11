#!/usr/bin/env python3
"""Test script for group code formatting"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app import format_group_code, generate_group_code

# Test format_group_code function
print("=" * 50)
print("Testing format_group_code() function")
print("=" * 50)

test_codes = [
    "123456",
    "999999", 
    "000000",
    "567890",
    "12345",  # Too short
    None,
    "",
    "123-456"  # Already formatted
]

for code in test_codes:
    formatted = format_group_code(code)
    print(f"Input: {code!r:15} -> Output: {formatted!r}")

print("\n" + "=" * 50)
print("Testing generate_group_code() function")
print("=" * 50)

# Generate 5 random codes
for i in range(5):
    raw_code = generate_group_code()
    formatted_code = format_group_code(raw_code)
    print(f"Generated {i+1}: {raw_code} -> {formatted_code}")

print("\n" + "=" * 50)
print("Testing code validation (should accept both formats)")
print("=" * 50)

test_inputs = [
    "123456",     # Raw format
    "123-456",    # Formatted
    "999-999",    # Formatted
    "000000",     # Raw
]

for code in test_inputs:
    clean_code = code.replace('-', '')
    print(f"Input: {code:10} -> Clean: {clean_code:6} -> Formatted: {format_group_code(clean_code)}")

print("\n✅ All formatting tests completed!")
