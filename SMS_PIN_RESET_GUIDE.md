# SMS PIN Reset - Troubleshooting Guide

## Current Status
PIN reset feature is **fully implemented** but SMS delivery is **not working** because Twilio phone number is not registered in your account.

## What's Working
✅ PIN reset modal UI (3-step flow)
✅ Reset code generation  
✅ Code storage in database
✅ Code validation flow
✅ PIN update functionality
✅ Twilio SDK installed and configured
✅ Backend endpoints created

## What's Not Working
❌ SMS delivery (Twilio phone number not registered)
❌ SMS sends from `+18574447891` - not in your account

## Root Cause

Your Twilio account has a **Trial Phone Number** assigned during account creation. The phone number you tried to use (`+18574447891`) is NOT that number. Twilio won't send SMS from unregistered numbers.

**Check your actual phone number:**
1. Go to: https://www.twilio.com/console/phone-numbers/incoming
2. Look for your phone number (should start with +1 or country code)
3. Copy the **exact** number from the console

##  Fix: Update Twilio Phone Number

### Step 1: Find Your Phone Number
Go to: https://www.twilio.com/console/phone-numbers/incoming

You should see at least one phone number (your trial number). Example format:
- `+14155552671` (USA trial)
- `+16175552368` (USA trial)
- `+353830244877` (Ireland trial)

### Step 2: Local Development
1. Update `.env` file:
   ```
   TWILIO_PHONE_NUMBER=+1XXXXXXXXXX  # Replace with your actual number
   ```

2. Test Twilio configuration:
   ```bash
   python test_twilio_config.py
   ```

3. Should show your phone number in the list.

### Step 3: PythonAnywhere Production
1. Login to PythonAnywhere: https://www.pythonanywhere.com
2. Go to: **Web app settings** → **Environment variables**
3. Find or add:
   ```
   TWILIO_PHONE_NUMBER=+1XXXXXXXXXX  # Same number as local
   ```
4. Click **Save**
5. **Reload web app** from Web tab
6. Pull latest code: `git pull origin main`

### Step 4: Test PIN Reset Again
1. Go to your app on PythonAnywhere
2. Test login page → "PIN kodumu unuttum?"
3. Enter phone, click "SMS Gönder"
4. Should now receive SMS with code
5. Enter code from SMS
6. Set new PIN

## Verification Steps

### Test 1: Local SMS Test
```bash
# Set your test phone
export TEST_PHONE_NUMBER=+905323133277

# Run config test
python test_twilio_config.py
```

Should show:
```
4. SMS Send Test:
   Sending test SMS to +905323133277...
   OK SMS sent successfully!
      Message SID: SM1234...
      Status: queued
```

### Test 2: Check PythonAnywhere Logs
1. Go to PythonAnywhere: **Web app** → **Error log**
2. Trigger PIN reset from browser
3. Look for logs with `[DEBUG]` and `[SMS]` tags
4. Should see either:
   - `[SMS] OK Reset code sent` - SUCCESS
   - `[SMS] [X] Twilio error: ...` - FAILURE (check message)

### Test 3: Check Server Output
On PythonAnywhere, console should show:
```
[DEBUG] request_pin_reset called
[DEBUG] Formatted phone: +905323133277
[DEBUG] User found: True
[DEBUG] Generated code: 123456
[DEBUG] Twilio - SID exists: True, Token exists: True, Phone: +1...
[SMS] OK Reset code sent: SM1234...
```

## Alternative: Buy a New Phone Number

If you want SMS from a Turkish number (+90):
1. Go to: https://www.twilio.com/console/phone-numbers/search
2. Select country: **Turkey**
3. Select type: **SMS**
4. Click **Buy** (may have cost)
5. Add to environment variables

## Debug Mode (Development Only)

If SMS still not working, debug code is available:

**Test all pending reset codes:**
```
GET /api/auth/debug-reset-codes
```

Response (dev mode only):
```json
{
  "message": "Pending PIN reset codes (DEV ONLY)",
  "count": 1,
  "codes": [
    {
      "phone": "+905323133277",
      "code": "123456",
      "expires_at": "2026-01-13T20:22:10.128243",
      "created_at": "2026-01-13T20:12:10.128243"
    }
  ]
}
```

Use this code to test the verification flow without waiting for SMS.

## Files Modified

- `backend/app.py`: 
  - Updated OTPVerification model with new fields
  - Enhanced PIN reset endpoints with detailed logging
  - Added debug endpoint for development
  
- `phone-join-group.html`:
  - Improved SMS error handling
  - Better status messages
  - Support for dev mode debug info

- `.env`:
  - Updated TWILIO_PHONE_NUMBER placeholder with instructions

- `TWILIO_SETUP.md`: 
  - Comprehensive setup guide
  
- `test_twilio_config.py`:
  - Tool to verify Twilio credentials and phone numbers
  
- `test_pin_reset_simple.py`:
  - Full flow test (local development)

## Quick Reference

| Issue | Solution |
|-------|----------|
| SMS not sending | Update TWILIO_PHONE_NUMBER to your actual Twilio number |
| "Phone number not registered" | Check https://www.twilio.com/console/phone-numbers/incoming |
| Error on PythonAnywhere | Check Web app settings → Environment variables → TWILIO_PHONE_NUMBER |
| Web app not reloading | Reload from PythonAnywhere Web tab after env var changes |
| Can't see my phone number | Check Twilio account dashboard (may need to buy a number) |
| SMS arrives but code wrong | Check backend logs for code generation |

## Emergency: Test Without SMS

To test the entire PIN reset flow without SMS:

1. POST to `/api/auth/request-pin-reset` with phone
2. GET `/api/auth/debug-reset-codes` to see generated code
3. Copy the code manually
4. POST to `/api/auth/verify-pin-reset` with code from step 2
5. POST to `/api/auth/confirm-pin-reset` to set new PIN

This works in development mode only.

## Support

If SMS still not working after these steps:
1. Check PythonAnywhere error log for exact error
2. Verify TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN are correct  
3. Ensure TWILIO_PHONE_NUMBER is from https://www.twilio.com/console/phone-numbers/incoming
4. Check Twilio account balance (trial accounts may have limits)
5. Verify phone number hasn't been deleted from Twilio account
