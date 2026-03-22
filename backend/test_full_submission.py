#!/usr/bin/env python
"""Complete test of listing submission workflow"""
import os
import django
import json
import base64
from io import BytesIO
from PIL import Image

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ntub_usedbooks.settings')
django.setup()

from django.test import Client
from accounts.models import User, UserProfile
from core.models import ClassGroup

# Create test user
user, created = User.objects.get_or_create(
    username='submituser',
    defaults={
        'email': 'submituser@ntub.edu.tw',
        'first_name': 'Submit',
        'last_name': 'User'
    }
)
if created:
    user.set_password('testpass123')
    user.save()
    UserProfile.objects.get_or_create(user=user)
    print(f"✓ User created: {user.username}")
else:
    # Reset password
    user.set_password('testpass123')
    user.save()
    UserProfile.objects.get_or_create(user=user)
    print(f"✓ User exists: {user.username}")

# Get ClassGroup
class_group = ClassGroup.objects.first()
if not class_group:
    print("ERROR: No ClassGroups found!")
    exit(1)

print(f"✓ ClassGroup: {class_group.name_zh}")

# Create test images
def create_test_image():
    """Create a simple 1x1 PNG image"""
    img = Image.new('RGB', (100, 100), color='red')
    img_buffer = BytesIO()
    img.save(img_buffer, format='PNG')
    img_buffer.seek(0)
    base64_str = base64.b64encode(img_buffer.getvalue()).decode('utf-8')
    return f"data:image/png;base64,{base64_str}"

images = [create_test_image() for _ in range(3)]
print(f"✓ Created {len(images)} test images")

# Prepare submission data
submit_data = {
    "new_book": {
        "isbn13": "",
        "isbn10": "",
        "title": "測試提交的書籍",
        "author_display": "提交測試作者",
        "publisher": "測試出版社"
    },
    "origin_academic_year": 113,
    "origin_term": 1,
    "origin_class_group_id": class_group.id,
    "used_price": "399.00",
    "condition_level": "LIKE_NEW",
    "description": "這是一本通過完整流程提交的書籍",
    "seller_note": "無筆記",
    "images": images
}

print("\nSubmission Data:")
print(f"  Title: {submit_data['new_book']['title']}")
print(f"  Author: {submit_data['new_book']['author_display']}")
print(f"  Price: {submit_data['used_price']}")
print(f"  Images: {len(submit_data['images'])}")
print(f"  Class Group ID: {submit_data['origin_class_group_id']}")

# Use Django test client
client = Client()

# Login
login_success = client.login(username='submituser', password='testpass123')
print(f"\nLogin: {'✓' if login_success else '✗'}")

if not login_success:
    print("ERROR: Could not login!")
    exit(1)

# Get CSRF token from form
response = client.get('/api/listings/')
csrf_token = None
if 'csrftoken' in response.cookies:
    csrf_token = response.cookies['csrftoken'].value
    print(f"CSRF Token: {csrf_token[:20]}...")
else:
    print("No CSRF token found in response")

# Submit listing
print("\nSending POST request to /api/listings/...")
response = client.post(
    '/api/listings/',
    data=json.dumps(submit_data),
    content_type='application/json',
    HTTP_X_CSRFTOKEN=csrf_token or '',
)

print(f"Response Status: {response.status_code}")

if response.status_code in [200, 201]:
    try:
        response_data = response.json()
        if response_data.get('success'):
            print(f"✓ SUCCESS! Created listing ID: {response_data['data']['id']}")
            print(f"  Book ID: {response_data['data']['book']['id']}")
            print(f"  ISBN: {response_data['data']['book']['isbn13']}")
            print(f"  Images: {len(response_data['data']['images'])}")
        else:
            print(f"✗ Error in response:")
            print(json.dumps(response_data, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"✗ Could not parse response: {e}")
        print(f"Response body: {response.content}")
else:
    print(f"✗ HTTP Error {response.status_code}")
    try:
        print(f"Response: {response.json()}")
    except:
        print(f"Response: {response.content[:500]}")
