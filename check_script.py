import re

with open('script.js', 'r', encoding='utf-8') as f:
    content = f.read()

print(f"File size: {len(content)} bytes")
print(f"api.request() count: {content.count('api.request(')}")

# Find loadActiveGroups function
match = re.search(r'function loadActiveGroups\(\)\s*\{', content)
if match:
    start = match.start()
    # Find matching closing brace
    brace_count = 0
    in_string = False
    string_char = None
    for i in range(match.end() - 1, len(content)):
        c = content[i]
        if c in ('"', "'", '`') and content[i-1] != '\\':
            if not in_string:
                in_string = True
                string_char = c
            elif c == string_char:
                in_string = False
        
        if not in_string:
            if c == '{':
                brace_count += 1
            elif c == '}':
                brace_count -= 1
                if brace_count == 0:
                    end = i + 1
                    break
    
    func_content = content[start:end]
    
    if 'api.request' in func_content:
        print('✅ loadActiveGroups: Uses api.request()')
    elif 'fetch(' in func_content and 'Authorization' in func_content:
        print('❌ loadActiveGroups: Uses fetch() with Authorization (WRONG!)')
        # Show problematic line
        for line in func_content.split('\n'):
            if 'Authorization' in line:
                print(f"   Problem line: {line.strip()[:100]}")
    else:
        print('⚠️ loadActiveGroups: Unknown format')
else:
    print("❌ loadActiveGroups function not found!")
