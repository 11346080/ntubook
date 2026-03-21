# NTUB 二手書平台 - 前端專案（Next.js）

## 📋 專案概述

這是一個前後端分離的 Next.js (App Router) 前端專案，旨在完全替代原有的 Django 模板渲染。所有 HTML、CSS 和 JavaScript 邏輯已轉換為 React 組件。

## 🏗️ 目錄結構

```
frontend/
├── app/
│   ├── components/                 # React 組件目錄
│   │   ├── Navbar.tsx             # 導航欄組件
│   │   ├── Footer.tsx             # 頁尾組件
│   │   ├── ListingCard.tsx        # 刊登卡片組件
│   │   ├── FilterSection.tsx      # 篩選欄組件
│   │   ├── Modal.tsx              # 彈窗組件
│   │   └── Pagination.tsx         # 分頁組件
│   │
│   ├── accounts/                   # 帳號相關頁面
│   │   ├── login/
│   │   │   └── page.tsx           # 登入頁面
│   │   └── register/
│   │       └── page.tsx           # 註冊頁面
│   │
│   ├── listings/
│   │   └── page.tsx               # 書籍列表頁面
│   │
│   ├── dashboard/
│   │   └── page.tsx               # 會員中心 / 個人區域
│   │
│   ├── notifications/
│   │   └── page.tsx               # 通知列表頁面
│   │
│   ├── layout.tsx                 # 根佈局（Navbar + Footer）
│   ├── globals.css                # 全域樣式 + Bootstrap
│   ├── page.tsx                   # 首頁
│   └── favicon.ico
│
├── public/                         # 靜態資源（圖片等）
├── package.json                   # 依賴管理
├── tsconfig.json                  # TypeScript 配置
├── next.config.ts                 # Next.js 配置
├── eslint.config.mjs              # ESLint 配置
└── README.md                       # 本檔案
```

## 🛠️ 已遷移的內容

### ✅ HTML 結構
- `base.html` → `app/layout.tsx` (導航欄和頁尾)
- `index.html` → `app/page.tsx` (首頁)
- `listings.html` → `app/listings/page.tsx` (書籍列表)
- `dashboard.html` → `app/dashboard/page.tsx` (會員中心)
- `accounts/login.html` → `app/accounts/login/page.tsx` (登入)
- `accounts/first_login.html` → `app/dashboard/page.tsx` (首次登入)
- `modals.html` → `app/components/Modal.tsx` (通用彈窗)
- `notifications/` → `app/notifications/page.tsx` (通知)

### ✅ CSS 樣式
- `base.css` → `app/globals.css` (全域樣式)
- `listings.css` → 整合至 `app/globals.css`
- `dashboard.css` → 整合至 `app/globals.css`
- `modals.css` → 整合至 `app/globals.css`

### ✅ Vanilla JS → React Hooks
- `listings.js` → `app/listings/page.tsx` (使用 `useState`, `useEffect`)
- `dashboard.js` → `app/dashboard/page.tsx` (標籤頁切換)
- `modals.js` → `app/components/Modal.tsx` (彈窗邏輯)

### 📦 第三方庫
- **Bootstrap 5.3.0**: 通過 npm install 引入，在 globals.css 導入
- **FontAwesome 6.4.0**: 通過 CDN 在 layout.tsx 引入
- **Google Fonts (Noto Sans TC)**: 在 layout.tsx 中引入

## 🚀 使用方式

### 1️⃣ 安裝依賴

在終端機執行以下命令（在 `frontend` 目錄中）：

```bash
npm install
```

或使用 yarn:

```bash
yarn install
```

### 2️⃣ 開發模式

啟動開發伺服器：

```bash
npm run dev
```

伺服器將運行於 `http://localhost:3000`

### 3️⃣ 生產構建

構建專案：

```bash
npm run build
npm start
```

### 4️⃣ 連接後端 API

目前所有 API 呼叫都被註釋為 `TODO`。要連接至 Django 後端，請：

1. 設定環境變數 (`.env.local`):
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

2. 在各頁面的 `useEffect` 中反註解 API 呼叫代碼

範例（listings/page.tsx）：
```javascript
useEffect(() => {
  const baseUrl = window.__BASEURL__ || 'http://localhost:8000';
  fetch(`${baseUrl}/api/listings/list/`)
    .then(res => res.json())
    .then(data => {
      setListings(data);
      setLoading(false);
    });
}, []);
```

## 📝 重要說明

### 頁面與路由
- Pages 使用 Next.js App Router 結構
- 所有頁面都用 `'use client'` 標記為客戶端組件
- 響應式設計基於 Bootstrap 5 Grid System

### 狀態管理
- 使用 React `useState` 進行局部狀態管理
- 使用 `useEffect` 進行副作用和 API 呼叫
- 未使用全局狀態管理工具（可根據需要後續加入 Redux、Zustand 等）

### 樣式
- 全域樣式在 `app/globals.css`
- Bootstrap CSS 在 globals.css 中導入
- 響應式媒體查詢已包含
- 所有顏色變數定義在 `:root` CSS 變數中

### TODO 清單
以下功能目前為佔位符，需要連接至後端 API：

1. 登入 / 登出
2. Google OAuth 認證
3. 書籍搜尋和篩選
4. 建立刊登
5. 預約請求
6. 通知管理
7. 用戶個人資料編輯

## 🔌 API 端點集成

後端 API 端點（已由 Django DRF 提供）：

```
GET    /api/accounts/profiles/          - 使用者檔案
GET    /api/books/list/                 - 書籍列表
GET    /api/books/applicabilities/      - 書籍適用對象
GET    /api/core/program-types/         - 學制
GET    /api/core/departments/           - 系所
GET    /api/core/class-groups/          - 班級
GET    /api/listings/list/              - 刊登列表
GET    /api/moderation/list/            - 檢舉案件
GET    /api/notifications/list/         - 通知
GET    /api/requests/list/              - 預約請求
```

## 🛣️ 路由映射

| 頁面 | 路由 | 文件 |
|------|------|------|
| 首頁 | `/` | `page.tsx` |
| 書籍列表 | `/listings` | `listings/page.tsx` |
| 會員中心 | `/dashboard` | `dashboard/page.tsx` |
| 登入 | `/accounts/login` | `accounts/login/page.tsx` |
| 註冊 | `/accounts/register` | `accounts/register/page.tsx` |
| 通知 | `/notifications` | `notifications/page.tsx` |

## 💡 下一步建議

1. **連接後端 API**: 反註解各頁面中的 `fetch` 邏輯
2. **加入認證**: 實作 JWT token 存儲和自動登出
3. **全局狀態**: 使用 Context API 或 Zustand 管理認證狀態
4. **錯誤處理**: 加強 API 錯誤捕捉和用戶反饋
5. **分頁**: 實現列表分頁功能
6. **搜尋和篩選**: 將前端篩選同步至後端查詢
7. **圖片上傳**: 實作書籍封面上傳功能

## 📦 已安裝的 npm 套件

```json
{
  "dependencies": {
    "next": "16.2.0",
    "react": "19.2.4",
    "react-dom": "19.2.4",
    "bootstrap": "^5.3.0"
  }
}
```

## 🐛 常見問題

### 問題：Bootstrap 樣式不生效
**解決**: 確保 `app/globals.css` 中導入了 Bootstrap：
```css
@import 'bootstrap/dist/css/bootstrap.min.css';
```

### 問題：字體不顯示
**解決**: 檢查 `layout.tsx` 中是否引入了 Google Fonts CDN

### 問題：API 連接失敗
**解決**: 檢查 CORS 設定和後端是否在運行，確保 `NEXT_PUBLIC_API_URL` 正確設定

## 📞 聯絡

如有任何問題或建議，請聯絡開發團隊。

---

**最後更新**: 2026-03-21
