#!/usr/bin/env python
"""
驗證個人主頁是否正確顯示待審核刊登 / Verify PENDING listings are shown in user dashboard
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ntub_usedbooks.settings')
django.setup()

from django.contrib.auth import get_user_model
from listings.models import Listing
from rest_framework.test import APIClient
import json

User = get_user_model()

def test_pending_listings_in_dashboard():
    """測試 PENDING 刊登是否在個人主頁顯示"""
    
    print("\n" + "="*60)
    print("驗證個人主頁待審核刊登顯示功能")
    print("="*60)
    
    # 1. 檢查資料庫中是否有 PENDING 刊登
    print("\n📋 檢查資料庫中的刊登狀態分佈：")
    status_counts = {}
    for status in Listing.Status.choices:
        count = Listing.objects.filter(status=status[0]).count()
        status_counts[status[0]] = count
        print(f"  {status[0]:15} : {count:3} 筆")
    
    pending_count = Listing.objects.filter(status=Listing.Status.PENDING).count()
    print(f"\n  📌 待審核 (PENDING): {pending_count} 筆")
    
    if pending_count == 0:
        print("  ⚠️  資料庫中沒有 PENDING 刊登，跳過 API 測試")
        print("\n  💡 提示: 如果要測試，請先創建一個 PENDING 刊登")
        return
    
    # 2. 取得第一個 PENDING 刊登的賣家
    pending_listing = Listing.objects.filter(status=Listing.Status.PENDING).first()
    seller = pending_listing.seller
    
    print(f"\n📊 測試刊登：'{pending_listing.book.title if pending_listing.book else '未知'}'")
    print(f"   賣家: {seller.email}")
    print(f"   狀態: {pending_listing.status}")
    print(f"   建立時間: {pending_listing.created_at}")
    
    # 3. 使用 API Client 測試 my-listings 端點
    print("\n🔗 測試 API 端點: /api/listings/my-listings/")
    
    client = APIClient()
    
    # 強制登入測試用戶
    client.force_authenticate(user=seller)
    
    response = client.get('http://localhost:8000/api/listings/my-listings/')
    
    if response.status_code != 200:
        print(f"  ❌ API 返回錯誤碼: {response.status_code}")
        print(f"     response: {response.content}")
        return
    
    print(f"  ✓ API 返回狀態碼: {response.status_code}")
    
    # 4. 驗證 PENDING 刊登是否在返回的列表中
    data = response.json()
    listings = data if isinstance(data, list) else data.get('data', [])
    
    print(f"\n📦 API 返回的刊登數: {len(listings)} 筆")
    
    # 分析返回的刊登狀態
    returned_status_counts = {}
    for listing in listings:
        status = listing.get('status', 'UNKNOWN')
        returned_status_counts[status] = returned_status_counts.get(status, 0) + 1
    
    print(f"\n   返回的刊登狀態分佈：")
    for status, count in sorted(returned_status_counts.items()):
        print(f"     {status:15} : {count:3} 筆")
    
    # 檢查是否包含 PENDING
    pending_in_api = returned_status_counts.get('PENDING', 0)
    if pending_in_api > 0:
        print(f"\n   ✅ API 正確返回了 {pending_in_api} 筆 PENDING 刊登")
        
        # 列出 PENDING 的刊登
        print(f"\n   待審核刊登列表：")
        for listing in listings:
            if listing.get('status') == 'PENDING':
                print(f"     - ID:{listing['id']:4} | {listing['book']['title'][:20]:<20} | 價格: NT${listing['used_price']}")
    else:
        print(f"\n   ❌ API 未返回任何 PENDING 刊登!")
        print(f"      預期: {pending_count} 筆 PENDING")
        print(f"      實際: 0 筆")
    
    # 5. 檢查序列化器是否包含 PENDING 狀態
    print(f"\n🔍 檢查 Listing.Status 枚舉：")
    available_statuses = [s[0] for s in Listing.Status.choices]
    print(f"   可用狀態: {', '.join(available_statuses)}")
    
    if 'PENDING' in available_statuses:
        print(f"   ✓ PENDING 在可用狀態中")
    else:
        print(f"   ❌ PENDING 不在可用狀態中 (這是個問題!)")
    
    # 6. 前端驗證提示
    print(f"\n🎨 前端驗證提示：")
    print(f"   如果上面 API 測試通過，在前端 Dashboard 中應該能看到：")
    print(f"   - 我刊登的藏書 tab 中包含 PENDING (標籤: 審核中) 的刊登")
    print(f"   - 刊登卡片上顯示 '審核中' 的黃色標籤")
    print(f"   - 個人資料左上角的「已刊登」統計數字應該包含 PENDING")
    
    print("\n" + "="*60)
    print(f"驗證完成!")
    print("="*60 + "\n")

if __name__ == '__main__':
    test_pending_listings_in_dashboard()
