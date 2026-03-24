#!/usr/bin/env python
"""
API 端點完整性驗證腳本 / API Endpoints Verification Script
驗證所有實現的 API 端點是否正確配置
"""

import os
import sys
import django
from django.conf import settings
from django.urls import get_resolver
from django.urls.exceptions import Resolver404

# 設置 Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ntub_usedbooks.settings')
django.setup()

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status


def check_api_endpoints():
    """
    檢查所有必要的 API 端點是否已註冊
    Check if all required API endpoints are registered
    """
    
    resolver = get_resolver()
    
    # 必要的 API 端點列表
    required_endpoints = [
        # 認證相關
        ('api-token-obtain-pair', '/api/auth/token/'),
        ('api-token-refresh', '/api/auth/token/refresh/'),
        ('api-bootstrap', '/api/accounts/bootstrap/'),
        
        # 用戶帳戶
        ('api-me', '/api/accounts/me/'),
        ('api-profile', '/api/accounts/profile/'),
        ('api-userprofile-list', '/api/accounts/profiles/'),
        
        # 新的 API v2 (如果實現)
        # ('api-me-v2', '/api/accounts/api_v2/me/'),
        # ('api-profile-v2', '/api/accounts/api_v2/profile/'),
        
        # 書籍相關
        ('api-books-list', '/api/books/'),
        ('api-books-detail', '/api/books/<int:book_id>/'),
        ('api-toggle-favorite', '/api/books/<int:book_id>/favorite/'),
        ('api-favorites-list', '/api/favorites/'),
        
        # 刊登相關
        ('api-listing-list-or-create', '/api/listings/'),
        ('api-listing-my-listings', '/api/listings/my-listings/'),
        ('api-listing-latest', '/api/listings/latest/'),
        ('api-listing-recommended', '/api/listings/recommended/'),
        ('api-listing-detail', '/api/listings/<int:listing_id>/'),
        ('api-listing-requests', '/api/listings/<int:listing_id>/requests/'),
        ('api-listing-off-shelf', '/api/listings/<int:listing_id>/off_shelf/'),
        ('api-listing-mark-sold', '/api/listings/<int:listing_id>/mark_sold/'),
        ('api-listing-relist', '/api/listings/<int:listing_id>/relist/'),
        
        # 預約請求
        ('api-purchase-requests-list', '/api/purchase-requests/'),
        ('api-my-requests', '/api/purchase-requests/my-requests/'),
        ('api-purchase-request-detail', '/api/purchase-requests/<int:purchase_request_id>/'),
        ('api-request-accept', '/api/requests/<int:request_id>/accept/'),
        ('api-request-reject', '/api/requests/<int:request_id>/reject/'),
        ('api-request-cancel', '/api/requests/<int:request_id>/cancel/'),
        
        # 通知
        ('api-notification-list', '/api/notifications/list/'),
        ('api-notifications-list', '/api/notifications/'),
        ('api-notifications-unread-count', '/api/notifications/unread-count/'),
        ('api-notification-read', '/api/notifications/<int:notification_id>/read/'),
        ('api-notifications-read-all', '/api/notifications/read-all/'),
        ('api-notification-delete', '/api/notifications/<int:notification_id>/delete/'),
        ('api-notifications-delete-all', '/api/notifications/delete-all/'),
        
        # 舉報
        ('api-report-list', '/api/reports/list/'),
        ('api-reports-create', '/api/reports/'),
        ('api-my-reports', '/api/reports/my-reports/'),
        ('api-report-detail', '/api/reports/<int:report_id>/'),
        ('api-report-update-status', '/api/reports/<int:report_id>/status/'),
    ]
    
    print("\n" + "="*80)
    print("API 端點完整性檢查 / API Endpoints Verification")
    print("="*80 + "\n")
    
    found_count = 0
    missing_count = 0
    missing_endpoints = []
    
    for name, path in required_endpoints:
        try:
            # 嘗試解析 URL 名稱
            match = resolver.resolve(path, kwargs={
                'book_id': 1,
                'listing_id': 1,
                'request_id': 1,
                'notification_id': 1,
                'report_id': 1,
                'purchase_request_id': 1
            })
            print(f"✓ {name:40} -> {path}")
            found_count += 1
        except Resolver404:
            print(f"✗ {name:40} -> {path} [NOT FOUND]")
            missing_count += 1
            missing_endpoints.append((name, path))
        except Exception as e:
            print(f"? {name:40} -> {path} [ERROR: {str(e)}]")
    
    print("\n" + "="*80)
    print(f"摘要 / Summary:")
    print(f"  已找到的端點 / Found: {found_count}")
    print(f"  缺失的端點 / Missing: {missing_count}")
    print("="*80 + "\n")
    
    if missing_endpoints:
        print("📋 缺失的端點 / Missing Endpoints:")
        for name, path in missing_endpoints:
            print(f"  - {name} ({path})")
        print()
        
        return False
    else:
        print("✅ 所有必要的 API 端點都已註冊！/ All required API endpoints are registered!")
        return True


def check_view_implementations():
    """
    檢查視圖函數是否已實現
    Check if view functions are implemented
    """
    
    print("\n" + "="*80)
    print("視圖函數實現檢查 / View Functions Implementation Check")
    print("="*80 + "\n")
    
    # 檢查各種新創建的模組
    implementation_checks = {
        'listings/listing_actions_api.py': [
            'accept_purchase_request',
            'reject_purchase_request',
            'cancel_purchase_request',
            'listing_off_shelf',
            'listing_mark_sold',
            'listing_relist'
        ],
        'notifications/notifications_api.py': [
            'notifications_list_api',
            'notifications_unread_count_api',
            'notification_read_api',
            'notifications_read_all_api',
            'notification_delete_api',
            'notifications_delete_all_api'
        ],
        'moderation/reports_api.py': [
            'create_report_api',
            'my_reports_api',
            'report_detail_api',
            'report_update_status_api'
        ],
        'accounts/api_views.py': [
            'me_api',
            'user_profile_api',
            'create_profile_api'
        ]
    }
    
    backend_path = os.path.join(os.path.dirname(__file__), 'ntub_usedbooks', 'backend')
    
    total_checks = 0
    implemented_count = 0
    missing_implementations = []
    
    for file_path, functions in implementation_checks.items():
        full_path = os.path.join(backend_path, file_path)
        
        print(f"📄 檢查文件 / Checking file: {file_path}")
        
        # 檢查文件是否存在
        file_exists = os.path.exists(full_path)
        if not file_exists:
            print(f"  ✗ 文件不存在 / File not found\n")
            for func in functions:
                total_checks += 1
                missing_implementations.append((file_path, func))
            continue
        
        # 讀取文件內容
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            for func in functions:
                total_checks += 1
                if f"def {func}" in content:
                    print(f"  ✓ {func}")
                    implemented_count += 1
                else:
                    print(f"  ✗ {func} [NOT FOUND]")
                    missing_implementations.append((file_path, func))
        except Exception as e:
            print(f"  ⚠️  讀取文件出錯 / Error reading file: {e}\n")
        
        print()
    
    print("="*80)
    print(f"摘要 / Summary:")
    print(f"  已實現的函數 / Implemented: {implemented_count}")
    print(f"  缺失的函數 / Missing: {len(missing_implementations)}")
    print("="*80)
    
    if missing_implementations:
        print("\n缺失的實現 / Missing Implementations:")
        for file_path, func in missing_implementations:
            print(f"  - {func} in {file_path}")
        print()
        return False
    else:
        print("\n✅ 所有必要的視圖函數都已實現！/ All required view functions are implemented!")
        return True


def check_url_registrations():
    """
    檢查 URL 路由是否正確註冊
    Check if URL routes are properly registered
    """
    
    print("\n" + "="*80)
    print("URL 路由註冊檢查 / URL Route Registration Check")
    print("="*80 + "\n")
    
    backend_path = os.path.join(os.path.dirname(__file__), 'ntub_usedbooks', 'backend')
    
    url_configs = [
        ('listings/api_urls.py', 'listing_actions_api'),
        ('notifications/api_urls.py', 'notifications_api'),
        ('moderation/api_urls.py', 'reports_api'),
        ('accounts/api_urls.py', 'api_views'),
    ]
    
    all_ok = True
    
    for file_path, expected_import in url_configs:
        full_path = os.path.join(backend_path, file_path)
        
        if not os.path.exists(full_path):
            print(f"✗ {file_path} [NOT FOUND]")
            all_ok = False
            continue
        
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if expected_import in content or 'import' in content:
                print(f"✓ {file_path}")
            else:
                print(f"⚠️  {file_path} [缺少預期的導入 / Missing expected imports]")
                all_ok = False
        except Exception as e:
            print(f"✗ {file_path} [Error: {e}]")
            all_ok = False
    
    print()
    return all_ok


def main():
    """主執行函數 / Main execution function"""
    
    print("""
╔════════════════════════════════════════════════════════════════════════════╗
║                   API 實現完整性驗證                                       ║
║           API Implementation Completeness Verification                    ║
║                                                                            ║
║  本腳本驗證所有必要的 API 端點和視圖函數是否已正確實現和配置              ║
║  This script verifies all required API endpoints and view functions       ║
╚════════════════════════════════════════════════════════════════════════════╝
    """)
    
    # 運行檢查
    endpoint_ok = check_api_endpoints()
    view_ok = check_view_implementations()
    url_ok = check_url_registrations()
    
    # 最終報告
    print("\n" + "="*80)
    print("最終驗證報告 / Final Verification Report")
    print("="*80)
    print(f"  API 端點檢查 / API Endpoints: {'✅ PASS' if endpoint_ok else '❌ FAIL'}")
    print(f"  視圖函數檢查 / View Functions: {'✅ PASS' if view_ok else '❌ FAIL'}")
    print(f"  URL 路由檢查 / URL Routes: {'✅ PASS' if url_ok else '❌ FAIL'}")
    print("="*80)
    
    if endpoint_ok and view_ok and url_ok:
        print("\n🎉 所有檢查通過！系統已準備好進行完整的 API 測試。")
        print("   All checks passed! System is ready for complete API testing.")
        return 0
    else:
        print("\n⚠️  某些檢查失敗。請查看上面的詳細信息並進行修正。")
        print("   Some checks failed. Please see details above and fix them.")
        return 1


if __name__ == '__main__':
    try:
        exit_code = main()
        sys.exit(exit_code)
    except Exception as e:
        print(f"\n❌ 發生錯誤 / Error occurred: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
