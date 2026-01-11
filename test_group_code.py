import requests
import json

# Login
login_response = requests.post('http://127.0.0.1:5000/api/auth/login', json={'email': 'metonline@gmail.com', 'password': 'test123'})
token = login_response.json().get('token')
print(f'Token: {token[:20]}...')

# Get group
headers = {'Authorization': f'Bearer {token}'}
group_response = requests.get('http://127.0.0.1:5000/api/groups/1', headers=headers)
group = group_response.json()
print(f'Group ID: {group.get("id")}')
print(f'Group Name: {group.get("name")}')
print(f'Group Code: {group.get("code")}')
print(f'Full Response: {json.dumps(group, indent=2)}')
