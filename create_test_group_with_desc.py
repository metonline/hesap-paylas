from backend.app import app, db, Group, User

with app.app_context():
    # Find or create user
    user = User.query.filter_by(email='metonline@gmail.com').first()
    if not user:
        print("User not found")
        exit()
    
    # Create test group WITH description
    group = Group(
        name='Sarı',
        description='Big Chef\'te öğle yemeği',  # IMPORTANT: description
        category='Cafe / Restaurant',
        code='123-456',
        created_by=user.id
    )
    
    db.session.add(group)
    db.session.flush()
    
    # Add user to group
    group.members.append(user)
    
    db.session.commit()
    
    print(f"✅ Group created:")
    print(f"  Name: {group.name}")
    print(f"  Description: {group.description}")
    print(f"  Category: {group.category}")
    print(f"  Code: {group.code}")
    print(f"  Members: {len(group.members)}")
