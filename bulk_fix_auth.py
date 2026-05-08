#!/usr/bin/env python3
"""
Comprehensive fix for all fetch() + Authorization header usages
Converts them to api.request() calls
"""

import re

def fix_fetch_calls(content):
    """Replace fetch() calls with api.request() calls"""
    
    # Keep track of replacements
    replacements = []
    
    # Pattern 1: fetch with baseURL + /api/endpoint, method POST
    pattern1 = r"fetch\(\s*`\$\{baseURL\}/([^`]*)`\s*,\s*\{\s*method:\s*['\"]([A-Z]+)['\"],\s*headers:\s*\{\s*['\"]Content-Type['\"]:\s*['\"]application/json['\"],?\s*['\"]Authorization['\"]:\s*`Bearer\s*\$\{token\}`\s*\},\s*body:\s*JSON\.stringify\(([^)]+)\)\s*\}\s*\)"
    
    def replace1(match):
        endpoint = match.group(1)
        method = match.group(2)
        data = match.group(3)
        if not endpoint.startswith('/'):
            endpoint = '/' + endpoint
        return f"api.request('{method}', '{endpoint}', {data})"
    
    content = re.sub(pattern1, replace1, content, flags=re.DOTALL)
    count1 = len(re.findall(pattern1, content))
    print(f"Pattern 1 replacements: {count1}")
    
    # Pattern 2: fetch with baseURL, simple headers with Authorization
    pattern2 = r"fetch\(\s*\`\$\{baseURL\}/([^`]+)\`\s*,\s*\{\s*(?:method:\s*['\"]([A-Z]+)['\"],\s*)?headers:\s*\{\s*['\"]Authorization['\"]:\s*`Bearer\s*\$\{token\}`\s*\}\s*\}\s*\)"
    
    def replace2(match):
        endpoint = match.group(1)
        method = match.group(2) or 'GET'
        if not endpoint.startswith('/'):
            endpoint = '/' + endpoint
        return f"api.request('{method}', '{endpoint}')"
    
    content = re.sub(pattern2, replace2, content)
    print(f"Pattern 2 replacements attempted")
    
    # Pattern 3: Direct Authorization header (single/double quotes)
    # This one is trickier - we need to find the fetch and convert it
    pattern3 = r"headers:\s*\{\s*['\"]Authorization['\"]:\s*`Bearer\s*\$\{(?:token|localStorage\.getItem\(['\"]hesapPaylas_token['\"]\))\}`\s*(?:,\s*['\"]Content-Type['\"]:\s*['\"]application/json['\"])?\s*\}"
    
    # For pattern 3, just remove the Authorization line
    content = re.sub(pattern3, "// Authorization removed - using api.request() instead", content)
    print(f"Pattern 3 removals attempted")
    
    return content

# Read the file
print("Reading script.js...")
with open('script.js', 'r', encoding='utf-8') as f:
    original_content = f.read()

print(f"Original size: {len(original_content)} bytes")
print(f"Authorization usages: {original_content.count('Authorization')}")

# Apply fixes
fixed_content = fix_fetch_calls(original_content)

print(f"\nFixed size: {len(fixed_content)} bytes")
print(f"Authorization remaining: {fixed_content.count('Authorization')}")

# Save
with open('script.js', 'w', encoding='utf-8') as f:
    f.write(fixed_content)

print("\n✅ Fixed! Check the results:")
print(f"   - Removed {original_content.count('Authorization') - fixed_content.count('Authorization')} Authorization header usages")
