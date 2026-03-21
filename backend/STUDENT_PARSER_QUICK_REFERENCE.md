"""
學號解析與 Allauth 整合 - 快速參考手冊

此檔案提供核心代碼片段的快速參考，用於理解系統如何運作。
"""

# ========== 1. 學號解析獨立使用 ==========

from accounts.student_parser import parse_student_number

# 簡單範例
result = parse_student_number('11346001')

if not result['errors']:
    print(f"學號：{result['student_no']}")
    print(f"入學年：{result['admission_year']}")
    print(f"校區：{result['campus_name']}")
    print(f"年級：{result['grade_no']}")
    print(f"學制：{result['program_type_info']}")
    print(f"系所代碼：{result['campus_dept_digit']}")
else:
    print(f"解析失敗：{', '.join(result['errors'])}")


# ========== 2. 手動進行 ORM 查詢（完整流程） ==========

from core.models import Campus, ProgramType, Department
from accounts.student_parser import parse_student_number

def bind_student_info(user, student_no):
    """
    手動綁定學生資訊到 UserProfile。
    (通常由 adapter 自動執行，此處為範例)
    """
    from accounts.models import UserProfile
    
    # 步驟 1：解析學號
    parsed_info = parse_student_number(student_no)
    
    if parsed_info['errors']:
        print(f"Failed to parse: {parsed_info['errors']}")
        return
    
    # 步驟 2：逐序進行 ORM 查詢（4層正規化）
    
    # 2a. 查詢校區
    campus_obj = Campus.objects.filter(
        name_zh=parsed_info['campus_name']
    ).first()
    
    if not campus_obj:
        print(f"Campus not found: {parsed_info['campus_name']}")
        return
    
    # 2b. 查詢學制
    program_type_code = parsed_info['program_type_info']['code']
    program_type_obj = ProgramType.objects.filter(
        code=program_type_code
    ).first()
    
    if not program_type_obj:
        print(f"ProgramType not found: {program_type_code}")
        return
    
    # 2c. 查詢系所（最關鍵的三層條件）
    department_obj = Department.objects.filter(
        campus=campus_obj,
        program_type=program_type_obj,
        code=parsed_info['campus_dept_digit']
    ).first()
    
    if not department_obj:
        print(
            f"Department not found for "
            f"campus={campus_obj.name_zh}, "
            f"program_type={program_type_code}, "
            f"code={parsed_info['campus_dept_digit']}"
        )
    
    # 步驟 3：更新 UserProfile
    profile, created = UserProfile.objects.get_or_create(user=user)
    profile.student_no = student_no
    profile.program_type = program_type_obj
    profile.department = department_obj  # 可能為 None
    profile.grade_no = parsed_info['grade_no']
    profile.display_name = profile.display_name or user.first_name or user.username
    profile.save()
    
    print(f"Updated UserProfile for {user.username}")
    print(f"  - student_no: {profile.student_no}")
    print(f"  - program_type: {profile.program_type}")
    print(f"  - department: {profile.department}")
    print(f"  - grade_no: {profile.grade_no}")


# ========== 3. Django Shell 快速測試 ==========

"""
在終端執行以下命令：

python manage.py shell

然後在 Python 互動模式中執行：

# 測試解析
from accounts.student_parser import parse_student_number
result = parse_student_number('11346001')
print(result)

# 檢查資料庫資料
from core.models import Campus, ProgramType, Department

# 列出所有校區
campuses = Campus.objects.all()
for c in campuses:
    print(f"{c.name_zh} (code={c.code})")

# 列出臺北校區的所有系所
from core.models import Campus
taipei = Campus.objects.get(name_zh='臺北校區')
depts = taipei.departments.all()
for d in depts:
    print(f"{d.code} - {d.name_zh}")

# 進行 Department 查詢（完全模擬 adapter 邏輯）
campus = Campus.objects.get(name_zh='臺北校區')
prog_type = ProgramType.objects.get(code='4')
dept = Department.objects.filter(
    campus=campus,
    program_type=prog_type,
    code='6'
).first()
print(f"Found: {dept}")

exit()
"""


# ========== 4. 在 View 中使用（可選） ==========

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from accounts.student_parser import parse_student_number

@login_required
def get_student_info(request):
    """
    API 端點：查詢登入用戶的學號解析資訊。
    """
    user = request.user
    
    try:
        profile = user.profile
        parsed = parse_student_number(profile.student_no)
        
        return JsonResponse({
            'success': True,
            'student_no': profile.student_no,
            'grade_no': profile.grade_no,
            'program_type': str(profile.program_type),
            'department': str(profile.department),
            'parsed_info': parsed,
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e),
        }, status=400)


# ========== 5. 信號與日誌 ==========

"""
系統會在以下時點記錄訊息到 logs/django.log：

1. Google 登入時
   - 信號 pre_social_login：驗證 @ntub.edu.tw
   - 信號 post_social_login：最終驗證

2. 學號解析時
   - INFO：成功解析
   - WARNING：無效代碼或格式錯誤
   - ERROR：異常狀況

3. UserProfile 更新時
   - INFO：成功更新
   - WARNING：Campus/ProgramType/Department 未找到

# 查看最後的日誌
tail -f logs/django.log

# 過濾特定的日誌
grep "Successfully parsed" logs/django.log
grep "Department not found" logs/django.log
"""


# ========== 6. 設定驗證清單 ==========

"""
部署前確認事項：

資料庫層面：
  ☐ 已執行 migrate core 和 migrate accounts
  ☐ Campus 表有data：臺北校區、桃園校區
  ☐ ProgramType 表有data：3、4、5
  ☐ Department 表有data，且 campus_id 已填入
  ☐ Department 的 unique_together 已生效

Django 設定：
  ☐ INSTALLED_APPS 包含 allauth 相關應用
  ☐ SOCIALACCOUNT_ADAPTER 指向 'accounts.adapter.StudentInfoSocialAccountAdapter'
  ☐ SITE_ID = 1
  ☐ EMAIL_BACKEND 已設定

Google OAuth：
  ☐ Django Admin 中有 Social Application (Google)
  ☐ Client ID 和 Secret 正確
  ☐ Sites 設定正確
  ☐ Callback URL 已登記到 Google Cloud Console

環境變數：
  ☐ DB_* 設定正確
  ☐ DJANGO_DEBUG 已設為適當值
  ☐ DJANGO_ALLOWED_HOSTS 包含使用的域名

日誌：
  ☐ logs/ 目錄已建立
  ☐ 日誌級別設為 INFO 或 DEBUG（開發環境）
"""


# ========== 7. 可能的錯誤與解決 ==========

"""
錯誤：ImportError: cannot import name 'StudentInfoSocialAccountAdapter'
解決：
  - 確認 accounts/adapter.py 檔案存在
  - 確認 Django 已重新啟動
  - 檢查 Python 路徑是否正確

錯誤：Department matching query does not exist
解決：
  - 檢查 Department 記錄中 campus, program_type, code 是否都存在
  - 執行 Django shell 進行手動查詢驗證

錯誤：学号解析失敗，顯示 "無效的學制代碼"
解決：
  - 檢查學號第 4 碼是否為 3、4 或 5
  - 確認學號長度為 8 碼

錯誤：Google 登入顯示 "Redirect URI mismatch"
解決：
  - 檢查 Google Cloud Console 的授權重定向 URI
  - 確認 Django Admin 中 Site 的 Domain name 正確
  - 確認 callback URL 為 /accounts/google/login/callback/
"""

---

**參考資源**

- [Django Allauth 官方文檔](https://django-allauth.readthedocs.io/)
- [Google OAuth 2.0](https://developers.google.com/identity/protocols/oauth2)
- [Django ORM Queries](https://docs.djangoproject.com/en/5.2/topics/db/queries/)
- [Django Signals](https://docs.djangoproject.com/en/5.2/topics/signals/)
