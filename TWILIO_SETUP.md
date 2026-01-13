# Twilio Setup Guide for PIN Reset SMS

## Problem
SMS is not sending because `TWILIO_PHONE_NUMBER` is not a valid incoming phone number in your Twilio account.

## Solution

### Option 1: Use Twilio Trial Phone Number (Recommended)
1. Go to https://www.twilio.com/console/phone-numbers/incoming
2. Look for your **Trial Phone Number** (usually given to you when you created the account)
3. Copy it exactly (should be in format +1XXXXXXXXXX)
4. Update `.env`:
   ```
   TWILIO_PHONE_NUMBER=+1XXXXXXXXXX
   ```
5. Update PythonAnywhere environment variables with the same number

### Option 2: Get a New Twilio Phone Number
1. Go to https://www.twilio.com/console/phone-numbers/search
2. Select a country (Turkey for +90, or USA for +1)
3. Click "Buy" to purchase a phone number
4. The number will appear in your account
5. Use that number as TWILIO_PHONE_NUMBER

### Option 3: Test Mode Without Real SMS (Development)
For development/testing without sending real SMS:
1. Keep the PIN code generation working
2. Manually copy the code from server logs
3. Use it for testing

## Steps to Fix

### 1. Find Your Twilio Trial Phone Number
```
1. Go to: https://www.twilio.com/console/phone-numbers/incoming
2. Look for a phone number starting with +1 (USA trial) or your country
3. Copy the exact number
```

### 2. Update Environment Variables

**Local Development (.env):**
```
TWILIO_PHONE_NUMBER=+1XXXXXXXXXX  (replace with your actual number)
```

**PythonAnywhere (Web app settings):**
1. Go to Web tab → "Web app settings"
2. Scroll to "Environment variables"
3. Add/Update:
   ```
   TWILIO_PHONE_NUMBER=+1XXXXXXXXXX
   ```
4. Click "Save"
5. Reload the web app

### 3. Verify Configuration
Run the test script:
```bash
python test_twilio_config.py
```

It should show your phone number in the list.

### 4. Test PIN Reset Again
1. Go to login page
2. Test PIN reset flow
3. SMS should now send successfully

## Current Status
- ✅ Twilio SDK installed
- ✅ Credentials configured
- ⚠️ **Phone number NOT registered in account** ← FIX THIS
- ❌ SMS sending fails due to invalid phone number

## Debugging
To see detailed logs from PIN reset attempt:
```
1. Try PIN reset on production
2. Go to PythonAnywhere → "Error log"
3. Look for "[DEBUG]", "[SMS]" messages
4. Share the error output
```
