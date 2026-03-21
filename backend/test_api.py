#!/usr/bin/env python
"""Test API connectivity"""
import requests

try:
    print("Testing API endpoint...")
    response = requests.get('http://localhost:8000/api/listings/latest/', timeout=5)
    print(f'✓ Status Code: {response.status_code}')
    print(f'✓ Response: {response.text[:300]}')
except ConnectionRefusedError:
    print('✗ Connection refused - Django server may not be running on port 8000')
except Exception as e:
    print(f'✗ Error: {type(e).__name__}: {e}')
