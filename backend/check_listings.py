#!/usr/bin/env python
"""診斷腳本：檢查 Listing 記錄狀態"""
import os
import django

# 設定 Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ntub_usedbooks.settings')
django.setup()

from listings.models import Listing
from django.db.models import Count

# 檢查可購買的書籍數量
available = Listing.objects.filter(
    status=Listing.Status.AVAILABLE,
    deleted_at__isnull=True
).count()
print(f"✓ Available listings (AVAILABLE + not deleted): {available}")

# 所有書籍
total = Listing.objects.count()
print(f"✓ Total listings in DB: {total}")

# 按狀態統計
print("\nListings by status:")
statuses = Listing.objects.values('status').annotate(count=Count('id')).order_by('status')
for item in statuses:
    print(f"  - {item['status']}: {item['count']}")

# 檢查 Listing.Status 枚舉值
print("\nAvailable statuses in Listing.Status:")
for status in Listing.Status:
    print(f"  - {status.name}: {status.value}")

# 試試序列化
if available > 0:
    from listings.serializers import ListingLatestSerializer
    listings = Listing.objects.filter(
        status=Listing.Status.AVAILABLE,
        deleted_at__isnull=True
    ).select_related(
        'book',
        'seller',
        'seller__profile',
        'seller__profile__department'
    ).prefetch_related('images')[:1]
    
    serializer = ListingLatestSerializer(listings, many=True)
    print(f"\n✓ Sample serialized data:\n{serializer.data}")
else:
    print("\n⚠️ No available listings found!")
