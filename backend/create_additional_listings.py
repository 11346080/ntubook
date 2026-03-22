#!/usr/bin/env python
"""Create additional test listings to improve testing"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ntub_usedbooks.settings')
django.setup()

from accounts.models import User
from books.models import Book
from listings.models import Listing
from core.models import ClassGroup

# Get or create user
user, _ = User.objects.get_or_create(
    username='testuser',
    defaults={'email': 'testuser@ntub.edu.tw', 'first_name': 'Test', 'last_name': 'User'}
)

# Test books with different conditions
books_data = [
    {'isbn13': '978-7-115-47849-9', 'title': '深入淺出 Python', 'author_display': 'Bill Lubanovic'},
    {'isbn13': '978-7-111-59261-5', 'title': '算法圖解', 'author_display': 'Adit Bhargava'},
    {'isbn13': '978-7-121-35937-4', 'title': '代碼整潔之道', 'author_display': 'Robert Martin'},
]

# Get existing Classgroup
class_groups = ClassGroup.objects.all()[:3]
if not class_groups:
    print("ERROR: No ClassGroups found!")
    exit(1)

# Create books and listings
for idx, book_data in enumerate(books_data):
    book, created = Book.objects.get_or_create(
        isbn13=book_data['isbn13'],
        defaults={
            'title': book_data['title'],
            'author_display': book_data['author_display'],
            'publisher': 'Tech Publishing',
            'publication_year': 2020 + idx,
            'metadata_source': Book.MetadataSource.MANUAL,
            'metadata_status': Book.MetadataStatus.MANUALLY_CONFIRMED
        }
    )
    print(f"Book: {book.title} {'created' if created else 'exists'} (ID: {book.id})")
    
    # Create listing with different conditions
    class_group = class_groups[idx % len(class_groups)]
    condition = [Listing.ConditionLevel.LIKE_NEW, Listing.ConditionLevel.GOOD, Listing.ConditionLevel.FAIR][idx]
    price = 300 - (idx * 30)
    
    listing, created = Listing.objects.get_or_create(
        seller=user,
        book=book,
        origin_academic_year=113,
        origin_term=1,
        origin_class_group=class_group,
        defaults={
            'condition_level': condition,
            'used_price': price,
            'status': Listing.Status.AVAILABLE,
            'description': f'Test listing #{idx+1} - Used condition: {condition}'
        }
    )
    print(f"  → Listing: {'created' if created else 'exists'} (ID: {listing.id}, Price: {price}, Condition: {condition})")

# Verify total count
total = Listing.objects.filter(status=Listing.Status.AVAILABLE).count()
print(f"\n✅ Total AVAILABLE listings: {total}")
