#!/usr/bin/env python
"""Populate test data - Simplified"""
import os
import django
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ntub_usedbooks.settings')
django.setup()

from django.db import transaction
from accounts.models import User, UserProfile
from core.models import Department, ProgramType, ClassGroup
from books.models import Book
from listings.models import Listing

@transaction.atomic
def populate_test_data():
    # 創建測試用戶
    print("Creating test user...")
    user, created = User.objects.get_or_create(
        username='testuser',
        defaults={'email': 'test@example.com', 'first_name': 'Test', 'last_name': 'User'}
    )
    print(f"  User: {user.username} ({'created' if created else 'exists'})")

    # 確保用戶有 Profile
    profile, created = UserProfile.objects.get_or_create(
        user=user,
        defaults={'display_name': 'Test Seller', 'student_id': 'B11234567'}
    )
    print(f"  Profile: {profile.display_name} ({'created' if created else 'exists'})")

    # 獲取或創建必要的核心數據
    print("\nSetting up core data...")
    try:
        program_type = ProgramType.objects.filter(is_active=True).first()
        if not program_type:
            program_type = ProgramType.objects.create(
                code='CB',
                name_zh='產業管理系',
                is_active=True
            )
            print(f"  Created ProgramType: {program_type.name_zh}")
        else:
            print(f"  Using existing ProgramType: {program_type.name_zh}")

        department = Department.objects.filter(is_active=True).first()
        if not department:
            department = Department.objects.create(
                code='IM',
                name_zh='產業管理系',
                program_type=program_type,
                is_active=True
            )
            print(f"  Created Department: {department.name_zh}")
        else:
            print(f"  Using existing Department: {department.name_zh}")

        class_group = ClassGroup.objects.filter(is_active=True).first()
        if not class_group:
            class_group = ClassGroup.objects.create(
                code='114A',
                name_zh='114年A班',
                grade_no=1,
                section_code='A',
                program_type=program_type,
                department=department,
                is_active=True
            )
            print(f"  Created ClassGroup: {class_group.name_zh}")
        else:
            print(f"  Using existing ClassGroup: {class_group.name_zh}")
    except Exception as e:
        print(f"  Warning: {e}")
        return

    # 創建測試書籍
    books_data = [
        {'title': '計算機概論', 'author': '劉邦俊', 'isbn13': '9789864345678'},
        {'title': 'Python 程式設計', 'author': 'Mark Lutz', 'isbn13': '9789876543210'},
        {'title': '數據結構與演算法', 'author': '郭瑞君', 'isbn13': '9789765432109'},
        {'title': '網頁設計基礎', 'author': '楊宗楷', 'isbn13': '9788765432100'},
        {'title': '資料庫管理系統', 'author': '黃宏燦', 'isbn13': '9877654321098'},
        {'title': 'JavaScript 完全指南', 'author': 'David Flanagan', 'isbn13': '9866543210987'},
    ]

    created_books = []
    print("\nCreating test books...")
    for data in books_data:
        book, created = Book.objects.get_or_create(
            title=data['title'],
            defaults={'author_display': data['author'], 'isbn13': data['isbn13']}
        )
        created_books.append(book)
        print(f"  {book.title} ({'created' if created else 'exists'})")

    # 創建測試 Listings
    print("\nCreating test listings...")
    for i, book in enumerate(created_books):
        listing, created = Listing.objects.get_or_create(
            book=book,
            seller=user,
            defaults={
                'origin_academic_year': 114,
                'origin_term': 1,
                'origin_class_group': class_group,
                'status': 'AVAILABLE',
                'used_price': 100 + (i * 50),
                'condition_level': ['LIKE_NEW', 'GOOD', 'FAIR', 'POOR'][i % 4],
            }
        )
        print(f"  {book.title} ({'created' if created else 'exists'}) - Price: ${listing.used_price}")

    print("\n✓ Test data created successfully!")

    # 驗證
    available = Listing.objects.filter(status='AVAILABLE', deleted_at__isnull=True).count()
    print(f"✓ Available listings in database: {available}")

if __name__ == '__main__':
    populate_test_data()
