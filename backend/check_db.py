#!/usr/bin/env python
"""Check database listings"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ntub_usedbooks.settings')
django.setup()

from listings.models import Listing
from books.models import Book
from accounts.models import User

# 檢查用戶
users = User.objects.all()
print(f"✓ Total users: {users.count()}")

# 檢查書籍
books = Book.objects.all()
print(f"✓ Total books: {books.count()}")

# 檢查 Listings
all_listings = Listing.objects.all()
print(f"✓ Total listings: {all_listings.count()}")

# 檢查可購買的 Listings
available = Listing.objects.filter(status='AVAILABLE', deleted_at__isnull=True)
print(f"✓ Available listings: {available.count()}")

# 列出所有狀態
from django.db.models import Count
statuses = Listing.objects.values('status').annotate(count=Count('id'))
print("\nListings by status:")
for item in statuses:
    print(f"  - {item['status']}: {item['count']}")

# 如果有任何 listing，顯示第一個
if all_listings.exists():
    listing = all_listings.first()
    print(f"\nFirst listing: ID={listing.id}, Status={listing.status}, Deleted={listing.deleted_at}")
