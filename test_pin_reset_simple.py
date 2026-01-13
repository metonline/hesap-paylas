#!/usr/bin/env python3
"""Test PIN reset flow locally"""

import sys
sys.path.insert(0, '.')

from backend.app import app, db, User, OTPVerification
from datetime import datetime, timedelta

def test_pin_reset():
    """Test PIN reset functionality"""
    with app.app_context():
        print("=" * 60)
        print("PIN RESET FLOW TEST")
        print("=" * 60)
        
        # Create tables if they don't exist
        print("\n0. Initializing database")
        db.create_all()
        print(f"   [OK] Database tables created/verified")
        
        # Test phone
        test_phone = '+905323133277'
        
        print(f"\n1. Checking user with phone: {test_phone}")
        user = User.query.filter_by(phone=test_phone).first()
        
        if user:
            print(f"   [OK] User found: {user.first_name} {user.last_name}")
        else:
            print(f"   [*] User not found - creating test user")
            # Create test user
            user = User(
                phone=test_phone, 
                first_name='Test', 
                last_name='User',
                email=f"test_{test_phone.replace('+', '')}@test.local"
            )
            user.set_password('1234')  # Default PIN
            db.session.add(user)
            db.session.commit()
            print(f"   [OK] Test user created: {user.first_name} {user.last_name}")
        
        # Test code generation
        print(f"\n2. Testing reset code generation")
        from random import randint
        reset_code = f"{randint(0, 999999):06d}"
        print(f"   Generated code: {reset_code}")
        
        # Test storing in DB
        print(f"\n3. Testing OTP record storage")
        otp = OTPVerification(
            phone=test_phone,
            code=reset_code,
            purpose='pin_reset',
            expires_at=datetime.utcnow() + timedelta(minutes=10)
        )
        db.session.add(otp)
        db.session.commit()
        print(f"   [OK] OTP record stored with ID: {otp.id}")
        
        # Test retrieval
        print(f"\n4. Testing OTP record retrieval")
        retrieved_otp = OTPVerification.query.filter_by(
            phone=test_phone,
            code=reset_code,
            purpose='pin_reset',
            used=False
        ).first()
        
        if retrieved_otp:
            print(f"   [OK] OTP record retrieved successfully")
            print(f"      Phone: {retrieved_otp.phone}")
            print(f"      Code: {retrieved_otp.code}")
            print(f"      Purpose: {retrieved_otp.purpose}")
            print(f"      Expires: {retrieved_otp.expires_at}")
            print(f"      Used: {retrieved_otp.used}")
        else:
            print(f"   [!] OTP record not found")
            return False
        
        # Test marking as used
        print(f"\n5. Testing OTP mark as used")
        retrieved_otp.used = True
        db.session.commit()
        print(f"   [OK] OTP marked as used")
        
        # Test PIN update
        print(f"\n6. Testing PIN update")
        new_pin = '5678'
        user.set_password(new_pin)
        db.session.commit()
        print(f"   [OK] PIN updated for user")
        
        # Verify new PIN
        if user.check_password(new_pin):
            print(f"   [OK] New PIN verified successfully")
        else:
            print(f"   [!] PIN verification failed")
            return False
        
        print("\n" + "=" * 60)
        print("[SUCCESS] ALL TESTS PASSED!")
        print("=" * 60)
        return True

if __name__ == '__main__':
    try:
        success = test_pin_reset()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n[ERROR] TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
