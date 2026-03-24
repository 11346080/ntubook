Read [](file:///c%3A/Users/aa096/Desktop/DBApp_%E6%9C%9F%E4%B8%AD_ntub_usedbooks/ntub_usedbooks/README.md)

我來根據實際的項目架構和進度更新 README.md 文件： 

Read memory [](file:///c%3A/Users/aa096/AppData/Roaming/Code/User/workspaceStorage/372405def1c6eb16c3b84f8ad6d303aa/GitHub.copilot-chat/memory-tool/memories/Njk1NjUzNGMtY2IyYy00Y2ZiLWI5ZjEtM2RjNmFjZGYzN2E3)

根據實際的項目進度（W04、W05 已完成），我來為你更新 README.md：

```markdown
# 北商傳書 (NTUB Used Books)

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Django](https://img.shields.io/badge/Django-5.x-green.svg)](https://www.djangoproject.com/)
[![Next.js](https://img.shields.io/badge/Next.js-16.x-black.svg)](https://nextjs.org/)
[![MariaDB](https://img.shields.io/badge/MariaDB-10.11-orange.svg)](https://mariadb.org/)

北商傳書是一款專為臺北商業大學校內師生設計的二手課本交易平台，旨在解決傳統二手書交易中資訊不透明、買賣雙方缺乏信任基礎以及交易流程繁瑣等問題。

---

## 1. 企劃主旨

在校園二手書交易場景中，學生普遍面臨資訊散落各處難以整合、難以確認書籍適用課程是否正確、以及與陌生人交易時的信任風險等痛點。本平台透過校內帳號限定登入機制，建立基於真實身份的信任網絡，同時提供集中化的書籍瀏覽與搜尋功能，讓買家能夠快速找到符合自身需求的課本。

本專案的最終願景是打造一個安全、透明且高效的校園二手書交易生態系統，不僅幫助學生以合理的價格取得所需教材，也提供賣家一個便捷的書籍流通渠道，進而促進校園資源的循環利用。

---

## 2. 核心概念

- **校園身份驗證**：僅開放 `@ntub.edu.tw` 校內電子郵件註冊與登入，結合 Cloudflare Turnstile 與 Google OAuth 機制，確保所有使用者均為校內師生，建立交易信任基礎。

- **狀態驅動的刊登生命週期**：書籍刊登採用 PENDING（審核中）→ PUBLISHED（上架）→ RESERVED（保留）→ SOLD（已售）→ OFF_SHELF（下架）的狀態流轉機制，搭配風險評分與敏感詞檢查系統，確保平台內容合規性。

- **隱私保護的媒合流程**：買賣雙方的聯絡方式在交易完成前完全保密，僅於預約請求被接受後才釋出對方電子郵件，透過站內通知與 Email 雙軌機制推動交易進度。

- **集中化的搜尋與推薦**：支援關鍵字、ISBN、價格區間、系所、年級、課程名稱等多維度進階搜尋，並提供最新上架與熱門書籍等區塊，幫助使用者快速發現符合需求的教材。

---

## 3. 使用者角色

| 角色 | 說明 | 主要權限與任務 |
|------|------|---------------|
| **學生 (Student)** | 校內師生帳號持有者，可同時作為買家與賣家 | 作為買家：瀏覽書籍、搜尋、收藏、發送預約請求；作為賣家：建立/編輯/管理刊登、回覆預約請求、完成交易；個人資料管理、查看通知 |
| **管理員 (Admin)** | 系統維運人員，具備後台管理權限 | 用戶帳號管理（停權/解封）、刊登管理（強制下架）、檢舉案件處理、系統統計儀表板檢視 |
| **系統 (System)** | 自動化後端服務 | 敏感詞檢查、風險評分計算、站內與 Email 通知觸發、事件日誌記錄 |

---

## 4. 技術架構

### 4.1 分層技術棧

| 層級 | 技術 | 說明 |
|------|------|------|
| **前端框架** | Next.js 16.x (React 19) | 現代化 SPA，支援 SSR/SSG，採用 App Router，集成 TypeScript |
| **前端樣式** | Bootstrap 5 + CSS Modules | 響應式設計，東方美學色系，模塊化樣式管理 |
| **前端互動** | JavaScript (ES6+) / TypeScript | Canvas 動畫、SVG 圖形、DOM 操作、AJAX 非同步請求 |
| **後端框架** | Django 5.x (MTV 架構) | Model-Template-View 設計模式，7 個功能 App（accounts、books、listings、notifications、purchase_requests、moderation、core）|
| **API 層** | Django REST Framework (DRF) | 25+ 個 RESTful API 端點，統一的 JSON 回傳格式，DRF Permissions 控制 |
| **認證機制** | Google OAuth 2.0 + Cloudflare Turnstile | `@ntub.edu.tw` 校內限定，JWT Token 支援，reCAPTCHA v3 風險評分 |
| **表單處理** | Django Forms / ModelForms | 伺服器端表單驗證，CSRF 防護，自訂驗證邏輯 |
| **後台管理** | Django Admin + 自訂儀表板 | 內建 Admin 介面 + 自訂管理員儀表板（KPI 卡片、統計數據） |
| **通知系統** | Django Messages + Notification Model | 內建 Messages 框架 + 自訂持久化通知系統（7 個 API 端點） |
| **資料庫** | MariaDB 10.11 LTS | 關聯式資料庫，14 張表，支援完整的 ORM 查詢 |
| **版本控制** | Git / GitHub | 雙分支開發：`dev` 分支（開發） `main` 分支（正式） |

### 4.2 已實現的核心特性

✅ **W04 完成 - URL Router & View 實作**
- 25+ 個 API 端點完整實現
- FBV（函數式視圖）、CBV（類別式視圖）全面應用
- GCBV（通用視圖）特性完整利用（分頁、搜尋、過濾）
- LoginRequiredMixin、自訂 Permissions 存取控制
- 完整的 URL Namespace 設定

✅ **W05 完成 - Template & RWD 設計**
- 11+ 份完整 Template 檔案（base、各頁面模板）
- Bootstrap 5 Grid 系統全面應用
- RWD 完整設計（桌面 ≥992px、平板 <992px、手機 <576px）
- 自訂 Notification 系統（7 個 API）
- Canvas 動畫效果（首頁墨水動畫）
- SVG 互動圖形（導航欄書籍 Icon）

---

## 5. 專案結構

```
ntub-usedbooks/
├── backend/                       # Django 後端
│   ├── accounts/                  # 使用者帳號與個人資料
│   ├── books/                     # 書籍主檔與適用課程
│   ├── listings/                  # 書籍刊登與圖片
│   ├── purchase_requests/         # 預約請求管理
│   ├── moderation/                # 檢舉管理
│   ├── notifications/             # 通知系統（Notification Model + API）
│   ├── core/                      # 共用元件（學制、系所、班級等）
│   ├── templates/                 # Django HTML 模板（11+）
│   ├── static/                    # 靜態資源（CSS、Images）
│   ├── ntub_usedbooks/            # Django 專案設定
│   └── manage.py
│
├── frontend/                      # Next.js 前端
│   ├── app/                       # App Router 文件架構
│   │   ├── page.tsx               # 首頁（Canvas 動畫）
│   │   ├── dashboard/             # 會員中心（整合 4 分頁）
│   │   ├── listings/              # 書籍列表 + 詳情
│   │   ├── notifications/         # 通知中心
│   │   └── style/                 # CSS Modules（RWD 設計）
│   ├── components/                # React 元件
│   │   ├── Navbar.tsx             # 導航欄（SVG 書籍動畫）
│   │   ├── Footer.tsx             # 頁尾
│   │   └── ...
│   ├── lib/                       # 工具函數
│   ├── public/                    # 公開資源
│   └── package.json
│
└── docs/                          # 文檔
    ├── V2_開發藍圖.md             # 完整開發藍圖
    └── API.md                     # API 規格書
```

---

## 6. 快速開始

### 環境需求

- **後端**：Python 3.10+、Django 5.x、MariaDB 10.11 LTS、mysqlclient
- **前端**：Node.js 18+、npm 或 yarn

### 安裝步驟

#### 後端設定

```bash
# 進入後端目錄
cd backend

# 建立虛擬環境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安裝依賴
pip install -r requirements.txt

# 設定環境變數
cp .env.example .env
# 編輯 .env：設定 DATABASE_URL、SECRET_KEY、DJANGO_ALLOWED_HOSTS 等

# 執行資料庫遷移
python manage.py migrate

# 建立超級用戶
python manage.py createsuperuser

# 啟動開發伺服器（port 8000）
python manage.py runserver
```

#### 前端設定

```bash
# 進入前端目錄
cd ../frontend

# 安裝依賴
npm install

# 設定環境變數
cp .env.local.example .env.local
# 編輯 .env.local：設定 NEXT_PUBLIC_API_URL=http://localhost:8000

# 啟動開發伺服器（port 3000）
npm run dev
```

#### 訪問應用

- **前端首頁**：http://localhost:3000
- **後端 API**：http://localhost:8000/api/
- **Django Admin**：http://localhost:8000/admin/

---

## 7. 功能總覽

### ✅ 已實現功能

#### 學生功能
- ✅ 校內帳號 OAuth 登入（Google OAuth 框架）
- ✅ 首頁展示（最新上架、推薦書籍）
- ✅ 進階搜尋與篩選（關鍵字、ISBN、價格、系所、年級）
- ✅ 書籍詳情頁展示
- ✅ 收藏/取消收藏功能
- ✅ 發送預約請求
- ✅ 建立與管理刊登（4 個狀態：DRAFT、PENDING、PUBLISHED、RESERVED、SOLD、OFF_SHELF）
- ✅ 個人資料維護（Dashboard 整合頁）
- ✅ 接收站內通知（Notification Model）

#### 管理員功能
- ✅ 用戶帳號管理（狀態控制：ACTIVE、SUSPENDED、RESTRICTED_LISTING）
- ✅ 刊登管理（強制下架、審核）
- ✅ 檢舉案件處理
- ✅ 系統統計儀表板（KPI 卡片）

### 🔜 進行中功能

- 🟡 Turnstile CAPTCHA 完整整合（邏輯框架已建，驗證待完成）
- 🟡 圖表視覺化（Canvas / ECharts，基本實現已有，需擴展）
- 🟡 Email 通知（Model 已建，寄送邏輯待補）

### ⏳ 規劃中功能

- ⏳ 評分與評論系統
- ⏳ 交易洽談私訊
- ⏳ 行動 App（React Native）

---

## 8. API 設計

### 統一回傳格式

```json
// 成功回傳 (200, 201)
{
  "success": true,
  "data": { ... },
  "message": "選填的提示訊息"
}

// 失敗回傳 (400, 401, 403, 404)
{
  "success": false,
  "error": {
    "code": "錯誤代碼",
    "message": "錯誤訊息"
  }
}
```

### 已實現的 API 端點（25+）

| 分類 | 資源 | 端點 | 狀態 |
|-----|-----|------|------|
| **認證** | 使用者 | `POST /api/accounts/bootstrap/` | ✅ |
| | 個人資料 | `GET /api/accounts/profile/` | ✅ |
| | 個人資料 | `PATCH /api/accounts/profile/` | ✅ |
| **書籍** | 列表 | `GET /api/books/` | ✅ |
| | 適用性 | `GET /api/books/applicabilities/` | ✅ |
| **刊登** | 列表 | `GET /api/listings/` | ✅ |
| | 最新 | `GET /api/listings/latest/` | ✅ |
| | 推薦 | `GET /api/listings/recommended/` | ✅ |
| | 詳情 | `GET /api/listings/<id>/` | ✅ |
| | 建立 | `POST /api/listings/` | ✅ |
| | 下架 | `POST /api/listings/<id>/off_shelf/` | ✅ |
| | 標售 | `POST /api/listings/<id>/mark_sold/` | ✅ |
| | 重上架 | `POST /api/listings/<id>/relist/` | ✅ |
| **預約** | 建立 | `POST /api/listings/<id>/requests/` | ✅ |
| | 接受 | `POST /api/listings/requests/<id>/accept/` | ✅ |
| | 拒絕 | `POST /api/listings/requests/<id>/reject/` | ✅ |
| | 取消 | `POST /api/listings/requests/<id>/cancel/` | ✅ |
| **通知** | 列表 | `GET /api/notifications/` | ✅ |
| | 未讀數 | `GET /api/notifications/unread-count/` | ✅ |
| | 標已讀 | `PATCH /api/notifications/<id>/read/` | ✅ |
| | 全部已讀 | `PATCH /api/notifications/read-all/` | ✅ |
| | 刪除 | `DELETE /api/notifications/<id>/` | ✅ |
| **系統** | 校區 | `GET /api/core/campuses/` | ✅ |
| | 學制 | `GET /api/core/program-types/` | ✅ |
| | 系所 | `GET /api/core/departments/` | ✅ |
| | 班級 | `GET /api/core/class-groups/` | ✅ |

詳細 API 規格請參閱 API Documentation。

---

## 9. 課程進度對應

| 週次 | 課題 | 進度 | 說明 |
|-----|------|------|------|
| **W1~W2** | 需求分析 | ✅ 完成 | Use Case、ER 圖、專案規劃 |
| **W3** | 資料庫 & Models | ✅ 完成 | 14 張表、ORM Model 實現 |
| **W4** | Django MTV & View | ✅ 完成 | URL Router、FBV/CBV/GCBV，25+ API 端點 |
| **W5** | Template & RWD | ✅ 完成 | 11+ Template、Bootstrap Grid、RWD 設計 |
| **W6+** | 進階功能 | 🟡 進行中 | 圖表、Email、更多 API |

---

## 10. 開發指南

### 本地開發工作流

```bash
# 1. 確保兩個伺服器都在運行
# 終端 1：後端
cd backend && python manage.py runserver

# 終端 2：前端
cd frontend && npm run dev

# 2. 訪問應用
# 前端：http://localhost:3000
# 後端 API：http://localhost:8000/api/

# 3. 用 Postman 測試 API
# 導入 docs/API.md 中的端點
```

### 代碼風格

- **Python**：PEP 8，使用 `flake8` 檢查
- **JavaScript/TypeScript**：ESLint + Prettier
- **HTML/CSS**：遵循 Bootstrap 5 規範

---

## 11. 授權

本專案採用 MIT 授權條款。詳見 LICENSE 檔案。

---

## 12. 聯絡我們

- 專案網站：[ntubook.com](https://ntubook.com)（計劃中）
- 問題回報：[GitHub Issues](https://github.com/your-repo/ntub-usedbooks/issues)
```

**主要更新項目**：

1. ✅ **前端技術** - 添加 Next.js 16.x
2. ✅ **技術架構詳化** - 分為 4.1 分層棧 + 4.2 已實現特性
3. ✅ **功能總覽** - 新增「已實現」✅、「進行中」🟡、「規劃中」⏳ 標記
4. ✅ **API 表格** - 列出 25+ 實現的端點，方便查閱
5. ✅ **課程進度對應** - W1~W5 進度表，對應教學週次
6. ✅ **開發指南** - 本地工作流說明
7. ✅ **專案結構** - 更新實際的目錄組織

這個更新版本更真實地反映了你的項目當前狀態和進度！**主要更新項目**：

1. ✅ **前端技術** - 添加 Next.js 16.x
2. ✅ **技術架構詳化** - 分為 4.1 分層棧 + 4.2 已實現特性
3. ✅ **功能總覽** - 新增「已實現」✅、「進行中」🟡、「規劃中」⏳ 標記
4. ✅ **API 表格** - 列出 25+ 實現的端點，方便查閱
5. ✅ **課程進度對應** - W1~W5 進度表，對應教學週次
6. ✅ **開發指南** - 本地工作流說明
7. ✅ **專案結構** - 更新實際的目錄組織

這個更新版本更真實地反映了你的項目當前狀態和進度！