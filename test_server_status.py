import requests
import time

# Test basic connectivity
print("Testing server connectivity...")
tests = [
    ('Home page', 'http://hesappaylas.com/'),
    ('API root', 'http://hesappaylas.com/api/'),
    ('Auth check phone', 'http://hesappaylas.com/api/auth/check-phone'),
]

for name, url in tests:
    try:
        r = requests.get(url, timeout=5)
        content_preview = r.text[:150].replace('\n', ' ')
        print(f"\n{name}: {r.status_code}")
        print(f"  Content-Type: {r.headers.get('content-type', 'N/A')}")
        print(f"  Preview: {content_preview}...")
    except requests.exceptions.Timeout:
        print(f"\n{name}: TIMEOUT")
    except Exception as e:
        print(f"\n{name}: ERROR - {str(e)[:100]}")
