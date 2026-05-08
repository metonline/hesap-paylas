import requests
import json

with open(r'c:\Users\metin\Desktop\BILL\script.js', 'r', encoding='utf-8') as f:
    content = f.read()

print(f"Uploading {len(content)} bytes of script.js...")

# Try to POST directly to the server's localhost:5001
# This needs to be run on the server or access the server's localhost
response = requests.post(
    'http://hesappaylas.com:5001/api/admin/update-script',
    json={'content': content},
    timeout=60
)
print(f"Status: {response.status_code}")
print(f"Response text: {response.text[:500]}")
if response.status_code == 200:
    try:
        print(f"Response JSON: {response.json()}")
    except:
        print("(No JSON response)")
else:
    print(f"Error: {response.text}")
