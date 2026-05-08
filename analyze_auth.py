#!/usr/bin/env python3
"""
Mass replace fetch() + Authorization with api.request()
This script identifies and converts fetch calls with Authorization headers
"""

import re

with open('script.js', 'r', encoding='utf-8') as f:
    content = f.read()

# Count before
before_count = content.count("'Authorization': `Bearer")
print(f"Found {before_count} Authorization header usages")

# Pattern 1: fetch with Authorization header as complete call
# This pattern matches:
# fetch(`...`, {
#     headers: { 'Authorization': ... },
#     ...
# })

patterns = [
    # Pattern for simple fetch with Authorization in headers object
    (
        r"fetch\(\`\$\{[^}]*\}/api([^`]*)\`\s*,\s*\{\s*(?:method:\s*['\"]([^'\"]*)['\"],\s*)?headers:\s*\{\s*'Content-Type':\s*'application/json',?\s*'Authorization':\s*`Bearer\s*\$\{token\}`\s*\},?(?:\s*body:\s*JSON\.stringify\(([^)]*)\))?\s*\}\)",
        lambda m: f"api.request('{m.group(2) or 'GET'}', '{m.group(1)}')" + (f", {m.group(3)}" if m.group(3) else "")
    ),
]

# Actually, let's do this differently - create a Python script to handle conversions more carefully
print("\nLet's check the context of these Authorization usages...")

# Find all Authorization lines with context
matches = list(re.finditer(r"Authorization.*Bearer", content))
print(f"Total matches: {len(matches)}")

# Sample a few
for i, match in enumerate(matches[:5]):
    start = max(0, match.start() - 200)
    end = min(len(content), match.end() + 200)
    context = content[start:end]
    line_num = content[:match.start()].count('\n') + 1
    print(f"\n--- Match {i+1} at line {line_num} ---")
    print(context)
    print("---")
