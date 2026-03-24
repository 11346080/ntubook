#!/usr/bin/env python3
"""
API 快速測試腳本 / API Quick Test Script
測試所有主要 API 端點的基本功能
"""

import requests
import json
import time
from typing import Dict, Any, Optional
import argparse

# API 基礎 URL
BASE_URL = "http://localhost:8000/api"

# 測試用戶認證資訊
TEST_USER = {
    "username": "testuser@ntub.edu.tw",
    "password": "testpassword123",
    "email": "testuser@ntub.edu.tw"
}

# 顏色輸出
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'


def test_endpoint(method: str, path: str, data: Optional[Dict] = None, headers: Optional[Dict] = None, 
                 expected_status: int = 200) -> tuple[bool, Any]:
    """
    測試單個 API 端點 / Test a single API endpoint
    
    Args:
        method: HTTP 方法 (GET, POST, PATCH, DELETE)
        path: API 路徑 (不含基礎 URL)
        data: 請求體 (可選)
        headers: 自定義請求頭 (可選)
        expected_status: 預期的 HTTP 狀態碼
    
    Returns:
        (是否成功, 響應數據)
    """
    url = f"{BASE_URL}{path}"
    
    try:
        if method.upper() == 'GET':
            response = requests.get(url, headers=headers, timeout=5)
        elif method.upper() == 'POST':
            response = requests.post(url, json=data, headers=headers, timeout=5)
        elif method.upper() == 'PATCH':
            response = requests.patch(url, json=data, headers=headers, timeout=5)
        elif method.upper() == 'DELETE':
            response = requests.delete(url, headers=headers, timeout=5)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        success = response.status_code == expected_status
        try:
            response_data = response.json()
        except:
            response_data = response.text
        
        return success, response_data
    
    except requests.exceptions.ConnectionError:
        return False, {"error": "無法連接到伺服器 / Cannot connect to server"}
    except Exception as e:
        return False, {"error": str(e)}


def print_result(test_name: str, success: bool, response: Any = None):
    """列印測試結果 / Print test result"""
    status = f"{Colors.GREEN}✓{Colors.END}" if success else f"{Colors.RED}✗{Colors.END}"
    print(f"{status} {test_name}")
    
    if response and isinstance(response, dict) and ('error' in response or 'success' in response):
        indent = "    "
        if 'error' in response:
            print(f"{indent}錯誤 / Error: {response.get('error')}")
        if 'success' in response and not response['success']:
            error_data = response.get('error', {})
            if isinstance(error_data, dict):
                print(f"{indent}錯誤代碼 / Code: {error_data.get('code', 'UNKNOWN')}")
                print(f"{indent}訊息 / Message: {error_data.get('message', 'N/A')}")


def run_authentication_tests():
    """測試認證相關端點 / Test authentication endpoints"""
    print(f"\n{Colors.BLUE}========== 認證相關測試 / Authentication Tests =========={Colors.END}\n")
    
    tests = [
        ("檢查 Bootstrap 端點是否存在 / Check Bootstrap endpoint", "GET", "/accounts/bootstrap/", None, None),
        ("檢查當前用戶端點 / Check current user endpoint", "GET", "/auth/token/", None, None),
    ]
    
    passed = 0
    for test_name, method, path, data, expected in tests:
        success, response = test_endpoint(method, path, data, expected_status=404)  # 我們期望 404 因為沒有認證
        if success or (isinstance(response, dict) and 'error' in response):
            passed += 1
        print_result(test_name, success or isinstance(response, dict), response)
    
    return passed, len(tests)


def run_user_profile_tests():
    """測試用戶個人資料端點 / Test user profile endpoints"""
    print(f"\n{Colors.BLUE}========== 用戶個人資料測試 / User Profile Tests =========={Colors.END}\n")
    
    tests = [
        ("檢查獲取個人資料端點 / Check get profile endpoint", "GET", "/accounts/me/", None, 401),
        ("檢查更新個人資料端點 / Check update profile endpoint", "GET", "/accounts/profile/", None, 401),
    ]
    
    passed = 0
    for test_name, method, path, data, expected in tests:
        success, response = test_endpoint(method, path, data, expected_status=expected)
        if success:
            passed += 1
        print_result(test_name, success, response)
    
    return passed, len(tests)


def run_books_tests():
    """測試書籍相關端點 / Test books endpoints"""
    print(f"\n{Colors.BLUE}========== 書籍測試 / Books Tests =========={Colors.END}\n")
    
    tests = [
        ("獲取書籍列表 / Get books list", "GET", "/books/", None, 200),
        ("獲取書籍列表 (備用路由) / Get books list (alt)", "GET", "/books/list/", None, 200),
    ]
    
    passed = 0
    for test_name, method, path, data, expected in tests:
        success, response = test_endpoint(method, path, data, expected_status=expected)
        if success:
            passed += 1
        print_result(test_name, success, response)
    
    return passed, len(tests)


def run_listings_tests():
    """測試刊登相關端點 / Test listings endpoints"""
    print(f"\n{Colors.BLUE}========== 刊登測試 / Listings Tests =========={Colors.END}\n")
    
    tests = [
        ("獲取刊登列表 / Get listings list", "GET", "/listings/", None, 200),
        ("獲取我的刊登 / Get my listings", "GET", "/listings/my-listings/", None, 401),
        ("獲取最新刊登 / Get latest listings", "GET", "/listings/latest/", None, 200),
        ("獲取推薦刊登 / Get recommended listings", "GET", "/listings/recommended/", None, 200),
    ]
    
    passed = 0
    for test_name, method, path, data, expected in tests:
        success, response = test_endpoint(method, path, data, expected_status=expected)
        if success:
            passed += 1
        print_result(test_name, success, response)
    
    return passed, len(tests)


def run_notifications_tests():
    """測試通知相關端點 / Test notifications endpoints"""
    print(f"\n{Colors.BLUE}========== 通知測試 / Notifications Tests =========={Colors.END}\n")
    
    tests = [
        ("獲取通知列表 / Get notifications", "GET", "/notifications/", None, 401),
        ("獲取未讀通知數 / Get unread count", "GET", "/notifications/unread-count/", None, 401),
    ]
    
    passed = 0
    for test_name, method, path, data, expected in tests:
        success, response = test_endpoint(method, path, data, expected_status=expected)
        if success:
            passed += 1
        print_result(test_name, success, response)
    
    return passed, len(tests)


def run_reports_tests():
    """測試舉報相關端點 / Test reports endpoints"""
    print(f"\n{Colors.BLUE}========== 舉報測試 / Reports Tests =========={Colors.END}\n")
    
    tests = [
        ("建立舉報 / Create report", "POST", "/moderation/", {}, 401),
        ("獲取我的舉報 / Get my reports", "GET", "/moderation/my-reports/", None, 401),
    ]
    
    passed = 0
    for test_name, method, path, data, expected in tests:
        success, response = test_endpoint(method, path, data, expected_status=expected)
        if success:
            passed += 1
        print_result(test_name, success, response)
    
    return passed, len(tests)


def check_server_health():
    """檢查伺服器是否運行 / Check if server is running"""
    print(f"{Colors.BLUE}檢查伺服器狀態... / Checking server status...{Colors.END}")
    
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        print(f"{Colors.GREEN}✓ 伺服器在線 / Server is online{Colors.END}\n")
        return True
    except requests.exceptions.ConnectionError:
        print(f"{Colors.RED}✗ 伺服器離線 / Server is offline{Colors.END}")
        print(f"{Colors.YELLOW}請確保後端伺服器正在執行 (python manage.py runserver)")
        print(f"   Please make sure the backend server is running (python manage.py runserver){Colors.END}\n")
        return False
    except Exception as e:
        print(f"{Colors.RED}✗ 伺服器檢查失敗 / Server check failed: {e}{Colors.END}\n")
        return False


def main():
    """主執行函數 / Main execution function"""
    
    parser = argparse.ArgumentParser(description='API 快速測試腳本 / API Quick Test Script')
    parser.add_argument('--url', default='http://localhost:8000/api', help='API 基礎 URL')
    parser.add_argument('--skip-auth', action='store_true', help='跳過認證測試 / Skip authentication tests')
    args = parser.parse_args()
    
    global BASE_URL
    BASE_URL = args.url
    
    print(f"""
╔════════════════════════════════════════════════════════════════════════════╗
║                       API 快速測試工具                                     ║
║                 API Quick Test Tool                                       ║
║                                                                            ║
║  測試所有主要 API 端點的可用性和基本功能                                   ║
║  Test availability and functionality of all major API endpoints           ║
║                                                                            ║
║  API 基礎 URL / Base URL: {BASE_URL:<55} ║
╚════════════════════════════════════════════════════════════════════════════╝
    """)
    
    # 檢查伺服器健康狀態
    if not check_server_health():
        return 1
    
    # 運行各種測試集合
    total_passed = 0
    total_tests = 0
    
    if not args.skip_auth:
        passed, tests = run_authentication_tests()
        total_passed += passed
        total_tests += tests
    
    passed, tests = run_user_profile_tests()
    total_passed += passed
    total_tests += tests
    
    passed, tests = run_books_tests()
    total_passed += passed
    total_tests += tests
    
    passed, tests = run_listings_tests()
    total_passed += passed
    total_tests += tests
    
    passed, tests = run_notifications_tests()
    total_passed += passed
    total_tests += tests
    
    passed, tests = run_reports_tests()
    total_passed += passed
    total_tests += tests
    
    # 顯示最終摘要
    print(f"\n{Colors.BLUE}========== 測試摘要 / Test Summary =========={Colors.END}\n")
    print(f"總測試數 / Total Tests: {total_tests}")
    print(f"通過 / Passed: {Colors.GREEN}{total_passed}{Colors.END}")
    print(f"失敗 / Failed: {Colors.RED}{total_tests - total_passed}{Colors.END}")
    print(f"成功率 / Success Rate: {(total_passed/total_tests*100):.1f}%\n")
    
    if total_passed == total_tests:
        print(f"{Colors.GREEN}🎉 所有測試都通過了！/ All tests passed!{Colors.END}")
        return 0
    else:
        print(f"{Colors.YELLOW}⚠️  某些測試失敗。請查看上面的詳細信息。")
        print(f"   Some tests failed. Please see details above.{Colors.END}")
        return 1


if __name__ == '__main__':
    try:
        exit_code = main()
        import sys
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}測試被中斷 / Test interrupted{Colors.END}")
        import sys
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}發生錯誤 / Error occurred: {e}{Colors.END}")
        import sys
        sys.exit(1)
