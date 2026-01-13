#!/usr/bin/env python3
"""Test script to verify Twilio configuration and SMS sending"""

import os
import sys

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except:
    print("dotenv not available, using system env vars")

print("=" * 60)
print("TWILIO CONFIGURATION TEST")
print("=" * 60)

# Check environment variables
account_sid = os.getenv('TWILIO_ACCOUNT_SID')
auth_token = os.getenv('TWILIO_AUTH_TOKEN')
phone_number = os.getenv('TWILIO_PHONE_NUMBER')

print(f"\n1. Environment Variables:")
print(f"   TWILIO_ACCOUNT_SID:    {account_sid[:10] + '...' if account_sid else 'NOT SET'}")
print(f"   TWILIO_AUTH_TOKEN:     {auth_token[:10] + '...' if auth_token else 'NOT SET'}")
print(f"   TWILIO_PHONE_NUMBER:   {phone_number if phone_number else 'NOT SET'}")

# Check if all are set
if not all([account_sid, auth_token, phone_number]):
    print("\n❌ ERROR: Missing Twilio credentials!")
    print("   Please set environment variables:")
    print("   - TWILIO_ACCOUNT_SID")
    print("   - TWILIO_AUTH_TOKEN")
    print("   - TWILIO_PHONE_NUMBER")
    sys.exit(1)

# Try to import and initialize Twilio
print(f"\n2. Testing Twilio Client:")
try:
    from twilio.rest import Client
    print("   ✅ Twilio SDK imported successfully")
    
    # Initialize client
    client = Client(account_sid, auth_token)
    print("   ✅ Client initialized successfully")
    
    # Verify account
    account = client.api.account.fetch()
    print(f"   ✅ Account verified: {account.friendly_name}")
    print(f"      Type: {account.type}")
    print(f"      Status: {account.status}")
    
except ImportError as e:
    print(f"   ❌ Failed to import Twilio: {e}")
    print("      Run: pip install twilio")
    sys.exit(1)
except Exception as e:
    print(f"   ❌ Failed to initialize Twilio client: {e}")
    sys.exit(1)

# Get available phone numbers
print(f"\n3. Checking Twilio Phone Numbers:")
try:
    incoming_numbers = client.incoming_phone_numbers.stream(limit=20)
    numbers_list = list(incoming_numbers)
    
    if numbers_list:
        print(f"   ✅ Found {len(numbers_list)} phone number(s):")
        for num in numbers_list:
            print(f"      - {num.phone_number} ({num.friendly_name})")
            if num.phone_number == phone_number or num.phone_number == '+' + phone_number:
                print(f"        ✅ Matches TWILIO_PHONE_NUMBER!")
    else:
        print("   ⚠️  No incoming phone numbers found")
        print("   (This might be normal for trial accounts)")
        
except Exception as e:
    print(f"   ⚠️  Could not fetch phone numbers: {e}")

print(f"\n4. SMS Send Test:")
test_phone = os.getenv('TEST_PHONE_NUMBER')
if not test_phone:
    print("   ℹ️  TEST_PHONE_NUMBER not set")
    print("   To test SMS sending, set TEST_PHONE_NUMBER env var")
    print("   Example: +905323133277")
else:
    try:
        print(f"   Sending test SMS to {test_phone}...")
        message = client.messages.create(
            body="Test message from Hesap Paylas - PIN Reset System",
            from_=phone_number,
            to=test_phone
        )
        print(f"   ✅ SMS sent successfully!")
        print(f"      Message SID: {message.sid}")
        print(f"      Status: {message.status}")
    except Exception as e:
        print(f"   ❌ Failed to send SMS: {e}")

print("\n" + "=" * 60)
print("Configuration test complete!")
print("=" * 60)
