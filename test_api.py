import requests

# Test if API is responding
try:
    r = requests.get('http://hesappaylas.com/api/test', timeout=10)
    print(f'Status: {r.status_code}')
    print(f'Content type: {r.headers.get("content-type")}')
    print(f'First 300 chars: {r.text[:300]}')
except Exception as e:
    print(f'Error: {e}')
