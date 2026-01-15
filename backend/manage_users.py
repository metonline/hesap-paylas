import os
from app import app, db, User

# Ensure app context for SQLAlchemy
with app.app_context():
    users = User.query.all()
    print("\nAll users in the database:")
    for user in users:
        print(f"ID: {user.id}, Name: {user.first_name} {user.last_name}, Phone: {user.phone}, Email: {user.email}")

    phone_to_update = input("\nEnter the phone number to update (or press Enter to skip): ").strip()
    if phone_to_update:
        user = User.query.filter_by(phone=phone_to_update).first()
        if user:
            new_email = input(f"Enter new email for {user.first_name} {user.last_name} ({user.phone}): ").strip()
            if new_email:
                user.email = new_email
                db.session.commit()
                print(f"Email updated to {new_email} for user {user.phone}")
            else:
                print("No email entered. No changes made.")
        else:
            print("No user found with that phone number.")
    else:
        print("No phone number entered. No changes made.")
