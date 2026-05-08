import requests
import json

# Test with small payload
test_payload = {
    'content': 'TEST CONTENT - This is a test to verify the endpoint works'
}

print("Testing admin endpoint with small payload...")
response = requests.post(
    'http://hesappaylas.com/api/admin/update-script',
    json=test_payload,
    timeout=10,
    headers={'Content-Type': 'application/json'}
)

print(f"Status: {response.status_code}")
print(f"Content-Type: {response.headers.get('content-type')}")
print(f"Content-Length: {len(response.text)}")
print(f"Full response text:\n{response.text}")

# Also check headers
print(f"\nAll response headers:")
for key, value in response.headers.items():
    print(f"  {key}: {value}")
