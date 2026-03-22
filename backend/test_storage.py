#!/usr/bin/env python
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ntub_usedbooks.settings')
django.setup()

from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import base64
from PIL import Image
from io import BytesIO

# Create a test image
img = Image.new('RGB', (100, 100), color='red')
img_bytes = BytesIO()
img.save(img_bytes, format='JPEG')
img_bytes.seek(0)

# Try to save it
test_file_path = 'test_listings/test_image.jpg'
try:
    file = ContentFile(img_bytes.read(), name='test_image.jpg')
    saved_path = default_storage.save(test_file_path, file)
    print(f"✓ File saved successfully!")
    print(f"  Saved path: {saved_path}")
    
    # Check if file exists
    if default_storage.exists(saved_path):
        print(f"  ✓ File exists in storage")
    else:
        print(f"  ✗ File not found after saving")
        
    # Check filesystem
    from django.conf import settings
    full_path = os.path.join(settings.MEDIA_ROOT, saved_path)
    print(f"  Full path: {full_path}")
    if os.path.exists(full_path):
        print(f"  ✓ File exists on filesystem")
        print(f"  File size: {os.path.getsize(full_path)} bytes")
    else:
        print(f"  ✗ File not found on filesystem")
        
except Exception as e:
    print(f"✗ Error saving file: {e}")
    import traceback
    traceback.print_exc()
