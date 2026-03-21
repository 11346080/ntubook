#!/usr/bin/env python
"""驗證 API 路由配置"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ntub_usedbooks.settings')
django.setup()

from django.urls import get_resolver

resolver = get_resolver()

print("=" * 60)
print("🔍 API Route Verification")
print("=" * 60)

# 檢查特定路由名稱
test_urls = [
    'api-listing-latest',
    'api-listing-list',
]

print("\n✓ Checking registered route names:")
for url_name in test_urls:
    try:
        pattern = resolver.reverse_dict[url_name]
        print(f"  ✓ '{url_name}' registered")
    except KeyError:
        print(f"  ✗ '{url_name}' NOT FOUND")

# 列出所有 API 路由
print("\n✓ All registered API routes:")
for pattern, callback, defaults in resolver.url_patterns:
    route_str = str(pattern.pattern)
    if 'api' in route_str or 'listings' in route_str:
        print(f"  {route_str}")

print("\n" + "=" * 60)
print("✓ Verification complete!")
print("=" * 60)
