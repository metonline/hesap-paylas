import os
from app import app, db, User

def delete_all_users():
    with app.app_context():
        num_deleted = User.query.delete()
        db.session.commit()
        print(f"Deleted {num_deleted} users from the database.")

if __name__ == "__main__":
    delete_all_users()
