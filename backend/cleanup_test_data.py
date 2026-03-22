#!/usr/bin/env python
"""清理測試數據的腳本"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ntub_usedbooks.settings')
django.setup()

from listings.models import Listing, ListingImage
from books.models import Book

def cleanup():
    print("開始清理測試數據...")
    
    # 刪除所有測試 listings (由 testuser 建立)
    test_listings = Listing.objects.filter(seller__username='testuser')
    count = test_listings.count()
    test_listings.delete()
    print(f"✓ 已刪除 {count} 個測試刊登")
    
    # 刪除沒有任何 listings 的書籍
    orphaned_books = Book.objects.filter(listings__isnull=True)
    book_count = orphaned_books.count()
    orphaned_books.delete()
    print(f"✓ 已刪除 {book_count} 本孤立書籍")
    
    print(f"\n✓ 清理完成！")
    print(f"  - 剩餘刊登: {Listing.objects.count()}")
    print(f"  - 剩餘書籍: {Book.objects.count()}")

if __name__ == '__main__':
    cleanup()
