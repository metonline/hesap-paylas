#!/usr/bin/env python3
"""Direct Twilio Verify API test - debug SMS delivery"""

import os
from dotenv import load_dotenv
from twilio.rest import Client

load_dotenv()

# Get credentials
ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
SERVICE_SID = os.getenv('TWILIO_SERVICE_SID')
PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')

print("=" * 60)
print("Twilio Configuration Debug")
print("=" * 60)
print(f"Account SID: {ACCOUNT_SID[:10]}...{'PRESENT' if ACCOUNT_SID else 'MISSING'}")
print(f"Auth Token: {AUTH_TOKEN[:10] if AUTH_TOKEN else 'MISSING'}...{'PRESENT' if AUTH_TOKEN else 'MISSING'}")
print(f"Service SID: {SERVICE_SID}")
print(f"Twilio Phone: {PHONE_NUMBER}")
print()

if not all([ACCOUNT_SID, AUTH_TOKEN, SERVICE_SID]):
    print("❌ Missing Twilio credentials!")
    exit(1)

try:
    client = Client(ACCOUNT_SID, AUTH_TOKEN)
    print("✅ Twilio client created successfully\n")
    
    # Test phone number - use your actual phone number
    test_phone = "+905323133277"  # User's phone from earlier
    
    print(f"Testing SMS verification for: {test_phone}")
    print("-" * 60)
    
    try:
        # Attempt to create verification
        verification = client.verify \
            .v2 \
            .services(SERVICE_SID) \
            .verifications \
            .create(to=test_phone, channel='sms')
        
        print(f"✅ Verification created successfully!")
        print(f"   Verification SID: {verification.sid}")
        print(f"   Status: {verification.status}")
        print(f"   Phone: {verification.to}")
        print(f"   Channel: sms")
        print()
        print(f"📱 OTP should be sent to: {test_phone}")
        print(f"⏱️  Check your phone for the SMS message")
        print()
        print("If you don't receive the message:")
        print("1. Phone number may not be verified in Twilio Console")
        print("2. Trial account may have restrictions")
        print("3. Check Twilio Console > Verify > Logs for errors")
        
    except Exception as e:
        print(f"❌ Failed to create verification: {str(e)}")
        print(f"   Error type: {type(e).__name__}")
        print()
        print("Common causes:")
        print("1. Service SID is incorrect or inactive")
        print("2. Phone number format is wrong")
        print("3. Account has reached SMS limit")
        print("4. Phone number not verified in trial account")
        
except Exception as e:
    print(f"❌ Failed to create Twilio client: {str(e)}")

print()
print("=" * 60)
