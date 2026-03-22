#!/usr/bin/env python
"""Test listing creation without ISBN"""
import os
import django
import base64
import json
from io import BytesIO
from PIL import Image

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ntub_usedbooks.settings')
django.setup()

from accounts.models import User
from books.models import Book
from listings.models import Listing
from core.models import ClassGroup
from django.test import Client
from django.contrib.auth import authenticate

# Create test user
user, created = User.objects.get_or_create(
    username='testcreator',
    defaults={
        'email': 'creator@test.edu.tw',
        'first_name': 'Test',
        'last_name': 'Creator'
    }
)
print(f"User: {user.username} (created: {created})")

# Set password for testing
user.set_password('testpass123')
user.save()
print(f"Set password for user: {user.username}")

# Get class group
class_group = ClassGroup.objects.first()
if not class_group:
    print("ERROR: No class groups found!")
    exit(1)

print(f"Using class group: {class_group.name_zh}")

# Generate test images (simple 1x1 PNG)
def generate_test_image():
    """Generate a simple test image and return as base64"""
    img = Image.new('RGB', (100, 100), color='red')
    img_bytes = BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    base64_str = base64.b64encode(img_bytes.read()).decode('utf-8')
    return f"data:image/png;base64,{base64_str}"

# Prepare test data WITHOUT ISBN
test_data = {
    "new_book": {
        "isbn13": "",  # Empty ISBN - should generate placeholder
        "isbn10": "",
        "title": "手動建立的書籍",
        "author_display": "測試作者",
        "publisher": "測試出版社"
    },
    "origin_academic_year": 113,
    "origin_term": 1,
    "origin_class_group_id": class_group.id,
    "used_price": "350.00",
    "condition_level": "LIKE_NEW",
    "description": "這是一本手動建立的二手書",
    "seller_note": "無筆記",
    "images": [
        generate_test_image(),
        generate_test_image(),
        generate_test_image()
    ]
}

print(f"\nTest data prepared:")
print(f"  Book: {test_data['new_book']['title']}")
print(f"  Price: {test_data['used_price']}")
print(f"  Images: {len(test_data['images'])}")
print(f"  Class Group ID: {test_data['origin_class_group_id']}")

# Create test client
client = Client()

# Login user
login_ok = client.login(username='testcreator', password='testpass123')
print(f"\nLogin: {'✓' if login_ok else '✗'}")

if not login_ok:
    print("ERROR: Could not login user")
    exit(1)

# Send POST request to create listing
print("\nSending POST request to /api/listings/...")
response = client.post(
    '/api/listings/',
    data=json.dumps(test_data),
    content_type='application/json'
)

print(f"Response Status: {response.status_code}")

try:
    response_data = response.json()
    print(f"Response Data: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
    
    if response_data.get('success'):
        listing_id = response_data.get('data', {}).get('id')
        print(f"\n✓ SUCCESS! Created listing ID: {listing_id}")
        
        # Verify listing was created
        listing = Listing.objects.get(id=listing_id)
        print(f"\nListing Details:")
        print(f"  ID: {listing.id}")
        print(f"  Book: {listing.book.title}")
        print(f"  Book ISBN-13: {listing.book.isbn13}")
        print(f"  Status: {listing.status}")
        print(f"  Price: {listing.used_price}")
        print(f"  Condition: {listing.condition_level}")
        print(f"  Images: {listing.images.count()}")
    else:
        print(f"\n✗ FAILED: {response_data.get('error')}")
except Exception as e:
    print(f"Error parsing response: {e}")
    print(f"Response text: {response.content}")
