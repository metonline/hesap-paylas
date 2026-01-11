from backend.app import app, db, Group

with app.app_context():
    groups = Group.query.all()
    for g in groups:
        print(f"Group: {g.name}")
        print(f"  Description: {repr(g.description)}")
        print(f"  Category: {g.category}")
        print()
