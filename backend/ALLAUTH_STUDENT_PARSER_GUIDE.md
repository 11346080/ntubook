"""
Django Allauth + 學號解析系統 - 實作與測試指南

本文檔說明如何部署和測試基於 4 層正規化架構的 Google OAuth 學號解析系統。
"""

# ========== 第 1 部分：部署步驟 ==========

## 1.1 執行資料庫遷移

```bash
# 遷移 core 應用（添加 Campus FK 到 Department）
python manage.py migrate core

# 遷移 accounts 應用
python manage.py migrate accounts

# 建立 Django Sites 框架表
python manage.py migrate sites
```

## 1.2 初始化基本資料

透過 Django Admin (http://localhost:8000/admin/) 添加：

### Campus（校區）
```
1. 臺北校區
   - code: TAIPEI
   - name_zh: 臺北校區
   - short_name: 台北

2. 桃園校區
   - code: TAOYUAN
   - name_zh: 桃園校區
   - short_name: 桃園
```

### ProgramType（學制）
```
1. 二技日間部
   - code: 3
   - name_zh: 二技日間部
   
2. 四技日間部
   - code: 4
   - name_zh: 四技日間部
   
3. 五專日間部
   - code: 5
   - name_zh: 五專日間部
```

### Department（系所）- 臺北校區範例
```
1. 會計系
   - campus: 臺北校區
   - program_type: 四技日間部 (code=4)
   - code: 1
   - name_zh: 會計系

2. 財經系
   - campus: 臺北校區
   - program_type: 四技日間部
   - code: 2
   - name_zh: 財經系

... (依此類推 3-7)
```

### Department（系所）- 桃園校區範例
```
1. 創設系
   - campus: 桃園校區
   - program_type: 四技日間部
   - code: A
   - name_zh: 創設系

2. 商設系
   - campus: 桃園校區
   - program_type: 四技日間部
   - code: B
   - name_zh: 商設系

3. 數媒系
   - campus: 桃園校區
   - program_type: 四技日間部
   - code: C
   - name_zh: 數媒系
```

### Site（Django Sites）
```
Domain name: 你的網域 (例如 localhost:8000 或 ntubook.com)
Display name: NTUB Used Books
```

## 1.3 Google OAuth 設定

1. 於 Google Cloud Console 建立 OAuth 2.0 認證
   - 應用類型：Web Application
   - 授權重定向 URI：http://localhost:8000/accounts/google/login/callback/
   
2. 於 Django Admin 新增 Social Application
   - Provider: Google
   - Name: Google OAuth
   - Client id: (複製 Google Cloud 的 Client ID)
   - Secret key: (複製 Google Cloud 的 Client Secret)
   - Sites: 選擇對應的 Site

## 1.4 環境變數 (.env)

```env
# Django 設定
DJANGO_DEBUG=True
DJANGO_SECRET_KEY=your-secret-key
DJANGO_ALLOWED_HOSTS=localhost:8000,127.0.0.1

# 資料庫
DB_ENGINE=django.db.backends.mysql
DB_NAME=ntub_usedbooks
DB_USER=root
DB_PASSWORD=password
DB_HOST=localhost
DB_PORT=3306

# Email（若使用 SMTP）
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=你的信箱@gmail.com
EMAIL_HOST_PASSWORD=你的應用密碼
DEFAULT_FROM_EMAIL=noreply@ntub.edu.tw
```

# ========== 第 2 部分：系統流程 ==========

## 2.1 Google OAuth 登入流程

```
1. 用戶點擊「Google 登入」
   ↓
2. 重定向到 Google OAuth 授權頁面
   ↓
3. 用戶以 @ntub.edu.tw 帳號授權
   ↓
4. Google 回傳：email, name, picture, google_sub 等
   ↓
5. Allauth pre_social_login 信號觸發
   - check_ntub_email(): 驗證 email 結尾是否為 @ntub.edu.tw
   ↓
6. StudentInfoSocialAccountAdapter.populate_user()
   - 從 email local part 提取學號 (例如 11346001)
   - 呼叫 student_parser.parse_student_number()
   - 解析結果暫存到 request.parsed_student_info
   ↓
7. Allauth 建立 User 物件
   - username, email, first_name, last_name 等
   ↓
8. StudentInfoSocialAccountAdapter.save_user()
   - 呼叫 _update_user_profile()
   - 進行 4 層 ORM 查詢
   - 更新 UserProfile (student_no, program_type, department, grade_no)
   ↓
9. Allauth post_social_login 信號觸發
   - link_to_local_user_if_exists(): 驗證與日誌記錄
   ↓
10. 登入成功，重定向到首頁或 dashboard
```

## 2.2 學號解析邏輯 (8 碼範例：11346001)

```
位數          值        含義
1-3          113       入學民國年 (ROC Year)
4            4         學制代碼：4 = 四技日間部
5            6         校區與系所代碼：6 = 臺北校區 資管系
6-8          001       班級與流水號

計算：
- 當前西元年 = 2026
- 當前民國年 = 2026 - 1911 = 115
- 當前月份 = 3 (< 8)
- 當前學年度 = 115 - 1 = 114
- 入學民國年 = 113
- 年級 = (114 - 113) + 1 = 2 (二年級)

查詢結果：
- Campus: 臺北校區
- ProgramType: 四技日間部 (code=4)
- Department: Department.objects.filter(
    campus__name_zh='臺北校區',
    program_type__code='4',
    code='6'
  ).first()
- Grade: 2
```

# ========== 第 3 部分：測試 ==========

## 3.1 單元測試 - 學號解析

```python
# 在 tests/test_student_parser.py 中執行

from accounts.student_parser import parse_student_number

# 測試案例 1：正常二技學號
result = parse_student_number('11346001')
assert result['admission_year'] == 113
assert result['program_type_digit'] == '4'
assert result['campus_dept_digit'] == '6'
assert result['is_taipei'] == True
assert result['campus_name'] == '臺北校區'
assert result['grade_no'] == 2  # 或根據當前日期變動
assert result['errors'] == []

# 測試案例 2：桃園校區學號
result = parse_student_number('11245A01')
assert result['campus_dept_digit'] == 'A'
assert result['is_taoyuan'] == True
assert result['campus_name'] == '桃園校區'
assert result['errors'] == []

# 測試案例 3：無效學制代碼
result = parse_student_number('11346901')
assert len(result['errors']) > 0
assert '無效的學制代碼' in result['errors'][0]

# 測試案例 4：無效系所代碼
result = parse_student_number('11349001')
assert len(result['errors']) > 0

# 測試案例 5：格式錯誤（少於 8 碼）
result = parse_student_number('1134')
assert len(result['errors']) > 0
assert '8 碼' in result['errors'][0]
```

## 3.2 集成測試 - Google OAuth 登入

```python
# 在 tests/test_social_login.py 中執行

from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import User, UserProfile
from core.models import Campus, ProgramType, Department

class GoogleLoginIntegrationTest(TestCase):
    
    def setUp(self):
        # 建立必要的資料
        campus = Campus.objects.create(
            code='TAIPEI',
            name_zh='臺北校區'
        )
        program_type = ProgramType.objects.create(
            code='4',
            name_zh='四技日間部'
        )
        Department.objects.create(
            campus=campus,
            program_type=program_type,
            code='6',
            name_zh='資管系'
        )
        
        self.client = Client()
    
    def test_login_with_valid_student_number(self):
        """
        測試：以有效的學號 Google 帳號登入
        預期：User 與 UserProfile 被正確建立，學號被解析
        """
        # 模擬 Google OAuth 回傳的資料
        # (實際測試需使用 Mock 或 VCR)
        pass
    
    def test_login_with_invalid_email_domain(self):
        """
        測試：以非 @ntub.edu.tw 帳號登入
        預期：被拒絕或警告記錄
        """
        pass
    
    def test_userprofile_fields_populated(self):
        """
        測試：UserProfile 所有欄位是否被正確填充
        - student_no
        - program_type
        - department
        - grade_no
        """
        pass
```

## 3.3 手動測試 - 完整流程

1. **啟動開發伺服器**
   ```bash
   python manage.py runserver
   ```

2. **存取登入頁面**
   - 瀏覽 http://localhost:8000/accounts/login/ 或相應的登入入口

3. **點擊「Google 登入」**
   - 若使用 Google 帳號 (例如 11346001@ntub.edu.tw) 授權

4. **驗證 UserProfile**
   - 存取 Django Admin http://localhost:8000/admin/accounts/userprofile/
   - 確認該用戶的 profiles 紀錄：
     - student_no: 11346001
     - program_type: 四技日間部
     - department: 資管系
     - grade_no: 2 (根據當前日期)

5. **檢查日誌**
   ```bash
   tail -f logs/django.log
   ```
   - 搜尋 "Successfully parsed student info" 信息
   - 檢查是否有任何 warning 或 error

# ========== 第 4 部分：故障排除 ==========

## 問題 1：登入後 UserProfile 沒有更新

**症狀**
- 用戶正常登入，但 UserProfile 欄位為空

**檢查清單**
1. 檢查 settings.py 中的 SOCIALACCOUNT_ADAPTER 設定
   ```python
   SOCIALACCOUNT_ADAPTER = 'accounts.adapter.StudentInfoSocialAccountAdapter'
   ```

2. 檢查 Django Admin 中 Campus 和 Department 資料是否正確
   - 名稱必須完全匹配（區分大小寫）

3. 檢查日誌 logs/django.log 中是否有錯誤訊息

## 問題 2：學號解析失敗

**症狀**
- 日誌顯示 "Failed to parse student number" 或錯誤訊息

**檢查清單**
1. 學號格式是否為 8 碼
2. 第 4 碼是否為有效的學制代碼 (3, 4, 5)
3. 第 5 碼是否為有效的系所代碼 (1-7 or A-C)

## 問題 3：Google OAuth 應用未設定

**症狀**
- 登入頁面沒有「Google 登入」按鈕，或點擊出現錯誤

**檢查清單**
1. 確認 Django Admin 中有新增 Social Application
2. Client ID 和 Secret 是否正確
3. Redirect URI 是否正確登記在 Google Cloud Console
4. Sites 設定是否正確

## 問題 4：Department 查詢返回 None

**症狀**
- 日誌顯示 "Department not found for campus=..."

**檢查清單**
1. Department 記錄中 campus, program_type, code 三個欄位是否都正確設定
2. 執行追蹤查詢：
   ```python
   python manage.py shell
   >>> from core.models import Campus, ProgramType, Department
   >>> campus = Campus.objects.get(name_zh='臺北校區')
   >>> prog = ProgramType.objects.get(code='4')
   >>> dept = Department.objects.filter(campus=campus, program_type=prog, code='6').first()
   >>> print(dept)
   ```

# ========== 第 5 部分：進階配置 ==========

## 5.1 強制 Email 驗證

若要求用戶驗證 Email，在 settings.py 中修改：

```python
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
```

並配置 Email 後端以發送驗證郵件。

## 5.2 自訂 ClassGroup 自動綁定

可在 adapter.py 的 `_update_user_profile()` 中添加邏輯，根據 grade_no 與 department 自動尋找對應的 ClassGroup：

```python
if department_obj and grade_no:
    class_group_obj = ClassGroup.objects.filter(
        department=department_obj,
        grade_no=grade_no
    ).first()
    user_profile.class_group = class_group_obj
```

## 5.3 WebHook 初始化資料

若要動態更新 Campus/Department/ProgramType，可建立管理 API 端點來批量匯入資料。

---

**最後更新**：2026-03-21
**作者**：GitHub Copilot
**版本**：1.0
