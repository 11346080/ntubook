import requests
import json
import html
import re

url = 'http://localhost:8000/api/accounts/bootstrap/'
headers = {
    'Content-Type': 'application/json',
    'X-Bootstrap-Secret': '0gxhtMfxRQIW5UT8nNiGqLNspyBOUeXwoEuKlk25Uj0',
}
data = {
    'google_sub': 'test123',
    'email': 'test@ntub.edu.tw',
    'name': 'Test User',
}

response = requests.post(url, headers=headers, json=data, timeout=5)
print(f"Status: {response.status_code}")
print(f"Content-Type: {response.headers.get('content-type')}")
print()

if 'html' in response.headers.get('content-type', ''):
    # Parse the error page
    title_match = re.search(r'<title>(.*?)</title>', response.text)
    if title_match:
        title = html.unescape(title_match.group(1))
        print(f"Error Title: {title}")
    
    # Find traceback table
    traceback_match = re.search(r'<table border="0" cellpadding="0" cellspacing="0">(.*?)</table>', response.text, re.DOTALL)
    if traceback_match:
        print("\n=== Django Traceback ===")
        # Clean up and print just the key parts
        tb = traceback_match.group(1)
        # Extract file paths and line info
        file_matches = re.findall(r'<tr><td.*?<code>(.*?)</code>', tb)
        for f in file_matches[:5]:  # Show first 5
            print(f)
    
    # Find exception details
    exc_match = re.search(r'<h3 class="exception_value">(.*?)</h3>', response.text, re.DOTALL)
    if exc_match:
        exc = html.unescape(exc_match.group(1)).strip()
        print(f"\nException Message: {exc}")
    
    # Try to get more context
    context_matches = re.findall(r'<div class="context".*?>(.*?)</div>', response.text, re.DOTALL)
    if context_matches:
        print(f"\nContext: {context_matches[0][:500]}")
else:
    print("Response:", response.text[:500])
