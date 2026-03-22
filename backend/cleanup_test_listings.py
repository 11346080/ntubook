#!/usr/bin/env python
"""
刪除所有測試刊登資料的腳本
Script to delete all test listings
"""
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ntub_usedbooks.settings')

import django
django.setup()

from listings.models import Listing, ListingImage

def cleanup():
    """刪除所有刊登和關聯的圖片"""
    # 先刪除所有 ListingImage
    listing_images = ListingImage.objects.all()
    count_images = listing_images.count()
    listing_images.delete()
    print(f"✓ 已刪除 {count_images} 張刊登圖片")
    
    # 再刪除所有 Listing
    listings = Listing.objects.all()
    count_listings = listings.count()
    listings.delete()
    print(f"✓ 已刪除 {count_listings} 個刊登")
    
    print("\n清理完成！")

if __name__ == '__main__':
    confirm = input("確定要刪除所有刊登資料嗎？(yes/no): ")
    if confirm.lower() == 'yes':
        cleanup()
    else:
        print("已取消")
