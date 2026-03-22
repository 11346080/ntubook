#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ntub_usedbooks.settings')
django.setup()

from accounts.models import User
from books.models import Book
from listings.models import Listing, ListingImage
from core.models import ClassGroup

# Create or get test user
user, created = User.objects.get_or_create(
    username='testuser',
    defaults={
        'email': 'testuser@ntub.edu.tw',
        'first_name': 'Test',
        'last_name': 'User'
    }
)
print(f"User (testuser): {'created' if created else 'existing'} - ID: {user.id}")

# Create or get test book
book, created = Book.objects.get_or_create(
    isbn13='978-7-519-05658-1',
    defaults={
        'title': 'Python 程式設計',
        'author_display': 'Guido van Rossum',
        'publisher': 'O Reilly Media',
        'publication_year': 2022,
        'metadata_source': Book.MetadataSource.MANUAL,
        'metadata_status': Book.MetadataStatus.MANUALLY_CONFIRMED
    }
)
print(f"Book (Python 程式設計): {'created' if created else 'existing'} - ID: {book.id}")

# Get existing ClassGroup (ID 277 from our earlier query)
try:
    class_group = ClassGroup.objects.get(id=277)
    print(f"ClassGroup found: {class_group.code} - {class_group.name_zh} (ID: {class_group.id})")
except ClassGroup.DoesNotExist:
    print("ERROR: ClassGroup 277 not found!")
    exit(1)

# Create listing
listing, created = Listing.objects.get_or_create(
    seller=user,
    book=book,
    origin_academic_year=113,
    origin_term=1,
    origin_class_group=class_group,
    defaults={
        'condition_level': Listing.ConditionLevel.LIKE_NEW,
        'used_price': 250,
        'status': Listing.Status.AVAILABLE,
        'description': 'Very clean, minimal notes. Only used for one semester.'
    }
)
print(f"Listing: {'created' if created else 'existing'} - ID: {listing.id}, Status: {listing.status}")

# Verify the listing is retrievable
count = Listing.objects.filter(status='AVAILABLE').count()
print(f"\nTotal AVAILABLE listings in database: {count}")

# Test the API endpoint would return
from listings.serializers import ListingLatestSerializer
if created:
    serializer = ListingLatestSerializer(listing)
    print(f"\nSerializer output: {serializer.data}")
