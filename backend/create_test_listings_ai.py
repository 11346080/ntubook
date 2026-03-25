#!/usr/bin/env python
"""
创建测试刊登用于 AI 审查演示
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ntub_usedbooks.settings')
django.setup()

from listings.models import Listing
from books.models import Book
from core.models import ClassGroup, Department
from accounts.models import User

# 創建測試用戶
user, _ = User.objects.get_or_create(
    username='test_seller_ai',
    defaults={'email': 'test@test.com', 'is_active': True}
)

# 獲取現有的 Department（或使用第一個）
dept = Department.objects.first()
if not dept:
    print('❌ 錯誤: 資料庫中沒有系所資料，請先執行 migrate 和填充基本資料')
    exit(1)

# 獲取該系所的班級（或使用第一個）
class_group = ClassGroup.objects.filter(department=dept).first()
if not class_group:
    print('❌ 錯誤: 資料庫中沒有班級資料')
    exit(1)

# 創建或獲取書籍
book, _ = Book.objects.get_or_create(
    title='未來的人工智能',
    defaults={
        'isbn13': 'TEST-AI-' + str(Listing.objects.count()),
        'isbn10': 'TEST-AI',
        'author_display': '測試作者',
        'publisher': '測試出版社',
        'publication_year': 2024
    }
)

# 清除舊的待審查刊登
Listing.objects.filter(status=Listing.Status.PENDING, seller=user).delete()

# 創建待審查刊登 (好的內容)
listing1 = Listing.objects.create(
    seller=user,
    book=book,
    origin_academic_year=113,
    origin_term=1,
    origin_class_group=class_group,
    used_price=350.00,
    description='這是一本很好的人工智能書籍，內容深入淺出，非常適合初學者和進階者閱讀。推薦購買！',
    status=Listing.Status.PENDING
)

print(f'✓ 已建立好內容待審查刊登: ID={listing1.id}')
print(f'  標題: {listing1.book.title}')
print(f'  描述: {listing1.description}')

# 創建待審查刊登 (壞的內容)
listing2 = Listing.objects.create(
    seller=user,
    book=book,
    origin_academic_year=113,
    origin_term=1,
    origin_class_group=class_group,
    used_price=200.00,
    description='爛透了的垃圾書，完全是浪費錢。該死的內容，非常糟糕。',
    status=Listing.Status.PENDING
)

print(f'\n✓ 已建立壞內容待審查刊登: ID={listing2.id}')
print(f'  標題: {listing2.book.title}')
print(f'  描述: {listing2.description}')

pending_count = Listing.objects.filter(status=Listing.Status.PENDING).count()
print(f'\n總共 {pending_count} 個待審查刊登')
