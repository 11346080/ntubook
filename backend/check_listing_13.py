#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ntub_usedbooks.settings')
django.setup()

from listings.models import Listing, ListingImage

try:
    listing = Listing.objects.get(id=13)
    images = listing.images.all()
    print(f"✓ Listing 13 found: {listing.book.title}")
    print(f"  Images count: {images.count()}")
    for img in images:
        print(f"  - File path: {img.file_path}")
except Listing.DoesNotExist:
    print("✗ Listing 13 not found in database")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
