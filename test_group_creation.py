from backend.app import app, db, User
import jwt
from datetime import datetime, timedelta

with app.app_context():
    user = User.query.filter_by(email='metonline@gmail.com').first()
    print(f'User: {user.email}')
    
    token = jwt.encode({
        'user_id': user.id,
        'exp': datetime.utcnow() + timedelta(days=7)
    }, app.config['JWT_SECRET'], algorithm='HS256')
    
    with app.test_client() as client:
        resp = client.post('/api/groups', 
            json={'name': 'Test Group', 'description': 'Test', 'category': 'Genel'},
            headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
        )
        print(f'Status: {resp.status_code}')
        data = resp.get_json()
        
        if resp.status_code == 201:
            print('SUCCESS: Group created!')
            group = data['group']
            print(f'  ID: {group["id"]}')
            print(f'  Name: {group["name"]}')
            print(f'  Code: {group["code"]}')
        else:
            print(f'Error: {data}')
