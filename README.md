# 北商傳書 (NTUBook)

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Django](https://img.shields.io/badge/Django-5.x-green.svg)](https://www.djangoproject.com/)
[![Next.js](https://img.shields.io/badge/Next.js-16.x-black.svg)](https://nextjs.org/)
[![MariaDB](https://img.shields.io/badge/MariaDB-10.11-orange.svg)](https://mariadb.org/)

北商傳書是一款專為臺北商業大學校內師生設計的二手課本交易平台，旨在解決傳統二手書交易中資訊不透明、買賣雙方缺乏信任基礎以及交易流程繁瑣等問題。

---

## 目錄

1. [企劃主旨](#1-企劃主旨)
2. [核心概念](#2-核心概念)
3. [使用者角色](#3-使用者角色)
4. [技術架構](#4-技術架構)
5. [專案結構](#5-專案結構)
6. [快速開始](#6-快速開始)
7. [功能總覽](#7-功能總覽)
8. [API 設計](#8-api-設計)
9. [課程進度對應](#9-課程進度對應)
10. [開發指南](#10-開發指南)
11. [授權](#11-授權)

---

## 1. 企劃主旨

在校園二手書交易場景中，學生普遍面臨資訊散落各處難以整合、難以確認書籍適用課程是否正確、以及與陌生人交易時的信任風險等痛點。本平台透過校內帳號限定登入機制，建立基於真實身份的信任網絡，同時提供集中化的書籍瀏覽與搜尋功能，讓買家能夠快速找到符合自身需求的課本。

本專案的最終願景是打造一個安全、透明且高效的校園二手書交易生態系統，不僅幫助學生以合理的價格取得所需教材，也提供賣家一個便捷的書籍流通渠道，進而促進校園資源的循環利用。

---

## 2. 核心概念

**校園身份驗證**
僅開放 `@ntub.edu.tw` 校內電子郵件註冊與登入，結合 Cloudflare Turnstile 與 Google OAuth 機制，確保所有使用者均為校內師生，建立交易信任基礎。

**狀態驅動的刊登生命週期**
書籍刊登採用 `PENDING` → `PUBLISHED` → `RESERVED` → `SOLD` → `OFF_SHELF` 的狀態流轉機制，搭配風險評分與敏感詞檢查系統，確保平台內容合規性。

**隱私保護的媒合流程**
買賣雙方的聯絡方式在交易完成前完全保密，僅於預約請求被接受後才釋出對方電子郵件，透過站內通知與 Email 雙軌機制推動交易進度。

**集中化的搜尋與推薦**
支援關鍵字、ISBN、價格區間、系所、年級、課程名稱等多維度進階搜尋，並提供最新上架與熱門書籍等區塊，幫助使用者快速發現符合需求的教材。

---

## 3. 使用者角色

| 角色 | 說明 | 主要權限與任務 |
|------|------|---------------|
| 學生 (Student) | 校內師生帳號持有者，可同時作為買家與賣家 | 作為買家：瀏覽書籍、搜尋、收藏、發送預約請求；作為賣家：建立／編輯／管理刊登、回覆預約請求、完成交易；個人資料管理、查看通知 |
| 管理員 (Admin) | 系統維運人員，具備後台管理權限 | 用戶帳號管理（停權／解封）、刊登管理（強制下架）、檢舉案件處理、系統統計儀表板檢視 |
| 系統 (System) | 自動化後端服務 | 敏感詞檢查、風險評分計算、站內與 Email 通知觸發、事件日誌記錄 |

---

## 4. 技術架構

### 4.1 分層技術棧

| 層級 | 技術 | 說明 |
|------|------|------|
| 前端框架 | Next.js 16.x (React 19) | 現代化 SPA，支援 SSR/SSG，採用 App Router，集成 TypeScript |
| 前端樣式 | Bootstrap 5 + CSS Modules | 響應式設計，東方美學色系，模塊化樣式管理 |
| 前端互動 | JavaScript (ES6+) / TypeScript | Canvas 動畫、SVG 圖形、DOM 操作、AJAX 非同步請求 |
| 後端框架 | Django 5.x (MTV 架構) | Model-Template-View 設計模式，7 個功能 App（accounts、books、listings、notifications、purchase_requests、moderation、core）|
| API 層 | Django REST Framework (DRF) | 25+ 個 RESTful API 端點，統一的 JSON 回傳格式，DRF Permissions 控制 |
| 認證機制 | Google OAuth 2.0 + Cloudflare Turnstile | `@ntub.edu.tw` 校內限定，JWT Token 支援，reCAPTCHA v3 風險評分 |
| 表單處理 | Django Forms / ModelForms | 伺服器端表單驗證，CSRF 防護，自訂驗證邏輯 |
| 後台管理 | Django Admin + 自訂儀表板 | 內建 Admin 介面 + 自訂管理員儀表板（KPI 卡片、統計數據） |
| 通知系統 | Django Messages + Notification Model | 內建 Messages 框架 + 自訂持久化通知系統（7 個 API 端點） |
| 資料庫 | MariaDB 10.11 LTS | 關聯式資料庫，14 張表，支援完整的 ORM 查詢 |
| 版本控制 | Git / GitHub | 雙分支開發：`dev`（開發）、`main`（正式） |

### 4.2 已實現的核心特性

**W04 — URL Router & View 實作**
- 25+ 個 API 端點完整實現
- FBV（函數式視圖）、CBV（類別式視圖）全面應用
- GCBV（通用視圖）特性完整利用（分頁、搜尋、過濾）
- LoginRequiredMixin、自訂 Permissions 存取控制
- 完整的 URL Namespace 設定

**W05 — Template & RWD 設計**
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
└── frontend/                      # Next.js 前端
    ├── app/                       # App Router 文件架構
    │   ├── page.tsx               # 首頁（Canvas 動畫）
    │   ├── dashboard/             # 會員中心（整合 4 分頁）
    │   ├── listings/              # 書籍列表 + 詳情
    │   ├── notifications/         # 通知中心
    │   └── style/                 # CSS Modules（RWD 設計）
    ├── components/                # React 元件
    │   ├── Navbar.tsx             # 導航欄（SVG 書籍動畫）
    │   ├── Footer.tsx             # 頁尾
    │   └── ...
    ├── lib/                       # 工具函數
    ├── public/                    # 公開資源
    └── package.json
```

---

## 6. 快速開始

### 環境需求

- **後端**：Python 3.10+、Django 5.x、MariaDB 10.11 LTS、mysqlclient
- **前端**：Node.js 18+、npm 或 yarn

### 後端設定

```bash
cd backend

python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env
# 編輯 .env：設定 DATABASE_URL、SECRET_KEY、DJANGO_ALLOWED_HOSTS 等

python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### 前端設定

```bash
cd frontend

npm install

cp .env.local.example .env.local
# 編輯 .env.local：設定 NEXT_PUBLIC_API_URL=http://localhost:8000

npm run dev
```

### 訪問應用

| 服務 | 網址 |
|------|------|
| 前端首頁 | http://localhost:3000 |
| 後端 API | http://localhost:8000/api/ |
| Django Admin | http://localhost:8000/admin/ |

---

## 7. 功能總覽

### 已實現功能

**學生功能**

| 功能 | 狀態 |
|------|------|
| 校內帳號 OAuth 登入（Google OAuth 框架） | 完成 |
| 首頁展示（最新上架、推薦書籍） | 完成 |
| 進階搜尋與篩選（關鍵字、ISBN、價格、系所、年級） | 完成 |
| 書籍詳情頁展示 | 完成 |
| 收藏／取消收藏功能 | 完成 |
| 發送預約請求 | 完成 |
| 建立與管理刊登（DRAFT、PENDING、PUBLISHED、RESERVED、SOLD、OFF_SHELF） | 完成 |
| 個人資料維護（Dashboard 整合頁） | 完成 |
| 接收站內通知（Notification Model） | 完成 |

**管理員功能**

| 功能 | 狀態 |
|------|------|
| 用戶帳號管理（ACTIVE、SUSPENDED、RESTRICTED_LISTING） | 完成 |
| 刊登管理（強制下架、審核） | 完成 |
| 檢舉案件處理 | 完成 |
| 系統統計儀表板（KPI 卡片） | 完成 |

### 進行中功能

| 功能 | 說明 |
|------|------|
| Turnstile CAPTCHA 整合 | 邏輯框架已建，驗證待完成 |
| 圖表視覺化 | Canvas / ECharts，基本實現已有，需擴展 |
| Email 通知 | Model 已建，寄送邏輯待補 |

### 規劃中功能

- 評分與評論系統
- 交易洽談私訊
- 行動 App（React Native）

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

### API 端點總覽

| 分類 | 資源 | 端點 | 方法 |
|------|------|------|------|
| 認證 | 使用者 | `/api/accounts/bootstrap/` | POST |
| | 個人資料 | `/api/accounts/profile/` | GET |
| | 個人資料 | `/api/accounts/profile/` | PATCH |
| 書籍 | 列表 | `/api/books/` | GET |
| | 適用性 | `/api/books/applicabilities/` | GET |
| 刊登 | 列表 | `/api/listings/` | GET |
| | 最新 | `/api/listings/latest/` | GET |
| | 推薦 | `/api/listings/recommended/` | GET |
| | 詳情 | `/api/listings/<id>/` | GET |
| | 建立 | `/api/listings/` | POST |
| | 下架 | `/api/listings/<id>/off_shelf/` | POST |
| | 標售 | `/api/listings/<id>/mark_sold/` | POST |
| | 重上架 | `/api/listings/<id>/relist/` | POST |
| 預約 | 建立 | `/api/listings/<id>/requests/` | POST |
| | 接受 | `/api/listings/requests/<id>/accept/` | POST |
| | 拒絕 | `/api/listings/requests/<id>/reject/` | POST |
| | 取消 | `/api/listings/requests/<id>/cancel/` | POST |
| 通知 | 列表 | `/api/notifications/` | GET |
| | 未讀數 | `/api/notifications/unread-count/` | GET |
| | 標已讀 | `/api/notifications/<id>/read/` | PATCH |
| | 全部已讀 | `/api/notifications/read-all/` | PATCH |
| | 刪除 | `/api/notifications/<id>/` | DELETE |
| 系統 | 校區 | `/api/core/campuses/` | GET |
| | 學制 | `/api/core/program-types/` | GET |
| | 系所 | `/api/core/departments/` | GET |
| | 班級 | `/api/core/class-groups/` | GET |

詳細 API 規格請參閱 [API Documentation](docs/API.md)。

---

## 9. 課程進度對應

| 週次 | 課題 | 進度 | 說明 |
|------|------|------|------|
| W1–W2 | 需求分析 | 完成 | Use Case、ER 圖、專案規劃 |
| W3 | 資料庫 & Models | 完成 | 14 張表、ORM Model 實現 |
| W4 | Django MTV & View | 完成 | URL Router、FBV/CBV/GCBV，25+ API 端點 |
| W5 | Template & RWD | 完成 | 11+ Template、Bootstrap Grid、RWD 設計 |
| W6+ | 進階功能 | 進行中 | 圖表、Email、更多 API |

---

## 10. 開發指南

### 本地開發工作流

```bash
# 終端 1：後端
cd backend && python manage.py runserver

# 終端 2：前端
cd frontend && npm run dev
```

訪問前端：http://localhost:3000  
訪問後端 API：http://localhost:8000/api/

使用 Postman 測試 API 時，可參考 `docs/API.md` 中的端點定義。

### 代碼風格

| 語言 | 規範 |
|------|------|
| Python | PEP 8，使用 `flake8` 檢查 |
| JavaScript / TypeScript | ESLint + Prettier |
| HTML / CSS | 遵循 Bootstrap 5 規範 |

---

## 11. 授權

本專案採用 [MIT 授權條款](LICENSE)。

---

## 聯絡

- 專案網站：[ntubook.com](https://ntubook.com)（計劃中）
- 問題回報：[GitHub Issues](https://github.com/your-repo/ntub-usedbooks/issues)
