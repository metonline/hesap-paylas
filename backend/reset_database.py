import os
from app import app, db

def drop_and_recreate_all():
    with app.app_context():
        db.drop_all()
        db.create_all()
        print("All tables dropped and recreated. Database is now empty.")

if __name__ == "__main__":
    drop_and_recreate_all()
